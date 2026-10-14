/* Native same-document links; JS only enhances active-section indication. */
(() => {
  'use strict';
  const page = document.body.dataset.page;
  const legacy = {research: '#research', publications: '#research', resume: '#experience', about: '#about'};
  if (legacy[page]) {
    const hash = location.hash === '#resume-publications' ? '#publications' : location.hash;
    location.replace('index.html' + location.search + (hash || legacy[page]));
    return;
  }
  if (location.hash === '#resume-publications') {
    location.replace('index.html' + location.search + '#publications');
    return;
  }
  // #inspiration is now native homepage content, not a redirect to About.
  const header = document.querySelector('.site-topbar');
  const sections = [['welcome','top'], ['news','news'], ['research','research'],
    ['experience','experience'], ['awards','awards'], ['about','about']]
    .map(([id, anchor]) => ({node: document.getElementById(id), anchor})).filter(s => s.node);
  const navLinks = [...document.querySelectorAll('.site-nav a, .site-footer nav a')];
  let pending = false;
  function updateNavigation() {
    pending = false;
    if (page !== 'index') return;
    const threshold = (header?.getBoundingClientRect().height || 0) + 45;
    let active = 'top';
    for (const section of sections) {
      if (section.node.getBoundingClientRect().top <= threshold) active = section.anchor;
    }
    if (window.scrollY > 0 && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) active = 'about';
    navLinks.forEach(a => {
      if (a.getAttribute('href') === '#' + active) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
  }
  function scheduleNavigation() {
    if (!pending) { pending = true; requestAnimationFrame(updateNavigation); }
  }
  function measureHeader() {
    if (header) document.documentElement.style.setProperty('--navigation-height', header.getBoundingClientRect().height + 'px');
    scheduleNavigation();
  }
  if ('ResizeObserver' in window && header) new ResizeObserver(measureHeader).observe(header);
  measureHeader();
  document.fonts?.ready.then(measureHeader);
  window.addEventListener('resize', measureHeader);
  window.addEventListener('scroll', scheduleNavigation, {passive: true});
  window.addEventListener('hashchange', scheduleNavigation);
  window.addEventListener('pageshow', measureHeader);
  // Play the original muted demo only while visible. Reduced-motion and
  // data-saving users keep native click-to-play controls. A manual pause is
  // respected until the user chooses to play again.
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('video[data-autoplay-on-view]').forEach(video => {
    let visible = false, manuallyPaused = false;
    const play = () => {
      if (visible && !document.hidden && !manuallyPaused && !motion.matches && !navigator.connection?.saveData) {
        video.play().catch(() => {});
      }
    };
    video.addEventListener('pause', () => {
      if (visible && !document.hidden && !motion.matches) manuallyPaused = true;
    });
    video.addEventListener('play', () => { manuallyPaused = false; });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        if (visible) play(); else video.pause();
      }, {threshold: 0.3}).observe(video);
    }
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) video.pause(); else play();
    });
    motion.addEventListener('change', () => {
      if (motion.matches) video.pause(); else play();
    });
  });
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
