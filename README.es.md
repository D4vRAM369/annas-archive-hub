# Anna's Archive Hub

> 🔥 **Rastreador de dominios auto-actualizable para Anna's Archive y shadow libraries — con verificación en tiempo real y publicación permanente en IPFS. No pierdas el acceso nunca más.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![IPFS](https://img.shields.io/badge/IPFS-Published-green.svg)](https://ipfs.io)

[🇬🇧 English version](README.md)

---

## 📡 Último Reporte (IPFS — Inmutable)

**CID actual:** `QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h`

| Gateway | Enlace |
|---------|--------|
| ipfs.io | [Abrir reporte](https://ipfs.io/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |
| dweb.link | [Abrir reporte](https://dweb.link/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |
| Pinata | [Abrir reporte](https://gateway.pinata.cloud/ipfs/QmaftecLqvZUsNccDNwguR6PVh449uDzQMQqpFh97q2J2h) |

> El CID se actualiza automáticamente cada 6 horas. Los CIDs anteriores permanecen accesibles para siempre.

---

## ✅ Dominios Activos (Última Verificación)

| Dominio | Estado |
|---------|--------|
| annas-archive.gl | ✅ Activo |
| annas-archive.pk | ✅ Activo |
| annas-archive.gd | ✅ Activo |
| libgen.bz | ✅ Activo |
| libgen.gl | ✅ Activo |
| libgen.la | ✅ Activo |
| libgen.vg | ✅ Activo |
| z-library.bz | ✅ Activo |
| z-library.se | ✅ Activo |
| welib.org | ✅ Activo |

> ⚠️ Algunos dominios (z-lib.gl, go-to-library.sk, etc.) requieren abrirse en el navegador por protección Cloudflare.

---

## 🚀 Cómo Funciona

```
open-slum.org ──┐
Reddit / X    ──┼──► candidatos ──► verifica HTTP ──► activos ──► IPFS ──► QR / pendrive
Telegram      ──┘
Mastodon      ──┘
```

| Función | Descripción |
|---------|-------------|
| 🕷️ Rastreador multi-fuente | open-slum.org + Reddit + X/Twitter + Telegram + Mastodon |
| ✅ Verificación inteligente | curl_cffi con impersonación de Chrome para evitar bloqueos |
| 🚫 Filtro anti-spam | Bloquea dominios falsos y canales de Telegram impostores |
| 📦 Publicación en IPFS | Reporte inmutable pinneado en Pinata — sin servidor propio |
| 🗳️ Sistema de votación | Verificación comunitaria para dominios dudosos |
| ⏱️ Automatización | Se ejecuta solo vía cron cada 6 horas |

---

## 🛠️ Instalación

```bash
git clone https://github.com/D4vRAM369/annas-archive-hub
cd anna-archive-hub
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # añade tus claves de Pinata (opcional pero recomendado)
```

### Ejecutar

```bash
python main.py    # menú interactivo (9 opciones)
python run.py     # pipeline automático completo
```

| Opción | Función |
|--------|---------|
| 1 | Probar dominios conocidos |
| 2 | Probar todos los dominios |
| 3 | Añadir dominio manualmente |
| 4 | Votar por un dominio |
| 5 | Ver dominios pendientes |
| 6 | Publicar reporte en IPFS |
| 7 | Ver CID y URLs públicas |
| 8 | Rastrear open-slum.org |
| 9 | Rastrear fuentes sociales |

### Automatizar con cron (cada 6 horas)

```bash
crontab -e
# Añadir:
0 */6 * * * cd /ruta/al/proyecto && source venv/bin/activate && python run.py >> logs/cron.log 2>&1
```

---

## ⚙️ Configuración

Copia `.env.example` a `.env` y añade tus credenciales de [Pinata](https://pinata.cloud) para publicación IPFS permanente (plan gratuito: 1GB):

```env
PINATA_API_KEY=tu_key_aqui
PINATA_API_SECRET=tu_secret_aqui
```

Sin Pinata, los reportes se publican en tu nodo IPFS local (requiere daemon corriendo).

---

## 📁 Estructura del Proyecto

```
anna-archive-hub/
├── main.py                    # Menú interactivo
├── run.py                     # Pipeline automático (para cron)
├── config/
│   └── settings.py            # Configuración central
├── core/
│   ├── domain_tester.py       # Verificación con curl_cffi
│   ├── domain_extractor.py    # Extracción regex de texto libre
│   ├── open_slum_crawler.py   # Rastreador de open-slum.org
│   ├── social_crawler.py      # Reddit, X, Telegram, Mastodon
│   ├── ipfs_publisher.py      # Publicación IPFS / Pinata
│   └── voter.py               # Sistema de votación comunitaria
├── data/
│   ├── current_report.json    # Último reporte generado
│   └── ipfs_hash.txt          # Último CID publicado
├── .env.example               # Plantilla de credenciales
└── requirements.txt
```

---

## 🤝 Contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licencia

MIT — Libre para todos. Mantén el conocimiento vivo.
