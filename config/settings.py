"""
Configuración central del proyecto
"""

# Configuración para domain_tester.py
TIMEOUT = 15
BROWSER_IMPRESONATION = "chrome120"

# Dominios verificables automáticamente (sin Cloudflare)
AUTO_VERIFIABLE = [
    "annas-archive.gl",
    "annas-archive.pk",
    "annas-archive.gd",
    "welib.org"
]

# Dominios con protección Cloudflare (requieren verificación manual)
MANUAL_VERIFY = [
    "z-lib.gl",
    "go-to-library.sk",
    "z-lib.gd",
    "z-library.sk",
    "1lib.sk"
]

# URLs de open-slum para rastrear
OPEN_SLUM_URLS = [
    "https://open-slum.org",
    "https://open-slum.pages.dev"
]

# Umbral de votos para verificar un dominio
VOTE_THRESHOLD = 3

# Archivos de datos
DATA_DIR = "data"
DOMAINS_FILE = f"{DATA_DIR}/domains.json"
VOTES_FILE = f"{DATA_DIR}/votes.json"
IPFS_HASH_FILE = f"{DATA_DIR}/ipfs_hash.txt"

# IPFS Gateway local
IPFS_GATEWAY = "http://localhost:8080/ipfs/"
