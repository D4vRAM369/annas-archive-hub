"""
Módulo para probar dominios usando curl_cffi (impersonación de navegador)
Incluye rastreador de open-slum.org para descubrir nuevos dominios automáticamente.
"""

import re
from urllib.parse import urlparse

from curl_cffi import requests
from config.settings import TIMEOUT, BROWSER_IMPERSONATION


_BLOCKED_DOMAINS = [
    "techblazing.com",
    "google.com",
    "facebook.com",
    "twitter.com",
    "youtube.com",
    "reddit.com",
    "wikipedia.org",
    "amazon.com",
    "cloudflare.com",
    "github.com",
    "ipfs.io",
    "dweb.link",
]

# Huellas por servicio: (regex sobre host final, regex sobre el HTML).
# Un dominio solo cuenta como Anna's Archive si el host final O el contenido lo confirman.
_FINGERPRINTS = {
    "annas_archive": (r"annas?-?archive", r"Anna[’'`]?s Archive|annas-archive"),
    "libgen": (r"libgen|librarygenesis", r"Library Genesis|Libgen"),
    # z-lib.qa es un clon SEO y está en BLOCKED_DOMAINS; el resto se acepta por host.
    "zlibrary": (r"z-?lib|1lib|go-to-library|welib", r"Z-Library|1lib"),
}


def classify(final_url, text):
    """Devuelve 'annas_archive' | 'libgen' | 'zlibrary' | None (no reconocido).

    Prioridad: host final (tras redirecciones) y luego <title> de la página.
    El cuerpo NO se usa: libgen/z-lib enlazan a Anna's y daban falsos positivos.
    """
    host = urlparse(final_url).netloc.lower()
    for service, (host_re, _) in _FINGERPRINTS.items():
        if re.search(host_re, host):
            return service
    m = re.search(r"<title[^>]*>(.*?)</title>", text or "", re.I | re.S)
    title = m.group(1) if m else ""
    for service, (_, title_re) in _FINGERPRINTS.items():
        if re.search(title_re, title, re.I):
            return service
    return None


class DomainTester:
    """
    Clase que prueba si un dominio está activo.
    Usa impersonación de navegador para evitar bloqueos.
    """

    def __init__(self):
        self.active_domains = []
        self.inactive_domains = []
        # servicio -> [url activa]; solo dominios cuyo contenido/host se reconoce
        self.by_service = {}

    def test_domain(self, domain, retries=2):
        """
        Prueba un dominio individual con reintentos.

        Args:
            domain: El dominio a probar (ej: "annas-archive.gl")
            retries: Número de reintentos en caso de fallo de red.

        Returns:
            str: La URL activa si funciona, None si no.
        """
        url = f"https://{domain}"

        for attempt in range(retries + 1):
            try:
                # La magia está aquí: impersonate engaña a Cloudflare
                response = requests.get(
                    url,
                    timeout=TIMEOUT,
                    impersonate=BROWSER_IMPERSONATION,
                    allow_redirects=True
                )

                # Solo 2xx/3xx = dominio usable
                if response.status_code < 400:
                    service = classify(response.url, response.text)
                    if service is None:
                        print(f"  ⚠️ {domain} -> {response.status_code} (no reconocido, descartado)")
                        return None
                    print(f"  ✅ {domain} -> {response.status_code} ({service})")
                    self.by_service.setdefault(service, []).append(response.url)
                    return response.url  # Puede ser la URL final tras redirección
                else:
                    print(f"  ❌ {domain} -> {response.status_code} (inactivo)")
                    return None

            except Exception as e:
                if attempt < retries:
                    print(f"  [!] {domain} falló (intento {attempt+1}), reintentando...")
                    continue
                print(f"  ❌ {domain} -> Error final: {str(e)[:50]}")

        return None

    def test_multiple(self, domains):
        """
        Prueba una lista de dominios.

        Args:
            domains: Lista de dominios a probar.

        Returns:
            list: URLs activas.
        """
        self.active_domains = []
        self.by_service = {}

        for domain in domains:
            if domain in _BLOCKED_DOMAINS:
                continue
            url = self.test_domain(domain)
            if url:
                self.active_domains.append(url)

        return self.active_domains
    
