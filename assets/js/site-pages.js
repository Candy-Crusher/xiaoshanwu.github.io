/* Progressive enhancement: the complete research record is native homepage HTML. */
(() => {
  'use strict';
  const page = document.body.dataset.page;
  const legacy = page === 'research' || page === 'publications';
  if (legacy) {
    location.replace('index.html' + location.search + (location.hash || '#research'));
    return;
  }
  function routeLegacyHash() {
    const hash = location.hash;
    if (!hash) return false;
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return false; }
    if (page === 'index') {
      const resume = ['background', 'education', 'experience', 'awards', 'skills'];
      if (resume.includes(id)) { location.replace('resume.html' + hash); return true; }
      if (id === 'inspiration') { location.replace('about.html' + hash); return true; }
      // Research and paper hashes now stay here. Never redirect back to the
      // legacy research.html alias: that would cause a navigation loop.
    }
    if (page === 'resume' && ['research-interests', 'resume-publications'].includes(id)) {
      location.replace('index.html#' + (id === 'resume-publications' ? 'publications' : 'research-interests'));
      return true;
    }
    return false;
  }
  if (routeLegacyHash()) return;
  window.addEventListener('hashchange', routeLegacyHash);
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
