#!/usr/bin/env python3
"""
Domain Tester Avanzado - Múltiples estrategias para evitar falsos negativos
"""

import requests
from curl_cffi import requests as curl_requests
import time

# Estrategias de prueba
STRATEGIES = [
    {
        "name": "curl_cffi_chrome",
        "func": lambda url: curl_requests.get(url, impersonate="chrome120", timeout=10)
    },
    {
        "name": "requests_firefox",
        "func": lambda url: requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }, timeout=10)
    }
]

def test_domain_advanced(domain):
    """Prueba un dominio con múltiples estrategias y verifica contenido."""
    url = f"https://{domain}"
    content_keywords = ["anna", "archive", "libgen", "download", "book", "library"]
    
    for strategy in STRATEGIES:
        try:
            response = strategy["func"](url)
            if response.status_code == 200:
                # Verificar contenido real
                content_lower = response.text.lower()
                for keyword in content_keywords:
                    if keyword in content_lower:
                        return True, f"{strategy['name']} - contenido verificado"
                return True, f"{strategy['name']} - código 200 (contenido no verificado)"
            elif response.status_code in [301, 302, 307, 308]:
                return True, f"{strategy['name']} - redirige a {response.headers.get('Location', '')}"
            elif response.status_code == 503:
                # 503 no es necesariamente un error, puede ser anti-bot
                # Segunda oportunidad con diferentes headers
                time.sleep(2)
                retry = strategy["func"](url)
                if retry.status_code == 200:
                    return True, f"{strategy['name']} - 503 inicial, luego 200"
        except Exception as e:
            continue
    
    return False, "No responde con ninguna estrategia"

# Lista de dominios a probar
test_domains = [
    "z-lib.gl",
    "go-to-library.sk",
    "welib.org",
    "z-lib.gd",
    "z-library.sk",
    "annas-archive.gl",
    "annas-archive.pk",
    "annas-archive.gd"
]

print("=== DOMAIN TESTER AVANZADO ===\n")
for domain in test_domains:
    success, reason = test_domain_advanced(domain)
    status = "✅ ACTIVO" if success else "❌ INACTIVO"
    print(f"{status} - {domain}: {reason}")