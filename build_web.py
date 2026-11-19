"""Náhled pro investory na https://yezedo.zdenekmatuska.cz/ (GitHub Pages, noindex).

Zdroj: web/ (ruční HTML, styles.css, app.js). Upravuje se přímo tam.
    python3 build_web.py      -> docs/  (pak git push = nasazení náhledu)

Od 19. 11. 2026 je náhled v kořeni domény (dřív /novy/). Staré adresy /novy/… přesměrují na kořen.
Ostrý web www.yezedokostice.cz se skládá jinak: build_prod.py z balíčku ateliéru (atelier/).
"""
import pathlib, re, shutil

SRC = pathlib.Path('web')
OUT = pathlib.Path('docs')
KEEP = {'CNAME', 'robots.txt', '.nojekyll'}
NOINDEX = '<meta name="robots" content="noindex, nofollow">'

OUT.mkdir(exist_ok=True)
for entry in OUT.iterdir():
    if entry.name in KEEP:
        continue
    shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
shutil.copytree(SRC, OUT, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('.DS_Store', 'Thumbs.db', '* 2.*', '* 2', 'robots.txt', 'sitemap.xml'))

pages = sorted(p.name for p in SRC.glob('*.html'))
for page in OUT.rglob('*.html'):
    html = page.read_text(encoding='utf-8')
    if NOINDEX not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + NOINDEX, 1)
    page.write_text(html, encoding='utf-8')

# staré odkazy na /novy/… -> kořen
novy = OUT / 'novy'
novy.mkdir(exist_ok=True)
for name in pages:
    target = '../' if name == 'index.html' else f'../{name}'
    (novy / name).write_text(f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8">{NOINDEX}<meta http-equiv="refresh" content="0;url={target}">
<link rel="canonical" href="https://yezedo.zdenekmatuska.cz/{'' if name == 'index.html' else name}">
<title>YEZEDO – přesměrování</title></head><body><p><a href="{target}">Pokračovat na web YEZEDO</a></p></body></html>
''', encoding='utf-8')

missing = set()
for page in OUT.rglob('*.html'):
    for ref in re.findall(r'(?:href|src)="([^"#?]+)', page.read_text(encoding='utf-8')):
        if ref.startswith(('http:', 'https:', 'mailto:', 'tel:')):
            continue
        if not (page.parent / ref).exists():
            missing.add(f'{page.relative_to(OUT)} -> {ref}')
print('\n'.join(sorted(missing)) or 'odkazy v pořádku')
print(f'hotovo: {OUT}/')
