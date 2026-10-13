"""Převede designové reference handoff/*.dc.html na čistý statický web v docs/.

Spuštění:  python3 optimize_images.py   (jen když se změní obrázky)
           python3 build.py         náhled pro klienta -> docs/ (GitHub Pages, yezedo.zdenekmatuska.cz)
           python3 build.py prod    ostrý web -> dist/ (www.yezedokostice.cz, nahrává deploy.py)
"""
import datetime
import html
import json
import os
import re
import shutil
import sys

SRC = 'handoff'
PROD = sys.argv[1:] == ['prod']
OUT = 'dist' if PROD else 'docs'
SITE = 'https://www.yezedokostice.cz' if PROD else 'https://yezedo.zdenekmatuska.cz'
# Ostrý web: dokud je True, vyhledávače ho neindexují (meta robots + robots.txt). Po schválení klientem
# přepnout na False, sestavit a nahrát. Náhled na subdoméně se neindexuje nikdy (byl by duplicitou).
NOINDEX_PROD = True
NOINDEX = NOINDEX_PROD if PROD else True

IMAGES = json.load(open('images.json'))

PAGES = {
    'Domu': {
        'out': 'index.html', 'path': '/',
        'title': 'Yezedo Kostice – smart zóna pro výrobu, služby a podnikání',
        'desc': 'Nová průmyslová a podnikatelská zóna v Kosticích u Břeclavi. Výrobní a skladové haly se zelenými střechami, retenční jezero, park a cesty propojené s obcí.',
        'og': 'viz/02-1.jpg',
    },
    'Development': {
        'out': 'development/index.html', 'path': '/development/',
        'title': 'Yezedo Development – haly a pozemky v Kosticích | Yezedo Kostice',
        'desc': 'Výrobní a skladové haly SO03–SO09 v zóně Yezedo Kostice. Dispozice na míru, kanceláře ve 2. NP a kompletní infrastruktura areálu.',
        'og': 'viz/03-1.jpg',
    },
    'Services': {
        'out': 'services/index.html', 'path': '/services/',
        'title': 'Yezedo Services – správa areálu | Yezedo Kostice',
        'desc': 'Yezedo Services zajistí správu a údržbu společných částí areálu – zeleň, komunikace, parkoviště i energetickou koncepci s KES Kostice.',
        'og': 'viz/services-01.jpg',
    },
    'BIQ': {
        'out': 'biq/index.html', 'path': '/biq/',
        'title': 'BIQ – Sýpka, Bílá ikona Kostic | Yezedo Kostice',
        'desc': 'Sýpka v areálu Yezedo Kostice se promění v inovační budovu se sdílenými dílnami, coworkingem, multifunkčním sálem a vyhlídkovou galerií.',
        'og': 'viz/biq-areal-letecky.png',
    },
    'Dokumenty': {
        'out': 'dokumenty/index.html', 'path': '/dokumenty/',
        'title': 'Dokumenty ke stažení | Yezedo Kostice',
        'desc': 'Průvodní list, situační výkresy a výkresová dokumentace hal zóny Yezedo Kostice ke stažení v PDF.',
        'og': 'viz/01.jpg',
    },
}

# Data ze skriptů v .dc.html (převzato 1:1)
STATUS = {
    'free': {'label': 'Volná', 'bg': '#cbb98e', 'fg': '#161c11'},
    'reserved': {'label': 'Rezervováno', 'bg': 'rgba(250,248,242,0.9)', 'fg': '#161c11'},
    'taken': {'label': 'Obsazeno', 'bg': 'rgba(22,28,17,0.75)', 'fg': 'rgba(250,248,242,0.8)'},
}
HALLS = [
    {'code': 'SO03', 'title': 'Výrobní hala', 'size': '54 × 24 m', 'area': '1 296 m²', 'units': '5', 'status': 'free', 'img': 'assets/viz/hall-SO03-b.jpg', 'pdf': 'dokumenty/SO03/SO03-01.01-PUDORYS.pdf', 'desc': 'Pět sekcí o šířce 9–12 m s vlastními vjezdy z obou stran haly.'},
    {'code': 'SO04', 'title': 'Výrobní hala', 'size': '66 × 24 m', 'area': '1 584 m²', 'units': '5', 'status': 'free', 'img': 'assets/viz/hall-SO04.jpg', 'pdf': 'dokumenty/SO04-pudorys.pdf', 'desc': 'Pět sekcí o šířce 12–15 m, největší z řady hal šířky 24 m.'},
    {'code': 'SO05', 'title': 'Výrobní hala', 'size': '36 × 18 m', 'area': '648 m²', 'units': '3', 'status': 'free', 'img': 'assets/viz/hall-SO05.jpg', 'pdf': 'dokumenty/SO05-pudorys.pdf', 'desc': 'Kompaktní hala se třemi sekcemi po 12 m pro menší provozy a služby.'},
    {'code': 'SO06', 'title': 'Výrobní hala', 'size': '66 × 54 m', 'area': '3 564 m²', 'units': '5+', 'status': 'free', 'img': 'assets/viz/03-23.jpg', 'pdf': 'dokumenty/SO06-pudorys.pdf', 'desc': 'Největší objekt areálu ve tvaru L, vhodný pro výrobu i skladování ve větším měřítku.'},
    {'code': 'SO07', 'title': 'Hala + technické zázemí', 'size': '66 × 18 m', 'area': '1 188 m²', 'units': '2', 'status': 'free', 'img': 'assets/viz/03-24.jpg', 'pdf': 'dokumenty/SO07-pudorys.pdf', 'desc': 'Dvě sekce po 33 m s technickým zázemím areálu.'},
    {'code': 'SO09', 'title': 'Výrobní hala', 'size': '54 × 18 m', 'area': '972 m²', 'units': '5', 'status': 'free', 'img': 'assets/viz/03-25.jpg', 'pdf': 'dokumenty/SO09-pudorys.pdf', 'desc': 'Pět sekcí o šířce 9–12 m v užší hale hloubky 18 m.'},
]
DOCS = [
    {'name': 'A – Průvodní list', 'group': 'Základní', 'key': 'base', 'href': 'dokumenty/A-pruvodni-list.pdf'},
    {'name': 'Seznam příloh', 'group': 'Základní', 'key': 'base', 'href': 'dokumenty/seznam-priloh.pdf'},
    {'name': 'C.1 – Situační výkres širších vztahů', 'group': 'Situace', 'key': 'sit', 'href': 'dokumenty/C1-situace-sirsich-vztahu.pdf'},
    {'name': 'C.2 – Katastrální situační výkres', 'group': 'Situace', 'key': 'sit', 'href': 'dokumenty/C2-katastralni-situace.pdf'},
    {'name': 'SO03 Výrobní hala – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO03-pudorys.pdf'},
    {'name': 'SO03 Výrobní hala – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO03-pohledy.pdf'},
    {'name': 'SO04 Výrobní hala – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO04-pudorys.pdf'},
    {'name': 'SO04 Výrobní hala – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO04-pohledy.pdf'},
    {'name': 'SO05 Výrobní hala – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO05-pudorys.pdf'},
    {'name': 'SO05 Výrobní hala – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO05-pohledy.pdf'},
    {'name': 'SO06 Výrobní hala – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO06-pudorys.pdf'},
    {'name': 'SO06 Výrobní hala – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO06-pohledy.pdf'},
    {'name': 'SO07 Hala + technické zázemí – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO07-pudorys.pdf'},
    {'name': 'SO07 Hala + technické zázemí – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO07-pohledy.pdf'},
    {'name': 'SO09 Výrobní hala – půdorys', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO09-pudorys.pdf'},
    {'name': 'SO09 Výrobní hala – pohledy', 'group': 'Objekty', 'key': 'obj', 'href': 'dokumenty/SO09-pohledy.pdf'},
]
TIMELINE = [
    {'title': 'Zahájení', 'date': '2024'},
    {'title': 'Kolaudace inženýrských sítí', 'date': '2026'},
    {'title': 'Projektová příprava', 'date': '2027'},
    {'title': 'Začátek výstavby hal', 'date': '2028'},
]
LIGHTBOX = {
    'openLake': 'viz/02-1.jpg', 'openRoad': 'viz/02-2.jpg', 'openYard': 'viz/03-22.jpg',
    'openShop': 'viz/03-25.jpg', 'openStreet': 'viz/03-24.jpg', 'openPlan': 'viz/01.jpg',
}

# Lorem ipsum na dlaždicích Domů -> první věty z klientských PDF (podklady/)
TILE_TEXTS = {
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Investor a developer průmyslové zóny.':
        'YEZEDO Development proměňuje areál bývalého zemědělského družstva v Kosticích v moderní podnikatelskou zónu.',
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.':
        'YEZEDO Services zajistí správu a údržbu společných částí areálu, aby se firmy mohly soustředit na své podnikání.',
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.':
        'Sýpka patří k výrazným stavbám někdejšího zemědělského areálu v Kosticích.',
}


def esc(v):
    return html.escape(str(v), quote=True)


def expand_for(tpl, name, items):
    """<sc-for list="{{ name }}" as="x"> ... </sc-for> -> opakovaný obsah s dosazenými hodnotami."""
    m = re.search(r'<sc-for list="\{\{ %s \}\}" as="(\w+)"[^>]*>(.*?)</sc-for>' % name, tpl, re.S)
    alias, body = m.group(1), m.group(2)
    out = []
    for item in items:
        chunk = re.sub(r'\{\{ %s\.(\w+) \}\}' % alias, lambda mm: esc(item.get(mm.group(1), '')), body)
        # <sc-if value="..."> uvnitř smyčky: prázdná hodnota = blok vynechat
        chunk = re.sub(r'<sc-if value="([^"]*)"[^>]*>(.*?)</sc-if>',
                       lambda mm: mm.group(2) if mm.group(1).strip() else '', chunk, flags=re.S)
        out.append(chunk)
    return tpl[:m.start()] + ''.join(out) + tpl[m.end():]


def page_specific(name, tpl):
    if name == 'Domu':
        for old, new in TILE_TEXTS.items():
            assert old in tpl, old
            tpl = tpl.replace(old, new)
        tpl = expand_for(tpl, 'timeline', TIMELINE)
        # Galerie: onClick -> data-lightbox, vlastní lightbox ve vanilla JS
        tpl = re.sub(r'onClick="\{\{ (open\w+) \}\}"',
                     lambda m: 'data-lightbox="/%s" role="button" tabindex="0"' % IMAGES[LIGHTBOX[m.group(1)]]['webp'], tpl)
        tpl = re.sub(r'\s*<sc-if value="\{\{ lightbox \}\}".*?</sc-if>', LIGHTBOX_HTML, tpl, flags=re.S)
        # tlačítko v hero odkazuje na #dokumenty, sekce ale neměla id
        tpl = tpl.replace('<section style="background:#161c11;padding:0 clamp(20px,5vw,44px);">\n    <a href="Dokumenty.dc.html"',
                          '<section id="dokumenty" style="background:#161c11;padding:0 clamp(20px,5vw,44px);">\n    <a href="Dokumenty.dc.html"')
        assert 'id="dokumenty"' in tpl
        # Dlaždice a sekce s videem: na tabletu pod sebou (jinak 2 + 1 a stlačené video)
        for marker, grid in (('data-pillars', 'grid-template-columns:repeat(auto-fit,minmax(260px,1fr));">'),
                             ('data-about', 'grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));gap:clamp(40px,6vw,96px);align-items:start;">')):
            old = '<div style="max-width:1240px;margin:0 auto;display:grid;' + grid
            assert tpl.count(old) == 1, marker
            tpl = tpl.replace(old, old.replace('<div ', '<div %s ' % marker))
        # Dlaždice jsou hned pod h1, takže h2 (ne h3)
        tpl, n = re.subn(r'<a href="\w+\.dc\.html" data-pillar.*?</a>',
                         lambda m: m.group(0).replace('<h3', '<h2').replace('</h3>', '</h2>'), tpl, flags=re.S)
        assert n == 3
        # Mapa: Google iframe (a jeho cookies) se načte až po kliknutí
        tpl, n = re.subn(r'<iframe title="[^"]*" src="(https://www\.google\.com/maps[^"]*)" style="[^"]*"></iframe>',
                         lambda m: '<div class="map"><button type="button" class="map-btn" data-map="%s">Zobrazit mapu</button>'
                                   '<p class="map-note">Mapu poskytuje Google, načte se až po kliknutí.</p></div>'
                                   % m.group(1).replace('&', '&amp;'), tpl)
        assert n == 1
        # Video: vlastní náhled, přehrávač YouTube (a jeho cookies) se načte až po kliknutí
        tpl, n = re.subn(r'<iframe src="https://www\.youtube\.com/embed/([\w-]+)" title="([^"]*)"[^>]*></iframe>',
                         r'<a class="yt" href="https://youtu.be/\1" data-yt="\1" data-title="\2" target="_blank"'
                         r' aria-label="Přehrát – \2"><span class="yt-play" aria-hidden="true"></span></a>', tpl)
        assert n == 1
    elif name == 'Development':
        halls = [{**h, 'status': STATUS[h['status']]['label'], 'statusBg': STATUS[h['status']]['bg'],
                  'statusFg': STATUS[h['status']]['fg']} for h in HALLS]
        tpl = expand_for(tpl, 'halls', halls)
    elif name == 'Dokumenty':
        tpl = tpl.replace('<a href="{{ doc.href }}"', '<a data-key="{{ doc.key }}" href="{{ doc.href }}"')
        tpl = expand_for(tpl, 'docs', DOCS)
        for key, suffix in (('all', 'All'), ('base', 'Base'), ('sit', 'Sit'), ('obj', 'Obj')):
            active = ' is-active' if key == 'all' else ''
            tpl = tpl.replace('onClick="{{ tab%s }}"' % suffix,
                              'data-tab="%s" class="tab%s" aria-pressed="%s"' % (key, active, 'true' if active else 'false'))
            tpl = tpl.replace('background:{{ bg%s }};color:{{ fg%s }};' % (suffix, suffix), '')
        tpl = tpl.replace('{{ count }} dokumentů', '<span data-count>%d</span> dokumentů' % len(DOCS))
    assert '{{' not in tpl and '<sc-' not in tpl, (name, re.findall(r'\{\{[^}]*\}\}|<sc-\w+', tpl))
    return tpl


CREDIT_URL = 'https://www.zdenekmatuska.cz/tvorba-webovych-stranek-breclav/'


def refine(tpl):
    """Úpravy nad rámec handoffu, stejné pro všechny stránky: kontrast, přístupnost, patička."""
    # Kontrast (WCAG AA 4.5:1): zlatohnědé popisky na světlém pozadí, slabý text na tmavém
    tpl = tpl.replace('color:#8e7f58', 'color:#766843')
    tpl = re.sub(r'color:rgba\(250,248,242,0\.(35|4|45)\)', 'color:rgba(250,248,242,0.55)', tpl)
    tpl = tpl.replace('font-size:11px', 'font-size:12px')
    # Mobilní menu: přepínač zůstává v pořadí tabulátoru (display:none ho z něj vyřadil)
    old = '<input type="checkbox" id="navtoggle" data-nav-toggle style="display:none;" />'
    assert old in tpl
    tpl = tpl.replace(old, '<input type="checkbox" id="navtoggle" data-nav-toggle class="vh" aria-label="Menu" />')
    # Odkaz „přeskočit na obsah“ a <main>
    assert tpl.count('<header') == 1 and tpl.count('<footer') == 1
    tpl = tpl.replace('<header', '<a class="skip" href="#obsah">Přeskočit na obsah</a>\n  <header', 1)
    tpl = tpl.replace('</header>', '</header>\n  <main id="obsah" tabindex="-1">', 1)
    tpl = tpl.replace('<footer', '</main>\n\n  <footer', 1)
    # Patička: na všech stránkách stejných sedm odkazů
    i = tpl.index('<footer')
    foot = tpl[i:]
    if 'Development.dc.html' not in foot:
        m = re.search(r'( *)<a href="[^"]*#zona"([^>]*)>Zóna</a>\n', foot)
        extra = ''.join('%s<a href="%s.dc.html"%s>%s</a>\n' % (m.group(1), page, m.group(2), page)
                        for page in ('Development', 'Services', 'BIQ'))
        tpl = tpl[:i] + foot[:m.end()] + extra + foot[m.end():]
    # Podpis autora webu v patičce
    old = '© 2026 Yezedo Kostice</div>'
    assert tpl.count(old) == 1
    tpl = tpl.replace(old, '© 2026 Yezedo Kostice · Web vytvořil <a class="credit" href="%s" target="_blank">Zdeněk Matuška</a></div>' % CREDIT_URL)
    return tpl


LIGHTBOX_HTML = '''
  <div data-lightbox-overlay hidden role="dialog" aria-modal="true" aria-label="Zvětšený obrázek" style="position:fixed;inset:0;z-index:90;background:rgba(10,12,8,0.94);display:flex;align-items:center;justify-content:center;padding:clamp(16px,5vw,56px);cursor:zoom-out;backdrop-filter:blur(6px);">
    <img alt="Zvětšená vizualizace" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:4px;box-shadow:0 30px 90px rgba(0,0,0,0.6);" />
    <button type="button" data-lightbox-close style="position:absolute;top:14px;right:22px;padding:14px;background:none;border:0;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:12px;letter-spacing:0.16em;text-transform:uppercase;color:#cbb98e;">Zavřít ✕</button>
  </div>'''


def rewrite_links(tpl):
    targets = {'Domu': '/', 'Development': '/development/', 'Services': '/services/', 'BIQ': '/biq/', 'Dokumenty': '/dokumenty/'}
    tpl = re.sub(r'href="(\w+)\.dc\.html(#[\w-]+)?"', lambda m: 'href="%s%s"' % (targets[m.group(1)], m.group(2) or ''), tpl)
    tpl = re.sub(r'(href|src)="(dokumenty|assets)/', r'\1="/\2/', tpl)
    tpl = tpl.replace('target="_blank"', 'target="_blank" rel="noopener"')
    return tpl


def pictures(tpl):
    """<img src="assets/x.jpg"> -> <picture> s WebP + fallbackem, rozměry a lazy loadingem."""
    first = [True]

    def repl(m):
        tag = m.group(0)
        src = re.search(r'src="/assets/([^"]+)"', tag)
        if not src:
            return tag
        info = IMAGES[src.group(1)]
        style = re.search(r'style="([^"]*)"', tag)
        style = style.group(1) if style else ''
        full = 'position:absolute' in style or 'height:clamp' in style
        sizes = '100vw' if full else '(max-width: 760px) 100vw, 50vw'
        srcset = '/%s 1920w' % info['webp'] if 'webp960' not in info else '/%s 960w, /%s %dw' % (info['webp960'], info['webp'], info['w'])
        attrs = 'width="%d" height="%d"' % (info['w'], info['h'])
        if first[0]:
            attrs += ' fetchpriority="high"'
            first[0] = False
        else:
            attrs += ' loading="lazy"'
        attrs += ' decoding="async"'
        tag = tag.replace(src.group(0), 'src="/%s" %s' % (info['fallback'], attrs))
        return '<picture><source type="image/webp" srcset="%s" sizes="%s">%s</picture>' % (srcset, sizes, tag)

    return re.sub(r'<img\b[^>]*>', repl, tpl)


class StyleSheet:
    """Inline styly (a style-hover) -> sdílené třídy v styles.css."""

    def __init__(self):
        self.classes = {}

    def cls(self, style, hover):
        key = (style.strip().rstrip(';'), hover.strip().rstrip(';'))
        if key not in self.classes:
            self.classes[key] = 'c%d' % (len(self.classes) + 1)
        return self.classes[key]

    def convert(self, tpl):
        def repl(m):
            tag = m.group(0)
            style = re.search(r'\sstyle="([^"]*)"', tag)
            hover = re.search(r'\sstyle-hover="([^"]*)"', tag)
            if not style and not hover:
                return tag
            name = self.cls(style.group(1) if style else '', hover.group(1) if hover else '')
            for s in (style, hover):
                if s:
                    tag = tag.replace(s.group(0), '', 1)
            existing = re.search(r'\sclass="([^"]*)"', tag)
            if existing:
                return tag.replace(existing.group(0), ' class="%s %s"' % (existing.group(1), name), 1)
            return re.sub(r'^<([\w-]+)', r'<\1 class="%s"' % name, tag)

        return re.sub(r'<[a-zA-Z][^>]*>', repl, tpl)

    def css(self):
        out = []
        for (style, _), name in self.classes.items():
            if style:
                out.append('.%s{%s}' % (name, style))
        for (_, hover), name in self.classes.items():
            if hover:
                out.append('.%s:hover{%s}' % (name, hover))
        return '\n'.join(out)


PLACE = {
    '@type': 'Place', '@id': 'https://www.yezedokostice.cz/#areal', 'name': 'Yezedo Kostice',
    'description': 'Průmyslová a podnikatelská zóna v Kosticích u Břeclavi – výrobní a skladové haly, služby a veřejný prostor.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Kostice', 'postalCode': '691 52',
                'addressRegion': 'Jihomoravský kraj', 'addressCountry': 'CZ'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': 48.751411, 'longitude': 16.969294},
    'hasMap': 'https://www.google.com/maps?q=48.751411,16.969294',
    'telephone': '+420725111277', 'email': 'starosta@kostice.cz',
}


def json_ld(meta):
    """Strukturovaná data: na Domů místo + web, na podstránkách drobečková navigace."""
    if meta['path'] == '/':
        graph = [dict(PLACE, url=SITE + '/', image=SITE + '/' + IMAGES[meta['og']]['fallback']),
                 {'@type': 'WebSite', '@id': SITE + '/#web', 'url': SITE + '/', 'name': 'Yezedo Kostice', 'inLanguage': 'cs'}]
    else:
        crumb = meta['title'].split(' | ')[0].split(' – ')[0]
        graph = [{'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Yezedo Kostice', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': crumb, 'item': SITE + meta['path']}]}]
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    return '<script type="application/ld+json">%s</script>' % data.replace('</', '<\\/')


def head(name, meta, indexable=True):
    url = SITE + meta['path']
    info = IMAGES[meta['og']]
    og = info['fallback']
    extra = json_ld(meta) if indexable else ''
    robots = '\n<meta name="robots" content="noindex, nofollow">' if NOINDEX or not indexable else ''
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['desc'])}">{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="cs_CZ">
<meta property="og:site_name" content="Yezedo Kostice">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['desc'])}">
<meta property="og:image" content="{SITE}/{og}">
<meta property="og:image:width" content="{info['w']}">
<meta property="og:image:height" content="{info['h']}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<script src="/main.js" defer></script>
{extra}
</head>
'''


BASE_CSS = '''/* Vygenerováno skriptem build.py z handoff/*.dc.html – needitovat ručně, upravit zdroj a znovu sestavit. */
body{margin:0;font-family:'DM Sans',sans-serif;background:#0f120c;}
body.page-dokumenty{background:#161c11;}
a{color:inherit;text-decoration:none;}
::selection{background:#cbb98e;color:#161c11;}
picture{display:contents;}
picture>source{display:none;}
img{max-width:100%;height:auto;}
[hidden]{display:none !important;}
.tab{background:transparent;color:rgba(250,248,242,0.75);transition:background .3s ease,color .3s ease;}
.tab.is-active{background:#cbb98e;color:#161c11;}
/* video: náhled s tlačítkem, iframe vloží main.js po kliknutí */
.yt{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border-radius:8px;overflow:hidden;background:#161c11 url(/assets/viz/02-3-960.webp) center/cover no-repeat;}
.yt::before{content:"";position:absolute;inset:0;background:rgba(15,18,12,0.28);transition:background .3s ease;}
.yt:hover::before{background:rgba(15,18,12,0.12);}
.yt-play{position:relative;width:clamp(64px,7vw,88px);aspect-ratio:1;border-radius:50%;background:#cbb98e;transition:transform .3s ease,background .3s ease;}
.yt-play::after{content:"";position:absolute;left:54%;top:50%;transform:translate(-50%,-50%);border-style:solid;border-width:.7em 0 .7em 1.15em;border-color:transparent transparent transparent #161c11;font-size:clamp(14px,1.5vw,19px);}
.yt:hover .yt-play{transform:scale(1.06);background:#ffffff;}
.yt:focus-visible{outline:2px solid #cbb98e;outline-offset:3px;}
.yt-frame{position:absolute;inset:0;width:100%;height:100%;border:0;display:block;border-radius:8px;}
/* klávesnice: fokus viditelný na světlém i tmavém pozadí */
:focus-visible{outline:2px solid #cbb98e;outline-offset:3px;box-shadow:0 0 0 3px #161c11;}
main:focus{outline:none;box-shadow:none;}
.vh{position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap;}
.skip{position:absolute;left:16px;top:-80px;z-index:100;padding:13px 20px;border-radius:100px;background:#cbb98e;color:#161c11;font-family:'DM Sans',sans-serif;font-weight:500;font-size:13px;letter-spacing:0.12em;text-transform:uppercase;transition:top .2s ease;}
.skip:focus{top:12px;}
[data-lightbox]{cursor:zoom-in;}
/* mapa: náhled se situací areálu, iframe Google vloží main.js po kliknutí */
.map{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;height:clamp(320px,42vw,460px);padding:24px;box-sizing:border-box;text-align:center;background:#161c11 url(/assets/viz/01-960.webp) center/cover no-repeat;}
.map::before{content:"";position:absolute;inset:0;background:rgba(15,18,12,0.74);}
.map-btn{position:relative;padding:17px 30px;border:0;border-radius:100px;background:#cbb98e;color:#161c11;font-family:'DM Sans',sans-serif;font-size:13px;letter-spacing:0.14em;text-transform:uppercase;cursor:pointer;transition:background .3s ease;}
.map-btn:hover{background:#ffffff;}
.map-note{position:relative;margin:0;max-width:30ch;font-family:'DM Sans',sans-serif;font-size:13px;line-height:1.5;color:rgba(250,248,242,0.78);}
.map-frame{display:block;width:100%;height:clamp(320px,42vw,460px);border:0;}
/* stránka 404 */
.e404{min-height:100vh;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;gap:22px;max-width:1240px;margin:0 auto;padding:clamp(28px,6vw,72px) clamp(20px,5vw,44px);background:#161c11;color:#faf8f2;}
.page-404{background:#161c11;}
.e404-logo{position:absolute;top:clamp(20px,4vw,32px);font-family:'Archivo',sans-serif;font-weight:800;font-size:19px;letter-spacing:0.34em;color:#ffffff;}
.e404 h1{margin:0;font-family:'Archivo',sans-serif;font-weight:800;font-size:clamp(40px,7vw,104px);line-height:0.94;letter-spacing:-0.035em;text-transform:uppercase;color:#ffffff;text-wrap:balance;}
.e404 p{margin:0;max-width:46ch;font-family:'DM Sans',sans-serif;font-size:18px;line-height:1.6;color:rgba(250,248,242,0.78);}
.e404-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;}
.e404-links a{padding:17px 30px;border-radius:100px;border:1px solid rgba(250,248,242,0.4);font-family:'DM Sans',sans-serif;font-size:13px;letter-spacing:0.14em;text-transform:uppercase;color:#ffffff;transition:background .3s ease,color .3s ease,border-color .3s ease;}
.e404-links a:first-child{background:#cbb98e;border-color:#cbb98e;color:#161c11;}
.e404-links a:hover{background:#ffffff;border-color:#ffffff;color:#161c11;}
.credit{color:rgba(250,248,242,0.82);text-decoration:underline;text-decoration-color:rgba(203,185,142,0.6);text-underline-offset:3px;transition:color .3s ease;}
.credit:hover{color:#cbb98e;}
/* popisek nad h1 leží na fotce */
main div:has(+ h1){color:#e6d9b4;text-shadow:0 0 3px rgba(15,18,12,0.85),0 1px 16px rgba(15,18,12,0.9);}
@media (min-width:901px){[data-nav-toggle]{display:none;}}
@media (max-width:900px){
  /* hamburger: fokus, křížek po otevření, neprůhledné menu */
  [data-nav-toggle]:focus-visible + [data-burger]{outline:2px solid #cbb98e;outline-offset:2px;border-radius:6px;}
  [data-burger] span{transition:transform .25s ease,opacity .2s ease;}
  [data-nav-toggle]:checked + [data-burger] span:nth-child(1){transform:translateY(6.5px) rotate(45deg);}
  [data-nav-toggle]:checked + [data-burger] span:nth-child(2){opacity:0;}
  [data-nav-toggle]:checked + [data-burger] span:nth-child(3){transform:translateY(-6.5px) rotate(-45deg);}
  header nav[data-nav]{background:#10140d;}
  /* Domů: dlaždice a text s videem pod sebou i na tabletu */
  [data-pillars],[data-about]{grid-template-columns:1fr !important;}
  [data-pillar]{border-right:none !important;border-bottom:1px solid rgba(203,185,142,0.2);padding-left:0 !important;padding-right:0 !important;}
  [data-pillar]:last-child{border-bottom:none;}
  /* dotykové plochy aspoň 44 px */
  header > a{padding:12px 0;margin:-12px 0;}
  footer nav{row-gap:0 !important;}
  footer nav a,footer > a{display:inline-block;padding:14px 0;}
  article a{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;}
  .tab{min-height:44px;}
  a[href^="mailto:"]{display:inline-block;padding:12px 0;}
  a[href^="tel:"]{display:inline-block;padding:8px 0;}
}
/* dlouhá slova v nadpisech na nejmenších mobilech */
@media (max-width:430px){.page-development h1{font-size:11vw;}}
@media (max-width:360px){h2{font-size:30px !important;}}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none !important;}
  .skip,[data-burger] span{transition:none;}
}
'''


def helmet_css(helmet):
    css = re.search(r'<style>(.*?)</style>', helmet, re.S).group(1)
    css = re.sub(r'^\s*(body|a|::selection)\{[^}]*\}\s*$', '', css, flags=re.M)
    return css


def split_rules(css):
    """Rozdělí CSS na top-level bloky (kvůli deduplikaci napříč stránkami)."""
    blocks, depth, cur = [], 0, ''
    for ch in css:
        cur += ch
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                blocks.append(re.sub(r'\s+', ' ', cur).strip())
                cur = ''
    return blocks


PAGE_404 = '''<body class="page-404">
<main class="e404">
  <a class="e404-logo" href="/">YEZEDO</a>
  <h1>Tahle stránka tu není</h1>
  <p>Adresa je nejspíš stará nebo je v ní překlep. Úvodní stránka i dokumenty jsou na svém místě.</p>
  <div class="e404-links"><a href="/">Zpět na úvod</a><a href="/dokumenty/">Dokumenty</a></div>
</main>
</body>
</html>
'''


def main():
    if PROD:
        # ostrý web se skládá načisto, obrázky se berou z náhledu (docs/assets, plní optimize_images.py)
        shutil.rmtree(OUT, ignore_errors=True)
        shutil.copytree('docs/assets', f'{OUT}/assets', ignore=shutil.ignore_patterns('.DS_Store'))
    elif os.path.exists(OUT):
        for entry in os.listdir(OUT):
            if entry not in ('assets', 'CNAME'):
                p = os.path.join(OUT, entry)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    sheet = StyleSheet()
    helmet_blocks = []
    for name, meta in PAGES.items():
        src = open(f'{SRC}/{name}.dc.html', encoding='utf-8').read()
        tpl = src[src.index('<x-dc>') + 6:src.index('</x-dc>')]
        helmet = re.search(r'<helmet>(.*?)</helmet>', tpl, re.S)
        for b in split_rules(helmet_css(helmet.group(1))):
            if b not in helmet_blocks:
                helmet_blocks.append(b)
        tpl = tpl.replace(helmet.group(0), '')
        tpl = page_specific(name, tpl)
        tpl = refine(tpl)
        tpl = rewrite_links(tpl)
        tpl = pictures(tpl)
        tpl = tpl.replace('<iframe ', '<iframe loading="lazy" ')
        tpl = sheet.convert(tpl)
        tpl = re.sub(r'\n{3,}', '\n\n', tpl).strip()
        body_cls = ' class="page-%s"' % meta['path'].strip('/') if meta['path'] != '/' else ' class="page-domu"'
        page = head(name, meta) + f'<body{body_cls}>\n{tpl}\n</body>\n</html>\n'
        path = os.path.join(OUT, meta['out'])
        os.makedirs(os.path.dirname(path) or OUT, exist_ok=True)
        open(path, 'w', encoding='utf-8').write(page)
        print('✓', path)

    # helmet pravidla (media queries s !important) před třídami, aby třídy měly stejnou prioritu jako původní inline styly
    # písma jsou na webu (fonts/), ne z Google Fonts; @font-face musí být před ostatními pravidly
    open(f'{OUT}/styles.css', 'w', encoding='utf-8').write(
        open('fonts/fonts.css', encoding='utf-8').read() + BASE_CSS + '\n'.join(helmet_blocks) + '\n' + sheet.css() + '\n')
    shutil.copytree('fonts', f'{OUT}/fonts', ignore=shutil.ignore_patterns('*.css', '.DS_Store'))
    for f in ('main.js', 'favicon.svg', 'favicon.png', 'apple-touch-icon.png'):
        shutil.copy(f, f'{OUT}/{f}')
    shutil.copytree(f'{SRC}/dokumenty', f'{OUT}/dokumenty', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.DS_Store'))
    meta404 = {'path': '/404.html', 'title': 'Stránka nenalezena | Yezedo Kostice',
               'desc': 'Tato stránka na webu Yezedo Kostice neexistuje.', 'og': PAGES['Domu']['og']}
    open(f'{OUT}/404.html', 'w', encoding='utf-8').write(head('404', meta404, indexable=False) + PAGE_404)
    if PROD:
        shutil.copy('web.config', f'{OUT}/web.config')
    else:
        open(f'{OUT}/CNAME', 'w').write('yezedo.zdenekmatuska.cz\n')
        open(f'{OUT}/.nojekyll', 'w').write('')
    today = datetime.date.today().isoformat()
    urls = '\n'.join(f'  <url><loc>{SITE}{m["path"]}</loc><lastmod>{today}</lastmod></url>' for m in PAGES.values())
    open(f'{OUT}/sitemap.xml', 'w').write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    robots = 'User-agent: *\nDisallow: /\n' if NOINDEX else f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n'
    open(f'{OUT}/robots.txt', 'w').write(robots)
    print('✓ styles.css: %d tříd' % len(sheet.classes))


if __name__ == '__main__':
    main()
