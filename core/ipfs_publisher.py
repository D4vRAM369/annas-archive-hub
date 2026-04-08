"""
Módulo para publicar reportes en IPFS.
"""

import json
import subprocess
import socket
from datetime import datetime

class IPFSPublisher:
    """Gestiona la publicación de reportes en IPFS."""
    
    def __init__(self, report_file="annas_report.json", hash_file="ipfs_hash.txt"):
        self.report_file = report_file
        self.hash_file = hash_file
    
    def is_ipfs_running(self):
        """Verifica si el demonio de IPFS está corriendo."""
        try:
            # Intentar conectar al puerto de la API de IPFS (5001)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 5001))
            sock.close()
            return result == 0
        except:
            return False
    
    def publish(self, active_domains):
        """Publica los dominios activos en IPFS."""
        
        # Verificar que IPFS esté corriendo
        if not self.is_ipfs_running():
            print("[!] IPFS no está corriendo.")
            print("[*] Abre otra terminal y ejecuta: ipfs daemon")
            print("[*] Luego vuelve a intentarlo.")
            return None
        
        print("[*] IPFS detectado. Publicando...")
        
        # Crear el reporte
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_domains": active_domains,
            "note": "Generado por Anna's Archive Hub"
        }
        
        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Publicar en IPFS
        try:
            result = subprocess.run(
                ["ipfs", "add", "-Q", self.report_file],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                hash_id = result.stdout.strip()
                
                # Fijar el hash
                subprocess.run(["ipfs", "pin", "add", hash_id], capture_output=True)
                
                with open(self.hash_file, "w") as f:
                    f.write(hash_id)
                
                print(f"[✔] Publicado en IPFS: {hash_id}")
                print(f"    Enlace: http://localhost:8080/ipfs/{hash_id}")
                return hash_id
            else:
                print(f"[!] Error al publicar: {result.stderr}")
        except Exception as e:
            print(f"[!] Error: {e}")
        return None
    
    def get_last_hash(self):
        """Obtiene el último hash publicado."""
        try:
            with open(self.hash_file, "r") as f:
                return f.read().strip()
        except:
            return None
