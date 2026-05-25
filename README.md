# Anna's Archive Hub

<img width="680" height="480" alt="Gemini_Generated_Image" src="https://github.com/user-attachments/assets/cfd41e9b-3230-4169-a1e2-b863e4d22e2d" />


> 🔥 **Self-updating domain tracker for Anna's Archive and shadow libraries — with real-time verification and permanent IPFS publishing. Never lose access again.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![IPFS](https://img.shields.io/badge/IPFS-Published-green.svg)](https://ipfs.io)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/D4vRAM369/annas-archive-hub)

[🇪🇸 Versión en español](README.es.md)

---

## 📡 Latest Report (IPFS — Immutable)

**Current CID:** `Qmew9o3AzbWzgVuX7QkWxGud1jm8Gdd4EbWnNHiNrx57tJ`

| Gateway | Link |
|---------|------|
| ipfs.io | [Open report](https://ipfs.io/ipfs/Qmew9o3AzbWzgVuX7QkWxGud1jm8Gdd4EbWnNHiNrx57tJ) |
| dweb.link | [Open report](https://dweb.link/ipfs/Qmew9o3AzbWzgVuX7QkWxGud1jm8Gdd4EbWnNHiNrx57tJ) |
| Pinata | [Open report](https://gateway.pinata.cloud/ipfs/Qmew9o3AzbWzgVuX7QkWxGud1jm8Gdd4EbWnNHiNrx57tJ) |

> The CID is updated automatically every 6 hours. Older CIDs remain permanently accessible.

---

## ✅ Active Domains (Last Verified)

| Domain | Status |
|--------|--------|
| annas-archive.gl | ✅ Active |
| annas-archive.pk | ✅ Active |
| annas-archive.gd | ✅ Active |
| libgen.bz | ✅ Active |
| libgen.gl | ✅ Active |
| libgen.la | ✅ Active |
| libgen.vg | ✅ Active |
| z-library.bz | ✅ Active |
| z-library.se | ✅ Active |
| welib.org | ✅ Active |

> ⚠️ Some domains (z-lib.gl, go-to-library.sk, etc.) require opening in a browser due to Cloudflare protection.

---

## 🚀 How It Works

```
open-slum.org ──┐
Reddit / X    ──┼──► candidates ──► HTTP verify ──► active ──► IPFS ──► QR / USB
Telegram      ──┘
Mastodon      ──┘
```

| Feature | Description |
|---------|-------------|
| 🕷️ Multi-source crawler | open-slum.org + Reddit + X/Twitter + Telegram + Mastodon |
| ✅ Smart verification | curl_cffi with Chrome impersonation to bypass blocks |
| 🚫 Spam filtering | Blocks fake domains and spam Telegram channels |
| 📦 IPFS publishing | Immutable report pinned to Pinata — no server needed |
| 🗳️ Voting system | Community verification for uncertain domains |
| ⏱️ Auto-scheduled | Runs unattended via cron every 6 hours |

---

## 🛠️ Installation

**Requirements:** Python 3.12+, Git

```bash
git clone https://github.com/annas-archive-hub/annas-archive-hub
cd annas-archive-hub

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env            # optional — see Configuration below
```

---

## 🖥️ Usage

There are two ways to use this tool:

### Option A — Interactive menu (`main.py`)

For manual control. Run it, pick an option, see results on screen.

```bash
python main.py
```

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        ANNA'S ARCHIVES HUB                                ║
║             Self-updating domain tracker + IPFS immortality                ║
╚════════════════════════════════════════════════════════════════════════════╝

  1. Test static domains          → checks the hardcoded domain list
  2. Test all domains             → static + community-voted domains
  3. Add a domain manually        → propose a new domain for testing
  4. Vote for a domain            → upvote a candidate domain
  5. View pending domains         → domains waiting for votes
  6. Publish report to IPFS       → pin results to Pinata / local node
  7. Show latest IPFS hash        → display current CID + public URLs
  8. Crawl open-slum.org          → discover new domains from open-slum
  9. Crawl social sources         → Reddit, X/Twitter, Telegram, Mastodon
  0. Exit
```

### Option B — Automated pipeline (`run.py`)

Runs everything unattended in sequence: crawl → verify → publish → log.
Designed for cron. No interaction needed.

```bash
python run.py
```

```
[1/5] Crawling open-slum.org...     → finds candidate domains
[2/5] Crawling social sources...    → Reddit, X, Telegram, Mastodon
[3/5] Testing N domains...          → verifies each one is alive
[4/5] Publishing to IPFS...         → pins report, prints CID
[5/5] Saving log...                 → appends to logs/update.log
✅ Done
```

### Automate with cron (every 6 hours)

```bash
crontab -e
```

Add this line (replace the path with your actual clone location):

```
0 */6 * * * cd /home/youruser/annas-archive-hub && source venv/bin/activate && python run.py >> logs/cron.log 2>&1
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your [Pinata](https://pinata.cloud) credentials for permanent IPFS pinning (free plan: 1 GB):

```env
PINATA_API_KEY=your_key_here
PINATA_API_SECRET=your_secret_here
```

**Without Pinata:** reports publish to your local IPFS node (requires the IPFS daemon running). The tool works without any credentials — IPFS publishing is optional.

---

## 📁 Project Structure

```
anna-archive-hub/
├── main.py                    # Interactive menu (9 options)
├── run.py                     # Automated pipeline (for cron)
├── config/
│   └── settings.py            # Central configuration
├── core/
│   ├── domain_tester.py       # Domain verification with curl_cffi
│   ├── domain_extractor.py    # Regex domain extraction from free text
│   ├── open_slum_crawler.py   # open-slum.org crawler
│   ├── social_crawler.py      # Reddit, X, Telegram, Mastodon sources
│   ├── ipfs_publisher.py      # IPFS / Pinata publishing
│   └── voter.py               # Community voting system
├── data/
│   ├── current_report.json    # Latest generated report
│   └── ipfs_hash.txt          # Latest published CID
├── .env.example               # Credentials template
└── requirements.txt
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT — Free for all. Keep knowledge alive.
