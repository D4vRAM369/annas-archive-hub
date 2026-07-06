"""
Script one-shot para limpiar pins antiguos en Pinata.

Uso:
    python cleanup_pinata.py --keep 10 --dry-run    # ver qué haría
    python cleanup_pinata.py --keep 10              # ejecutar de verdad

Requiere las mismas variables de entorno que ipfs_publisher.py:
    PINATA_API_KEY
    PINATA_API_SECRET
"""
import argparse
import os
import sys
import time
import requests

PINATA_API = "https://api.pinata.cloud"


def list_all_pins(api_key: str, api_secret: str):
    """Devuelve TODOS los pins activos de la cuenta, paginando."""
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }
    all_pins = []
    offset = 0
    page_size = 1000  # máximo permitido por la API
    while True:
        params = {
            "status": "pinned",
            "pageLimit": page_size,
            "pageOffset": offset,
        }
        r = requests.get(f"{PINATA_API}/data/pinList", headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print(f"[!] Error listando pins ({r.status_code}): {r.text[:200]}")
            sys.exit(1)
        data = r.json()
        rows = data.get("rows", [])
        all_pins.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size
    return all_pins


def unpin(cid: str, api_key: str, api_secret: str) -> bool:
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }
    r = requests.delete(f"{PINATA_API}/pinning/unpin/{cid}", headers=headers, timeout=30)
    if r.status_code == 200:
        return True
    print(f"    [!] Fallo unpin {cid}: {r.status_code} {r.text[:120]}")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", type=int, default=10,
                        help="Cuántos pins más recientes conservar (por fecha).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Muestra qué haría sin borrar nada.")
    parser.add_argument("--name-filter", type=str, default="current_report.json",
                        help="Solo actúa sobre pins cuyo nombre coincida. "
                             "Usa '*' para ignorar el filtro y actuar sobre TODOS los pins.")
    args = parser.parse_args()

    api_key = os.getenv("PINATA_API_KEY", "")
    api_secret = os.getenv("PINATA_API_SECRET", "")
    if not api_key or not api_secret:
        print("[!] Falta PINATA_API_KEY o PINATA_API_SECRET en el entorno.")
        sys.exit(1)

    print(f"[*] Listando todos los pins de la cuenta...")
    pins = list_all_pins(api_key, api_secret)
    print(f"[+] Total pins en la cuenta: {len(pins)}")

    if args.name_filter != "*":
        filtered = [p for p in pins if p.get("metadata", {}).get("name") == args.name_filter]
        print(f"[+] Pins con nombre '{args.name_filter}': {len(filtered)}")
    else:
        filtered = pins
        print(f"[!] Filtro desactivado — actuando sobre TODOS los pins.")

    # Orden descendente por fecha de pin (más reciente primero)
    filtered.sort(key=lambda p: p.get("date_pinned", ""), reverse=True)

    to_keep = filtered[: args.keep]
    to_delete = filtered[args.keep:]

    print(f"\n[+] Conservar (últimos {args.keep} por fecha):")
    for p in to_keep:
        print(f"    KEEP  {p.get('date_pinned', '?')[:19]}  {p['ipfs_pin_hash']}  {p.get('size', '?')}B")

    print(f"\n[+] Despinnear ({len(to_delete)} pins):")
    for p in to_delete:
        print(f"    DROP  {p.get('date_pinned', '?')[:19]}  {p['ipfs_pin_hash']}  {p.get('size', '?')}B")

    if not to_delete:
        print("\n[+] Nada que borrar. Fin.")
        return

    total_size = sum(p.get("size", 0) for p in to_delete)
    print(f"\n[*] Espacio a liberar: {total_size / 1024 / 1024:.2f} MB")

    if args.dry_run:
        print("\n[*] --dry-run activado, no se borra nada.")
        return

    confirm = input(f"\n¿Confirmar borrado de {len(to_delete)} pins? [y/N]: ").strip().lower()
    if confirm != "y":
        print("[*] Abortado.")
        return

    ok, fail = 0, 0
    for i, p in enumerate(to_delete, 1):
        cid = p["ipfs_pin_hash"]
        print(f"  [{i}/{len(to_delete)}] Unpin {cid}...", end=" ", flush=True)
        if unpin(cid, api_key, api_secret):
            ok += 1
            print("OK")
        else:
            fail += 1
        # Pequeña pausa para no reventar rate limits
        time.sleep(0.3)

    print(f"\n[+] Terminado. OK: {ok}, fallos: {fail}")


if __name__ == "__main__":
    main()
