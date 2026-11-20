"""Varianta B hlavní stránky (web/varianta-b.html): nejdřív dohoda pro investora, pak areál.

Skládá se z web/index.html (hlavička, patička, poloha, haly, mapa, lidé, kontakt), takže zůstává v souladu.
Pořadí:  python3 polish_pages.py -> python3 make_halls.py -> python3 make_variant_b.py -> python3 build_web.py
Co neznáme, je označené „Doplní obec“ (nic si nevymýšlíme).
"""
import pathlib, re

WEB = pathlib.Path('web')
src = pathlib.Path('templates/index-a.html').read_text(encoding='utf-8')


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
head = re.sub(r'<title>.*?</title>', '<title>YEZEDO Kostice — postavte s obcí soběstačnou zónu u D2</title>', head)
DESC = 'Obec Kostice hledá strategického investora pro soběstačnou a ekologickou zónu u dálnice D2: 6 hal o 10 176 m², hotové sítě a studie, první zájemci o haly.'
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="YEZEDO Kostice — postavte s obcí soběstačnou zónu u D2">', head)
head = head.replace('square-night', 'hero').replace('imagesrcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w"',
                                                   'imagesrcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w"')
head = head.replace('href="#napiste-nam" class="nav-cta"', 'href="#napiste-nam" class="nav-cta"')

poloha = poloha.replace('<b>02</b> Poloha', '<b>05</b> Poloha')
project_video = cut(r'<div class="inv-video inv-reveal">\n<div class="video" data-video="sWQShSMKCxE">.*?</p>\n</div>')
checklist = cut(r'<ol class="inv-checklist">.*?</ol>')
_zaj = '<li class="done inv-reveal"><span class="inv-state">Už teď</span><h3>První zájemci o haly</h3><p>Firmy, které chtějí v halách sídlit, se obci ozývají už teď. Investor nezačíná s prázdnými halami.</p>' + todo('Kdy mohou být haly v provozu.') + '</li>'
checklist = checklist.replace('<li class="next inv-reveal"><span class="inv-state">Konec 2027</span>', _zaj + '\n<li class="next inv-reveal"><span class="inv-state">Konec 2027</span>', 1)
biq_card = cut(r'<article class="inv-reveal">\n<img src="assets/images/biq-square-small.webp".*?</article>')
service = cut(r'<div class="inv-service inv-reveal">.*?</div>')
hodnota = f'''<section class="inv-chapter" id="hodnota">
<div class="container">
<p class="inv-num"><b>04</b> Přidaná hodnota</p>
<h2 class="inv-reveal">SOBĚSTAČNÝ AREÁL.<br>NE DALŠÍ HALA NA POLI.</h2>
<p class="lead inv-narrow inv-reveal">Yezedo je navržené jako areál, který si většinu toho, co potřebuje, zajistí sám: energii z místních zdrojů, vodu z vlastních srážek a materiál z původních staveb. Místo nového záboru pole vrací život bývalému družstvu.</p>
{project_video}
<div class="vb-eco">
<article class="inv-reveal"><span class="inv-state">Připravuje se</span><h3>Energie z místních zdrojů</h3><p>Napojení na komunitní energetickou síť KES Kostice. Prověřuje se fotovoltaika, akumulace, kogenerace i využití odpadního tepla.</p></article>
<article class="inv-reveal"><span class="inv-state">Cíl návrhu</span><h3>Voda zůstává v areálu</h3><p>Veškerá dešťová voda se má využít přímo v areálu, bez odtoku mimo území. Park s vodou a zeleň ochlazují okolí hal.</p></article>
<article class="inv-reveal"><span class="inv-state">Cíl návrhu</span><h3>Materiály se vracejí do oběhu</h3><p>Cihly, trámy a technické prvky původního JZD se znovu použijí. Areál vzniká na brownfieldu, ne na poli.</p></article>
<article class="inv-reveal"><span class="inv-state">Cíl návrhu</span><h3>Chytrá správa</h3><p>IoT monitoring má ověřovat úspory v reálném provozu. Digitální velín obce bude v sýpce BIQ.</p></article>
</div>
<div class="vb-investor-eco inv-reveal">
<h3>Co to znamená pro investora</h3>
<ul>
<li><b>Stabilnější náklady na energie.</b> Část energie z místních zdrojů místo plné závislosti na cenách z trhu.</li>
<li><b>Haly, které firmy chtějí.</b> Nájemci stále častěji vyžadují udržitelné budovy a vykazují svou uhlíkovou stopu (ESG).</li>
<li><b>Projekt s příběhem.</b> Obnova brownfieldu s podporou programu MPO Smart Parks for the Future.</li>
</ul>
</div>
<div class="inv-values vb-values">
{biq_card}
</div>
{service}
</div>
</section>'''

main = f'''
<!-- ÚVOD -->
<section class="inv-hero vb-hero" id="top">
<div class="inv-hero-media">
<img src="assets/images/hero.webp" srcset="assets/images/hero-small.webp 800w, assets/images/hero.webp 2000w" sizes="100vw" alt="Letecká vizualizace smartzóny Yezedo: haly se zelenými střechami, park s vodou a obec Kostice" width="2000" height="1328" fetchpriority="high">
</div>
<div class="inv-hero-inner">
<p class="inv-kicker"><span>Investiční příležitost · Kostice u D2</span></p>
<h1>POSTAVTE S OBCÍ<br><em>ZÓNU U D2.</em></h1>
<p class="inv-lead">Obec Kostice jako developer připravuje soběstačnou a ekologickou zónu u dálnice D2. Území, sítě i studie šesti hal jsou hotové. Hledáme strategického investora, se kterým projekt společně doladíme a postavíme.</p>
<div class="inv-hero-actions">
<a class="button yz-light" href="#dohoda">Co nabízíme<span aria-hidden="true">↓</span></a>
<a class="button secondary yz-ghost" href="#napiste-nam">Domluvit jednání<span aria-hidden="true">↗</span></a>
</div>
</div>
<dl class="inv-hero-facts">
<div><dt>Plocha 6 hal</dt><dd>10 176 m²</dd></div>
<div><dt>Brno · Bratislava · Vídeň</dt><dd>30/45/60 min</dd></div>
<div><dt>Sítě a komunikace</dt><dd>Hotovo</dd></div>
<div><dt>Zájemci o haly</dt><dd>Už teď</dd></div>
</dl>
</section>

<nav class="inv-chapters" aria-label="Kapitoly">
<a href="#dohoda"><b>01</b><span>Nabídka</span></a>
<a href="#cisla"><b>02</b><span>Investice a čas</span></a>
<a href="#nabidka"><b>03</b><span>Podoba projektu</span></a>
<a href="#hodnota"><b>04</b><span>Přidaná hodnota</span></a>
<a href="#poloha"><b>05</b><span>Poloha</span></a>
<a href="#jistota"><b>06</b><span>Jistota a postup</span></a>
<a href="#napiste-nam"><b>07</b><span>Kontakt</span></a>
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
<div class="vb-demand inv-reveal">
<p class="vb-demand-label">Poptávka už je</p>
<h3>Haly nebudou stát prázdné.</h3>
<p>Ještě se nestaví, a obec už má první firmy, které chtějí v halách sídlit. Investor tak od začátku ví, že prostory mají odbyt. Podrobnosti o zájemcích probereme na prvním jednání.</p>
</div>
</div>
</section>

<!-- 02 INVESTICE A ČAS -->
<section class="inv-chapter inv-dark" id="cisla">
<div class="container">
<p class="inv-num"><b>02</b> Investice a čas</p>
<h2 class="inv-reveal">KOLIK TO STOJÍ<br>A KDY SE STAVÍ.</h2>
<div class="inv-ready">
{checklist}
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
<section class="inv-chapter inv-sage" id="nabidka">
<div class="container">
<p class="inv-num"><b>03</b> Podoba projektu</p>
<h2 class="inv-reveal">ŠEST HAL.<br>JEŠTĚ SE NESTAVÍ.</h2>
<p class="lead inv-narrow inv-reveal">Haly jsou modulární, v měřítku původního družstva. Vnitřní prostor lze dělit na sekce, součástí může být kancelářské patro i showroom. Konstrukční systém i dispozici lze přizpůsobit charakteru provozu.</p>
<p class="vb-callout inv-reveal"><b>Projekt doladíme společně.</b> Obec má hotovou studii, ale investora bere jako partnera. O konečné podobě projektu, například velikosti hal, etapách nebo využití, se s ním chce domluvit.</p>
{hmap}
{halls}
</div>
</section>

<!-- 04 PŘIDANÁ HODNOTA -->
{hodnota}

<!-- 05 POLOHA -->
{poloha}

<!-- 06 JISTOTA A POSTUP -->
<section class="inv-chapter" id="jistota">
<div class="container">
<p class="inv-num"><b>06</b> Jistota a postup</p>
<h2 class="inv-reveal">PROJEKT VEDE OBEC.<br>NA DLOUHO.</h2>
<div class="inv-split inv-split-top">
<div>
<p class="lead inv-reveal">Obec pod vedením starosty Mgr. Libora Balgy vzala budoucnost bývalého zemědělského areálu do vlastních rukou. Architektonickou koncepci garantuje Atelier Dohnalovi.</p>
<ol class="inv-steps">
<li class="inv-reveal"><b>01</b><div><h3>Představte se</h3><p>Kdo jste, jaké projekty máte za sebou a co vás na Yezedu zaujalo.</p></div></li>
<li class="inv-reveal"><b>02</b><div><h3>Projděme areál a podklady</h3><p>Prohlídka na místě, studie, dokumentace a stav infrastruktury.</p></div></li>
<li class="inv-reveal"><b>03</b><div><h3>Domluvme spolupráci</h3><p>Podoba investice, role obce a investora, další postup.</p></div></li>
</ol>
</div>
{people}
{video}
</section>

<!-- 07 KONTAKT -->
{contact.replace('<b>08</b> Kontakt', '<b>07</b> Kontakt')}

<a class="inv-sticky" href="#napiste-nam">Máte zájem? Napište nám <span aria-hidden="true">↗</span></a>
'''

(WEB / 'index.html').write_text(head + main + foot, encoding='utf-8')
# stará adresa varianty B -> hlavní stránka
(WEB / 'varianta-b.html').write_text('<!doctype html>\n<html lang="cs"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html"><link rel="canonical" href="https://www.yezedokostice.cz/"><title>YEZEDO</title></head><body><p><a href="index.html">Pokračovat na web YEZEDO</a></p></body></html>\n', encoding='utf-8')
print('ok web/index.html')
