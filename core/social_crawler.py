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

        unique = list(dict.fromkeys(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
