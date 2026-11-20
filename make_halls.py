"""Stránky jednotlivých hal (web/hala-so0X.html) a klikací mapa areálu na hlavní stránce.

    python3 make_halls.py      (pak python3 build_web.py)

Data hal: web (nabídka ateliéru) + studie RIVESTA Consult, průvodní list A, 07/2026 (konstrukce, obestavěný
prostor, odhad nákladů). Polohy hal na situaci plan.webp (1662 × 852 px) určené podle výkresu
C2-katastralni-situace (je otočený o 180° proti plan.webp), 19. 11. 2026.
"""
import pathlib, re

WEB = pathlib.Path('web')

HALLS = [
    dict(code='SO03', kind='Výrobní hala', dims='54 × 24 m', area='1 296 m²', sections='5',
         desc='Pět sekcí o šířce 9–12 m s vlastními vjezdy z obou stran haly.',
         construction='Ocelová konstrukce', volume='8 775 m³', cost='27,7 mil. Kč',
         img='so03', drawing=False, rect=(243, 320, 171, 86)),
    dict(code='SO04', kind='Výrobní hala', dims='66 × 24 m', area='1 584 m²', sections='5',
         desc='Pět sekcí o šířce 12–15 m, největší z řady hal šířky 24 m.',
         construction='Ocelová konstrukce', volume='10 607 m³', cost='33,5 mil. Kč',
         img='so04', drawing=False, rect=(473, 322, 212, 82)),
    dict(code='SO05', kind='Výrobní hala', dims='36 × 18 m', area='648 m²', sections='3',
         desc='Kompaktní hala se třemi sekcemi po 12 m pro menší provozy a služby.',
         construction='Ocelová konstrukce', volume='4 388 m³', cost='13,7 mil. Kč',
         img='so05', drawing=False, rect=(622, 423, 64, 131)),
    dict(code='SO06', kind='Výrobní hala', dims='68 × 66 m', area='4 488 m²', sections='podle záměru',
         desc='Největší hala v areálu. Prostor pro rozsáhlejší výrobní záměry.',
         construction='Železobetonový skelet (zadní část), ocelová konstrukce (přední část)',
         volume='42 545 m³', cost='97,4 mil. Kč', img='so06', drawing=False, rect=(716, 390, 226, 232)),
    dict(code='SO07', kind='Hala + technické zázemí', dims='66 × 18 m', area='1 188 m²', sections='2',
         desc='Dvě sekce po 33 m s technickým zázemím areálu.',
         construction='Ocelová konstrukce', volume='8 309 m³', cost='26,1 mil. Kč',
         img='so07-drawing', drawing=True, rect=(263, 200, 197, 63)),
    dict(code='SO09', kind='Výrobní hala', dims='54 × 18 m', area='972 m²', sections='5',
         desc='Pět sekcí o šířce 9–12 m v užší hale hloubky 18 m.',
         construction='Ocelová konstrukce', volume='6 563 m³', cost='20,6 mil. Kč',
         img='so09-drawing', drawing=True, rect=(258, 570, 178, 66)),
]
for h in HALLS:
    h['page'] = f'hala-{h["code"].lower()}.html'


def plan_map(active=None, new_tab=False):
    """Situace s klikacími halami. active = kód zvýrazněné haly (stránka haly)."""
    target = ' target="_blank" rel="noopener"' if new_tab else ''
    shapes = []
    for h in HALLS:
        x, y, w, hh = h['rect']
        cls = 'hmap-hall' + (' is-active' if h['code'] == active else '')
        cur = ' aria-current="page"' if h['code'] == active else ''
        tip = f'Hala {h["code"]}, {h["area"]}' + (', otevře se v nové záložce' if new_tab else '')
        # štítek do levého horního rohu, ať nepřekrývá čísla zón 1–6 na situaci
        lx, ly = (x + 50, y + 26) if w >= 120 else (x + w / 2, y + 26)
        shapes.append(f'''<a href="{h['page']}"{target} class="{cls}" data-hall="{h['code']}" aria-label="{tip}"{cur}>
<rect x="{x}" y="{y}" width="{w}" height="{hh}" rx="3"/>
<g class="hmap-tag" transform="translate({lx:.0f} {ly:.0f})"><rect x="-44" y="-20" width="88" height="40" rx="2"/><text y="8">{h['code']}</text></g>
</a>''')
    return f'''<div class="hmap{' hmap-small' if active else ''}">
<img src="assets/images/plan.webp" srcset="assets/images/plan-small.webp 800w, assets/images/plan.webp 1662w" sizes="(max-width: 1240px) 100vw, 1240px" alt="Návrhová situace smartzóny Yezedo" width="1662" height="852" loading="lazy" decoding="async">
<svg viewBox="0 0 1662 852" role="group" aria-label="Haly na situaci areálu">
{chr(10).join(shapes)}
</svg>
</div>'''


def shell():
    src = pathlib.Path('templates/index-a.html').read_text(encoding='utf-8')
    head = src[:src.index('<main id="obsah"')]
    foot = src[src.index('</main>') + len('</main>'):]
    head = head.replace('<a href="#napiste-nam" class="nav-cta">', '<a href="index.html#napiste-nam" class="nav-cta">')
    head = re.sub(r'<link rel="preload" as="image"[^>]*>\n?', '', head)
    head = head.replace('<body data-page="index.html">', '<body data-page="hala.html">')
    foot = foot.replace('<a href="index.html" aria-current="page">', '<a href="index.html">')
    return head, foot


def meta(html, title, desc, url, image):
    html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html)
    for prop, val in (('og:title', title), ('og:description', desc), ('og:url', url), ('og:image', image)):
        html = re.sub(rf'(<meta property="{prop}" content=")[^"]*', lambda m: m.group(1) + val, html)
    html = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, html)
    html = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, html)
    return html


def hall_page(i, h, head, foot):
    prev_h, next_h = HALLS[i - 1], HALLS[(i + 1) % len(HALLS)]
    code = h['code']
    if h['drawing']:
        media = f'<img src="assets/images/{h["img"]}.webp" alt="Výkres haly {code}" width="1400" height="989" fetchpriority="high" class="hall-drawing">'
    else:
        media = (f'<img src="assets/images/{h["img"]}.webp" srcset="assets/images/{h["img"]}-small.webp 800w, '
                 f'assets/images/{h["img"]}.webp 2000w" sizes="100vw" alt="Vizualizace haly {code}" width="2000" height="1000" fetchpriority="high">')
    main = f'''<main id="obsah" tabindex="-1" class="hall-page">
<section class="hall-hero">
<div class="container">
<p class="hall-crumbs"><a href="index.html#nabidka">Haly</a> <span aria-hidden="true">/</span> {code}</p>
<p class="inv-kicker"><span>Připravovaná hala</span><span>{h['kind']}</span></p>
<h1>HALA {code}</h1>
<dl class="hall-key">
<div><dt>Rozměry</dt><dd>{h['dims']}</dd></div>
<div><dt>Zastavěná plocha</dt><dd>{h['area']}</dd></div>
<div><dt>Sekce</dt><dd>{h['sections']}</dd></div>
<div><dt>Odhad nákladů stavby</dt><dd>{h['cost']}</dd></div>
</dl>
</div>
</section>
<figure class="hall-visual{' is-drawing' if h['drawing'] else ''}">
{media}
</figure>
<section class="inv-chapter">
<div class="container hall-cols">
<div>
<h2>{h['desc']}</h2>
<p class="lead">Modulární hala v měřítku původního zemědělského družstva. Vnitřní prostor lze libovolně dělit, součástí může být kancelářské patro, administrativní vestavby i showroom. Reprezentativní fasáda a vstup směřují do sdíleného veřejného prostoru.</p>
<ul class="hall-feats">
<li><b>Dispozice na míru</b>Konstrukční systém i vnitřní dispozici lze přizpůsobit charakteru provozu.</li>
<li><b>Kanceláře ve 2. NP</b>Součástí řešení může být druhé podlaží pro kanceláře a zázemí.</li>
<li><b>Hotová infrastruktura</b>Komunikace, vodovod, kanalizace, osvětlení a rozvody NN jsou zkolaudované (2026).</li>
<li><b>Společná správa</b>Zeleň, komunikace a parkoviště spravuje YEZEDO Services za měsíční servisní poplatek.</li>
</ul>
</div>
<aside class="hall-params">
<h3>Parametry</h3>
<dl>
<div><dt>Typ</dt><dd>{h['kind']}</dd></div>
<div><dt>Konstrukce</dt><dd>{h['construction']}</dd></div>
<div><dt>Rozměry</dt><dd>{h['dims']}</dd></div>
<div><dt>Zastavěná plocha</dt><dd>{h['area']}, orientačně, nikoli užitná</dd></div>
<div><dt>Sekce</dt><dd>{h['sections']}</dd></div>
<div><dt>Obestavěný prostor</dt><dd>{h['volume']}</dd></div>
<div><dt>Odhad nákladů stavby</dt><dd>{h['cost']} bez DPH</dd></div>
<div><dt>Stav</dt><dd>Studie 07/2026, stavební povolení předpoklad 2027</dd></div>
</dl>
<p class="fine">Obestavěný prostor a odhad nákladů podle studie RIVESTA Consult (07/2026, cenové ukazatele 2026, bez spodní stavby). Konkrétní podmínky ověříme při jednání.</p>
<div class="hall-docs">
<a href="assets/docs/{code}-pudorys.pdf" target="_blank" rel="noopener"><span>PDF</span>Půdorys haly {code}</a>
<a href="assets/docs/{code}-pohledy.pdf" target="_blank" rel="noopener"><span>PDF</span>Pohledy haly {code}</a>
</div>
</aside>
</div>
</section>
<section class="inv-chapter inv-sage hall-where">
<div class="container">
<p class="inv-num">Poloha v areálu</p>
<h2>KDE HALA {code} STOJÍ.</h2>
{plan_map(active=code)}
<p class="fine">Klikněte na jinou halu pro její detail. Návrhová situace: Zásady rozvoje Smartzóny YEZEDO Kostice, 07/2026.</p>
</div>
</section>
<section class="inv-chapter inv-dark hall-cta">
<div class="container inv-split">
<div>
<h2>MÁTE ZÁJEM<br>O HALU {code}?</h2>
<p class="lead">Napište nám, jaký provoz plánujete. Projdeme s vámi dispozici, technické návaznosti i obchodní model.</p>
</div>
<div class="hall-cta-actions">
<a class="button yz-light" href="index.html?hala={code}#napiste-nam">Mám zájem o {code}<span aria-hidden="true">↗</span></a>
<p><b>Libor Balga</b>, starosta obce Kostice<br><a href="tel:+420725111277">+420 725 111 277</a> · <a href="mailto:starosta@kostice.cz?subject=Z%C3%A1jem%20o%20halu%20{code}">starosta@kostice.cz</a></p>
</div>
</div>
</section>
<nav class="hall-pager container" aria-label="Další haly">
<a href="{prev_h['page']}"><span>← Předchozí hala</span><b>{prev_h['code']}</b><small>{prev_h['area']}</small></a>
<a href="index.html#nabidka" class="hall-pager-all">Přehled všech hal</a>
<a href="{next_h['page']}"><span>Další hala →</span><b>{next_h['code']}</b><small>{next_h['area']}</small></a>
</nav>
</main>'''
    img = f'https://www.yezedokostice.cz/assets/images/{h["img"]}.webp'
    page = meta(head, f'Hala {code} — {h["dims"]}, {h["area"]} — YEZEDO Kostice',
                f'Hala {code} ve smartzóně YEZEDO Kostice u D2: {h["dims"]}, {h["area"]}, {h["sections"]} sekcí. {h["desc"]}',
                f'https://www.yezedokostice.cz/{h["page"]}', img)
    (WEB / h['page']).write_text(page + main + foot, encoding='utf-8')


def patch_index():
    block = f'''<!--HMAP-->
<div class="inv-plan inv-reveal">
{plan_map(new_tab=True)}
<p class="hmap-hint"><span aria-hidden="true">↗</span> Klikněte na halu, otevře se její detail v nové záložce.</p>
<p class="fine">Návrhová situace: Zásady rozvoje Smartzóny YEZEDO Kostice, 07/2026.</p>
</div>
<!--/HMAP-->'''
    # mapa v šabloně (z ní make_variant_b.py skládá hlavní stránku) i v hlavní stránce
    for p in (pathlib.Path('templates/index-a.html'), WEB / 'index.html'):
        if not p.exists():
            continue
        t = p.read_text(encoding='utf-8')
        if '<!--HMAP-->' not in t:
            continue
        t = re.sub(r'<!--HMAP-->.*?<!--/HMAP-->', lambda m: block, t, flags=re.S)
        t = re.sub(r'href="nabidka-hal\.html#(SO0\d)"', lambda m: f'href="hala-{m.group(1).lower()}.html"', t)
        p.write_text(t, encoding='utf-8')


def patch_nabidka():
    p = WEB / 'nabidka-hal.html'
    t = p.read_text(encoding='utf-8')
    if '<!--HMAP2-->' not in t:
        return
    block = f'''<!--HMAP2-->
<section class="inv-chapter inv-sage hall-where" id="mapa">
<div class="container">
<p class="inv-num">Haly na mapě</p>
<h2>VYBERTE SI HALU.</h2>
<p class="lead inv-narrow">Šest hal o celkové zastavěné ploše 10 176 m², od 648 do 4 488 m². Klikněte na halu a otevře se její detail s parametry, výkresy a polohou v areálu.</p>
{plan_map()}
<p class="fine">Návrhová situace: Zásady rozvoje Smartzóny YEZEDO Kostice, 07/2026.</p>
</div>
</section>
<!--/HMAP2-->'''
    t = re.sub(r'<!--HMAP2-->.*?<!--/HMAP2-->', lambda m: block, t, flags=re.S)
    p.write_text(t, encoding='utf-8')


patch_index()
patch_nabidka()
head, foot = shell()
for i, h in enumerate(HALLS):
    hall_page(i, h, head, foot)
print('hotovo:', ', '.join(h['page'] for h in HALLS))
