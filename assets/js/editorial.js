/* A progressively enhanced image viewer; research links remain ordinary links. */
(() => {
  // Preserve previously shared publication permalinks after separating the full list.
  if (document.body.dataset.page === 'home' && /^#pub-[a-z0-9-]+$/.test(location.hash)) {
    location.replace('publications.html' + location.hash);
    return;
  }
  const dialog = document.querySelector('#research-figure');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('.figure-dialog-image');
  const caption = dialog.querySelector('.figure-dialog-caption');
  const close = dialog.querySelector('.figure-close');
  let opener = null;
  document.querySelectorAll('a[data-figure]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      opener = link;
      image.src = link.href;
      image.alt = link.querySelector('img')?.alt || 'Research method figure';
      caption.textContent = link.dataset.caption || image.alt;
      dialog.showModal();
      close.focus();
    });
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    if (opener?.isConnected) opener.focus();
  });
})();
