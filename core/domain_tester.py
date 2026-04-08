"""
Módulo para probar dominios usando curl_cffi (impersonación de navegador)
"""

from curl_cffi import requests
from config import TIMEOUT, BROWSER_IMPRESONATION

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
                impersonate=BROWSER_IMPRESONATION,
                allow_redirects=True
            )
            
            # Códigos 2xx = éxito, 3xx = redirección
            if response.status_code < 400:
                print(f"  ✅ {domain} -> {response.status_code} (activo)")
                return response.url  # Puede ser la URL final tras redirección
            
            # Códigos 4xx/5xx = error, pero a veces el dominio existe
            elif response.status_code < 500:
                print(f"  ⚠️ {domain} -> {response.status_code} (existe pero con error)")
                return url
            
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
            url = self.test_domain(domain)
            if url:
                self.active_domains.append(url)
        
        return self.active_domains
