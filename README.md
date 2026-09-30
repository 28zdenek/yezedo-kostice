# Yezedo Kostice – web

Statický web na https://yezedo.zdenekmatuska.cz (GitHub Pages ze složky `docs/`).

- `handoff/` – designové podklady (`*.dc.html`, obrázky, PDF), nejsou v gitu
- `python3 optimize_images.py` – zmenší obrázky do `docs/assets` (WebP + JPG/PNG fallback)
- `python3 build.py` – převede `handoff/*.dc.html` na `docs/` (HTML, `styles.css`, sitemap, robots)
- `NOINDEX = True` v `build.py` = náhled, vyhledávače web neindexují; po schválení klientem přepnout na `False` a znovu sestavit
