# core/social_crawler.py
"""
Rastrea fuentes sociales para descubrir nuevos dominios de Anna's Archive.

Fuentes implementadas:
  - Reddit (JSON API pública, sin autenticación)
  - X/Twitter vía instancias Nitter públicas
  - Telegram canales públicos (vía t.me/s/)
  - Mastodon (API pública)
"""

import re
import time
from curl_cffi import requests

from config.settings import (
    BROWSER_IMPERSONATION,
    REDDIT_SUBREDDITS, REDDIT_QUERIES,
    NITTER_INSTANCES, NITTER_QUERIES,
    TELEGRAM_CHANNELS, TELEGRAM_SPAM_KEYWORDS,
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

            except (ValueError, KeyError) as e:
                print(f"  [!] Reddit {subreddit}/{query} - respuesta malformada: {e}")
            except Exception as e:
                print(f"  [!] Reddit {subreddit}/{query} - error de red: {type(e).__name__}: {str(e)[:80]}")

    print(f"  [Reddit] {len(candidates)} candidatos crudos")
    return candidates


def _crawl_nitter() -> list[str]:
    """
    Busca en X/Twitter usando instancias públicas de Nitter.
    Prueba cada instancia en orden y usa la primera que responde.
    Si todas fallan, devuelve lista vacía sin error fatal.
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

                tweet_texts = re.findall(
                    r'class="tweet-content[^"]*"[^>]*>(.*?)</div>',
                    r.text,
                    re.DOTALL
                )
                for raw in tweet_texts:
                    clean = re.sub(r'<[^>]+>', ' ', raw)
                    candidates.extend(extract_domains(clean))

                break  # instancia funcionó, pasar a siguiente query

            except Exception as e:
                print(f"  [!] Nitter {instance}: {type(e).__name__}: {str(e)[:80]}")
                continue

    print(f"  [Nitter/X] {len(candidates)} candidatos crudos")
    return candidates


def _is_telegram_spam(text: str) -> bool:
    """Descarta mensajes de Telegram que contienen indicadores de spam."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in TELEGRAM_SPAM_KEYWORDS)


def _crawl_telegram() -> list[str]:
    """
    Rastrea canales públicos de Telegram vía t.me/s/{canal}.
    Solo funciona con canales públicos.
    TELEGRAM_CHANNELS está vacío por defecto — añade canales verificados manualmente.
    """
    if not TELEGRAM_CHANNELS:
        print("  [Telegram] Sin canales configurados (vacío por defecto).")
        return []

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

            messages = re.findall(
                r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
                r.text,
                re.DOTALL
            )
            for raw in messages:
                clean = re.sub(r'<[^>]+>', ' ', raw)
                if _is_telegram_spam(clean):
                    continue
                candidates.extend(extract_domains(clean))

        except Exception as e:
            print(f"  [!] Telegram @{channel}: {type(e).__name__}: {str(e)[:80]}")

    print(f"  [Telegram] {len(candidates)} candidatos crudos")
    return candidates


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
                    raw = status.get("content", "")
                    clean = re.sub(r'<[^>]+>', ' ', raw)
                    candidates.extend(extract_domains(clean))

            except (ValueError, KeyError) as e:
                print(f"  [!] Mastodon {instance} - respuesta malformada: {e}")
            except Exception as e:
                print(f"  [!] Mastodon {instance}: {type(e).__name__}: {str(e)[:80]}")

    print(f"  [Mastodon] {len(candidates)} candidatos crudos")
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

        print("[*] Rastreando X/Twitter (Nitter)...")
        all_candidates.extend(_crawl_nitter())

        print("[*] Rastreando Telegram...")
        all_candidates.extend(_crawl_telegram())

        print("[*] Rastreando Mastodon...")
        all_candidates.extend(_crawl_mastodon())

        unique = list(dict.fromkeys(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
