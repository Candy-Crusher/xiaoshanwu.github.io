
(() => {
 'use strict';
 const modal=document.querySelector('#figure-dialog');
 if(modal && typeof modal.showModal==='function'){
  document.querySelectorAll('.figure-link').forEach(link=>link.addEventListener('click',e=>{
   if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
   e.preventDefault(); const image=modal.querySelector('img'); image.src=link.href; image.alt=link.querySelector('img').alt; modal.showModal();
  }));
  modal.querySelector('.close').addEventListener('click',()=>modal.close());
  modal.addEventListener('click',e=>{if(e.target===modal)modal.close();});
 }
 document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
  const code=document.querySelector('#bibtex'),status=document.querySelector('#copy-status');
  try{await navigator.clipboard.writeText(code.textContent);status.textContent='Copied.';}
  catch(_){const range=document.createRange();range.selectNodeContents(code);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);status.textContent='Citation selected. Press Ctrl+C or ⌘C to copy.';}
 }));
 if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
   if(!entry.isIntersecting)return;
   document.querySelectorAll('.topnav a[href^="#"]').forEach(link=>{link.removeAttribute('aria-current');if(link.hash==='#'+entry.target.id)link.setAttribute('aria-current','location');});
  }),{rootMargin:'-12% 0px -55% 0px'});
  document.querySelectorAll('main section[id]').forEach(section=>observer.observe(section));
 }
})();
