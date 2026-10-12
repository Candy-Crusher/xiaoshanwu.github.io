
(() => {
 'use strict';
 const root=document.documentElement,toggle=document.querySelector('.theme-toggle');
 function dark(){return root.dataset.theme?root.dataset.theme==='dark':window.matchMedia('(prefers-color-scheme:dark)').matches;}
 function label(){if(toggle){toggle.textContent=dark()?'☀':'☾';toggle.setAttribute('aria-label',dark()?'Use light theme':'Use dark theme');toggle.setAttribute('aria-pressed',String(dark()));}}
 try{const t=localStorage.getItem('research-theme');if(['light','dark'].includes(t))root.dataset.theme=t;}catch(_){}
 label();if(toggle)toggle.addEventListener('click',()=>{root.dataset.theme=dark()?'light':'dark';try{localStorage.setItem('research-theme',root.dataset.theme);}catch(_){}label();});
 const modal=document.querySelector('#figure-dialog');
 if(modal&&typeof modal.showModal==='function'){
  document.querySelectorAll('a.figure-link').forEach(a=>a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();const im=modal.querySelector('img');im.src=a.href;im.alt=a.querySelector('img')?.alt||'Original research figure';modal.querySelector('.dialog-caption').textContent=a.closest('figure')?.querySelector('figcaption')?.textContent||im.alt;modal.showModal();}));
  modal.querySelector('.close').addEventListener('click',()=>modal.close());modal.addEventListener('click',e=>{if(e.target===modal){const r=modal.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)modal.close();}});
 }
 document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const code=document.getElementById(b.dataset.copy||'bibtex'),status=document.querySelector('#copy-status');try{await navigator.clipboard.writeText(code.textContent);status.textContent='Copied.';}catch(_){const range=document.createRange();range.selectNodeContents(code);const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);status.textContent='Citation selected. Press Ctrl+C or ⌘C.';}}));
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>{for(const e of es)if(e.isIntersecting){document.querySelectorAll('.navlinks a').forEach(a=>{a.removeAttribute('aria-current');if(a.hash==='#'+e.target.id)a.setAttribute('aria-current','location');});}}, {rootMargin:'-14% 0px -65% 0px'});document.querySelectorAll('main>section[id]').forEach(s=>io.observe(s));}
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(!e.isIntersecting&&!v.paused){v.dataset.resume='1';v.pause();}else if(e.isIntersecting&&v.dataset.resume==='1'){v.play().catch(()=>{});delete v.dataset.resume;}}),{threshold:.05});document.querySelectorAll('video.demo-video').forEach(v=>io.observe(v));}
})();
