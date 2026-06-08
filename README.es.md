# Anna's Archive Hub

<img width="680" height="480" alt="Gemini_Generated_Image" src="https://github.com/user-attachments/assets/cfd41e9b-3230-4169-a1e2-b863e4d22e2d" />

> 🔥 **Rastreador de dominios auto-actualizable para Anna's Archive y shadow libraries — con verificación en tiempo real y publicación permanente en IPFS. No pierdas el acceso nunca más.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![IPFS](https://img.shields.io/badge/IPFS-Published-green.svg)](https://ipfs.io)

[🇬🇧 English version](README.md)

---

## 📡 Último Reporte (IPFS — Inmutable)

**CID actual:** `QmVd1ZsHpex7o2w3MbxNCsRMpTLwWfZip9HW5u9jQ9W8e1`

| Gateway | Enlace |
|---------|--------|
| ipfs.io | [Abrir reporte](https://ipfs.io/ipfs/QmVd1ZsHpex7o2w3MbxNCsRMpTLwWfZip9HW5u9jQ9W8e1) |
| dweb.link | [Abrir reporte](https://dweb.link/ipfs/QmVd1ZsHpex7o2w3MbxNCsRMpTLwWfZip9HW5u9jQ9W8e1) |
| Pinata | [Abrir reporte](https://gateway.pinata.cloud/ipfs/QmVd1ZsHpex7o2w3MbxNCsRMpTLwWfZip9HW5u9jQ9W8e1) |

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

**Requisitos:** Python 3.12+, Git

```bash
git clone https://github.com/annas-archive-hub/annas-archive-hub
cd annas-archive-hub

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env            # opcional — ver Configuración
```

---

## 🖥️ Uso

Hay dos formas de usar la herramienta:

### Opción A — Menú interactivo (`main.py`)

Para control manual. Lánzalo, elige una opción, ve los resultados en pantalla.

```bash
python main.py
```

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        ANNA'S ARCHIVES HUB                                ║
║             Self-updating domain tracker + IPFS immortality                ║
╚════════════════════════════════════════════════════════════════════════════╝

  1. Probar dominios estáticos       → comprueba la lista de dominios fijos
  2. Probar todos los dominios       → estáticos + dominios votados
  3. Añadir dominio manualmente      → proponer un nuevo dominio
  4. Votar por un dominio            → dar un voto a un dominio candidato
  5. Ver dominios pendientes         → candidatos esperando votos
  6. Publicar reporte en IPFS        → pinnear en Pinata / nodo local
  7. Mostrar último hash IPFS        → CID actual + URLs públicas
  8. Rastrear open-slum.org          → descubrir dominios nuevos
  9. Rastrear fuentes sociales       → Reddit, X/Twitter, Telegram, Mastodon
  0. Salir
```

### Opción B — Pipeline automático (`run.py`)

Ejecuta todo en secuencia sin intervención: rastrear → verificar → publicar → log.
Diseñado para cron. No requiere interacción.

```bash
python run.py
```

```
[1/5] Rastreando open-slum.org...    → encuentra dominios candidatos
[2/5] Rastreando fuentes sociales... → Reddit, X, Telegram, Mastodon
[3/5] Probando N dominios...         → verifica cuáles están activos
[4/5] Publicando en IPFS...          → pinnea el reporte, muestra CID
[5/5] Guardando log...               → añade línea a logs/update.log
✅ Ejecución completada
```

### Automatizar con cron (cada 6 horas)

```bash
crontab -e
```

Añade esta línea (reemplaza la ruta con la ubicación real del proyecto):

```
0 */6 * * * cd /home/tuusuario/annas-archive-hub && source venv/bin/activate && python run.py >> logs/cron.log 2>&1
```

---

## ⚙️ Configuración

Copia `.env.example` a `.env` y añade tus credenciales de [Pinata](https://pinata.cloud) para publicación IPFS permanente (plan gratuito: 1 GB):

```env
PINATA_API_KEY=tu_key_aqui
PINATA_API_SECRET=tu_secret_aqui
```

**Sin Pinata:** los reportes se publican en tu nodo IPFS local (requiere el daemon corriendo). La herramienta funciona sin credenciales — la publicación en IPFS es opcional.

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
