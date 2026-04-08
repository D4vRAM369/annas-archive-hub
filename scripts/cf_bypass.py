#!/usr/bin/env python3
"""
Cloudflare Bypass Tester - Para dominios con protección avanzada
"""

import cloudscraper

print("=== CLOUDFLARE BYPASS TESTER ===\n")

# Crear el scraper
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=15
)

# Dominios a probar
domains = [
    "https://z-lib.gl",
    "https://go-to-library.sk",
    "https://z-lib.gd",
    "https://z-library.sk",
    "https://welib.org"
]

for url in domains:
    print(f"[*] Probando: {url}")
    try:
        response = scraper.get(url, timeout=30)
        if response.status_code == 200:
            if "just a moment" not in response.text.lower():
                print(f"  ✅ ACTIVO - {url}")
            else:
                print(f"  ⚠️ VERIFICACIÓN - {url}")
        else:
            print(f"  ❌ INACTIVO - {url} (código {response.status_code})")
    except Exception as e:
        print(f"  ❌ ERROR - {url}: {str(e)[:50]}")
