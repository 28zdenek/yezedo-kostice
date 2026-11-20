(() => {
  // Compatibility with links to chapters of the original homepage.
  if (document.body.dataset.page === 'index.html') {
    const oldDestinations = {
      zona:'pribeh.html#vize', system:'areal.html#koncepce', areal:'areal.html#orientace',
      galerie:'areal.html#koncepce', biq:'biq.html', haly:'areal.html#haly',
      krajina:'areal.html#krajina', 'verejny-prostor':'areal.html#verejny-prostor',
      cirkularita:'areal.html#cirkularita', pece:'services.html',
      partnerstvi:'development.html#partnerstvi', kontakt:'kontakt.html',
      'ke-stazeni':'kontakt.html#ke-stazeni', dokumenty:'nabidka-hal.html#dokumenty'
    };
    const resolveOldLink = () => {
      const destination = oldDestinations[location.hash.slice(1)];
      if (destination) location.replace(destination);
    };
    resolveOldLink();
    window.addEventListener('hashchange', resolveOldLink);
  }
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  const closeMenu = () => {nav?.classList.remove('open');toggle?.setAttribute('aria-expanded','false');};
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded',String(open));nav?.classList.toggle('open',open);
  });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click',closeMenu));
  document.addEventListener('keydown',e => {
    if(e.key==='Escape' && nav?.classList.contains('open')){closeMenu();toggle.focus();}
  });
  document.addEventListener('click',e => {if(!e.target.closest('.header'))closeMenu();});
  window.matchMedia('(min-width:981px)').addEventListener('change',closeMenu);
  let activeVideo = null;
  document.querySelectorAll('.video-launch').forEach(button => button.addEventListener('click',() => {
    const wrapper=button.closest('[data-video]');
    if (location.protocol === 'file:') {
      window.open(`https://youtu.be/${encodeURIComponent(wrapper.dataset.video)}`, '_blank', 'noopener');
      return;
    }
    if(activeVideo && activeVideo.wrapper!==wrapper) {
      activeVideo.wrapper.replaceChildren(activeVideo.button);
    }
    const frame=document.createElement('iframe');
    frame.src=`https://www.youtube-nocookie.com/embed/${encodeURIComponent(wrapper.dataset.video)}?autoplay=1&rel=0&playsinline=1`;
    frame.title=button.getAttribute('aria-label').replace('Přehrát: ','');
    frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
    wrapper.replaceChildren(frame);frame.focus();
    activeVideo={wrapper,button};
  }));
  document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click',() => {
    const filter=button.dataset.filter;let count=0;
    document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    document.querySelectorAll('[data-category]').forEach(a=>{a.hidden=filter!=='all'&&a.dataset.category!==filter;if(!a.hidden)count++;});
    document.querySelector('#document-count').textContent=`${count} ${count===1?'dokument':count<5?'dokumenty':'dokumentů'}`;
  }));

  // Local map: wheel zoom (1–3×), drag, accessible buttons and keyboard controls.
  document.querySelectorAll('.map-widget').forEach(widget => {
    const viewport = widget.querySelector('.map-viewport');
    const image = viewport.querySelector('.map-image');
    const readout = widget.querySelector('.map-scale');
    const zoomIn = widget.querySelector('[data-map-zoom="in"]');
    const zoomOut = widget.querySelector('[data-map-zoom="out"]');
    const reset = widget.querySelector('[data-map-reset]');
    let scale = 1, x = 0, y = 0, drag = null;
    let width = viewport.clientWidth, height = viewport.clientHeight;
    const clamp = () => {
      x = Math.max(width * (1 - scale), Math.min(0, x));
      y = Math.max(height * (1 - scale), Math.min(0, y));
    };
    const render = () => {
      clamp();
      image.style.transform = `translate3d(${x}px,${y}px,0) scale(${scale})`;
      viewport.dataset.scale = scale.toFixed(2);
      viewport.dataset.x = x.toFixed(1);
      viewport.dataset.y = y.toFixed(1);
      viewport.dataset.zoomed = String(scale > 1.001);
      readout.textContent = `${Math.round(scale * 100)} %`;
      zoomIn.disabled = scale >= 3;
      zoomOut.disabled = scale <= 1;
    };
    const zoom = (next, px = width / 2, py = height / 2) => {
      next = Math.max(1, Math.min(3, next));
      const ratio = next / scale;
      x = px - (px - x) * ratio;
      y = py - (py - y) * ratio;
      scale = next;
      if (scale === 1) x = y = 0;
      render();
    };
    zoomIn.addEventListener('click', () => zoom(scale + .25));
    zoomOut.addEventListener('click', () => zoom(scale - .25));
    reset.addEventListener('click', () => zoom(1));
    viewport.addEventListener('wheel', event => {
      const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? height : 1);
      const next = Math.max(1, Math.min(3, scale * Math.exp(-delta * .0025)));
      if (Math.abs(next - scale) < .0001) return;
      event.preventDefault();
      const rect = viewport.getBoundingClientRect();
      zoom(next, event.clientX - rect.left, event.clientY - rect.top);
    }, {passive: false});
    viewport.addEventListener('pointerdown', event => {
      if (scale <= 1 || (event.pointerType === 'mouse' && event.button !== 0)) return;
      drag = {id: event.pointerId, px: event.clientX, py: event.clientY, x, y};
      viewport.setPointerCapture(event.pointerId);
      viewport.classList.add('dragging');
      event.preventDefault();
    });
    viewport.addEventListener('pointermove', event => {
      if (!drag || event.pointerId !== drag.id) return;
      x = drag.x + event.clientX - drag.px;
      y = drag.y + event.clientY - drag.py;
      render();
    });
    const stopDrag = () => { drag = null; viewport.classList.remove('dragging'); };
    viewport.addEventListener('pointerup', stopDrag);
    viewport.addEventListener('pointercancel', stopDrag);
    viewport.addEventListener('lostpointercapture', stopDrag);
    viewport.addEventListener('keydown', event => {
      if (event.key === '+' || event.key === '=') zoom(scale + .25);
      else if (event.key === '-') zoom(scale - .25);
      else if (event.key === '0' || event.key === 'Home') zoom(1);
      else if (scale > 1 && ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)) {
        if (event.key === 'ArrowLeft') x += 40;
        if (event.key === 'ArrowRight') x -= 40;
        if (event.key === 'ArrowUp') y += 40;
        if (event.key === 'ArrowDown') y -= 40;
        render();
      } else return;
      event.preventDefault();
    });
    new ResizeObserver(() => {
      const nextWidth = viewport.clientWidth, nextHeight = viewport.clientHeight;
      if (width && height) { x *= nextWidth / width; y *= nextHeight / height; }
      width = nextWidth; height = nextHeight;
      render();
    }).observe(viewport);
    render();
  });
})();

// Poptávkový formulář: bez serveru, sestaví e-mail pro starostu (mailto).
(() => {
  const form = document.querySelector('#poptavka-form');
  if (!form) return;
  const hala = new URLSearchParams(location.search).get('hala');
  if (hala && /^SO0\d$/.test(hala)) form.prostor.value = `Hala ${hala}`;
  const space = form.querySelector('[data-for-role]');
  const sync = () => { space.hidden = form.role.value !== space.dataset.forRole; };
  form.querySelectorAll('[name=role]').forEach(r => r.addEventListener('change', sync));
  sync();
  form.addEventListener('submit', e => {
    e.preventDefault();
    const status = document.querySelector('#poptavka-stav');
    const missing = [...form.querySelectorAll('[required]')].find(f => !f.value.trim() || (f.type === 'email' && !f.checkValidity()));
    if (missing) { status.textContent = 'Vyplňte prosím jméno, platný e-mail a zprávu.'; missing.focus(); return; }
    const role = form.role.value;
    const lines = [`Píšu jako: ${role}`, `Jméno: ${form.jmeno.value.trim()}`];
    if (form.firma.value.trim()) lines.push(`Firma: ${form.firma.value.trim()}`);
    lines.push(`E-mail: ${form.email.value.trim()}`);
    if (form.telefon.value.trim()) lines.push(`Telefon: ${form.telefon.value.trim()}`);
    if (!space.hidden && form.prostor.value) lines.push(`Hledaný prostor: ${form.prostor.value}`);
    lines.push('', form.zprava.value.trim());
    const subject = `YEZEDO – ${role}${!space.hidden && form.prostor.value ? ' – ' + form.prostor.value : ''}`;
    location.href = `mailto:starosta@kostice.cz?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
    status.textContent = 'Otevírá se váš e-mailový program. Pokud se neotevřel, napište na starosta@kostice.cz.';
  });
})();

// Formulář: předvyplnění role z odkazu (?role=investor|obcan|firma)
(() => {
  const form = document.querySelector('#poptavka-form');
  const role = new URLSearchParams(location.search).get('role');
  const map = {investor: 'Investor / partner', obcan: 'Občan', firma: 'Firma / živnostník'};
  if (!form || !map[role]) return;
  const input = form.querySelector(`[name=role][value="${map[role]}"]`);
  if (input) { input.checked = true; input.dispatchEvent(new Event('change')); }
})();

// Hlavní stránka pro investory: odkrývání, ukazatel kapitol, plovoucí tlačítko, formulář
(() => {
  const root = document.querySelector('main.inv');
  if (!root) return;
  document.documentElement.classList.add('js');
  const io = 'IntersectionObserver' in window;
  const reveals = root.querySelectorAll('.inv-reveal');
  if (io) {
    const ro = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); } }), {rootMargin: '0px 0px -8% 0px'});
    reveals.forEach(el => ro.observe(el));
  } else reveals.forEach(el => el.classList.add('in'));

  const nav = document.querySelector('.inv-chapters');
  const sticky = document.querySelector('.inv-sticky');
  const hero = document.querySelector('.inv-hero');
  const contact = document.querySelector('#napiste-nam');
  const links = nav ? [...nav.querySelectorAll('a')] : [];
  const chapters = links.map(a => document.querySelector(a.getAttribute('href')));
  const update = () => {
    const y = window.scrollY, h = window.innerHeight;
    const pastHero = hero.getBoundingClientRect().bottom < h * 0.4;
    const atContact = contact.getBoundingClientRect().top < h * 0.8;
    nav && nav.classList.toggle('show', pastHero);
    sticky && sticky.classList.toggle('show', pastHero && !atContact);
    let current = -1;
    chapters.forEach((c, i) => { if (c && c.getBoundingClientRect().top < h * 0.45) current = i; });
    links.forEach((a, i) => a.classList.toggle('active', i === current));
    if (current >= 0 && nav) nav.classList.toggle('on-dark', chapters[current].classList.contains('inv-dark'));
  };
  window.addEventListener('scroll', update, {passive: true});
  window.addEventListener('resize', update);
  update();

  const form = document.querySelector('#investor-form');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const status = document.querySelector('#investor-stav');
    const missing = [...form.querySelectorAll('[required]')].find(f => !f.value.trim() || (f.type === 'email' && !f.checkValidity()));
    if (missing) { status.textContent = 'Vyplňte prosím jméno, platný e-mail a váš záměr.'; missing.focus(); return; }
    const v = n => form[n].value.trim();
    const lines = [`Zájem: ${form.zajem.value}`, `Jméno: ${v('jmeno')}`];
    if (v('firma')) lines.push(`Společnost: ${v('firma')}`);
    lines.push(`E-mail: ${v('email')}`);
    if (v('telefon')) lines.push(`Telefon: ${v('telefon')}`);
    lines.push('', v('zprava'));
    const subject = `YEZEDO – ${form.zajem.value}${v('firma') ? ' – ' + v('firma') : ''}`;
    location.href = `mailto:starosta@kostice.cz?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
    status.textContent = 'Otevírá se váš e-mailový program. Pokud se neotevřel, napište na starosta@kostice.cz.';
  });
})();

// Hlavní stránka: předvyplnění formuláře z odkazu ?hala=SO03 (ze stránky haly)
(() => {
  const form = document.querySelector('#investor-form');
  const hala = new URLSearchParams(location.search).get('hala');
  if (!form || !/^SO0\d$/.test(hala || '')) return;
  const r = form.querySelector('[name=zajem][value="Výstavba nebo koupě haly"]');
  if (r) r.checked = true;
  if (!form.zprava.value) form.zprava.value = `Mám zájem o halu ${hala}. `;
})();

// Postupné odkrývání obsahu na podstránkách (hlavní stránka má vlastní .inv-reveal)
(() => {
  if (document.querySelector('main.inv') || !('IntersectionObserver' in window)) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('js');
  const sel = 'main section:not(.sub-hero):not(.cover) h2, main .prose, main .photo, main .photo-pair, main .principles > *, main .hall-card, main .timeline li, main .text-item, main .hmap, main .yz-card, main .yz-pics > figure, main .yz-short li, main .yz-faq, main .news-section article, main .floor-line, main .steps > li, main .responsibilities article, main .technology-list li, main .ob-four li, main .ob-compare figure, main .ob-tile, main .ob-places li, main .ob-time li, main .ob-gains article, main .ob-news article, main .ob-plan, main .ob-mayor';
  const els = [...document.querySelectorAll(sel)].filter(el => el.getBoundingClientRect().top > innerHeight * 0.9);
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), {rootMargin: '0px 0px -6% 0px'});
  els.forEach(el => { el.classList.add('rv'); io.observe(el); });
})();

// Tlačítko „Domluvit schůzku“ v menu skryté, dokud jsou vidět tlačítka v úvodní fotce
(() => {
  const header = document.querySelector('.header');
  const heroActions = document.querySelector('.inv-hero .inv-hero-actions, .sub-hero .inv-hero-actions, .ob-hero .inv-hero-actions');
  if (!header || !heroActions || !('IntersectionObserver' in window)) return;
  header.classList.add('cta-wait');
  new IntersectionObserver(([e]) => {
    header.classList.toggle('cta-wait', e.isIntersecting || e.boundingClientRect.top > 0);
  }, {rootMargin: `-${header.offsetHeight}px 0px 0px 0px`}).observe(heroActions);
})();
