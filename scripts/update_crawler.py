#!/usr/bin/env python3
"""
Script automático para actualizar dominios y publicar en IPFS.
Ideal para ejecutar en cron (ej: cada 6 horas).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import AUTO_VERIFIABLE, MANUAL_VERIFY
from core.domain_tester import DomainTester
from core.open_slum_crawler import crawl_open_slum
from core.ipfs_publisher import IPFSPublisher

def main():
    print("=== ACTUALIZACIÓN AUTOMÁTICA ===\n")
    
    # 1. Rastrear open-slum para encontrar nuevos dominios
    print("[*] Rastreando open-slum...")
    new_domains = crawl_open_slum()
    print(f"  [+] Dominios encontrados: {new_domains}")
    
    # 2. Probar dominios automáticos
    print("\n[*] Probando dominios verificables...")
    tester = DomainTester()
    active = tester.test_multiple(AUTO_VERIFIABLE)
    
    # 3. Publicar en IPFS
    print("\n[*] Publicando en IPFS...")
    publisher = IPFSPublisher()
    hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    
    if hash_id:
        print(f"\n✅ Publicado en IPFS: {hash_id}")
        print(f"   Enlace: {publisher.get_ipfs_url(hash_id)}")
    else:
        print("\n❌ Error al publicar en IPFS")

if __name__ == "__main__":
    main()
