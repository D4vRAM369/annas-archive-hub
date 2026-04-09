"""
Módulo para rastrear open-slum.org y extraer dominios candidatos.
"""

import re
from curl_cffi import requests
from config.settings import OPEN_SLUM_URLS, BROWSER_IMPERSONATION

# Patrones nombre → plantilla de dominio
_PATTERNS = [
    (r"Anna's Archive ([A-Z]{2,3})", "annas-archive.{code}"),
    (r"Libgen\+([A-Z]{2,3})",        "libgen.{code}"),
    (r"Libgen\+([A-Z]{2,3})",        "librarygenesis.{code}"),
    (r"Z-Library ([A-Z]{2,3})",      "z-lib.{code}"),
    (r"Z-Library ([A-Z]{2,3})",      "zlibrary.{code}"),
    (r'z-lib ([a-z]{2,3})',          "z-lib.{code}"),
    (r'1lib ([a-z]{2,3})',           "1lib.{code}"),
]

# Dominios con TLD característicos — sin grupo de captura para obtener dominio completo
_TLD_PATTERN = r'[a-z0-9\-]+\.(?:gl|gd|pk|vg|sk|la|bz)'


def crawl_open_slum():
    """
    Visita open-slum.org y extrae dominios candidatos.

    Returns:
        list[str]: Lista deduplicada de dominios (sin probar).
    """
    candidates = []

    for url in OPEN_SLUM_URLS:
        print(f"[*] Rastreando: {url}")
        try:
            r = requests.get(url, impersonate=BROWSER_IMPERSONATION, timeout=15)
            if r.status_code != 200:
                print(f"  [!] HTTP {r.status_code}")
                continue

            text = r.text

            # Patrones nombre → dominio construido
            for pattern, template in _PATTERNS:
                for match in re.findall(pattern, text):
                    candidates.append(template.format(code=match.lower()))

            # Dominios .sk directos
            for match in re.findall(r'([a-z0-9\-]+\.sk)', text):
                candidates.append(match.lower())

            # Cualquier dominio con TLD de archivo (sin grupo de captura → devuelve dominio completo)
            for match in re.findall(_TLD_PATTERN, text, re.IGNORECASE):
                candidates.append(match.lower())

        except Exception as e:
            print(f"  [!] Error: {e}")

    candidates = list(set(c.strip() for c in candidates if c and len(c) > 5))
    print(f"[+] Candidatos encontrados: {len(candidates)}")
    if candidates:
        print(f"[*] Muestra: {candidates[:10]}")

    return candidates
