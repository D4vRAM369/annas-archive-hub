"""
Módulo para probar dominios usando curl_cffi (impersonación de navegador)
Incluye rastreador de open-slum.org para descubrir nuevos dominios automáticamente.
"""

import re
from curl_cffi import requests
from config.settings import TIMEOUT, BROWSER_IMPRESONATION

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
    
    def crawl_open_slum(self):
        """
        Visita open-slum.org y extrae todos los dominios candidatos
        que aparecen en su monitor de salud.
        
        Returns:
            list: Lista de dominios candidatos (sin probar).
        """
        urls = [
            "https://open-slum.org",
            "https://open-slum.pages.dev"
        ]
        
        candidates = []
        
        # Patrones para extraer nombres
        patterns = [
            (r"Anna's Archive ([A-Z]{2,3})", "annas-archive.{code}"),
            (r"Libgen\+([A-Z]{2,3})", "libgen.{code}"),
            (r"Libgen\+([A-Z]{2,3})", "librarygenesis.{code}"),
            (r"Z-Library ([A-Z]{2,3})", "z-lib.{code}"),
            (r"Z-Library ([A-Z]{2,3})", "zlibrary.{code}"),
            (r'([a-z0-9\-]+\.sk)', None),  # Dominios .sk directos
            (r'z-lib ([a-z]{2,3})', "z-lib.{code}"),
            (r'1lib ([a-z]{2,3})', "1lib.{code}")
        ]
        
        for url in urls:
            print(f"[*] Rastreando: {url}")
            try:
                r = requests.get(url, impersonate="chrome120", timeout=15)
                if r.status_code == 200:
                    text = r.text
                    
                    # Aplicar cada patrón
                    for pattern, template in patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            if template:
                                # Construir dominio a partir de la plantilla
                                domain = template.format(code=match.lower())
                                candidates.append(domain)
                            else:
                                # Dominio directo
                                candidates.append(match.lower())
                    
                    # Extracción adicional: buscar cualquier dominio .gl, .gd, .pk, .vg
                    # que pueda estar suelto en el texto
                    tld_pattern = r'[a-z0-9\-]+\.(gl|gd|pk|vg|sk|la|bz)'
                    tld_matches = re.findall(tld_pattern, text, re.IGNORECASE)
                    for match in tld_matches:
                        candidates.append(match)
                    
            except Exception as e:
                print(f"  [!] Error: {e}")
        
        # Limpiar y eliminar duplicados
        candidates = list(set([c.lower().strip() for c in candidates if c and len(c) > 5]))
        print(f"[+] Candidatos encontrados: {len(candidates)}")
        
        # Mostrar los primeros 10 como ejemplo
        if candidates:
            print(f"[*] Muestra: {candidates[:10]}")
        
        return candidates
