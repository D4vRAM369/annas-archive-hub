#!/usr/bin/env python3
"""
Script principal de ejecución automática.
Actualiza dominios, prueba y publica en IPFS.
Ideal para ejecutar con cron.
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import AUTO_VERIFIABLE, MANUAL_VERIFY
from core.domain_tester import DomainTester
from core.open_slum_crawler import crawl_open_slum
from core.ipfs_publisher import IPFSPublisher
from core.voter import Voter

def main():
    print("=" * 50)
    print("   ANNA'S ARCHIVE HUB - EJECUCIÓN AUTOMÁTICA")
    print("=" * 50)
    print(f"Timestamp: {__import__('datetime').datetime.now()}\n")
    
    # 1. Rastrear open-slum para encontrar nuevos dominios
    print("[1/4] Rastreando open-slum...")
    new_domains = crawl_open_slum()
    if new_domains:
        print(f"  [+] Nuevos dominios encontrados: {new_domains}")
        # Aquí podrías añadirlos automáticamente al sistema de votación
    else:
        print("  [!] No se encontraron nuevos dominios")
    
    # 2. Probar dominios verificables automáticamente
    print("\n[2/4] Probando dominios automáticos...")
    tester = DomainTester()
    active = tester.test_multiple(AUTO_VERIFIABLE)
    print(f"  [+] Activos: {len(active)}")
    
    # 3. Publicar reporte en IPFS
    print("\n[3/4] Publicando en IPFS...")
    publisher = IPFSPublisher()
    hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    
    if hash_id:
        print(f"  [+] Hash IPFS: {hash_id}")
        print(f"  [+] Enlace: {publisher.get_ipfs_url(hash_id)}")
    else:
        print("  [!] Error al publicar en IPFS")
    
    # 4. Guardar log
    print("\n[4/4] Guardando log...")
    with open("logs/update.log", "a") as f:
        from datetime import datetime
        f.write(f"{datetime.now()} - Hash: {hash_id} - Activos: {len(active)}\n")
    
    print("\n✅ Ejecución completada")

if __name__ == "__main__":
    # Crear carpeta de logs si no existe
    os.makedirs("logs", exist_ok=True)
    main()
