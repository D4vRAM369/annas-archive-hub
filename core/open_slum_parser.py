#!/usr/bin/env python3
"""
Open SLUM Link Extractor - Extrae TODOS los enlaces de open-slum.org y .pages.dev
"""

import re
from curl_cffi import requests
from urllib.parse import urlparse, urljoin

URLS = [
    "https://open-slum.org",
    "https://open-slum.pages.dev"
]

def extract_all_links(html, base_url):
    """Extrae todos los enlaces (href) del HTML."""
    # Patrón para encontrar href="..."
    pattern = r'href=["\'](.*?)["\']'
    links = re.findall(pattern, html)
    
    # También buscar enlaces en texto plano (dominios sueltos)
    domain_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-z]{2,})'
    domain_links = re.findall(domain_pattern, html)
    
    # Limpiar y completar URLs relativas
    full_links = []
    for link in links:
        if link.startswith('/'):
            full_links.append(urljoin(base_url, link))
        elif link.startswith('http'):
            full_links.append(link)
        elif '.' in link and '/' not in link:
            full_links.append(f"https://{link}")
    
    full_links.extend(domain_links)
    
    # Eliminar duplicados
    return list(set(full_links))

def is_relevant_url(url):
    """Filtra URLs que no son relevantes (anuncios, redes sociales, etc.)."""
    exclude = ['twitter.com', 'facebook.com', 'github.com', 'youtube.com', 
               'discord', 'telegram', 'reddit', 'google', 'cloudflare',
               'bootstrap', 'jquery', 'fontawesome', 'cdn', 'cookie']
    for ex in exclude:
        if ex in url.lower():
            return False
    return True

def test_url(url):
    """Prueba si la URL responde."""
    try:
        r = requests.get(url, impersonate="chrome120", timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    print("\n=== OPEN SLUM LINK EXTRACTOR ===\n")
    all_links = []
    
    for url in URLS:
        print(f"[*] Analizando: {url}")
        try:
            response = requests.get(url, impersonate="chrome120", timeout=15)
            if response.status_code == 200:
                links = extract_all_links(response.text, url)
                print(f"  [+] Enlaces encontrados: {len(links)}")
                all_links.extend(links)
            else:
                print(f"  [!] Error HTTP {response.status_code}")
        except Exception as e:
            print(f"  [!] Error: {e}")
    
    # Limpiar duplicados y filtrar
    all_links = list(set(all_links))
    relevant_links = [l for l in all_links if is_relevant_url(l)]
    
    print(f"\n[*] Total enlaces únicos: {len(all_links)}")
    print(f"[*] Enlaces relevantes: {len(relevant_links)}")
    
    # Mostrar enlaces relevantes
    print("\n[+] Enlaces encontrados:")
    for link in relevant_links:
        print(f"    {link}")
    
    # Probar cuáles funcionan
    print("\n[*] Probando enlaces activos...")
    active = []
    for link in relevant_links:
        if test_url(link):
            active.append(link)
            print(f"  ✅ {link}")
        else:
            print(f"  ❌ {link}")
    
    print(f"\n[+] Enlaces activos: {len(active)}")
    for link in active:
        print(f"    {link}")

if __name__ == "__main__":
    main()
