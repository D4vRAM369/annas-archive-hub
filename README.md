# Anna's Archive Hub

> 🔥 **Self-updating domain tracker for Anna's Archive and shadow libraries — with real-time verification and permanent IPFS publishing. Never lose access again.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![IPFS](https://img.shields.io/badge/IPFS-Published-green.svg)](https://ipfs.io)

[🇪🇸 Versión en español](README.es.md)

---

## 📡 Latest Report (IPFS — Immutable)

**Current CID:** `QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h`

| Gateway | Link |
|---------|------|
| ipfs.io | [Open report](https://ipfs.io/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |
| dweb.link | [Open report](https://dweb.link/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |
| Pinata | [Open report](https://gateway.pinata.cloud/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |

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

## 🛠️ Quick Start

```bash
git clone https://github.com/D4vRAM369/annas-archive-hub
cd anna-archive-hub
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your Pinata keys (optional but recommended)
```

### Run

```bash
python main.py    # interactive menu
python run.py     # full automated pipeline
```

### Automate with cron (every 6 hours)

```bash
crontab -e
# Add:
0 */6 * * * cd /path/to/anna-archive-hub && source venv/bin/activate && python run.py >> logs/cron.log 2>&1
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your [Pinata](https://pinata.cloud) credentials for permanent IPFS pinning (free plan: 1GB):

```env
PINATA_API_KEY=your_key_here
PINATA_API_SECRET=your_secret_here
```

Without Pinata, reports are published to your local IPFS node (requires daemon running).

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
