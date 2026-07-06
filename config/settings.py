"""
Configuración central del proyecto.
Las credenciales sensibles (Pinata) se leen desde variables de entorno o .env.
"""
import os
from dotenv import load_dotenv
# Cargar variables de entorno desde .env (si existe)
load_dotenv()
# Configuración para domain_tester.py
TIMEOUT = 15
BROWSER_IMPERSONATION = "chrome120"
# Pinata configuration (desde variables de entorno, seguras)
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET", "")
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

# Dominios bloqueados de forma permanente: NUNCA deben aparecer en el reporte
# publicado, sin importar cuántas veces el crawler los redescubra ni qué
# status code devuelvan al testearlos. El filtro se aplica en run.py antes
# de testear, así que ni siquiera se gasta una petición de red contra ellos.
#
# Nivel de confirmación por dominio (documentar SIEMPRE el motivo y la fecha,
# para no perder el contexto en unos meses):
#
#   CONFIRMADO por el usuario (no solo heurística automática):
#     zlibrary.sk - 2026-07-06: redirige a página de "verificación humana"
#                   que induce a copiar/pegar un comando PowerShell malicioso
#                   (patrón ClickFix: iex+irm ejecutando código remoto oculto).
#
#   SOSPECHA razonable por nombre/semántica, NO verificado visitando la
#   página ni con escáner externo (urlscan.io / virustotal.com) — revisar
#   antes de asumir que son maliciosos, podrían ser solo ruido inofensivo
#   del crawler:
#     techblazing.com               - sin relación temática con el proyecto
#     nicsell.com                   - marketplace de dominios, no un espejo
#     pagelearnnext.monster         - patrón típico de spam (.monster + nombre sin sentido)
#     frozensignalnodedust.monster  - mismo patrón que el anterior
#     filter.explorads.com          - subdominio de red publicitaria
#     live.pornamigo.com            - sin relación temática
#     www.google.com                - fallo de captura del crawler, no un espejo
#     search-bits.com               - agregador genérico, sin relación visible
#     push.newsvot.com              - agregador genérico, sin relación visible
BLOCKED_DOMAINS = [
    "zlibrary.sk",
    "techblazing.com",
    "nicsell.com",
    "pagelearnnext.monster",
    "frozensignalnodedust.monster",
    "filter.explorads.com",
    "live.pornamigo.com",
    "www.google.com",
    "search-bits.com",
    "push.newsvot.com",
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
# ── Fuentes sociales ──────────────────────────────────────────────────────────
# Subreddits a rastrear (API JSON pública, sin auth)
REDDIT_SUBREDDITS = [
    "Annas_Archive",
    "DataHoarder",
    "Piracy",
    "opendirectories",
]
# Términos de búsqueda para Reddit
REDDIT_QUERIES = [
    "anna archive mirror",
    "annas-archive new domain",
    "anna archive link",
]
# Instancias de Nitter (frontend público de X/Twitter, sin API key)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
]
NITTER_QUERIES = [
    "annas-archive new",
    "anna archive mirror site",
    "annasarchive link",
]
# Canales de Telegram — VACÍO POR DEFECTO.
#
# La mayoría de canales que usan el nombre "Anna's Archive" en Telegram
# son spam, impostores o bots inactivos. Añade aquí SOLO canales que hayas
# verificado manualmente que son legítimos y activos.
#
# Formato: solo el @username sin la arroba (ej: "mi_canal_verificado")
TELEGRAM_CHANNELS: list[str] = []
# Palabras que indican que un mensaje de Telegram es spam o irrelevante.
# Si el mensaje contiene alguna de estas palabras → se descarta.
TELEGRAM_SPAM_KEYWORDS = [
    "earn money", "ganar dinero", "investment", "crypto", "bitcoin",
    "subscribe to premium", "join our vip", "click here to unlock",
    "18+", "adult", "casino", "betting", "forex", "trading signal",
    "contact admin", "dm for access", "pay to access",
    "telegram bot", "@bot", "promoción", "oferta", "gratis por tiempo",
]
# Instancias de Mastodon con API pública
MASTODON_INSTANCES = [
    "https://mastodon.social",
    "https://infosec.exchange",
]
MASTODON_QUERIES = [
    "annas-archive",
    "anna archive mirror",
]