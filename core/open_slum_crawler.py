"""
Crawler para open-slum.org - Extrae dominios automáticamente
"""

import re
from curl_cffi import requests
from config.settings import OPEN_SLUM_URLS

def crawl_open_slum():
    """
    Extrae todos los dominios candidatos de open-slum.org
    Returns:
        list: Lista de dominios encontrados
    """
    candidates = []
    
    for url in OPEN_SLUM_URLS:
        try:
            response = requests.get(url, impersonate="chrome120", timeout=15)
            if response.status_code == 200:
                # Extraer patrones como "annas-archive.gl", "libgen.bz", etc.
                patterns = [
                    r'[a-z0-9\-]+\.(gl|gd|pk|vg|li|bz|la|sk)',
                    r'anna[s]?\-archive\.[a-z]{2,3}',
                    r'z\-lib\.[a-z]{2,3}',
                    r'welib\.org'
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    candidates.extend([m.lower() for m in matches])
        except Exception as e:
            print(f"Error rastreando {url}: {e}")
    
    return list(set(candidates))
