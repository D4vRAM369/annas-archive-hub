# Contributing Guide

Thanks for wanting to contribute to Anna's Archive Hub.

---

## Getting started

```bash
git clone https://github.com/D4vRAM369/annas-archive-hub
cd annas-archive-hub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt pytest
cp .env.example .env
python -m pytest tests -q   # all tests must pass before opening a PR
```

---

## Ways to contribute

### Add new domains
If you find an active domain the system doesn't detect:
1. Open an Issue with the domain and how you found it
2. Or run `python main.py` → option 3 to add it locally

### Add new discovery sources
Sources live in `core/social_crawler.py`. Each source is an independent function that returns `list[str]`:

```python
def _crawl_my_source() -> list[str]:
    candidates = []
    # ... scraping logic
    candidates.extend(extract_domains(text))
    return candidates
```

Add it to `crawl_all()` inside `SocialCrawler`.

### Improve domain verification
The verifier is in `core/domain_tester.py`. It uses `curl_cffi` with Chrome impersonation. If you find domains that give false negatives, open an Issue with the domain and the response code you get.

Every active domain is **classified** by `classify()` (Anna's Archive, Libgen or Z-Library) using the final host and the page `<title>`; anything not recognized is discarded. If a legitimate mirror doesn't show up, open an Issue with the domain and the `<title>` it displays. Suspicious or malicious domains are added to `BLOCKED_DOMAINS` in `config/settings.py` **with the reason and date**.

### Report verified Telegram channels
If you find a legitimate Telegram channel (not spam, active, shares real domains), open an Issue with the channel name and why you consider it verified.

---

## Conventions

- The README (CID, links and domain tables) is rewritten by the bot every 12 h: don't edit those zones by hand
- **Python 3.12+**
- No credentials in code — use environment variables via `.env`
- Each source function returns a `list[str]` of domains without `https://`
- Domains are always lowercase

## Pull Requests

1. Fork the repository
2. Use a descriptive branch name: `feat/new-lemmy-source`, `fix/tld-regex`, etc.
3. One PR per logical change
4. Describe what it does and why in the PR description
