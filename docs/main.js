// Mobilní menu: po kliknutí na odkaz (kotvu na stejné stránce) menu zavřít
document.querySelectorAll('nav[data-nav] a').forEach(function (a) {
  a.addEventListener('click', function () {
    var t = document.getElementById('navtoggle');
    if (t) t.checked = false;
  });
});

// Galerie na Domů: zvětšení obrázku
(function () {
  var overlay = document.querySelector('[data-lightbox-overlay]');
  if (!overlay) return;
  var img = overlay.querySelector('img');
  function close() { overlay.hidden = true; img.removeAttribute('src'); }
  document.querySelectorAll('[data-lightbox]').forEach(function (el) {
    el.addEventListener('click', function () {
      img.src = el.getAttribute('data-lightbox');
      overlay.hidden = false;
    });
  });
  overlay.addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) close(); });
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
