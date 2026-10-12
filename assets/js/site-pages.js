
(() => {
  'use strict';
  const page=document.body.dataset.page;
  const oldDestination = hash => {
    const id=hash.replace(/^#/,'');
    if(['background','education','experience','awards'].includes(id)) return 'resume.html'+hash;
    if(id==='inspiration') return 'about.html'+hash;
    if(id==='direction'||id==='selected-research'||id==='publications'||id.startsWith('selected-')||id.startsWith('pub-')) return 'research.html'+hash;
    return null;
  };
  if(page==='home'&&location.hash){const target=oldDestination(location.hash);if(target){location.replace(target);return;}}
  function revealHash(){
    if(!location.hash) return;
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
    const target=document.getElementById(id);
    if(!target)return;
    let node=target;
    while(node){if(node.tagName==='DETAILS')node.open=true;node=node.parentElement;}
    if(target.tagName==='DETAILS')target.open=true;
    requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));
  }
  window.addEventListener('hashchange',revealHash);
  document.querySelectorAll('a[href="#publications"]').forEach(a=>a.addEventListener('click',()=>{const d=document.getElementById('publications');if(d)d.open=true;}));
  revealHash();
})();
