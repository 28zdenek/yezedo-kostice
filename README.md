# Yezedo Kostice – web

Statický web na https://yezedo.zdenekmatuska.cz (GitHub Pages ze složky `docs/`).

- `handoff/` – designové podklady (`*.dc.html`, obrázky, PDF), nejsou v gitu
- `python3 optimize_images.py` – zmenší obrázky do `docs/assets` (WebP + JPG/PNG fallback)
- `python3 build.py` – převede `handoff/*.dc.html` na `docs/` (HTML, `styles.css`, sitemap, robots)
- `NOINDEX = True` v `build.py` = náhled, vyhledávače web neindexují; po schválení klientem přepnout na `False` a znovu sestavit

## Nová verze (podklad Atelier Dohnalovi, 11/2026)
- Zdroj: `web/` (ruční HTML + `styles.css` + `app.js`), upravuje se přímo tam.
- `python3 build_web.py` → `docs/novy/` = náhled https://yezedo.zdenekmatuska.cz/novy/ (noindex).
- Oproti dodávce: nový úvod (investoři / firmy / občané), původní úvod přesunut do `pribeh.html`, nové menu,
  poptávkový formulář na Kontaktu (mailto), písma WOFF2, STAY ve WebP, odstraněny zbytky offline balíčku.
- Bloky „Doplní obec“ (oranžově přerušovaně) se musí před spuštěním vyplnit nebo smazat.
- Před přepnutím ostrého webu: 301 přesměrování starých adres (`/development/`, `/services/`, `/biq/`, `/dokumenty/`)
  ve `web.config`, vypnout zámek heslem a noindex, CSP zůstává `'self'` + YouTube.
