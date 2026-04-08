#!/usr/bin/env python3
"""
Script principal de ejecución automática.
Actualiza dominios desde todas las fuentes y publica en IPFS.
Ideal para ejecutar con cron (ej: cada 6 horas).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import AUTO_VERIFIABLE, MANUAL_VERIFY
from core.domain_tester import DomainTester
from core.open_slum_crawler import crawl_open_slum
from core.social_crawler import SocialCrawler
from core.ipfs_publisher import IPFSPublisher


def main():
    print("=" * 50)
    print("   ANNA'S ARCHIVE HUB - EJECUCIÓN AUTOMÁTICA")
    print("=" * 50)
    print(f"Timestamp: {__import__('datetime').datetime.now()}\n")

    # 1. Rastrear open-slum
    print("[1/5] Rastreando open-slum...")
    slum_domains = crawl_open_slum()
    print(f"  [+] open-slum: {len(slum_domains)} candidatos")

    # 2. Rastrear fuentes sociales
    print("\n[2/5] Rastreando fuentes sociales...")
    sc = SocialCrawler()
    social_domains = sc.crawl_all()
    print(f"  [+] Sociales: {len(social_domains)} candidatos")

    # 3. Probar todos los candidatos
    all_candidates = list(dict.fromkeys(
        slum_domains + social_domains + list(AUTO_VERIFIABLE)
    ))
    print(f"\n[3/5] Probando {len(all_candidates)} dominios...")
    tester = DomainTester()
    active = tester.test_multiple(all_candidates)
    print(f"  [+] Activos: {len(active)}")

    # 4. Publicar en IPFS
    print("\n[4/5] Publicando en IPFS...")
    publisher = IPFSPublisher()
    hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    if hash_id:
        print(f"  [+] CID: {hash_id}")
        for url in publisher.get_public_urls(hash_id):
            print(f"  [+] {url}")
    else:
        print("  [!] Error al publicar en IPFS")

    # 5. Guardar log
    print("\n[5/5] Guardando log...")
    os.makedirs("logs", exist_ok=True)
    with open("logs/update.log", "a") as f:
        from datetime import datetime
        f.write(
            f"{datetime.now()} | cid={hash_id} | activos={len(active)}"
            f" | slum={len(slum_domains)} | social={len(social_domains)}\n"
        )

    print("\n✅ Ejecución completada")


if __name__ == "__main__":
    main()
