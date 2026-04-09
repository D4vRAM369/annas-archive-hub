"""
Publicación de reportes en IPFS.

Estrategia de publicación (en orden de prioridad):
  1. Pinata (pinning service gratuito) — no requiere daemon local, el archivo
     queda vivo en la red pública aunque tu ordenador esté apagado.
  2. IPFS daemon local — fallback si Pinata no está configurado.

Para usar Pinata, configura en tu entorno (o en un archivo .env):
  PINATA_API_KEY=<tu_key>
  PINATA_SECRET_KEY=<tu_secret>
"""

import json
import os
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


class IPFSPublisher:
    def __init__(self):
        self.report_file = f"{DATA_DIR}/current_report.json"
        self.pinata_key    = os.getenv("PINATA_API_KEY", "")
        self.pinata_secret = os.getenv("PINATA_API_SECRET", "")

    # ── Público ──────────────────────────────────────────────────────────────

    def publish_report(self, active_domains, manual_domains):
        """
        Genera el reporte JSON y lo publica en IPFS.
        Devuelve el CID (hash) o None si falla todo.
        """
        self._write_report(active_domains, manual_domains)

        if self.pinata_key and self.pinata_secret:
            cid = self._pin_to_pinata(self.report_file)
            if cid:
                self._save_hash(cid)
                print(f"  [+] Pinneado en Pinata: {cid}")
                print(f"  [+] Acceso público: {PUBLIC_GATEWAYS[0].format(cid=cid)}")
                return cid
            print("  [!] Pinata falló, intentando daemon local...")

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

    # ── Privado ───────────────────────────────────────────────────────────────

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

    def _pin_to_pinata(self, filepath):
        """Sube el archivo a Pinata y devuelve el CID."""
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key":    self.pinata_key,
            "pinata_secret_api_key": self.pinata_secret,
        }
        try:
            with open(filepath, "rb") as f:
                response = http.post(url, files={"file": f}, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json().get("IpfsHash")
            print(f"  [!] Pinata error {response.status_code}: {response.text[:120]}")
        except Exception as e:
            print(f"  [!] Pinata excepción: {e}")
        return None

    def _publish_local(self):
        """Fallback: publica vía daemon IPFS local."""
        result = subprocess.run(
            ["ipfs", "add", "-Q", self.report_file],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            cid = result.stdout.strip()
            subprocess.run(["ipfs", "pin", "add", cid], capture_output=True)
            self._save_hash(cid)
            print(f"  [+] Publicado localmente: {cid}")
            print("  [!] Solo accesible mientras el daemon esté corriendo.")
            print("  [!] Configura PINATA_API_KEY para publicación permanente.")
            return cid
        print(f"  [!] IPFS local falló: {result.stderr[:120]}")
        return None

    def _save_hash(self, cid):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(IPFS_HASH_FILE, "w") as f:
            f.write(cid)
