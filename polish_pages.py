"""Sjednocení podstránek náhledu (web/) se stylem hlavní stránky pro investory. Lze spouštět opakovaně.

    python3 polish_pages.py     (pak python3 make_halls.py a python3 build_web.py)

- úvod podstránky: velká fotka + nadpis + tlačítka (texty nadpisů a perexů ateliéru zůstávají)
- Haly a pronájem: klikací mapa hal nahoře, u každé karty odkaz na stránku haly
- odkazy nabidka-hal.html#SO0X -> stránky hal hala-so0x.html
"""
import pathlib, re

WEB = pathlib.Path('web')
CTA = '<a class="button yz-light" href="index.html#napiste-nam">Domluvit jednání<span aria-hidden="true">↗</span></a>'

# stránka: (štítek, fotka, šířka, výška, druhé tlačítko)
PAGES = {
    'areal.html': ('Areál', 'hero', 2000, 1328,
                   '<a class="button secondary yz-ghost" href="nabidka-hal.html#mapa">Haly na mapě<span aria-hidden="true">↗</span></a>'),
    'nabidka-hal.html': ('Nabídka hal', 'life', 2000, 1125,
                         '<a class="button secondary yz-ghost" href="#mapa">Vybrat halu na mapě<span aria-hidden="true">↓</span></a>'),
    'biq.html': ('Sýpka BIQ', 'biq-square', 2000, 1125,
                 '<a class="button secondary yz-ghost" href="#podlazi">Tři podlaží<span aria-hidden="true">↓</span></a>'),
    'development.html': ('Development', 'so04', 2000, 1000,
                         '<a class="button secondary yz-ghost" href="#partnerstvi">Hledáme partnera<span aria-hidden="true">↓</span></a>'),
    'services.html': ('Services', 'square-services', 1920, 1091,
                      '<a class="button secondary yz-ghost" href="#servisni-poplatek">Servisní poplatek<span aria-hidden="true">↓</span></a>'),
    'aktuality.html': ('Aktuality', 'open', 1707, 1280, None),
    'kontakt.html': ('Kontakt', 'winter', 2000, 1125,
                     '<a class="button secondary yz-ghost" href="tel:+420725111277">Zavolat: +420 725 111 277<span aria-hidden="true">↗</span></a>'),
}


def sub_hero(page, label, img, w, h, second, eyebrow, h1, lead):
    first = ('<a class="button yz-light" href="#poptavka">Napsat zprávu<span aria-hidden="true">↓</span></a>'
             if page == 'kontakt.html' else
             '<a class="button yz-light" href="obcane.html">Co to přinese Kosticím<span aria-hidden="true">↗</span></a>'
             if page == 'aktuality.html' else CTA)
    buttons = first + ('\n' + second if second else '')
    kicker = f'<span>{label}</span>' + (f'<span>{eyebrow}</span>' if eyebrow else '<span>Smartzóna YEZEDO Kostice</span>')
    return f'''<!--SUBHERO-->
<section class="sub-hero" id="top">
<img class="sub-hero-photo" src="assets/images/{img}.webp" srcset="assets/images/{img}-small.webp 800w, assets/images/{img}.webp {w}w" sizes="100vw" alt="" width="{w}" height="{h}" fetchpriority="high">
<div class="sub-hero-inner">
<p class="inv-kicker">{kicker}</p>
<h1>{h1}</h1>
<p class="inv-lead">{lead}</p>
<div class="inv-hero-actions">
{buttons}
</div>
</div>
</section>
<!--/SUBHERO-->'''


for page, (label, img, w, h, second) in PAGES.items():
    p = WEB / page
    t = p.read_text(encoding='utf-8')
    if '<!--SUBHERO-->' in t:
        old = re.search(r'<!--SUBHERO-->.*?<!--/SUBHERO-->', t, re.S).group(0)
        eyebrow = re.search(r'<p class="inv-kicker"><span>[^<]*</span><span>(.*?)</span></p>', old).group(1)
        eyebrow = '' if eyebrow == 'Smartzóna YEZEDO Kostice' else eyebrow
        h1 = re.search(r'<h1>(.*?)</h1>', old, re.S).group(1)
        lead = re.search(r'<p class="inv-lead">(.*?)</p>', old, re.S).group(1)
    else:
        old = re.search(r'<section class="page-heading[^"]*" id="top">.*?</section>', t, re.S).group(0)
        em = re.search(r'<p class="eyebrow">(.*?)</p>', old)
        eyebrow = em.group(1) if em else ''
        h1 = re.search(r'<h1>(.*?)</h1>', old, re.S).group(1)
        lead = re.search(r'<p class="lead">(.*?)</p>', old, re.S).group(1)
    t = t.replace(old, sub_hero(page, label, img, w, h, second, eyebrow, h1, lead))
    # úvodní fotku načíst hned
    t = re.sub(r'<link rel="preload" as="image"[^>]*>\n?', '', t)
    t = t.replace('<link rel="stylesheet"', f'<link rel="preload" as="image" href="assets/images/{img}.webp" imagesrcset="assets/images/{img}-small.webp 800w, assets/images/{img}.webp {w}w" imagesizes="100vw">\n<link rel="stylesheet"', 1)
    t = re.sub(r'href="nabidka-hal\.html#(SO0\d)"', lambda m: f'href="hala-{m.group(1).lower()}.html"', t)
    if page == 'nabidka-hal.html':
        # odkaz na stránku haly v každé kartě
        def add_detail(m):
            code = m.group(1)
            block = m.group(0)
            if 'class="button secondary hall-detail"' in block:
                return block
            return block.replace('<div class="actions">',
                                 f'<div class="actions">\n<a class="button secondary hall-detail" href="hala-{code.lower()}.html">Detail haly<span aria-hidden="true">↗</span></a>', 1)
        t = re.sub(r'<article class="hall-card" id="(SO0\d)">.*?</article>', add_detail, t, flags=re.S)
        if '<!--HMAP2-->' not in t:
            t = t.replace('<!--/SUBHERO-->', '<!--/SUBHERO-->\n<!--HMAP2--><!--/HMAP2-->', 1)
    p.write_text(t, encoding='utf-8')
    print('ok', page)
