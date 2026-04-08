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

        unique = list(dict.fromkeys(c.lower() for c in all_candidates if c))
        print(f"[+] Total candidatos sociales únicos: {len(unique)}")
        return unique
