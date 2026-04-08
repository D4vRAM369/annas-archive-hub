"""
Configuración central del proyecto
"""

# Dominios estáticos (los que ya conocemos)
STATIC_DOMAINS = [
    "annas-archive.gl",
    "annas-archive.pk",
    "annas-archive.gd"
]

# Umbral de votos para que un dominio se considere verificado
VOTE_THRESHOLD = 3

# Tiempo de espera para pruebas (segundos)
TIMEOUT = 15

# Impersonación de navegador (chrome120, chrome110, edge, safari)
BROWSER_IMPRESONATION = "chrome120"

# Archivos de datos
DATA_DIR = "data"
DOMAINS_FILE = f"{DATA_DIR}/domains.json"
VOTES_FILE = f"{DATA_DIR}/votes.json"
IPFS_HASH_FILE = f"{DATA_DIR}/ipfs_hash.txt"
