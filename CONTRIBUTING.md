# Guía para contribuidores

Gracias por querer contribuir a Anna's Archive Hub.

---

## Cómo empezar

```bash
git clone https://github.com/annas-archive-hub/anna-archive-hub
cd anna-archive-hub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

---

## Tipos de contribución

### Añadir nuevos dominios
Si encuentras un dominio activo que el sistema no detecta:
1. Abre un Issue con el dominio y cómo lo encontraste
2. O ejecuta `python main.py` → opción 3 para añadirlo localmente

### Añadir nuevas fuentes de descubrimiento
Las fuentes están en `core/social_crawler.py`. Cada fuente es una función independiente que devuelve `list[str]`:

```python
def _crawl_mi_fuente() -> list[str]:
    candidates = []
    # ... lógica de scraping
    candidates.extend(extract_domains(texto))
    return candidates
```

Añádela a `crawl_all()` dentro de `SocialCrawler`.

### Mejorar la verificación de dominios
El verificador está en `core/domain_tester.py`. Usa `curl_cffi` con impersonación de Chrome. Si encuentras dominios que dan falsos negativos, abre un Issue con el dominio y el código de respuesta que obtienes.

### Reportar canales de Telegram verificados
Si encuentras un canal de Telegram legítimo (no spam, activo, comparte dominios reales), abre un Issue con el nombre del canal y por qué lo consideras verificado.

---

## Convenciones

- **Python 3.12+**
- Sin credenciales en el código — usar variables de entorno vía `.env`
- Cada función de fuente devuelve `list[str]` de dominios sin `https://`
- Los dominios siempre en minúsculas

## Pull Requests

1. Fork del repositorio
2. Rama descriptiva: `feat/nueva-fuente-lemmy`, `fix/regex-tld`, etc.
3. Un PR por cambio lógico
4. Describe qué hace y por qué en la descripción del PR
