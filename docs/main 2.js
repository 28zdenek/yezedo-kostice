// Mobilní menu: po kliknutí na odkaz (kotvu na stejné stránce) menu zavřít
document.querySelectorAll('nav[data-nav] a').forEach(function (a) {
  a.addEventListener('click', function () {
    var t = document.getElementById('navtoggle');
    if (t) t.checked = false;
  });
});

// Video na Domů: přehrávač YouTube se vloží až po kliknutí na náhled
document.querySelectorAll('a[data-yt]').forEach(function (a) {
  a.addEventListener('click', function (e) {
    e.preventDefault();
    var f = document.createElement('iframe');
    f.className = 'yt-frame';
    f.src = 'https://www.youtube-nocookie.com/embed/' + a.getAttribute('data-yt') + '?autoplay=1&rel=0';
    f.title = a.getAttribute('data-title');
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    f.allowFullscreen = true;
    a.replaceWith(f);
  });
});

// Mapa na Domů: iframe Google se vloží až po kliknutí
document.querySelectorAll('[data-map]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var f = document.createElement('iframe');
    f.className = 'map-frame';
    f.src = btn.getAttribute('data-map');
    f.title = 'Mapa: Kostice u Břeclavi';
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    btn.parentNode.replaceWith(f);
    f.focus();
  });
});

// Mobilní menu z klávesnice: Enter přepíná, Escape zavírá
(function () {
  var t = document.getElementById('navtoggle');
  if (!t) return;
  t.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); t.checked = !t.checked; }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && t.checked) { t.checked = false; t.focus(); }
  });
})();

// Galerie na Domů: zvětšení obrázku (myš, dotyk i klávesnice)
(function () {
  var overlay = document.querySelector('[data-lightbox-overlay]');
  if (!overlay) return;
  var img = overlay.querySelector('img');
  var blank = img.getAttribute('src');
  var closeBtn = overlay.querySelector('[data-lightbox-close]');
  var opener = null;
  function open(el) {
    var thumb = el.querySelector('img');
    opener = el;
    img.src = el.getAttribute('data-lightbox');
    img.alt = thumb ? thumb.alt : '';
    overlay.hidden = false;
    closeBtn.focus();
  }
  function close() {
    overlay.hidden = true;
    img.src = blank;
    if (opener) opener.focus();
  }
  document.querySelectorAll('[data-lightbox]').forEach(function (el) {
    var thumb = el.querySelector('img');
    el.setAttribute('aria-label', 'Zvětšit obrázek' + (thumb && thumb.alt ? ': ' + thumb.alt : ''));
    el.addEventListener('click', function () { open(el); });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(el); }
    });
  });
  overlay.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (overlay.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
  });
})();

// Dokumenty: filtr podle skupiny
(function () {
  var tabs = document.querySelectorAll('[data-tab]');
  if (!tabs.length) return;
  var rows = document.querySelectorAll('a[data-key]');
  var count = document.querySelector('[data-count]');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var key = tab.getAttribute('data-tab');
      var n = 0;
      tabs.forEach(function (t) {
        var on = t === tab;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      rows.forEach(function (r) {
        var show = key === 'all' || r.getAttribute('data-key') === key;
        r.hidden = !show;
        if (show) n++;
      });
      if (count) count.textContent = n;
    });
  });
})();
