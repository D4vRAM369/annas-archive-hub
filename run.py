#!/usr/bin/env python3
"""
Script principal de ejecución automática.
Actualiza dominios desde todas las fuentes y publica en IPFS.
Optimizado para GitHub Actions y sincronización con la DB.
"""

import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import AUTO_VERIFIABLE, MANUAL_VERIFY, BLOCKED_DOMAINS
from core.domain_tester import DomainTester
from core.open_slum_crawler import crawl_open_slum
from core.social_crawler import SocialCrawler
from core.ipfs_publisher import IPFSPublisher
from core.voter import Voter


def update_readme(cid):
    """Actualiza el CID en los archivos README (inglés y español)."""
    files = ["README.md", "README.es.md"]

    for filename in files:
        if not os.path.exists(filename):
            continue

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex para encontrar el CID (asumiendo formato Qm...)
        # Busca patrones tipo `**Current CID:** `Qm...` o `CID actual: `Qm...`
        new_content = re.sub(
            r"((?:Current CID:|CID actual:)\*\*? `)(Qm[a-zA-Z0-9]+)(`)",
            r"\1" + cid + r"\3",
            content
        )

        # También actualizar los links de IPFS en las tablas
        new_content = re.sub(
            r"/ipfs/Qm[a-zA-Z0-9]+",
            f"/ipfs/{cid}",
            new_content
        )

        if content != new_content:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[+] {filename} actualizado con el nuevo CID")
        else:
            print(f"[*] {filename} ya estaba actualizado o no se encontró el patrón")


def main():
    print("=" * 50)
    print("   ANNA'S ARCHIVE HUB - EJECUCIÓN AUTOMÁTICA")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}\n")

    voter = Voter()
    tester = DomainTester()
    publisher = IPFSPublisher()

    # 1. Rastrear candidatos
    print("[1/5] Rastreando candidatos...")
    slum_domains = crawl_open_slum()
    sc = SocialCrawler()
    social_domains = sc.crawl_all()

    # 2. Obtener dominios conocidos de la base de datos
    verified_domains = voter.get_verified()
    print(f"  [+] Dominios verificados en DB: {len(verified_domains)}")

    # 3. Consolidar y Probar
    # Combinamos: estáticos + verificados en DB + nuevos candidatos de crawlers
    all_candidates = list(dict.fromkeys(
        slum_domains + social_domains + list(AUTO_VERIFIABLE) + verified_domains
    ))

    # Filtrar bloqueados ANTES de testear: ni siquiera queremos gastar una
    # petición de red contra un dominio ya confirmado como malicioso o ruido.
    blocked_found = [d for d in all_candidates if d in BLOCKED_DOMAINS]
    if blocked_found:
        print(f"  [!] Ignorando {len(blocked_found)} dominio(s) bloqueado(s): {blocked_found}")
    all_candidates = [d for d in all_candidates if d not in BLOCKED_DOMAINS]

    print(f"\n[2/5] Probando {len(all_candidates)} dominios...")
    active = tester.test_multiple(all_candidates)
    print(f"  [+] Activos encontrados: {len(active)}")

    # 4. Auto-proponer nuevos al sistema de votos
    # Si un crawler encontró algo que no teníamos, lo metemos en la DB
    for url in active:
        domain = url.replace("https://", "").split('/')[0]
        if domain not in AUTO_VERIFIABLE and domain not in verified_domains:
            voter.propose(domain, proposed_by="auto-crawler")

    # 5. Publicar en IPFS
    print("\n[3/5] Publicando en IPFS...")
    try:
        hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    except Exception as e:
        print(f"[!] Excepción inesperada en publish_report: {e}")
        hash_id = None

    if hash_id is None:
        print("[!] No se obtuvo CID nuevo (Pinata falló y no hay daemon IPFS local).")
        print("[!] Manteniendo el CID anterior si existe. El pipeline continúa.")
        previous = publisher.get_current_hash()
        if previous:
            print(f"[*] CID anterior conservado: {previous}")
            hash_id = previous
        else:
            print("[!] No hay CID previo. Los steps siguientes que dependan de él pueden fallar.")

    if hash_id:
        print(f"  [+] CID: {hash_id}")
        # 6. Actualizar README
        print("\n[4/5] Actualizando documentación...")
        update_readme(hash_id)
    else:
        print("  [!] Error al publicar en IPFS")

    # 7. Guardar log
    print("\n[5/5] Guardando log...")
    os.makedirs("logs", exist_ok=True)
    with open("logs/update.log", "a") as f:
        f.write(
            f"{datetime.now()} | cid={hash_id} | activos={len(active)}"
            f" | slum={len(slum_domains)} | social={len(social_domains)}\n"
        )

    print("\n✅ Ejecución completada")


if __name__ == "__main__":
    main()