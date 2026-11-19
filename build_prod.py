"""Ostrý web www.yezedokostice.cz z balíčku od Atelieru Dohnalovi.

    python3 build_prod.py      -> dist/  (pak deploy.py, viz README)

atelier/   balíček přesně tak, jak ho ateliér poslal (novou dodávku sem jen nakopírovat, nic v něm neupravovat)
Navíc oproti dodávce:
  - stránka Pro občany (obcane.html): obsah z web/obcane.html, hlavička a patička z atelier/kontakt.html,
    styly v obcane.css (jen pro tuto stránku), odkaz „Pro občany“ v menu všech stránek
  - z patičky pryč odkaz „Správa webu: Zdeněk Matuška“
  - 404.html, web.config (atelier.web.config), sitemap s obcane.html
  - bez Thumbs.db a kopií „… 2“ z iCloudu
"""
import pathlib, re, shutil

SRC = pathlib.Path('atelier')
OUT = pathlib.Path('dist')
rd = lambda p: pathlib.Path(p).read_text(encoding='utf-8')

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns('.DS_Store', 'Thumbs.db', '* 2.*', '* 2'))

CREDIT = re.compile(r'\s*<a href="https://www\.zdenekmatuska\.cz/"[^>]*>Správa webu: Zdeněk Matuška</a>')
NAV_ITEM = '<a href="obcane.html">Pro občany</a>\n'


def add_nav(html):
    # „Pro občany“ před Kontakt v hlavním i spodním menu
    return html.replace('<a href="kontakt.html">Kontakt</a>', NAV_ITEM + '<a href="kontakt.html">Kontakt</a>')


# --- stránka Pro občany ---
shell = rd(SRC / 'kontakt.html')
main = re.search(r'<main id="obsah".*?</main>', rd('web/obcane.html'), re.S).group(0)
# neodpovězené otázky („Doplní obec“) na ostrý web nepatří
main = re.sub(r'<article class="yz-card yz-todo">.*?</article>\n?', '', main, flags=re.S)
main = re.sub(r'<details>\s*<summary>[^<]*</summary>\s*<p class="yz-todo-line">.*?</details>\n?', '', main, flags=re.S)
assert 'yz-todo' not in main, 'zůstal blok Doplní obec'
main = main.replace('kontakt.html?role=obcan#poptavka', 'kontakt.html').replace('href="pribeh.html"', 'href="index.html#pribeh"')
page = re.sub(r'<main id="obsah".*?</main>', lambda m: main, shell, flags=re.S)
title = 'Pro občany — YEZEDO Kostice'
desc = 'Co bude ve starém JZD v Kosticích: park s vyhlídkou, průchozí areál, kavárna v sýpce a haly pro menší firmy. Odpovědi na otázky občanů.'
url = 'https://www.yezedokostice.cz/obcane.html'
page = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', page)
for prop, val in (('og:title', title), ('og:description', desc), ('og:url', url),
                  ('og:image', 'https://www.yezedokostice.cz/assets/images/existing.webp')):
    page = re.sub(rf'(<meta property="{prop}" content=")[^"]*', lambda m: m.group(1) + val, page)
page = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, page)
page = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, page)
page = page.replace('data-page="kontakt.html"', 'data-page="obcane.html"')
page = page.replace(' aria-current="page"', '')
page = re.sub(r'(<link rel="stylesheet" href="styles\.css[^"]*">)', r'\1\n<link rel="stylesheet" href="obcane.css?v=1">', page, count=1)
(OUT / 'obcane.html').write_text(page, encoding='utf-8')

css = rd('web/styles.css')
(OUT / 'obcane.css').write_text('/* Stránka Pro občany – doplněk k styles.css ateliéru */\n'
                                + css[css.index('/* ===== Úvod pro investory, firmy a občany'):], encoding='utf-8')

# --- 404 ve stylu ateliéru ---
p404 = re.sub(r'<main id="obsah".*?</main>', '''<main id="obsah" tabindex="-1">
<section class="page-heading sage" id="top">
<div class="container">
<p class="eyebrow">Chyba 404</p>
<h1>STRÁNKA<br>NENALEZENA.</h1>
<p class="lead">Odkaz je neplatný nebo stránka změnila adresu. <a href="/">Pokračujte na úvod</a>.</p>
</div>
</section>
</main>''', shell, flags=re.S)
p404 = re.sub(r'<title>.*?</title>', '<title>Stránka nenalezena — YEZEDO Kostice</title>', p404)
p404 = p404.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
p404 = p404.replace(' aria-current="page"', '')
# 404 se zobrazuje i na hlubších adresách, odkazy musí být od kořene webu
p404 = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)', r'\1="/', p404)
(OUT / '404.html').write_text(p404, encoding='utf-8')

# --- úpravy všech stránek ---
for f in OUT.rglob('*.html'):
    t = rd(f)
    t = CREDIT.sub('', t)
    t = add_nav(t)
    if f.name == 'obcane.html':
        t = t.replace('<a href="obcane.html">', '<a href="obcane.html" aria-current="page">')
    f.write_text(t, encoding='utf-8')

shutil.copy('atelier.web.config', OUT / 'web.config')
sm = rd(OUT / 'sitemap.xml')
if 'obcane.html' not in sm:
    sm = sm.replace('</urlset>', '<url><loc>https://www.yezedokostice.cz/obcane.html</loc></url></urlset>')
    (OUT / 'sitemap.xml').write_text(sm, encoding='utf-8')

# --- kontrola ---
problems = []
for f in OUT.rglob('*.html'):
    t = rd(f)
    if 'Zdeněk Matuška' in t or 'zdenekmatuska' in t:
        problems.append(f'{f}: zůstal odkaz na zdenekmatuska')
    for ref in re.findall(r'(?:href|src)="([^"#?]+)', t):
        if ref.startswith(('http:', 'https:', 'mailto:', 'tel:')):
            continue
        target = OUT / ref.lstrip('/') if ref.startswith('/') else f.parent / ref
        if not target.exists():
            problems.append(f'{f.relative_to(OUT)} -> {ref}')
print('\n'.join(sorted(set(problems))) or 'kontrola v pořádku')
print(f'hotovo: {OUT}, stránek {len(list(OUT.rglob("*.html")))}')
