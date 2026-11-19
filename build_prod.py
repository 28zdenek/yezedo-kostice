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

# Zámek heslem (login.aspx + pravidlo ve web.config, heslo v .site-password, změna přes set_password.py).
# Zdeněk 19. 11. 2026: přihlášení zatím nechat. Zveřejnění = LOCKED = False, sestavit a nahrát.
LOCKED = True

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

sm = rd(OUT / 'sitemap.xml')
if 'obcane.html' not in sm:
    sm = sm.replace('</urlset>', '<url><loc>https://www.yezedokostice.cz/obcane.html</loc></url></urlset>')
    (OUT / 'sitemap.xml').write_text(sm, encoding='utf-8')

LOGIN_ASPX = '''<%@ Page Language="C#" EnableViewState="false" EnableSessionState="false" %>
<%@ Import Namespace="System.Configuration" %>
<%@ Import Namespace="System.Security.Cryptography" %>
<%@ Import Namespace="System.Text" %>
<script runat="server">
string chyba = "";
void Page_Load(object sender, EventArgs e) {
    Response.Cache.SetCacheability(HttpCacheability.NoCache);
    if (Request.HttpMethod != "POST") return;
    string salt = ConfigurationManager.AppSettings["LoginSalt"] ?? "";
    string hash = ConfigurationManager.AppSettings["LoginHash"] ?? "";
    string heslo = Request.Form["heslo"] ?? "";
    var kdf = new Rfc2898DeriveBytes(Encoding.UTF8.GetBytes(heslo), Encoding.UTF8.GetBytes(salt), 100000);
    string hex = BitConverter.ToString(kdf.GetBytes(32)).Replace("-", "").ToLowerInvariant();
    int diff = hex.Length ^ hash.Length;
    for (int i = 0; i < Math.Min(hex.Length, hash.Length); i++) diff |= hex[i] ^ hash[i];
    if (hash.Length == 64 && diff == 0) {
        var cookie = new HttpCookie("yezedo", ConfigurationManager.AppSettings["LoginToken"]);
        cookie.Expires = DateTime.Now.AddDays(30);
        cookie.HttpOnly = true;
        cookie.Secure = true;
        cookie.Path = "/";
        Response.Cookies.Add(cookie);
        // jen adresa na tomto webu, ne přesměrování jinam
        string zpet = Request.QueryString["ReturnUrl"] ?? "/";
        if (!zpet.StartsWith("/") || zpet.StartsWith("//") || zpet.StartsWith("/\\\\")) zpet = "/";
        Response.Redirect(zpet);
    }
    System.Threading.Thread.Sleep(1000);
    chyba = "Heslo nesouhlasí, zkuste to znovu.";
}
</script>
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Přihlášení | Yezedo Kostice</title>
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="/assets/images/mark.png">
<style>
@font-face{font-family:BarlowCondensed;src:url('/assets/fonts/BarlowCondensed-Bold.ttf') format('truetype');font-weight:700}
@font-face{font-family:Barlow;src:url('/assets/fonts/Barlow-Regular.ttf') format('truetype');font-weight:400}
@font-face{font-family:Barlow;src:url('/assets/fonts/Barlow-Bold.ttf') format('truetype');font-weight:700}
html,body{margin:0;min-height:100%;background:#222721;color:#f3f1ea;font:400 18px/1.6 Barlow,Arial,sans-serif}
main{min-height:100vh;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;padding:40px clamp(24px,6vw,100px);max-width:900px}
img{width:52px;height:auto;margin-bottom:48px}
h1{font:700 clamp(46px,6vw,86px)/1.01 BarlowCondensed,'Arial Narrow',sans-serif;margin:0 0 20px;text-transform:uppercase}
p{margin:0 0 28px;max-width:560px}
form{display:flex;flex-wrap:wrap;gap:12px;max-width:560px}
label{flex-basis:100%;font-size:13px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;color:#c6d3a9}
input{flex:1 1 240px;min-height:52px;box-sizing:border-box;padding:0 18px;border:1px solid #9ba58f;background:transparent;color:#fff;font:inherit}
input:focus{outline:3px solid #bd652f;outline-offset:3px}
button{min-height:52px;padding:0 28px;border:1px solid #c6d3a9;background:#c6d3a9;color:#222721;font:700 15px Barlow,Arial,sans-serif;cursor:pointer}
button:hover{background:#f3f1ea;border-color:#f3f1ea}
.login-err{color:#e6b4a0;margin-top:18px}
</style>
</head>
<body>
<main>
  <img src="/assets/images/mark.png" alt="Yezedo" width="158" height="180">
  <h1>Web je zatím neveřejný.</h1>
  <p>Pro zobrazení zadejte heslo, které jste dostali od provozovatele zóny.</p>
  <form method="post">
    <label for="heslo">Heslo</label>
    <input id="heslo" name="heslo" type="password" autocomplete="current-password" required autofocus>
    <button type="submit">Vstoupit</button>
  </form>
  <% if (chyba != "") { %><p class="login-err" role="alert"><%= chyba %></p><% } %>
</main>
</body>
</html>
'''

config = rd('atelier.web.config')
if LOCKED:
    import json
    auth = json.load(open('.site-password'))
    for key in ('salt', 'hash', 'token'):
        config = config.replace('@@LOGIN_%s@@' % key.upper(), auth[key])
    # s BOM, aby ASP.NET četl češtinu jako UTF-8
    (OUT / 'login.aspx').write_text(LOGIN_ASPX, encoding='utf-8-sig')
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
else:
    config = re.sub(r'\s*<appSettings>.*?</appSettings>', '', config, flags=re.S)
    config = re.sub(r'\s*<!--HESLO-->.*?<!--/HESLO-->', '', config, flags=re.S)
assert not re.search(r'@@LOGIN_[A-Z]+@@', config), 'nedosazené heslo'
(OUT / 'web.config').write_text(config, encoding='utf-8')

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
