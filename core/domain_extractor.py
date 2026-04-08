# core/domain_extractor.py
"""
Extrae dominios de texto libre usando patrones conocidos.
Funciona sobre cualquier fuente: Reddit, Telegram, HTML, etc.
"""

import re

# Servicios conocidos y sus variantes de nombre
_KNOWN_PREFIXES = r'(?:annas?-?archive|z-lib(?:rary)?|libgen|librarygenesis|1lib|go-to-library|welib|shadowlib)'

# TLDs que estos servicios suelen usar
_KNOWN_TLDS = r'(?:gl|gd|pk|sk|vg|la|bz|org|net|se|rs|st)'

# Patrón 1: dominios de servicios conocidos (annas-archive.gl, z-lib.gd, etc.)
_SERVICE_DOMAIN = re.compile(
    rf'\b({_KNOWN_PREFIXES}\.{_KNOWN_TLDS})\b',
    re.IGNORECASE
)

# Patrón 2: cualquier URL con TLD de biblioteca en contexto relevante
_URL_WITH_LIB_TLD = re.compile(
    r'https?://([a-z0-9][a-z0-9\-]{2,63}\.(?:gl|gd|pk|sk|vg|la|bz))[/\s"\']',
    re.IGNORECASE
)

# Patrón 3: dominio suelto con TLD de biblioteca (sin https://)
_BARE_LIB_TLD = re.compile(
    r'\b([a-z0-9][a-z0-9\-]{2,30}\.(?:gl|gd|pk|sk|vg|la|bz))\b',
    re.IGNORECASE
)

# Palabras clave que deben aparecer cerca para que el contexto sea relevante
_CONTEXT_KEYWORDS = re.compile(
    r'anna|archive|libgen|library|mirror|book|ebook|pdf|download|zlibrary|z-lib',
    re.IGNORECASE
)


def extract_domains(text: str, require_context: bool = True) -> list[str]:
    """
    Extrae dominios candidatos de un bloque de texto.

    Args:
        text: Texto a analizar (post de Reddit, tweet, mensaje de Telegram, etc.)
        require_context: Si True, solo extrae dominios cuando el texto contiene
                         palabras clave de biblioteca (reduce falsos positivos).

    Returns:
        Lista deduplicada de dominios en minúsculas (sin https://).
    """
    if require_context and not _CONTEXT_KEYWORDS.search(text):
        return []

    found = set()

    for pattern in (_SERVICE_DOMAIN, _URL_WITH_LIB_TLD, _BARE_LIB_TLD):
        for match in pattern.findall(text):
            domain = match.lower().strip().rstrip('/')
            if len(domain) > 5:
                found.add(domain)

    return list(found)
