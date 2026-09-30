"""Převede designové reference handoff/*.dc.html na čistý statický web v docs/.

Spuštění:  python3 optimize_images.py   (jen když se změní obrázky)
           python3 build.py
"""
import html
import json
import os
import re
import shutil

SRC = 'handoff'
OUT = 'docs'
SITE = 'https://yezedo.zdenekmatuska.cz'
# Náhled pro klienta: dokud je True, vyhledávače web neindexují (meta robots + robots.txt).
NOINDEX = True

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
    {'title': 'Zahájení výstavby zóny', 'date': '2025'},
    {'title': 'Kolaudace první etapy hal', 'date': '2026'},
    {'title': 'Dokončení celého areálu', 'date': '2028', 'note': 'předpoklad'},
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
                     lambda m: 'data-lightbox="/%s"' % IMAGES[LIGHTBOX[m.group(1)]]['webp'], tpl)
        tpl = re.sub(r'\s*<sc-if value="\{\{ lightbox \}\}".*?</sc-if>', LIGHTBOX_HTML, tpl, flags=re.S)
        # tlačítko v hero odkazuje na #dokumenty, sekce ale neměla id
        tpl = tpl.replace('<section style="background:#161c11;padding:0 clamp(20px,5vw,44px);">\n    <a href="Dokumenty.dc.html"',
                          '<section id="dokumenty" style="background:#161c11;padding:0 clamp(20px,5vw,44px);">\n    <a href="Dokumenty.dc.html"')
        assert 'id="dokumenty"' in tpl
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


LIGHTBOX_HTML = '''
  <div data-lightbox-overlay hidden style="position:fixed;inset:0;z-index:90;background:rgba(10,12,8,0.94);display:flex;align-items:center;justify-content:center;padding:clamp(16px,5vw,56px);cursor:zoom-out;backdrop-filter:blur(6px);">
    <img alt="Zvětšená vizualizace" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:4px;box-shadow:0 30px 90px rgba(0,0,0,0.6);" />
    <span style="position:absolute;top:28px;right:36px;font-family:'DM Sans',sans-serif;font-size:12px;letter-spacing:0.16em;text-transform:uppercase;color:#cbb98e;">Zavřít ✕</span>
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


def head(name, meta):
    url = SITE + meta['path']
    og = IMAGES[meta['og']]['fallback']
    robots = '\n<meta name="robots" content="noindex, nofollow">' if NOINDEX else ''
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
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
<script src="/main.js" defer></script>
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


def main():
    if os.path.exists(OUT):
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
    open(f'{OUT}/styles.css', 'w', encoding='utf-8').write(
        BASE_CSS + '\n'.join(helmet_blocks) + '\n' + sheet.css() + '\n')
    shutil.copy('main.js', f'{OUT}/main.js')
    shutil.copy('favicon.svg', f'{OUT}/favicon.svg')
    shutil.copytree(f'{SRC}/dokumenty', f'{OUT}/dokumenty', dirs_exist_ok=True)
    open(f'{OUT}/CNAME', 'w').write('yezedo.zdenekmatuska.cz\n')
    open(f'{OUT}/.nojekyll', 'w').write('')
    urls = '\n'.join(f'  <url><loc>{SITE}{m["path"]}</loc></url>' for m in PAGES.values())
    open(f'{OUT}/sitemap.xml', 'w').write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    robots = 'User-agent: *\nDisallow: /\n' if NOINDEX else f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n'
    open(f'{OUT}/robots.txt', 'w').write(robots)
    print('✓ styles.css: %d tříd' % len(sheet.classes))


if __name__ == '__main__':
    main()
