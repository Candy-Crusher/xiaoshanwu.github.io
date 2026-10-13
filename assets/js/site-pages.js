/* Progressive enhancement: the complete research record is native homepage HTML. */
(() => {
  'use strict';
  const page = document.body.dataset.page;
  const resumeAnchors = new Set(['resume','background','education','experience','skills','awards']);
  function normalizedHash(hash, fallback) {
    if (!hash) return fallback;
    if (hash === '#resume-publications') return '#publications';
    return hash;
  }
  if (['research', 'publications', 'resume'].includes(page)) {
    const hash = normalizedHash(location.hash, page === 'resume' ? '#resume' : '#research');
    location.replace('index.html' + location.search + hash);
    return;
  }
  function routeLegacyHash() {
    if (page !== 'index') return false;
    if (location.hash === '#inspiration') {
      location.replace('about.html' + location.search + location.hash);
      return true;
    }
    if (location.hash === '#resume-publications') {
      location.replace('index.html' + location.search + '#publications');
      return true;
    }
    // Resume, education and awards anchors now stay on this document.
    return false;
  }
  if (routeLegacyHash()) return;
  function updateNavigation() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { id = ''; }
    const resumeSelected = resumeAnchors.has(id);
    document.querySelectorAll('.site-nav a, .site-footer nav a').forEach(a => {
      if (page !== 'index') return;
      a.removeAttribute('aria-current');
      const target = a.getAttribute('href');
      if (target === '#resume' && resumeSelected) a.setAttribute('aria-current', 'location');
      if (target === '#top' && !resumeSelected) a.setAttribute('aria-current', 'location');
    });
  }
  function measureHeader() {
    const height = document.querySelector('.site-topbar')?.getBoundingClientRect().height;
    if (height) document.documentElement.style.setProperty('--navigation-height', height + 'px');
  }
  measureHeader();
  window.addEventListener('resize', measureHeader);
  updateNavigation();
  window.addEventListener('hashchange', () => { if (!routeLegacyHash()) updateNavigation(); });
  const dialog = document.getElementById('research-figure');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  let opener = null;
  const image = dialog.querySelector('img');
  const caption = dialog.querySelector('.figure-dialog-caption');
  const close = dialog.querySelector('.figure-close');
  document.querySelectorAll('a[data-figure]').forEach(a => a.addEventListener('click', e => {
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault(); opener = a; image.src = a.href;
    image.alt = a.closest('[data-paper]')?.querySelector('.pub-title')?.textContent || 'Research figure';
    caption.textContent = a.dataset.caption || image.alt;
    dialog.showModal(); close.focus();
  }));
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => {
    if (e.target !== dialog) return;
    const b = dialog.getBoundingClientRect();
    if (e.clientX < b.left || e.clientX > b.right || e.clientY < b.top || e.clientY > b.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => { image.removeAttribute('src'); if (opener?.isConnected) opener.focus(); });
})();
