/* Native scrolling with bounded desktop parallax; no animation dependencies. */
(() => {
  'use strict';
  const cover = document.querySelector('.cinematic-shell');
  const navigation = document.querySelector('.hero-navigation');
  if (!cover || !navigation) return;
  const media = cover.querySelector('.hero-media');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const desktop = window.matchMedia('(min-width: 981px) and (min-aspect-ratio: 1/1) and (pointer: fine)');
  let height = cover.offsetHeight;
  let ticking = false;
  function paint() {
    const y = window.scrollY || 0;
    navigation.classList.toggle('is-scrolled', y > 70);
    const shift = !motion.matches && desktop.matches ? Math.min(height * .04, y * .10) : 0;
    media.style.setProperty('--hero-shift', `${shift.toFixed(1)}px`);
    ticking = false;
  }
  function requestPaint() { if (!ticking) { ticking = true; window.requestAnimationFrame(paint); } }
  window.addEventListener('scroll', requestPaint, {passive: true});
  window.addEventListener('resize', () => { height = cover.offsetHeight; requestPaint(); }, {passive: true});
  motion.addEventListener('change', requestPaint);
  desktop.addEventListener('change', requestPaint);
  paint();
})();
