# Social Crawler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir un módulo `social_crawler.py` que descubra nuevos dominios de Anna's Archive rastreando Reddit, X/Twitter (vía Nitter), Telegram y Mastodon, integrándolo en el pipeline existente.

**Architecture:** Un `SocialCrawler` orquesta fuentes independientes (cada una es una función que devuelve `list[str]`). Un extractor de dominios compartido (`domain_extractor.py`) parsea texto libre buscando patrones conocidos de dominios de bibliotecas. Los candidatos se unen a los de `open_slum_crawler` antes de pasar al `DomainTester`.

**Tech Stack:** `curl_cffi` (ya instalado), `requests` (ya instalado), regex stdlib, `config/settings.py` para configuración de fuentes.

---

## Mapa de archivos

| Acción | Archivo | Responsabilidad |
|--------|---------|----------------|
| Crear | `core/domain_extractor.py` | Regex para extraer dominios de texto libre |
| Crear | `core/social_crawler.py` | Orquestador + fuentes Reddit/Nitter/Telegram/Mastodon |
| Modificar | `config/settings.py` | Añadir SOCIAL_SOURCES, KEYWORDS, KNOWN_SERVICES |
| Modificar | `run.py` | Integrar `SocialCrawler` en el pipeline automático |
| Modificar | `main.py` | Añadir opción 9: rastreo de fuentes sociales |

---

## Task 1: Extractor de dominios (`core/domain_extractor.py`)

**Files:**
- Create: `core/domain_extractor.py`

- [ ] **Step 1: Crear el módulo con los patrones regex**

```python
# core/domain_extractor.py
"""
Extrae dominios de texto libre usando patrones conocidos.
Funciona sobre cualquier fuente: Reddit, Telegram, HTML, etc.
"""

import re

# Servicios conocidos y sus variantes de nombre
_KNOWN_PREFIXES = r'(?:annas?-?archive|z-lib(?:rary)?|libgen|librarygenesis|1lib|go-to-library|welib|shadowlib)'

# TLDs que estos servicios suelen usar
_KNOWN_TLDS = r'(?:gl|gd|pk|sk|vg|la|bz|org|net|se|rs|st)'

# Patrón 1: dominios de servicios conocidos (annas-archive.gl, z-lib.gd, etc.)
_SERVICE_DOMAIN = re.compile(
    rf'\b({_KNOWN_PREFIXES}\.{_KNOWN_TLDS})\b',
    re.IGNORECASE
)

# Patrón 2: cualquier URL con TLD de biblioteca en contexto relevante
_URL_WITH_LIB_TLD = re.compile(
    r'https?://([a-z0-9][a-z0-9\-]{2,63}\.(?:gl|gd|pk|sk|vg|la|bz))[/\s"\']',
    re.IGNORECASE
)

# Patrón 3: dominio suelto con TLD de biblioteca (sin https://)
_BARE_LIB_TLD = re.compile(
    r'\b([a-z0-9][a-z0-9\-]{2,30}\.(?:gl|gd|pk|sk|vg|la|bz))\b',
    re.IGNORECASE
)

# Palabras clave que deben aparecer cerca para que el contexto sea relevante
_CONTEXT_KEYWORDS = re.compile(
    r'anna|archive|libgen|library|mirror|book|ebook|pdf|download|zlibrary|z-lib',
    re.IGNORECASE
)


def extract_domains(text: str, require_context: bool = True) -> list[str]:
    """
    Extrae dominios candidatos de un bloque de texto.

    Args:
        text: Texto a analizar (post de Reddit, tweet, mensaje de Telegram, etc.)
        require_context: Si True, solo extrae dominios cuando el texto contiene
                         palabras clave de biblioteca (reduce falsos positivos).

    Returns:
        Lista deduplicada de dominios en minúsculas (sin https://).
    """
    if require_context and not _CONTEXT_KEYWORDS.search(text):
        return []

    found = set()

    for pattern in (_SERVICE_DOMAIN, _URL_WITH_LIB_TLD, _BARE_LIB_TLD):
        for match in pattern.findall(text):
            domain = match.lower().strip().rstrip('/')
            if len(domain) > 5:
                found.add(domain)

    return list(found)
```

- [ ] **Step 2: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
from core.domain_extractor import extract_domains

# Test básico
text = 'Try the new mirror at annas-archive.gl for books'
result = extract_domains(text)
assert 'annas-archive.gl' in result, f'Falló: {result}'

# Test con URL completa
text2 = 'New link: https://z-lib.gd/book/123 works great'
result2 = extract_domains(text2)
assert 'z-lib.gd' in result2, f'Falló: {result2}'

# Test sin contexto relevante (debe devolver vacío con require_context=True)
text3 = 'buy annas-archive.gl domain cheap'
result3 = extract_domains(text3, require_context=False)
assert 'annas-archive.gl' in result3, f'Falló: {result3}'

print('✅ domain_extractor OK:', result, result2)
"
```

Expected output: `✅ domain_extractor OK: ['annas-archive.gl'] ['z-lib.gd']`

- [ ] **Step 3: Commit**

```bash
git add core/domain_extractor.py
git commit -m "feat: add domain_extractor module for social source parsing"
```

---

## Task 2: Configuración de fuentes sociales (`config/settings.py`)

**Files:**
- Modify: `config/settings.py`

- [ ] **Step 1: Añadir configuración al final de `config/settings.py`**

```python
# ── Fuentes sociales ──────────────────────────────────────────────────────────

# Subreddits a rastrear (JSON API sin autenticación)
REDDIT_SUBREDDITS = [
    "Annas_Archive",
    "DataHoarder",
    "Piracy",
    "opendirectories",
    "libgen",
]

# Términos de búsqueda para Reddit
REDDIT_QUERIES = [
    "anna archive mirror",
    "annas-archive new domain",
    "anna archive link",
]

# Instancias de Nitter para rastrear X/Twitter (se prueban en orden)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
]

# Consultas de búsqueda para X/Nitter
NITTER_QUERIES = [
    "annas-archive new",
    "anna archive mirror site",
    "annasarchive link",
]

# Canales públicos de Telegram (vía t.me/s/{canal})
TELEGRAM_CHANNELS = [
    "shadowlibraries",
    "annasarchive",
    "piracylinks",
]

# Instancias de Mastodon a consultar
MASTODON_INSTANCES = [
    "https://mastodon.social",
    "https://infosec.exchange",
]

# Queries para Mastodon
MASTODON_QUERIES = [
    "annas-archive",
    "anna archive mirror",
]
```

- [ ] **Step 2: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
from config.settings import REDDIT_SUBREDDITS, NITTER_INSTANCES, TELEGRAM_CHANNELS
assert len(REDDIT_SUBREDDITS) > 0
assert len(NITTER_INSTANCES) > 0
assert len(TELEGRAM_CHANNELS) > 0
print('✅ settings OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add config/settings.py
git commit -m "feat: add social sources configuration to settings"
```

---

## Task 3: Social Crawler — fuente Reddit

**Files:**
- Create: `core/social_crawler.py` (parcial, solo Reddit en este task)

- [ ] **Step 1: Crear el módulo con la fuente Reddit**

```python
# core/social_crawler.py
"""
Rastrea fuentes sociales para descubrir nuevos dominios de Anna's Archive.

Fuentes implementadas:
  - Reddit (JSON API pública, sin autenticación)
  - X/Twitter vía instancias Nitter públicas
  - Telegram canales públicos (vía t.me/s/)
  - Mastodon (API pública)
"""

import time
from curl_cffi import requests

from config.settings import (
    BROWSER_IMPERSONATION,
    REDDIT_SUBREDDITS, REDDIT_QUERIES,
    NITTER_INSTANCES, NITTER_QUERIES,
    TELEGRAM_CHANNELS,
    MASTODON_INSTANCES, MASTODON_QUERIES,
)
from core.domain_extractor import extract_domains

_HEADERS_JSON = {
    "User-Agent": "anna-archive-hub/1.0 (domain tracker; educational)"
}


def _crawl_reddit() -> list[str]:
    """Busca en subreddits usando la API JSON pública de Reddit."""
    candidates = []

    for subreddit in REDDIT_SUBREDDITS:
        for query in REDDIT_QUERIES:
            url = (
                f"https://old.reddit.com/r/{subreddit}/search.json"
                f"?q={query}&sort=new&limit=25&restrict_sr=1"
            )
            try:
                r = requests.get(url, headers=_HEADERS_JSON, timeout=10)
                if r.status_code != 200:
                    continue

                posts = r.json().get("data", {}).get("children", [])
                for post in posts:
                    data = post.get("data", {})
                    text = f"{data.get('title', '')} {data.get('selftext', '')}"
                    candidates.extend(extract_domains(text))

                time.sleep(1)  # respetar rate limit de Reddit

            except Exception as e:
                print(f"  [!] Reddit {subreddit}/{query}: {e}")

    print(f"  [Reddit] {len(candidates)} candidatos crudos")
    return candidates


class SocialCrawler:
    """Orquesta todas las fuentes sociales."""

    def crawl_all(self) -> list[str]:
        """
        Rastrea todas las fuentes configuradas.

        Returns:
            Lista deduplicada de dominios candidatos.
        """
        all_candidates = []

        print("[*] Rastreando Reddit...")
        all_candidates.extend(_crawl_reddit())

        # (las demás fuentes se añaden en tasks posteriores)

        unique = list(set(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
```

- [ ] **Step 2: Verificar sintaxis e imports**

```bash
source venv/bin/activate && python -c "
from core.social_crawler import SocialCrawler
sc = SocialCrawler()
print('✅ SocialCrawler importado correctamente')
"
```

- [ ] **Step 3: Commit**

```bash
git add core/social_crawler.py
git commit -m "feat: add SocialCrawler with Reddit source"
```

---

## Task 4: Fuente X/Twitter vía Nitter

**Files:**
- Modify: `core/social_crawler.py` — añadir `_crawl_nitter()`

- [ ] **Step 1: Añadir función `_crawl_nitter` antes de la clase `SocialCrawler`**

```python
def _crawl_nitter() -> list[str]:
    """
    Busca en X/Twitter usando instancias públicas de Nitter.
    Prueba cada instancia en orden y usa la primera que responde.
    """
    candidates = []

    for query in NITTER_QUERIES:
        query_encoded = query.replace(" ", "+")
        for instance in NITTER_INSTANCES:
            url = f"{instance}/search?q={query_encoded}&f=tweets"
            try:
                r = requests.get(
                    url,
                    impersonate=BROWSER_IMPERSONATION,
                    timeout=12,
                    allow_redirects=True,
                )
                if r.status_code != 200:
                    continue

                # Nitter devuelve HTML — extraer texto de tweets
                # Los tweets están en divs con class "tweet-content"
                import re
                tweet_texts = re.findall(
                    r'class="tweet-content[^"]*"[^>]*>(.*?)</div>',
                    r.text,
                    re.DOTALL
                )
                for raw in tweet_texts:
                    # Limpiar tags HTML básicos
                    clean = re.sub(r'<[^>]+>', ' ', raw)
                    candidates.extend(extract_domains(clean))

                break  # instancia funcionó, pasar a siguiente query

            except Exception as e:
                print(f"  [!] Nitter {instance}: {e}")
                continue

    print(f"  [Nitter/X] {len(candidates)} candidatos crudos")
    return candidates
```

- [ ] **Step 2: Actualizar `crawl_all` en la clase para incluir Nitter**

```python
    def crawl_all(self) -> list[str]:
        all_candidates = []

        print("[*] Rastreando Reddit...")
        all_candidates.extend(_crawl_reddit())

        print("[*] Rastreando X/Twitter (Nitter)...")
        all_candidates.extend(_crawl_nitter())

        unique = list(set(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
```

- [ ] **Step 3: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
import ast; ast.parse(open('core/social_crawler.py').read()); print('✅ syntax ok')
"
```

- [ ] **Step 4: Commit**

```bash
git add core/social_crawler.py
git commit -m "feat: add Nitter/X source to SocialCrawler"
```

---

## Task 5: Fuente Telegram (canales públicos)

**Files:**
- Modify: `core/social_crawler.py` — añadir `_crawl_telegram()`

- [ ] **Step 1: Añadir función `_crawl_telegram` antes de la clase**

```python
def _crawl_telegram() -> list[str]:
    """
    Rastrea canales públicos de Telegram vía t.me/s/{canal}.
    No requiere autenticación — solo funciona con canales públicos.
    """
    import re
    candidates = []

    for channel in TELEGRAM_CHANNELS:
        url = f"https://t.me/s/{channel}"
        try:
            r = requests.get(
                url,
                impersonate=BROWSER_IMPERSONATION,
                timeout=12,
            )
            if r.status_code != 200:
                print(f"  [!] Telegram @{channel}: HTTP {r.status_code}")
                continue

            # Mensajes en divs con class "tgme_widget_message_text"
            messages = re.findall(
                r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
                r.text,
                re.DOTALL
            )
            for raw in messages:
                clean = re.sub(r'<[^>]+>', ' ', raw)
                candidates.extend(extract_domains(clean))

        except Exception as e:
            print(f"  [!] Telegram @{channel}: {e}")

    print(f"  [Telegram] {len(candidates)} candidatos crudos")
    return candidates
```

- [ ] **Step 2: Actualizar `crawl_all`**

```python
    def crawl_all(self) -> list[str]:
        all_candidates = []

        print("[*] Rastreando Reddit...")
        all_candidates.extend(_crawl_reddit())

        print("[*] Rastreando X/Twitter (Nitter)...")
        all_candidates.extend(_crawl_nitter())

        print("[*] Rastreando Telegram...")
        all_candidates.extend(_crawl_telegram())

        unique = list(set(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
```

- [ ] **Step 3: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
import ast; ast.parse(open('core/social_crawler.py').read()); print('✅ syntax ok')
"
```

- [ ] **Step 4: Commit**

```bash
git add core/social_crawler.py
git commit -m "feat: add Telegram public channel source to SocialCrawler"
```

---

## Task 6: Fuente Mastodon

**Files:**
- Modify: `core/social_crawler.py` — añadir `_crawl_mastodon()`

- [ ] **Step 1: Añadir función `_crawl_mastodon` antes de la clase**

```python
def _crawl_mastodon() -> list[str]:
    """
    Busca en instancias de Mastodon usando su API pública de búsqueda.
    No requiere autenticación para búsquedas públicas básicas.
    """
    candidates = []

    for instance in MASTODON_INSTANCES:
        for query in MASTODON_QUERIES:
            url = f"{instance}/api/v2/search"
            params = {"q": query, "type": "statuses", "limit": 40}
            try:
                r = requests.get(url, params=params, timeout=10)
                if r.status_code != 200:
                    continue

                statuses = r.json().get("statuses", [])
                for status in statuses:
                    # El contenido viene como HTML con tags
                    import re
                    raw = status.get("content", "")
                    clean = re.sub(r'<[^>]+>', ' ', raw)
                    candidates.extend(extract_domains(clean))

            except Exception as e:
                print(f"  [!] Mastodon {instance}: {e}")

    print(f"  [Mastodon] {len(candidates)} candidatos crudos")
    return candidates
```

- [ ] **Step 2: Actualizar `crawl_all` (versión final)**

```python
    def crawl_all(self) -> list[str]:
        """
        Rastrea todas las fuentes configuradas.
        Returns: Lista deduplicada de dominios candidatos.
        """
        all_candidates = []

        print("[*] Rastreando Reddit...")
        all_candidates.extend(_crawl_reddit())

        print("[*] Rastreando X/Twitter (Nitter)...")
        all_candidates.extend(_crawl_nitter())

        print("[*] Rastreando Telegram...")
        all_candidates.extend(_crawl_telegram())

        print("[*] Rastreando Mastodon...")
        all_candidates.extend(_crawl_mastodon())

        unique = list(set(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
```

- [ ] **Step 3: Verificar sintaxis completa**

```bash
source venv/bin/activate && python -c "
import ast; ast.parse(open('core/social_crawler.py').read()); print('✅ syntax ok')
from core.social_crawler import SocialCrawler
sc = SocialCrawler()
print('✅ SocialCrawler instanciado correctamente')
"
```

- [ ] **Step 4: Commit**

```bash
git add core/social_crawler.py
git commit -m "feat: add Mastodon source, complete SocialCrawler"
```

---

## Task 7: Integrar en `run.py`

**Files:**
- Modify: `run.py`

- [ ] **Step 1: Añadir import y paso de rastreo social en `run.py`**

Reemplazar el bloque de rastreo existente:

```python
# Antes del import de crawl_open_slum, añadir:
from core.social_crawler import SocialCrawler

# En main(), reemplazar el paso 1 así:
def main():
    print("=" * 50)
    print("   ANNA'S ARCHIVE HUB - EJECUCIÓN AUTOMÁTICA")
    print("=" * 50)
    print(f"Timestamp: {__import__('datetime').datetime.now()}\n")

    # 1. Rastrear open-slum para encontrar nuevos dominios
    print("[1/5] Rastreando open-slum...")
    from core.open_slum_crawler import crawl_open_slum
    new_domains = crawl_open_slum()
    if new_domains:
        print(f"  [+] open-slum encontró: {len(new_domains)} candidatos")
    else:
        print("  [!] Sin nuevos candidatos en open-slum")

    # 2. Rastrear fuentes sociales
    print("\n[2/5] Rastreando fuentes sociales...")
    sc = SocialCrawler()
    social_domains = sc.crawl_all()
    print(f"  [+] Fuentes sociales encontraron: {len(social_domains)} candidatos")

    # Unir candidatos de todas las fuentes
    all_candidates = list(set(new_domains + social_domains + list(AUTO_VERIFIABLE)))

    # 3. Probar dominios
    print(f"\n[3/5] Probando {len(all_candidates)} dominios...")
    tester = DomainTester()
    active = tester.test_multiple(all_candidates)
    print(f"  [+] Activos: {len(active)}")

    # 4. Publicar en IPFS
    print("\n[4/5] Publicando en IPFS...")
    publisher = IPFSPublisher()
    hash_id = publisher.publish_report(active, MANUAL_VERIFY)
    if hash_id:
        print(f"  [+] Hash IPFS: {hash_id}")
        for url in publisher.get_public_urls(hash_id):
            print(f"  [+] {url}")
    else:
        print("  [!] Error al publicar en IPFS")

    # 5. Guardar log
    print("\n[5/5] Guardando log...")
    import os
    os.makedirs("logs", exist_ok=True)
    with open("logs/update.log", "a") as f:
        from datetime import datetime
        f.write(
            f"{datetime.now()} | hash={hash_id} | activos={len(active)} "
            f"| candidatos_sociales={len(social_domains)}\n"
        )

    print("\n✅ Ejecución completada")
```

- [ ] **Step 2: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
import ast; ast.parse(open('run.py').read()); print('✅ run.py syntax ok')
"
```

- [ ] **Step 3: Commit**

```bash
git add run.py
git commit -m "feat: integrate SocialCrawler into automated pipeline"
```

---

## Task 8: Añadir opción 9 en `main.py`

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Añadir import y opción de menú**

Añadir el import al inicio del archivo (junto a los otros imports):
```python
from core.social_crawler import SocialCrawler
```

Añadir en el menú (después de la opción 8):
```python
print("  9. 🔍 Rastrear fuentes sociales (Reddit, X, Telegram)")
```

Añadir el handler (después del bloque `elif option == "8":`):
```python
        elif option == "9":
            print("\n[🔍] Rastreando fuentes sociales...")
            sc = SocialCrawler()
            candidates = sc.crawl_all()
            if candidates:
                print(f"\n[*] Probando {len(candidates)} candidatos...")
                active = tester.test_multiple(candidates)
                print(f"\n[+] Dominios activos encontrados: {len(active)}")
                for url in active:
                    print(f"    {url}")
                    add = input(f"\n¿Añadir {url} al sistema de votación? (s/n): ").strip().lower()
                    if add == 's':
                        domain = url.replace("https://", "").split('/')[0]
                        voter.propose(domain, proposed_by="social-crawler")
                        print(f"[+] Propuesto: {domain}")
            else:
                print("[!] No se encontraron candidatos en fuentes sociales.")
            input("\nPresiona Enter...")
```

- [ ] **Step 2: Verificar sintaxis**

```bash
source venv/bin/activate && python -c "
import ast; ast.parse(open('main.py').read()); print('✅ main.py syntax ok')
"
```

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add option 9 for social sources crawling in interactive menu"
```

---

## Self-review

**Cobertura:**
- ✅ Reddit (JSON API pública, sin auth)
- ✅ X/Twitter (Nitter, sin API key)
- ✅ Telegram (canales públicos vía t.me/s/)
- ✅ Mastodon (API pública)
- ✅ Integración en pipeline automático (`run.py`)
- ✅ Integración en menú interactivo (`main.py`, opción 9)
- ✅ Extractor de dominios compartido con contexto semántico
- ✅ Sin API keys requeridas (todo público)

**Limitaciones conocidas:**
- X/Twitter: Nitter es inestable. Si todas las instancias fallan, se omite sin error fatal.
- Telegram: Solo canales públicos. Canales privados requieren API oficial de Telegram.
- Reddit: Rate limit de 1 req/seg respetado con `time.sleep(1)`.
- Mastodon: Sin autenticación = solo resultados públicos y limitados.

**Falsos positivos:** El `require_context=True` en `extract_domains()` reduce significativamente los falsos positivos filtrando texto que no habla de libros/archivos.

