#!/usr/bin/env python3
"""
Publica el último reporte en IPFS sin rastrear ni probar.
Útil cuando ya tienes los dominios actualizados manualmente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import AUTO_VERIFIABLE, MANUAL_VERIFY
from core.domain_tester import DomainTester
from core.ipfs_publisher import IPFSPublisher

def main():
    print("=== PUBLICAR EN IPFS ===\n")
    
    tester = DomainTester()
    publisher = IPFSPublisher()
    
    print("[*] Probando dominios...")
    active = tester.test_multiple(AUTO_VERIFIABLE)
    
    print("[*] Publicando...")
    hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    
    if hash_id:
        print(f"\n✅ Publicado: {hash_id}")
        print(f"   Enlace: {publisher.get_ipfs_url(hash_id)}")
    else:
        print("\n❌ Error al publicar")

if __name__ == "__main__":
    main()
