"""Varianta B hlavní stránky (web/varianta-b.html): nejdřív dohoda pro investora, pak areál.

Skládá se z web/index.html (hlavička, patička, poloha, haly, mapa, lidé, kontakt), takže zůstává v souladu.
Pořadí:  python3 polish_pages.py -> python3 make_halls.py -> python3 make_variant_b.py -> python3 build_web.py
Co neznáme, je označené „Doplní obec“ (nic si nevymýšlíme).
"""
import pathlib, re

WEB = pathlib.Path('web')
src = (WEB / 'index.html').read_text(encoding='utf-8')


def cut(pattern):
    m = re.search(pattern, src, re.S)
    assert m, pattern
    return m.group(0)


def todo(text):
    return f'<p class="vb-todo"><span>Doplní obec</span>{text}</p>'


head = cut(r'^.*?<main id="obsah" tabindex="-1" class="inv">')
foot = cut(r'</main>.*$')
poloha = cut(r'<section class="inv-chapter inv-dark" id="poloha">.*?</section>')
hmap = cut(r'<!--HMAP-->.*?<!--/HMAP-->')
halls = cut(r'<div class="inv-total inv-reveal">.*?<div class="yz-actions">.*?</div>')
people = cut(r'<div class="inv-people">.*?</div>\n</div>')
video = cut(r'<div class="inv-video inv-video-people inv-reveal">.*?</div>\n</div>')
contact = cut(r'<section class="inv-chapter inv-dark inv-contact" id="napiste-nam">.*?</section>')

# hlavička stránky
head = re.sub(r'<title>.*?</title>', '<title>YEZEDO Kostice — postavte s obcí zónu u D2 (varianta B)</title>', head)
head = head.replace('square-night', 'hero').replace('imagesrcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w"',
                                                   'imagesrcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w"')
head = head.replace('data-page="index.html"', 'data-page="varianta-b.html"')
head = head.replace('href="#napiste-nam" class="nav-cta"', 'href="#napiste-nam" class="nav-cta"')

poloha = poloha.replace('<b>02</b> Poloha', '<b>04</b> Poloha')

main = f'''
<p class="vb-switch" aria-label="Porovnání variant"><a href="index.html">Varianta A</a><a href="varianta-b.html" aria-current="page">Varianta B</a></p>

<!-- ÚVOD -->
<section class="inv-hero vb-hero" id="top">
<div class="inv-hero-media">
<img src="assets/images/hero.webp" srcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w" sizes="100vw" alt="Letecká vizualizace smartzóny Yezedo: haly se zelenými střechami, park s vodou a obec Kostice" width="2000" height="1328" fetchpriority="high">
</div>
<div class="inv-hero-inner">
<p class="inv-kicker"><span>Investiční příležitost · Kostice u D2</span></p>
<h1>POSTAVTE S OBCÍ<br><em>ZÓNU U D2.</em></h1>
<p class="inv-lead">Obec Kostice jako developer připravila území, sítě i studii šesti hal. Hledáme strategického investora, se kterým projekt společně doladíme a postavíme.</p>
<div class="inv-hero-actions">
<a class="button yz-light" href="#dohoda">Co nabízíme<span aria-hidden="true">↓</span></a>
<a class="button secondary yz-ghost" href="#napiste-nam">Domluvit jednání<span aria-hidden="true">↗</span></a>
</div>
</div>
<dl class="inv-hero-facts">
<div><dt>Plocha 6 hal</dt><dd>10 176 m²</dd></div>
<div><dt>Odhad investice do hal</dt><dd>≈ 219 mil. Kč</dd></div>
<div><dt>Sítě a komunikace</dt><dd>Hotovo</dd></div>
<div><dt>Stavební povolení</dt><dd>konec 2027</dd></div>
</dl>
</section>

<nav class="inv-chapters" aria-label="Kapitoly">
<a href="#dohoda"><b>01</b><span>Nabídka</span></a>
<a href="#cisla"><b>02</b><span>Investice a čas</span></a>
<a href="#na-miru"><b>03</b><span>Podoba projektu</span></a>
<a href="#poloha"><b>04</b><span>Poloha</span></a>
<a href="#jistota"><b>05</b><span>Jistota a postup</span></a>
<a href="#napiste-nam"><b>06</b><span>Kontakt</span></a>
</nav>

<!-- 01 NABÍDKA -->
<section class="inv-chapter" id="dohoda">
<div class="container">
<p class="inv-num"><b>01</b> Nabídka pro investora</p>
<h2 class="inv-reveal">CO VKLÁDÁ OBEC.<br>CO ZÍSKÁ INVESTOR.</h2>
<p class="lead inv-narrow inv-reveal">Obec udělala práci, která u podobných projektů trvá nejdéle. Hledá investora, který s ní areál postaví. Konkrétní podobu spolupráce dohodneme na jednání.</p>
<div class="vb-deal">
<article class="inv-reveal"><h3>Obec vkládá</h3><ul>
<li>Pozemky, většinou ve vlastnictví obce</li>
<li>Územní plán pro lehkou výrobu</li>
<li>Zkolaudované komunikace a sítě</li>
<li>Architektonickou studii a konstrukční řešení šesti hal</li>
<li>Koncepci společné správy areálu (YEZEDO Services)</li>
</ul></article>
<article class="inv-reveal"><h3>Investor přináší</h3><ul>
<li>Kapitál na výstavbu</li>
<li>Zkušenosti s výstavbou a provozem hal</li>
<li>Dlouhodobý zájem o rozvoj areálu</li>
</ul></article>
<article class="vb-gain inv-reveal"><h3>Investor získá</h3>
{todo('Forma: vlastnictví hal, právo stavby na pozemcích obce, nebo podíl ve společné firmě. Z čeho plyne výnos: nájem, prodej hal firmám, podíl na výnosu.')}
</article>
</div>
{todo('Kdo bude haly pronajímat a kdo bude provozovat YEZEDO Services.')}
</div>
</section>

<!-- 02 INVESTICE A ČAS -->
<section class="inv-chapter inv-dark" id="cisla">
<div class="container">
<p class="inv-num"><b>02</b> Investice a čas</p>
<h2 class="inv-reveal">KOLIK TO STOJÍ<br>A KDY SE STAVÍ.</h2>
<div class="inv-ready">
<ol class="inv-checklist">
<li class="done inv-reveal"><span class="inv-state">Hotovo 2026</span><h3>Sítě a komunikace</h3><p>Komunikace, kanalizace, vodovod, osvětlení a rozvody NN zkolaudovány, s podporou programu MPO Smart Parks for the Future.</p></li>
<li class="done inv-reveal"><span class="inv-state">Hotovo 07/2026</span><h3>Studie a konstrukce hal</h3><p>Atelier Dohnalovi, konstrukční řešení RIVESTA Consult.</p></li>
<li class="next inv-reveal"><span class="inv-state">Konec 2027</span><h3>Stavební povolení</h3><p>Předpokládané vydání pro sýpku a prvních šest hal.</p></li>
<li class="next inv-reveal"><span class="inv-state">2028</span><h3>Zahájení výstavby</h3><p>První etapa: sýpka a haly SO03–SO09.</p></li>
<li class="done inv-reveal"><span class="inv-state">Už teď</span><h3>První zájemci o haly</h3><p>Obec už má první firmy, které projevily zájem o prostory v halách.</p>{todo('Kdy mohou být haly v provozu.')}</li>
</ol>
<aside class="inv-cost inv-reveal">
<p class="inv-cost-label">Odhad nákladů šesti hal</p>
<p class="inv-cost-value">≈ 219<small> mil. Kč</small></p>
<p>bez DPH, podle studie RIVESTA Consult a cenových ukazatelů pro rok 2026</p>
{todo('Kolik stojí sýpka BIQ a park a kdo je platí.')}
<a class="text-link" href="assets/docs/A-pruvodni-list.pdf" target="_blank" rel="noopener">Průvodní list studie (PDF) ↗</a>
</aside>
</div>
</div>
</section>

<!-- 03 PODOBA PROJEKTU -->
<section class="inv-chapter inv-sage" id="na-miru">
<div class="container">
<p class="inv-num"><b>03</b> Podoba projektu</p>
<h2 class="inv-reveal">ŠEST HAL.<br>JEŠTĚ SE NESTAVÍ.</h2>
<p class="lead inv-narrow inv-reveal">Haly jsou modulární, v měřítku původního družstva. Vnitřní prostor lze dělit na sekce, součástí může být kancelářské patro i showroom. Konstrukční systém i dispozici lze přizpůsobit charakteru provozu.</p>
<p class="vb-callout inv-reveal"><b>Projekt doladíme společně.</b> Obec má hotovou studii, ale investora bere jako partnera. O konečné podobě projektu, například velikosti hal, etapách nebo využití, se s ním chce domluvit.</p>
{hmap}
{halls}
</div>
</section>

<!-- 04 POLOHA -->
{poloha}

<!-- 05 JISTOTA A POSTUP -->
<section class="inv-chapter" id="jistota">
<div class="container">
<p class="inv-num"><b>05</b> Jistota a postup</p>
<h2 class="inv-reveal">PROJEKT VEDE OBEC.<br>NA DLOUHO.</h2>
<div class="inv-split inv-split-top">
<div>
<p class="lead inv-reveal">Obec pod vedením starosty Mgr. Libora Balgy vzala budoucnost bývalého zemědělského areálu do vlastních rukou. Architektonickou koncepci garantuje Atelier Dohnalovi.</p>
<ul class="vb-trust">
<li class="inv-reveal"><h3>Rozhodnutí zastupitelstva</h3>{todo('Usnesení, kterým zastupitelstvo projekt a hledání investora schválilo.')}</li>
<li class="inv-reveal"><h3>Podmínky dotace</h3>{todo('Udržitelnost a omezení z dotace MPO na infrastrukturu.')}</li>
<li class="inv-reveal"><h3>Výběr investora</h3>{todo('Kdo rozhoduje, jak výběr proběhne a do kdy.')}</li>
</ul>
<ol class="inv-steps">
<li class="inv-reveal"><b>01</b><div><h3>Představte se</h3><p>Kdo jste, jaké projekty máte za sebou a co vás na Yezedu zaujalo.</p></div></li>
<li class="inv-reveal"><b>02</b><div><h3>Projděme areál a podklady</h3><p>Prohlídka na místě, studie, dokumentace a stav infrastruktury.</p></div></li>
<li class="inv-reveal"><b>03</b><div><h3>Domluvme spolupráci</h3><p>Podoba investice, role obce a investora, další postup.</p></div></li>
</ol>
</div>
{people}
{video}
</section>

<!-- 06 KONTAKT -->
{contact.replace('<b>08</b> Kontakt', '<b>06</b> Kontakt')}

<a class="inv-sticky" href="#napiste-nam">Máte zájem? Napište nám <span aria-hidden="true">↗</span></a>
'''

(WEB / 'varianta-b.html').write_text(head + main + foot, encoding='utf-8')

# přepínač variant i na variantě A
idx = src
if 'class="vb-switch"' not in idx:
    idx = idx.replace('<!-- ÚVOD -->', '<p class="vb-switch" aria-label="Porovnání variant"><a href="index.html" aria-current="page">Varianta A</a><a href="varianta-b.html">Varianta B</a></p>\n\n<!-- ÚVOD -->', 1)
    (WEB / 'index.html').write_text(idx, encoding='utf-8')
print('ok varianta-b.html')
