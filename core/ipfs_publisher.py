"""
Publicación de reportes en IPFS con rotación automática de pins antiguos.

Estrategia:
  1. Pinata (pinning service) — ruta principal. Marca cada pin con metadata
     que identifica el proyecto para poder rotar después.
  2. Rotación: tras un pin exitoso, lista los pins del proyecto en Pinata,
     conserva los N más recientes y despinnea el resto.
  3. Fallback local: solo se intenta si el binario `ipfs` existe. Si no,
     degrada limpiamente sin lanzar excepción.

Variables de entorno:
  PINATA_API_KEY          — obligatoria para usar Pinata
  PINATA_API_SECRET       — obligatoria para usar Pinata
  PINATA_KEEP_LAST        — opcional, cuántos pins conservar (default 10)
"""
import json
import os
import shutil
import subprocess
from datetime import datetime

import requests as http

from config.settings import DATA_DIR, IPFS_GATEWAY, IPFS_HASH_FILE

# Gateways públicos donde el CID será accesible una vez pinneado en Pinata
PUBLIC_GATEWAYS = [
    "https://ipfs.io/ipfs/{cid}",
    "https://cloudflare-ipfs.com/ipfs/{cid}",
    "https://dweb.link/ipfs/{cid}",
    "https://gateway.pinata.cloud/ipfs/{cid}",
]

# Identificador del proyecto en la metadata de Pinata.
# Se usa para no tocar pins de otros proyectos que compartan la cuenta.
PROJECT_TAG = "annas-archive-hub"

PINATA_API = "https://api.pinata.cloud"


class IPFSPublisher:
    def __init__(self):
        self.report_file = f"{DATA_DIR}/current_report.json"
        self.pinata_key = os.getenv("PINATA_API_KEY", "")
        self.pinata_secret = os.getenv("PINATA_API_SECRET", "")
        try:
            self.keep_last = int(os.getenv("PINATA_KEEP_LAST", "10"))
        except ValueError:
            self.keep_last = 10

    # ── Público ────────────────────────────────────────────────────────────
    def publish_report(self, active_domains, manual_domains):
        """
        Genera el reporte JSON y lo publica en IPFS.
        Devuelve el CID (hash) o None si falla todo.
        Nunca lanza excepción hacia fuera: los errores se registran y se
        devuelve None para que el pipeline pueda decidir qué hacer.
        """
        try:
            self._write_report(active_domains, manual_domains)
        except Exception as e:
            print(f"  [!] No se pudo escribir el reporte local: {e}")
            return None

        cid = None
        if self.pinata_key and self.pinata_secret:
            cid = self._pin_to_pinata(self.report_file)
            if cid:
                self._save_hash(cid)
                print(f"  [+] Pinneado en Pinata: {cid}")
                print(f"  [+] Acceso público: {PUBLIC_GATEWAYS[0].format(cid=cid)}")
                # Rotación: liberar cuota borrando pins antiguos del proyecto
                self._rotate_old_pins()
                return cid
            print("  [!] Pinata falló, intentando daemon local...")
        else:
            print("  [!] PINATA_API_KEY/SECRET no configurados. Saltando Pinata.")

        return self._publish_local()

    def get_current_hash(self):
        """Devuelve el último CID publicado."""
        try:
            with open(IPFS_HASH_FILE) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def get_ipfs_url(self, cid):
        """URL del gateway local (para uso con daemon corriendo)."""
        return f"{IPFS_GATEWAY}{cid}"

    def get_public_urls(self, cid=None):
        """Lista de URLs públicas donde el reporte debería estar disponible."""
        cid = cid or self.get_current_hash()
        if not cid:
            return []
        return [gw.format(cid=cid) for gw in PUBLIC_GATEWAYS]

    # ── Privado ────────────────────────────────────────────────────────────
    def _write_report(self, active_domains, manual_domains):
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_auto": active_domains,
            "manual_verify": manual_domains,
            "gateways": [gw.split("/ipfs/")[0] for gw in PUBLIC_GATEWAYS],
            "note": "manual_verify requiere abrir en navegador (protección Cloudflare)",
        }
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _pinata_headers(self):
        return {
            "pinata_api_key": self.pinata_key,
            "pinata_secret_api_key": self.pinata_secret,
        }

    def _pin_to_pinata(self, filepath):
        """Sube el archivo a Pinata con metadata del proyecto y devuelve el CID."""
        url = f"{PINATA_API}/pinning/pinFileToIPFS"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        pinata_metadata = {
            "name": f"{PROJECT_TAG}-report-{timestamp}",
            "keyvalues": {
                "project": PROJECT_TAG,
                "type": "domain-report",
            },
        }
        try:
            with open(filepath, "rb") as f:
                response = http.post(
                    url,
                    files={"file": f},
                    data={"pinataMetadata": json.dumps(pinata_metadata)},
                    headers=self._pinata_headers(),
                    timeout=30,
                )
            if response.status_code == 200:
                return response.json().get("IpfsHash")
            print(f"  [!] Pinata error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"  [!] Pinata excepción: {e}")
        return None

    def _rotate_old_pins(self):
        """
        Lista los pins del proyecto, conserva los self.keep_last más recientes
        y despinnea el resto. Errores aquí NO deben romper el pipeline: la
        publicación ya fue exitosa, la rotación es best-effort.
        """
        try:
            pins = self._list_project_pins()
        except Exception as e:
            print(f"  [!] No se pudo listar pins para rotación: {e}")
            return

        if len(pins) <= self.keep_last:
            print(f"  [*] Rotación: {len(pins)} pins ≤ keep_last={self.keep_last}, nada que borrar.")
            return

        # Orden descendente por fecha (más reciente primero)
        pins.sort(key=lambda p: p.get("date_pinned", ""), reverse=True)
        to_delete = pins[self.keep_last:]

        print(f"  [*] Rotación: conservando {self.keep_last}, despinneando {len(to_delete)}...")
        ok, fail = 0, 0
        for p in to_delete:
            cid = p.get("ipfs_pin_hash")
            if not cid:
                continue
            if self._unpin(cid):
                ok += 1
            else:
                fail += 1
        print(f"  [+] Rotación completada. OK: {ok}, fallos: {fail}")

    def _list_project_pins(self):
        """Lista todos los pins activos etiquetados con este proyecto."""
        headers = self._pinata_headers()
        all_pins = []
        offset = 0
        page_size = 1000
        # Filtro por metadata: solo pins con keyvalues.project == PROJECT_TAG
        metadata_filter = json.dumps({
            "keyvalues": {"project": {"value": PROJECT_TAG, "op": "eq"}}
        })
        while True:
            params = {
                "status": "pinned",
                "pageLimit": page_size,
                "pageOffset": offset,
                "metadata": metadata_filter,
            }
            r = http.get(
                f"{PINATA_API}/data/pinList",
                headers=headers,
                params=params,
                timeout=30,
            )
            if r.status_code != 200:
                raise RuntimeError(f"pinList {r.status_code}: {r.text[:150]}")
            data = r.json()
            rows = data.get("rows", [])
            all_pins.extend(rows)
            if len(rows) < page_size:
                break
            offset += page_size
        return all_pins

    def _unpin(self, cid):
        try:
            r = http.delete(
                f"{PINATA_API}/pinning/unpin/{cid}",
                headers=self._pinata_headers(),
                timeout=30,
            )
            if r.status_code == 200:
                return True
            print(f"    [!] Unpin {cid} falló: {r.status_code} {r.text[:100]}")
        except Exception as e:
            print(f"    [!] Unpin {cid} excepción: {e}")
        return False

    def _publish_local(self):
        """
        Fallback: publica vía daemon IPFS local.
        Si el binario `ipfs` no está en PATH (típico en GitHub Actions),
        se salta sin lanzar excepción.
        """
        ipfs_bin = shutil.which("ipfs")
        if ipfs_bin is None:
            print("  [!] Binario 'ipfs' no encontrado en PATH.")
            print("  [!] Saltando fallback local (entorno CI o daemon no instalado).")
            return None
        try:
            result = subprocess.run(
                [ipfs_bin, "add", "-Q", self.report_file],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                cid = result.stdout.strip()
                subprocess.run([ipfs_bin, "pin", "add", cid], capture_output=True, timeout=60)
                self._save_hash(cid)
                print(f"  [+] Publicado localmente: {cid}")
                print("  [!] Solo accesible mientras el daemon esté corriendo.")
                return cid
            print(f"  [!] IPFS local falló: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("  [!] IPFS local timeout.")
        except Exception as e:
            print(f"  [!] IPFS local excepción: {e}")
        return None

    def _save_hash(self, cid):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(IPFS_HASH_FILE, "w") as f:
            f.write(cid)
