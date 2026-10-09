/* Figure links still work as ordinary image links when JavaScript is unavailable. */
(() => {
  const dialog = document.querySelector('#research-figure');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('.figure-dialog-image');
  const caption = dialog.querySelector('.figure-dialog-caption');
  const close = dialog.querySelector('.figure-close');
  let opener = null;
  document.querySelectorAll('a[data-figure]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      image.src = link.href;
      image.alt = link.dataset.caption || link.querySelector('img')?.alt || 'Research figure';
      caption.textContent = image.alt;
      dialog.showModal();
      close.focus();
    });
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    if (opener && document.contains(opener)) opener.focus();
  });
})();
