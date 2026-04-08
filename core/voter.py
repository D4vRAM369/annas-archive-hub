"""
Módulo para la votación colaborativa de dominios.
"""

import json
import os
from datetime import datetime
from config.settings import DOMAINS_FILE, VOTES_FILE, VOTE_THRESHOLD

class Voter:
    """
    Gestiona las propuestas y votos de la comunidad.
    """
    
    def __init__(self):
        self.domains = self._load_json(DOMAINS_FILE)
        self.votes = self._load_json(VOTES_FILE)
    
    def _load_json(self, filepath):
        """Carga un archivo JSON o devuelve estructura vacía."""
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return {}
    
    def _save_json(self, filepath, data):
        """Guarda datos en un archivo JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def propose(self, domain, proposed_by="anonymous"):
        """Propone un nuevo dominio."""
        if domain not in self.domains:
            self.domains[domain] = {
                "proposed_by": proposed_by,
                "timestamp": datetime.now().isoformat(),
                "votes": 0,
                "verified": False
            }
            self._save_json(DOMAINS_FILE, self.domains)
            print(f"[+] Propuesto: {domain}")
        else:
            print(f"[*] Ya existe: {domain}")
    
    def vote(self, domain):
        """Vota por un dominio."""
        if domain in self.domains:
            self.domains[domain]["votes"] += 1
            
            if self.domains[domain]["votes"] >= VOTE_THRESHOLD:
                self.domains[domain]["verified"] = True
                print(f"[+] ¡VERIFICADO! {domain}")
            
            self._save_json(DOMAINS_FILE, self.domains)
            print(f"[+] Voto registrado para {domain}")
        else:
            print(f"[!] Dominio no encontrado: {domain}")
    
    def get_pending(self):
        """Devuelve dominios pendientes de verificación."""
        return [d for d, info in self.domains.items() if not info.get("verified", False)]
    
    def get_verified(self):
        """Devuelve dominios ya verificados."""
        return [d for d, info in self.domains.items() if info.get("verified", False)]
