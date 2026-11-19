"""Nová verze webu (podklad od Atelieru Dohnalovi, upraveno 11/2026).

Zdroj: web/ (ruční HTML, styles.css, app.js). Upravuje se přímo tam.
    python3 build_web.py      -> docs/novy/  náhled na https://yezedo.zdenekmatuska.cz/novy/ (noindex)

Ostrý web zatím běží ze staré verze (build.py -> dist/). Před přepnutím na novou verzi viz README.
"""
import pathlib, re, shutil

SRC = pathlib.Path('web')
OUT = pathlib.Path('docs/novy')
NOINDEX = '<meta name="robots" content="noindex, nofollow">'

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns('.DS_Store', 'Thumbs.db', '* 2.*', 'robots.txt', 'sitemap.xml'))

for page in OUT.rglob('*.html'):
    html = page.read_text(encoding='utf-8')
    if NOINDEX not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + NOINDEX, 1)
    page.write_text(html, encoding='utf-8')

# hlídání odkazů: každý místní odkaz musí vést na existující soubor
missing = set()
for page in OUT.rglob('*.html'):
    for ref in re.findall(r'(?:href|src)="([^"#?]+)', page.read_text(encoding='utf-8')):
        if ref.startswith(('http:', 'https:', 'mailto:', 'tel:')):
            continue
        if not (page.parent / ref).exists():
            missing.add(f'{page.relative_to(OUT)} -> {ref}')
print('\n'.join(sorted(missing)) or 'odkazy v pořádku')
print(f'hotovo: {OUT}')
