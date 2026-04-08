"""
Publicación de reportes en IPFS con sincronización
"""

import json
import subprocess
from datetime import datetime
from config.settings import DATA_DIR, IPFS_GATEWAY, IPFS_HASH_FILE

class IPFSPublisher:
    def __init__(self):
        self.report_file = f"{DATA_DIR}/current_report.json"
    
    def publish_report(self, active_domains, manual_domains):
        """
        Publica un reporte en IPFS y devuelve el hash.
        El hash cambia SOLO cuando el contenido cambia.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_auto": active_domains,
            "manual_verify": manual_domains,
            "note": "Los dominios 'manual_verify' requieren abrirse en navegador (Cloudflare)"
        }
        
        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Calcular hash del contenido
        result = subprocess.run(
            ["ipfs", "add", "-Q", self.report_file],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            hash_id = result.stdout.strip()
            # Fijar el hash para que no expire
            subprocess.run(["ipfs", "pin", "add", hash_id], capture_output=True)
            
            # Guardar el hash
            with open(IPFS_HASH_FILE, "w") as f:
                f.write(hash_id)
            
            return hash_id
        return None
    
    def get_current_hash(self):
        """Devuelve el último hash publicado"""
        try:
            with open(IPFS_HASH_FILE, "r") as f:
                return f.read().strip()
        except:
            return None
    
    def get_ipfs_url(self, hash_id):
        """Devuelve la URL del gateway local"""
        return f"{IPFS_GATEWAY}{hash_id}"
