# Anna's Archive Hub

Sistema descentralizado para rastrear, verificar y compartir dominios activos de Anna's Archive y otras shadow libraries.

Los resultados se publican en **IPFS** — inmutables y accesibles sin servidor propio.

---

## ¿Qué hace?

```
open-slum.org ──┐
                ├──► candidatos ──► verifica HTTP ──► activos ──► IPFS ──► QR/pendrive
Reddit/X/TG  ───┘
```

1. **Rastrea** dominios nuevos desde open-slum.org, Reddit, X (Nitter), Telegram y Mastodon
2. **Verifica** cuáles responden (impersonando Chrome para evitar bloqueos de Cloudflare)
3. **Vota** — la comunidad puede proponer y votar dominios dudosos
4. **Publica** el reporte en IPFS: hash inmutable accesible desde cualquier gateway público
5. **Automatiza** con cron — sin necesidad de tener el ordenador encendido 24/7

---

## Instalación

```bash
git clone https://github.com/tu-usuario/anna-archive-hub
cd anna-archive-hub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y rellena tus credenciales de Pinata (opcional, pero recomendado):

```bash
cp .env.example .env
# editar .env con tu editor
```

---

## Uso

### Modo interactivo (menú completo)

```bash
python main.py
```

| Opción | Función |
|--------|---------|
| 1 | Probar dominios estáticos conocidos |
| 2 | Probar todos (estáticos + verificados por la comunidad) |
| 3 | Añadir un dominio manualmente |
| 4 | Votar por un dominio pendiente |
| 5 | Ver dominios pendientes de verificación |
| 6 | Publicar reporte en IPFS |
| 7 | Ver hash IPFS y URLs públicas |
| 8 | Rastrear open-slum.org |
| 9 | Rastrear fuentes sociales (Reddit, X, Telegram, Mastodon) |

### Modo automático (para cron)

```bash
python run.py
```

### Automatizar con cron (cada 6 horas)

```bash
crontab -e
# Añadir:
0 */6 * * * cd /ruta/al/proyecto && source venv/bin/activate && python run.py >> logs/cron.log 2>&1
```

---

## Publicación en IPFS

Sin Pinata configurado, el reporte se publica en tu nodo local IPFS (requiere daemon corriendo).

Con Pinata, el reporte queda accesible permanentemente en la red pública:

```
https://ipfs.io/ipfs/<CID>
https://cloudflare-ipfs.com/ipfs/<CID>
https://dweb.link/ipfs/<CID>
https://gateway.pinata.cloud/ipfs/<CID>
```

Para configurar Pinata:
1. Crea cuenta gratuita en [pinata.cloud](https://pinata.cloud)
2. Ve a **Developers → API Keys → New Key** (activa `pinFileToIPFS`)
3. Añade las claves a `.env`:
   ```
   PINATA_API_KEY=tu_key
   PINATA_API_SECRET=tu_secret
   ```

---

## Fuentes de descubrimiento

| Fuente | Método | Auth requerida |
|--------|--------|----------------|
| open-slum.org | HTML scraping | No |
| Reddit | JSON API pública | No |
| X/Twitter | Nitter (instancias públicas) | No |
| Telegram | t.me/s/ (canales públicos) | No |
| Mastodon | API pública v2 | No |

> **Nota sobre Telegram:** `TELEGRAM_CHANNELS` está vacío por defecto. Añade solo canales que hayas verificado manualmente — la mayoría de canales con nombres de shadow libraries son spam o impostores.

---

## Estructura del proyecto

```
anna-archive-hub/
├── main.py                    # Menú interactivo
├── run.py                     # Pipeline automático (para cron)
├── config/
│   └── settings.py            # Configuración central
├── core/
│   ├── domain_tester.py       # Verificación de dominios con curl_cffi
│   ├── domain_extractor.py    # Extracción de dominios de texto libre
│   ├── open_slum_crawler.py   # Rastreador de open-slum.org
│   ├── social_crawler.py      # Reddit, X, Telegram, Mastodon
│   ├── ipfs_publisher.py      # Publicación en IPFS / Pinata
│   └── voter.py               # Sistema de votación comunitaria
├── data/
│   ├── current_report.json    # Último reporte generado
│   └── ipfs_hash.txt          # Último CID publicado
├── .env.example               # Plantilla de variables de entorno
└── requirements.txt
```

---

## Por qué IPFS

El CID (Content Identifier) es la huella digital del archivo calculada de su contenido. Es inmutable: el mismo contenido siempre produce el mismo CID, y nadie puede modificarlo sin cambiar el CID. Esto hace el sistema resistente a censura: para eliminarlo habría que tumbar simultáneamente Protocol Labs, Cloudflare y Pinata.

---

## Contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Licencia

MIT
