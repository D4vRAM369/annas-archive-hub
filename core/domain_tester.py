"""
Módulo para probar dominios usando curl_cffi (impersonación de navegador)
Incluye rastreador de open-slum.org para descubrir nuevos dominios automáticamente.
"""

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

class DomainTester:
    """
    Clase que prueba si un dominio está activo.
    Usa impersonación de navegador para evitar bloqueos.
    """

    def __init__(self):
        self.active_domains = []
        self.inactive_domains = []

    def test_domain(self, domain):
        """
        Prueba un dominio individual.

        Args:
            domain: El dominio a probar (ej: "annas-archive.gl")

        Returns:
            str: La URL activa si funciona, None si no.
        """
        url = f"https://{domain}"

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
                print(f"  ✅ {domain} -> {response.status_code} (activo)")
                return response.url  # Puede ser la URL final tras redirección
            else:
                print(f"  ❌ {domain} -> {response.status_code} (inactivo)")

        except Exception as e:
            print(f"  ❌ {domain} -> Error: {str(e)[:50]}")

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

        for domain in domains:
            if domain in _BLOCKED_DOMAINS:
                continue
            url = self.test_domain(domain)
            if url:
                self.active_domains.append(url)

        return self.active_domains
    
