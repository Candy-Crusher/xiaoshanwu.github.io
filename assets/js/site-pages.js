/* Progressive enhancement only: every paper is readable without JavaScript. */
(() => {
  'use strict';
  const page = document.body.dataset.page;
  const hash = location.hash;
  if (page === 'publications') { location.replace('research.html' + hash); return; }
  if (page === 'index' && hash) {
    const id = hash.slice(1);
    const resume = ['background', 'education', 'experience', 'awards', 'skills', 'research-interests'];
    const target = resume.includes(id) ? 'resume.html' : id === 'inspiration' ? 'about.html' :
      ['direction', 'selected-research', 'publications', 'projects'].includes(id) || /^(selected-|pub-)/.test(id) ? 'research.html' : '';
    if (target) { location.replace(target + hash); return; }
  }
  // Old Resume interest links now point to the research record rather than a
  // second copy of the same paragraph.
  if (page === 'resume' && ['#research-interests','#resume-publications'].includes(hash)) {
    location.replace('research.html' + (hash === '#resume-publications' ? '#publications' : '#direction')); return;
  }
  const dialog = document.getElementById('research-figure');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  let opener = null;
  const image = dialog.querySelector('img');
  const caption = dialog.querySelector('.figure-dialog-caption');
  const close = dialog.querySelector('.figure-close');
  document.querySelectorAll('a[data-figure]').forEach(a => a.addEventListener('click', e => {
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault(); opener = a; image.src = a.href;
    image.alt = a.closest('[data-paper]')?.querySelector('h3')?.textContent || 'Research figure';
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
