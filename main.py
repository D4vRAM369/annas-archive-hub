#!/usr/bin/env python3
"""
Anna's Archive Hub - Punto de entrada principal
"""

import os
from config import STATIC_DOMAINS
from core.domain_tester import DomainTester
from core.voter import Voter
from core.ipfs_publisher import IPFSPublisher

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("=" * 50)
    print("    ANNA'S ARCHIVE - HUB")
    print("=" * 50)
    print("  Rastrea, vota y comparte dominios activos.")
    print("  Los datos se publican en IPFS para siempre.")
    print("=" * 50)

def main():
    tester = DomainTester()
    voter = Voter()
    publisher = IPFSPublisher()
    
    while True:
        clear_screen()
        print_header()
        print("\n  1. Probar dominios estáticos")
        print("  2. Probar todos los dominios (estáticos + verificados)")
        print("  3. Añadir un dominio manualmente")
        print("  4. Votar por un dominio")
        print("  5. Ver dominios pendientes")
        print("  6. Publicar reporte en IPFS")
        print("  7. Mostrar último hash IPFS")
        print("  0. Salir")
        print("-" * 50)
        
        option = input("Elige una opción: ").strip()
        
        if option == "1":
            print("\n[*] Probando dominios estáticos...")
            active = tester.test_multiple(STATIC_DOMAINS)
            print(f"\n[+] Activos: {len(active)}")
            for url in active:
                print(f"    {url}")
            input("\nPresiona Enter...")
        
        elif option == "2":
            all_domains = STATIC_DOMAINS + voter.get_verified()
            print(f"\n[*] Probando {len(all_domains)} dominios...")
            active = tester.test_multiple(all_domains)
            print(f"\n[+] Activos: {len(active)}")
            input("\nPresiona Enter...")
        
        elif option == "3":
            domain = input("\nDominio (ej: annas-archive.xyz): ").strip()
            if domain:
                voter.propose(domain)
            input("\nPresiona Enter...")
        
        elif option == "4":
            pending = voter.get_pending()
            if not pending:
                print("\n[!] No hay dominios pendientes.")
            else:
                print("\nDominios pendientes:")
                for i, d in enumerate(pending):
                    print(f"  {i+1}. {d}")
                try:
                    idx = int(input("\nElige número para votar: ")) - 1
                    if 0 <= idx < len(pending):
                        voter.vote(pending[idx])
                except:
                    pass
            input("\nPresiona Enter...")
        
        elif option == "5":
            pending = voter.get_pending()
            if pending:
                print("\nDominios pendientes:")
                for d in pending:
                    print(f"  • {d}")
            else:
                print("\n[!] No hay dominios pendientes.")
            input("\nPresiona Enter...")
        
        elif option == "6":
            print("\n[*] Publicando en IPFS...")
            active = tester.test_multiple(STATIC_DOMAINS + voter.get_verified())
            publisher.publish(active)
            input("\nPresiona Enter...")
        
        elif option == "7":
            hash_id = publisher.get_last_hash()
            if hash_id:
                print(f"\n[+] Último hash: {hash_id}")
                print(f"    http://localhost:8080/ipfs/{hash_id}")
            else:
                print("\n[!] No hay hash publicado aún.")
            input("\nPresiona Enter...")
        
        elif option == "0":
            print("\n[+] ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
