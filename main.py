#!/usr/bin/env python3
"""
Anna's Archive Hub - Punto de entrada principal
"""

import os
from config.settings import AUTO_VERIFIABLE as STATIC_DOMAINS, MANUAL_VERIFY
from core.domain_tester import DomainTester
from core.voter import Voter
from core.ipfs_publisher import IPFSPublisher
from core.social_crawler import SocialCrawler
from core.open_slum_crawler import crawl_open_slum

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                        ANNA'S ARCHIVES HUB                                ║")
    print("║                                                                            ║")
    print("║             Self-updating domain tracker + IPFS immortality                ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

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
        print("  8. 🌐 Rastrear open-slum y buscar nuevos dominios")
        print("  9. 🔍 Rastrear fuentes sociales (Reddit, X, Telegram, Mastodon)")
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
                    votes = voter.domains.get(d, {}).get("votes", 0)
                    print(f"  {i+1}. {d} (votos: {votes})")
                try:
                    idx = int(input("\nElige número para votar: ")) - 1
                    if 0 <= idx < len(pending):
                        voter.vote(pending[idx])
                except (ValueError, IndexError):
                    print("  [!] Entrada no válida.")
            input("\nPresiona Enter...")
        
        elif option == "5":
            pending = voter.get_pending()
            if pending:
                print("\nDominios pendientes:")
                for d in pending:
                    votes = voter.domains.get(d, {}).get("votes", 0)
                    print(f"  • {d} (votos: {votes})")
            else:
                print("\n[!] No hay dominios pendientes.")
            input("\nPresiona Enter...")
        
        elif option == "6":
            print("\n[*] Publicando en IPFS...")
            active = tester.test_multiple(STATIC_DOMAINS + voter.get_verified())
            publisher.publish_report(active, MANUAL_VERIFY)
            input("\nPresiona Enter...")
        
        elif option == "7":
            hash_id = publisher.get_current_hash()
            if hash_id:
                print(f"\n[+] CID: {hash_id}")
                print("\n[+] Acceso público (no necesitan daemon):")
                for url in publisher.get_public_urls(hash_id):
                    print(f"    {url}")
                print("\n[+] Acceso local (necesita daemon corriendo):")
                print(f"    {publisher.get_ipfs_url(hash_id)}")
            else:
                print("\n[!] Aún no hay hash publicado.")
                print("    Usa la opción 6 para publicar.")
            input("\nPresiona Enter...")
        
        elif option == "8":
            print("\n[🌐] Rastreando open-slum.org...")
            candidates = crawl_open_slum()
            if candidates:
                print(f"\n[*] Probando {len(candidates)} candidatos...")
                active = tester.test_multiple(candidates)
                print(f"\n[+] Dominios activos encontrados: {len(active)}")
                for url in active:
                    print(f"    {url}")
                    add = input(f"\n¿Añadir {url} al sistema de votación? (s/n): ").strip().lower()
                    if add == 's':
                        domain = url.replace("https://", "").split('/')[0]
                        voter.propose(domain, proposed_by="open-slum")
                        print(f"[+] Añadido: {domain}")
            else:
                print("[!] No se encontraron nuevos candidatos.")
            input("\nPresiona Enter...")
        
        elif option == "9":
            print("\n[🔍] Rastreando fuentes sociales...")
            sc = SocialCrawler()
            candidates = sc.crawl_all()
            if candidates:
                print(f"\n[*] Probando {len(candidates)} candidatos...")
                active = tester.test_multiple(candidates)
                print(f"\n[+] Dominios activos encontrados: {len(active)}")
                for url in active:
                    print(f"    {url}")
                    add = input(f"\n¿Añadir {url} al sistema de votación? (s/n): ").strip().lower()
                    if add == 's':
                        domain = url.replace("https://", "").split('/')[0]
                        voter.propose(domain, proposed_by="social-crawler")
                        print(f"[+] Propuesto: {domain}")
            else:
                print("[!] No se encontraron candidatos en fuentes sociales.")
            input("\nPresiona Enter...")

        elif option == "0":
            print("\n[+] ¡Hasta luego!")
            break
        
        else:
            print("\n[!] Opción no válida.")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
