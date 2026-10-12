#!/usr/bin/env python3
"""Apply the user-selected UGG layout to the seven existing research websites.
Only presentation changes; original HTML is retained as reversible source.
All research media, interactive viewer files and the four personal pages stay.
"""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import hashlib, json, re
from bs4 import BeautifulSoup, Tag
ROOT=Path(__file__).resolve().parents[1]
SLUGS=('sandbox','eag3r','videossm','game','lifr-seg','lifr-v2','evsplat')
NAMES=dict(zip(SLUGS,('S4NDBOX','EAG3R','VideoSSM','GaMe','LiFR-Seg','LiFR v2','EVSplat')))
SOURCES=ROOT/'_site_content/project-sources'
VERSION='ugg-20261012-v1'
SOURCE_REF='sky-lzy/UGG-website@8c34c46fbb780f79045ef6fd0f176b15a2d219db'
# UGG/MoSE3 foundations: typefaces, axis colors, gradient header, sticky navigation,
# 1120px measure, section bands and rounded panels. No UGG research media imported.
CSS=r'''
:root{--bg:#fff;--surface:#f7f7f9;--surface-2:#ececef;--line:#e3e3e6;--text:#15171a;--dim:#5b6169;--faint:#8a9099;--axis-x:#d6473a;--axis-y:#2e9c5b;--axis-z:#3b63c7;--maxw:1120px;--measure:760px;--radius:10px;--display:"Space Grotesk",ui-sans-serif,system-ui,sans-serif;--body:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111316;--surface:#181a1e;--surface-2:#22252a;--line:#2a2e34;--text:#eceef1;--dim:#a2a9b2;--faint:#787f88;--axis-x:#f0685a;--axis-y:#48c179;--axis-z:#6e91e8}}
:root[data-theme="dark"]{--bg:#111316;--surface:#181a1e;--surface-2:#22252a;--line:#2a2e34;--text:#eceef1;--dim:#a2a9b2;--faint:#787f88;--axis-x:#f0685a;--axis-y:#48c179;--axis-z:#6e91e8}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:78px}body.ugg-page{margin:0;background:var(--bg);color:var(--text);font:400 16.5px/1.65 var(--body);-webkit-font-smoothing:antialiased}img,video{max-width:100%}.ugg-page a{color:var(--axis-z);text-underline-offset:4px}.ugg-page button{font-family:var(--body)}.ugg-wrap{width:100%;max-width:var(--maxw);margin:0 auto;padding:0 24px}.measure{max-width:var(--measure);margin-left:auto;margin-right:auto}.ugg-page section.ugg-section{padding:62px 0;margin:0;border:0;display:block}.ugg-page section.ugg-section+section.ugg-section{border-top:1px solid var(--line)}.ugg-page section.ugg-section:nth-of-type(2n+3){background:color-mix(in srgb,var(--surface) 55%,var(--bg))}.ugg-page .ugg-section h2{font:600 32px/1.2 var(--display);color:var(--text);letter-spacing:-.02em;margin:0 0 12px;text-align:center}.ugg-page .ugg-section h2::before{content:"";display:block;width:34px;height:3px;border-radius:2px;margin:0 auto 18px;background:linear-gradient(90deg,var(--axis-x),var(--axis-y),var(--axis-z))}.ugg-page .lede{color:var(--dim);text-align:center;margin:0 auto 30px;max-width:var(--measure);font-size:16px;line-height:1.65}.ugg-page .ugg-section h3{font:600 19px/1.3 var(--display);color:var(--text);margin:30px 0 12px}.ugg-page .prose{max-width:var(--measure);margin-inline:auto;text-align:left;color:var(--text);font-size:17.5px;line-height:1.7}.ugg-page .prose p{margin:0 0 20px}.ugg-page .prose strong{color:var(--axis-z)}
nav.ugg-top{position:sticky;top:0;z-index:60;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}nav.ugg-top>.ugg-wrap{display:flex;align-items:center;gap:15px;min-height:58px}nav.ugg-top .brand{font:700 18px/1 var(--display);letter-spacing:-.02em;color:var(--text);text-decoration:none;white-space:nowrap;flex:none}nav.ugg-top .navlinks{display:flex;gap:2px;margin-left:auto;min-width:0;overflow-x:auto;scrollbar-width:none}nav.ugg-top .navlinks a{font:500 13px/1 var(--body);color:var(--dim);text-decoration:none;padding:9px 10px;border-radius:7px;white-space:nowrap}nav.ugg-top .navlinks a:hover,nav.ugg-top .navlinks a[aria-current]{background:var(--surface-2);color:var(--text)}.theme-toggle{border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--text);padding:7px 10px;min-width:38px;min-height:36px;cursor:pointer;flex:none;font-size:15px}.nav-back{font:500 12px/1 var(--body);white-space:nowrap;color:var(--dim)!important;text-decoration:none}.ugg-header{padding:72px 0 45px;text-align:center;background:radial-gradient(55% 60% at 12% 0%,rgba(59,99,199,.14),transparent 70%),radial-gradient(45% 55% at 88% 8%,rgba(214,71,58,.10),transparent 70%),radial-gradient(40% 40% at 50% 100%,rgba(46,156,91,.08),transparent 70%)}.ugg-page .ugg-header h1{font:700 clamp(34px,5.4vw,56px)/1.12 var(--display);letter-spacing:-.03em;margin:0 auto 25px;max-width:30ch;text-wrap:balance;color:var(--text)}.ugg-header h1 .m{color:var(--axis-z)}.ugg-page .ugg-header .authors{display:block;font:400 19px/1.7 var(--body);margin:0 auto 9px;max-width:880px;letter-spacing:0;color:var(--text)}.ugg-header .au{display:inline-block;white-space:nowrap}.ugg-header .authors a{color:var(--text);text-decoration:none;border-bottom:1px solid var(--line)}.ugg-header .authors sup{font-size:.7em;color:var(--faint)}.ugg-page .ugg-header .affil{color:var(--dim);font-size:16.5px;margin:0 auto 8px;max-width:860px}.ugg-header .affil>span+span{margin-left:15px}.ugg-header .equal{color:var(--dim);font-size:12px;margin:0 auto 18px}.ugg-page .ugg-header .venue{font:600 17px/1.4 var(--display);letter-spacing:.01em;color:var(--axis-x);margin:18px auto 22px;background:none;border:0;padding:0}.ugg-header .links{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}.ugg-header .links a{display:inline-flex;align-items:center;gap:8px;background:var(--text);color:var(--bg);text-decoration:none;padding:11px 22px;border-radius:999px;font:500 14px/1 var(--body);border:1px solid var(--text);box-shadow:0 6px 18px -10px rgba(0,0,0,.5);transition:background .15s,transform .15s}.ugg-header .links a:hover{background:var(--axis-z);border-color:var(--axis-z);color:#fff;transform:translateY(-1px)}.ugg-header .link-placeholder{display:inline-flex;align-items:center;padding:9px 17px;border:1px solid var(--line);border-radius:999px;color:var(--dim);font-size:12px;gap:7px}.ugg-header .link-placeholder small{font-size:10px}.ugg-page .tldr{display:block;margin:28px auto 0;max-width:78ch;font:400 17px/1.55 var(--body);color:var(--dim);text-align:center;text-wrap:pretty}.tldr .k{font:400 12px/1 var(--mono);letter-spacing:.12em;color:var(--faint);margin-right:9px}.tldr strong{color:var(--text)}
.ugg-page .hero-teaser{padding-top:14px!important}.ugg-page figure{margin:24px 0 0}.ugg-page .hero-teaser figure{margin-top:0}.ugg-page .figbox{border:1px solid var(--line);border-radius:14px;padding:20px;background:var(--surface);text-align:center;box-shadow:0 18px 40px -30px rgba(0,0,0,.35)}.ugg-page .figure-link{display:block;cursor:zoom-in;overflow:hidden;border-radius:6px;background:#fff}.ugg-page .figure-link img{display:block;max-width:100%;width:auto;max-height:740px;height:auto!important;object-fit:contain;margin:0 auto}.ugg-page .figbox img{border-radius:4px}.ugg-page figcaption,.ugg-page .figure-caption{font:400 13px/1.65 var(--body);color:var(--dim);margin:14px auto 0;text-align:center;max-width:1000px}.ugg-page .zoom-hint{margin-left:12px;font-size:11px;white-space:nowrap}.ugg-page .source-pdf{margin-left:8px;white-space:nowrap}.ugg-page .steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:28px 0}.ugg-page .step{background:var(--surface);border:1px solid var(--line);padding:23px;border-radius:14px;min-width:0}.ugg-page .step h3{margin:8px 0 12px}.ugg-page .step .number{font:400 12px var(--mono);color:var(--axis-z)}.ugg-page .step p{font-size:14px;color:var(--dim);line-height:1.7;margin:0}.ugg-page .table-wrap,.ugg-page .mirror-table-scroll{overflow-x:auto;max-width:100%;border:1px solid var(--line);border-radius:12px}.ugg-page table.results{width:100%;border-collapse:collapse;font:400 14px/1.6 var(--body);color:var(--text);background:var(--bg)}.ugg-page table.results th,.ugg-page table.results td{border:0;border-bottom:1px solid var(--line);padding:15px 16px;text-align:right}.ugg-page table.results th:first-child,.ugg-page table.results td:first-child{text-align:left}.ugg-page table.results thead th{color:var(--dim);background:var(--surface);font-weight:500;font-size:13px}.ugg-page table.results td:last-child{color:var(--axis-z);font-weight:600}.ugg-page .table-note{font:400 13px/1.7 var(--body);color:var(--dim);margin:20px auto 8px;max-width:var(--measure)}.source-link{display:block;text-align:center;font-size:13px;margin-top:14px}.ugg-page pre{background:var(--surface);border:1px solid var(--line);color:var(--text);padding:22px;border-radius:11px;overflow-x:auto;font:400 12.5px/1.7 var(--mono);text-align:left;white-space:pre-wrap;overflow-wrap:anywhere;margin:20px auto;max-width:920px}.ugg-page pre code{font:inherit;background:none;color:inherit;padding:0}.citation-tools{text-align:right;max-width:920px;margin:auto}.copy-button{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:8px 16px;color:var(--text);font-size:12px;cursor:pointer}.copy-status{font-size:12px;color:var(--dim);margin-left:12px}.ugg-page .release{max-width:var(--measure);margin:auto;color:var(--dim);font-size:15px;line-height:1.8;padding:25px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}.focus{display:flex;justify-content:center;gap:24px;flex-wrap:wrap;margin:0 auto;padding:30px;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--dim)}.ugg-page .related{text-align:center;font-size:14px;padding:24px}.ugg-footer{padding:36px 0 45px;text-align:center;background:var(--surface);border-top:1px solid var(--line);color:var(--dim);font-size:13px}.ugg-footer p{margin:0 0 12px}.ugg-footer .fine{font:400 11px/1.8 var(--mono);color:var(--dim)}.ugg-footer .project-links{display:flex;justify-content:center;gap:10px 22px;flex-wrap:wrap;margin:23px auto}.ugg-footer a{color:var(--dim)}.ugg-page .skip-link{position:fixed;top:-80px;left:15px;z-index:100;background:var(--bg);padding:12px 16px}.ugg-page .skip-link:focus{top:8px}.ugg-page :focus-visible{outline:2px solid var(--axis-z);outline-offset:4px}
.ugg-page .legacy-content>.container{width:100%;max-width:100%;padding:0}.ugg-page .legacy-content .container.is-max-desktop{max-width:100%}.ugg-page .legacy-content .content{color:var(--text);font-family:var(--body)}.ugg-page .legacy-content .content p{line-height:1.8}.ugg-page .legacy-content .content strong{color:inherit}.ugg-page .legacy-content .content h2{margin-top:0}.ugg-page .legacy-content .hero-body{padding:0}.ugg-page .content-block{background:transparent;color:var(--text);padding:0;margin:24px 0}.ugg-page .content-block p{color:var(--text)}.ugg-page .method-grid{margin-top:25px;gap:18px}.ugg-page .method-card{background:var(--surface);border:1px solid var(--line);border-radius:14px;color:var(--text)}.ugg-page .highlight-box{background:var(--surface);border:1px solid var(--line);color:var(--text);border-radius:14px}.ugg-page .highlight-box p{color:var(--text)}.ugg-page .content-image.half-width{max-width:min(600px,100%);box-sizing:border-box}.ugg-page .content-image.full-width{max-width:100%;box-sizing:border-box}.ugg-page .teaser-container{max-width:900px;margin:auto}.ugg-page .video-compare-container,.ugg-page .vis-comparison-container{max-width:100%;box-sizing:border-box}.ugg-page .legacy-content h3{color:var(--text)}.ugg-page .legacy-content .table{background:var(--bg);color:var(--text)}.ugg-page .legacy-content .table th,.ugg-page .legacy-content .table td{color:var(--text);border-color:var(--line)}.ugg-page .legacy-content .table thead{background:var(--surface)}.ugg-page .sim-view-controls button{font-family:var(--body)}.ugg-page .demo-video{width:100%;display:block;max-height:620px;background:#000;border-radius:10px}.ugg-page .video-panel{background:var(--surface);padding:16px;border:1px solid var(--line);border-radius:14px}.ugg-page .rdf-frame{max-width:100%;box-sizing:border-box}.ugg-page .legacy-content mjx-container:not([display="true"]){display:inline-block;max-width:100%;overflow-x:auto;overflow-y:hidden;vertical-align:middle}.ugg-page .legacy-content .figure-caption{max-width:900px}.ugg-page .legacy-content .has-text-grey{color:var(--dim)!important}.ugg-page .legacy-content .is-max-desktop>.columns{margin:0}.ugg-page .legacy-content .column{min-width:0}
.ugg-page dialog{border:1px solid var(--line);border-radius:12px;padding:50px 22px 20px;width:max-content;max-width:96vw;max-height:94vh;background:var(--bg);color:var(--text)}.ugg-page dialog::backdrop{background:#10151dd4}.ugg-page dialog img{max-width:90vw;max-height:77vh;display:block;margin:auto;object-fit:contain;background:#fff}.ugg-page dialog .close{position:absolute;top:10px;right:15px;padding:7px 12px;background:var(--surface);color:var(--text);border:1px solid var(--line);border-radius:20px;cursor:pointer}.dialog-caption{font-size:12px;color:var(--dim);max-width:850px;margin:12px auto 0}
@media(max-width:760px){.ugg-top>.ugg-wrap{flex-wrap:wrap;gap:4px 12px;padding-block:9px}.ugg-top .navlinks{order:3;width:100%;flex-basis:100%;margin:0!important}.ugg-top .nav-back{margin-left:auto}.ugg-top .theme-toggle{min-height:32px;padding:5px 9px}.ugg-top .navlinks a{padding:9px!important}.ugg-header{padding-top:47px}.ugg-page .ugg-header h1{max-width:100%;font-size:clamp(33px,6vw,46px)}.ugg-page .ugg-header .authors{font-size:16px}.ugg-page .ugg-header .affil{font-size:14px}.ugg-page section.ugg-section{padding:44px 0}.ugg-page .ugg-section h2{font-size:28px}.ugg-page .steps{grid-template-columns:1fr}.ugg-page .step{padding:20px}.ugg-page .prose{font-size:16px}.ugg-page table.results th,.ugg-page table.results td{padding:11px 8px}.ugg-page table.results{font-size:12px}.ugg-page .legacy-content .table{font-size:12px}.ugg-page .legacy-content .columns{max-width:100%;margin-inline:0}.ugg-page .legacy-content .method-grid{grid-template-columns:1fr}.ugg-page .tldr{font-size:15px}.ugg-page .figbox{padding:10px}.ugg-page .ugg-section figcaption{font-size:11px}.ugg-page .zoom-hint{display:none}.ugg-page .links a{padding:11px 18px}.ugg-page pre{font-size:11px;padding:17px}.ugg-page .legacy-content .rdf-panel,.ugg-page .legacy-content .rdf-panel-body{min-width:0}.ugg-page .legacy-content .table-scroll{max-width:100%;overflow-x:auto}}
@media(max-width:420px){.ugg-wrap{padding-inline:18px}.ugg-page .ugg-header h1{font-size:33px}.ugg-page .ugg-section h2{font-size:26px}.ugg-page .ugg-header .venue{font-size:15px}.ugg-page .focus{padding:22px;font-size:14px;gap:12px}.ugg-top .navlinks a{font-size:12px!important}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}*{transition:none!important;animation:none!important}}
@media print{.ugg-top,.theme-toggle,.links,.copy-button,.ugg-footer,dialog{display:none!important}.ugg-header{background:none;padding-top:0}.ugg-page{color:#000;background:#fff}.ugg-page section.ugg-section{padding:25px 0}.ugg-page figure{break-inside:avoid}.ugg-page .steps{display:block}}
'''
JS=r'''
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
'''
def parse(s):return BeautifulSoup(s,'html.parser')
def text(t):return t.get_text(' ',strip=True) if t else ''
def inner(t):return t.decode_contents() if t else ''
def tag(doc,tag_name,**attrs):return doc.new_tag(tag_name,attrs=attrs)
def load_source(slug):
 path=ROOT/'projects'/slug/'index.html';raw=path.read_text();source=SOURCES/(slug+'.html')
 if 'data-project-template="ugg"' not in raw:
  source.parent.mkdir(parents=True,exist_ok=True);source.write_text(raw)
 elif not source.is_file():raise RuntimeError('Original source missing for '+slug)
 return parse(source.read_text())
def adapt_figure(fig):
 fig=deepcopy(fig)
 if 'figbox' not in fig.get('class',[]):fig['class']=fig.get('class',[])+['figbox']
 for a in fig.select('a:has(img)'):
  if re.search(r'\.(webp|png|jpe?g)(?:\?|$)',a.get('href','')):a['class']=list(dict.fromkeys(a.get('class',[])+['figure-link']))
 return fig

def section(doc,ident,title=None,lede=None,classes=''):
 sec=tag(doc,'section',id=ident,**{'class':'ugg-section '+classes});w=tag(doc,'div',**{'class':'ugg-wrap'});sec.append(w)
 if title:h=tag(doc,'h2');h.string=title;w.append(h)
 if lede:p=tag(doc,'p',**{'class':'lede'});p.string=lede;w.append(p)
 return sec,w

def make_header(doc,slug,title,authors,affil,credit,venue,actions,tldr):
 head=tag(doc,'header',id='paper',**{'class':'ugg-header'});w=tag(doc,'div',**{'class':'ugg-wrap'});head.append(w)
 h=tag(doc,'h1');m=tag(doc,'span',**{'class':'m'});m.string=NAMES[slug];h.append(m);h.append(': '+title);w.append(h)
 for cls,value in [('authors',authors),('affil',affil),('equal',credit)]:
  if value:a=tag(doc,'div',**{'class':cls});a.append(parse(value));w.append(a)
 if venue:p=tag(doc,'p',**{'class':'venue'});p.string=venue;w.append(p)
 links=tag(doc,'div',**{'class':'links'})
 for label,href in actions:
  if not href or href=='#':continue
  a=tag(doc,'a',href=href);a.string=label
  if href.startswith('http'):a['target']='_blank';a['rel']='noopener'
  links.append(a)
 if links.contents:w.append(links)
 if tldr:
  p=tag(doc,'p',**{'class':'tldr'});k=tag(doc,'span',**{'class':'k'});k.string='TL;DR';p.append(k);p.append(parse(tldr));w.append(p)
 return head

def transform_five(doc,source,slug):
 old=source.select_one('header.hero');title=text(old.select_one('.subtitle'));au=[]
 for child in old.select_one('.authors').find_all(['a','span'],recursive=False):c=deepcopy(child);c['class']='au';au.append(str(c))
 actions=[(text(a).replace(' ↗',''),a['href']) for a in old.select('.actions a')]
 brief=deepcopy(source.select_one('main>.tldr'))
 for b in brief.select('strong'):
  if text(b).startswith('TL'):b.decompose()
 header=make_header(doc,slug,title,', '.join(au),inner(old.select_one('.affiliation')),inner(old.select_one('.credit')),text(old.select_one('.status')),actions,inner(brief))
 main=tag(doc,'main',id='main');nav=[]
 for child in source.select_one('main').children:
  if not isinstance(child,Tag) or child.name=='header' or 'statement' in child.get('class',[]) or 'tldr' in child.get('class',[]):continue
  if child.name=='figure':
   sec,w=section(doc,'teaser',classes='hero-teaser');w.append(adapt_figure(child));main.append(sec)
  elif child.name=='section':
   ident=child.get('id','overview');original_title=text(child.find('h2'));title={'overview':'Overview','method':'Method','results':'Results','citation':'BibTeX','materials':'Resources'}.get(ident,original_title)
   sec,w=section(doc,ident,title,original_title if title not in ['Overview','Resources','BibTeX'] else None)
   for c in [x for x in child.children if isinstance(x,Tag)]:
    if c.find('h2'):continue
    if c.name=='figure':w.append(adapt_figure(c));continue
    clone=deepcopy(c)
    if 'copy' in clone.get('class',[]):clone['class']='prose measure'
    if 'citation' in clone.get('class',[]):
     for b in clone.select('[data-copy]'):b['data-copy']='bibtex'
    w.append(clone)
   nav.append((title,ident));main.append(sec)
  else:
   sec,w=section(doc,child.get('id','related' if child.name=='aside' else 'resources-note'));w.append(deepcopy(child));main.append(sec)
 return header,main,nav,[]

def transform_legacy(doc,source,slug):
 scripts=[deepcopy(s) for s in source.find_all('script')];nav=[];main=tag(doc,'main',id='main')
 if slug=='sandbox':
  header=make_header(doc,slug,text(source.select_one('h1')),inner(source.select_one('.publication-authors')),'','','Working draft · Under review',[('Interactive 4D','#rdf-single-view'),('Robot demos','#sim2real'),('BibTeX','#BibTeX')],'Explicit 4D prediction connects visual imagination to robot control, guiding actions and checking geometric agreement before execution.')
  teaser=source.select_one('section.teaser');sec,w=section(doc,'teaser',classes='hero-teaser');wrap=tag(doc,'div',**{'class':'legacy-content figbox'});wrap.append(deepcopy(teaser.select_one('.hero-body')));w.append(wrap);main.append(sec)
  ids=['abstract','method','results','rdf-single-view','sim2real','BibTeX'];labels=['Abstract','Method','Results','Interactive 4D','Sim-to-real','BibTeX']
  originals=[s for s in source.find_all('section') if 'section' in s.get('class',[])]
  if len(originals)!=6:raise RuntimeError('Unexpected SANDBOX structure; inspect original before migrating')
  for old,ident,label in zip(originals,ids,labels):
   sec,w=section(doc,ident,classes='legacy-section');content=tag(doc,'div',**{'class':'legacy-content'})
   for c in old.children:
    if isinstance(c,Tag):content.append(deepcopy(c))
   for h in content.select('h2'):h['class']=''
   for table in content.select('table'):
    if not table.find_parent(class_='mirror-table-scroll'):
     wrap=tag(doc,'div',**{'class':'mirror-table-scroll','tabindex':'0','role':'region','aria-label':'Scrollable research result table'});table.wrap(wrap)
   w.append(content);main.append(sec);nav.append((label,ident))
  cover=source.select_one('#cover-video')
  if cover:
   sec,w=section(doc,'cover','Robot demonstration','Stack Cups under moving coloured lighting · 10× speed');video=deepcopy(cover);video['class']='demo-video';video['controls']='';video['preload']='metadata';video.attrs.pop('autoplay',None);panel=tag(doc,'div',**{'class':'video-panel'});panel.append(video);w.append(panel);main.find('section',id='sim2real').insert_after(sec)
  scripts=[s for s in scripts if 'Cover video: fade in' not in s.get_text()]
 else:
  old=source.find('header');title=re.sub(r'^EAG3R:\s*','',text(old.find('h1')));actions=[(text(a),a['href']) for a in old.select('.links a') if a.get('href')!='#'];authors=deepcopy(old.select_one('.authors'))
  for a in authors.find_all('a',href='#'):
   if text(a)=='Xiaoshan Wu':a['href']='../../about.html'
   else:a.unwrap()
  header=make_header(doc,slug,title,inner(authors),inner(old.select_one('.affiliations')),inner(old.select_one('.equal-contribution')),text(old.select_one('.venue')),actions,'Event-augmented geometry estimation for dynamic scenes and challenging illumination.')
  ids=['teaser','abstract','method','results','citation'];labels=['Teaser','Abstract','Method','Results','BibTeX'];originals=source.find_all('section')
  if len(originals)!=5:raise RuntimeError('Unexpected EAG3R section structure')
  for old,ident,label in zip(originals,ids,labels):
   sec,w=section(doc,ident,classes='hero-teaser' if ident=='teaser' else 'legacy-section');content=tag(doc,'div',**{'class':'legacy-content'})
   for c in old.children:
    if isinstance(c,Tag):content.append(deepcopy(c))
   for h in content.select('h2'):h['class']=''
   w.append(content);main.append(sec)
   if ident!='teaser':nav.append((label,ident))
 for sec in main.select('section'):
  pre=sec.find('pre')
  if pre and pre.find('code'):
   pre.find('code')['id']='bibtex';row=tag(doc,'div',**{'class':'citation-tools'});b=tag(doc,'button',type='button',**{'class':'copy-button','data-copy':'bibtex'});b.string='Copy BibTeX';row.append(b);st=tag(doc,'span',id='copy-status',role='status',**{'class':'copy-status','aria-live':'polite'});row.append(st);pre.insert_before(row)
 return header,main,nav,scripts

def build(slug):
 source=load_source(slug);doc=parse('<!doctype html><html lang="en"><head></head><body></body></html>');doc.html['data-project-template']='ugg';doc.body['class']='ugg-page';doc.body['id']='top';doc.body['data-project']=slug
 for t in source.head.find_all(['meta','title'],recursive=False):
  if t.name=='meta' and t.get('name')=='color-scheme':continue
  doc.head.append(deepcopy(t))
 if not doc.head.find('meta',attrs={'name':'viewport'}):doc.head.append(tag(doc,'meta',name='viewport',content='width=device-width,initial-scale=1'))
 doc.head.append(tag(doc,'meta',name='color-scheme',content='light dark'));doc.head.append(tag(doc,'meta',name='project-template',content=VERSION));doc.head.append(tag(doc,'link',rel='canonical',href=f'https://candy-crusher.github.io/xiaoshanwu.github.io/projects/{slug}/'))
 if slug in ('sandbox','eag3r'):
  for link in source.head.select('link[rel="stylesheet"]'):
   if 'fonts.googleapis.com' not in link.get('href',''):doc.head.append(deepcopy(link))
  for style in source.head.find_all('style'):
   if style.get('id')!='mirror-compatibility':doc.head.append(deepcopy(style))
 doc.head.append(tag(doc,'link',rel='preconnect',href='https://fonts.googleapis.com'));doc.head.append(tag(doc,'link',rel='stylesheet',href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap'));doc.head.append(tag(doc,'link',rel='stylesheet',href=f'../assets/ugg-template.css?v={VERSION}'))
 early=tag(doc,'script');early.string="try{const t=localStorage.getItem('research-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(_){}";doc.head.append(early)
 header,main,nav,scripts=transform_legacy(doc,source,slug) if slug in ('sandbox','eag3r') else transform_five(doc,source,slug)
 skip=tag(doc,'a',href='#main',**{'class':'skip-link'});skip.string='Skip to content';doc.body.append(skip)
 top=tag(doc,'nav',**{'class':'ugg-top','aria-label':'Project navigation'});w=tag(doc,'div',**{'class':'ugg-wrap'});top.append(w);brand=tag(doc,'a',href='#top',**{'class':'brand'});brand.string=NAMES[slug];w.append(brand);links=tag(doc,'div',**{'class':'navlinks'})
 for label,ident in nav:a=tag(doc,'a',href='#'+ident);a.string=label;links.append(a)
 w.append(links);back=tag(doc,'a',href='../../research.html#projects',**{'class':'nav-back'});back.string='← Research';w.append(back);theme=tag(doc,'button',type='button',**{'class':'theme-toggle','aria-label':'Switch color theme'});theme.string='◐';w.append(theme)
 doc.body.append(top);doc.body.append(header);doc.body.append(main)
 footer=tag(doc,'footer',**{'class':'ugg-footer'});fw=tag(doc,'div',**{'class':'ugg-wrap'});footer.append(fw);p=tag(doc,'p');p.string=NAMES[slug]+' · Research project';fw.append(p);n=tag(doc,'nav',**{'class':'project-links','aria-label':'Other research projects'})
 for s in SLUGS:
  a=tag(doc,'a',href='../'+s+'/');a.string=NAMES[s]
  if s==slug:a['aria-current']='page'
  n.append(a)
 fw.append(n);p=tag(doc,'p');p.append(parse('<a href="../../">Home</a> · <a href="../../about.html">About</a> · <a href="../../resume.html">Resume</a> · <a href="../../research.html">Research</a>'));fw.append(p);p=tag(doc,'p',**{'class':'fine'});p.append(parse('Layout adapted from <a href="https://github.com/sky-lzy/UGG-website">UGG</a> and <a href="https://github.com/mose3-tracker/mose3-tracker.github.io">MoSE3</a>. Figures and results belong to their respective authors.'));fw.append(p);doc.body.append(footer)
 modal=tag(doc,'dialog',id='figure-dialog',**{'aria-label':'Enlarged original research figure'});b=tag(doc,'button',type='button',**{'class':'close'});b.string='Close ×';modal.append(b);modal.append(tag(doc,'img',alt=''));modal.append(tag(doc,'p',**{'class':'dialog-caption'}));doc.body.append(modal)
 for s in scripts:doc.body.append(s)
 doc.body.append(tag(doc,'script',src=f'../assets/ugg-template.js?v={VERSION}',defer=''))
 return str(doc)

def main():
 assets=ROOT/'projects/assets';assets.mkdir(parents=True,exist_ok=True);(assets/'ugg-template.css').write_text(CSS);(assets/'ugg-template.js').write_text(JS)
 manifest={'template':SOURCE_REF,'version':VERSION,'scope':list(SLUGS),'notes':['Imports presentation only; no UGG research media or paper text.','Original media, interactive viewer files and personal-site pages are preserved.'],'pages':{}}
 for slug in SLUGS:
  output=build(slug);(ROOT/'projects'/slug/'index.html').write_text(output);manifest['pages'][slug]={'source_sha256':hashlib.sha256((SOURCES/(slug+'.html')).read_bytes()).hexdigest(),'html_sha256':hashlib.sha256(output.encode()).hexdigest()}
 (assets/'ugg-template-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (SOURCES/'README.md').write_text('# Research-page sources\n\nPre-UGG HTML for the seven existing project pages, retained for editing and rollback. This directory contains only the user\'s existing project content, not UGG media or manuscript text.\n\nFor the five generated pages, edit scripts/build-project-pages.py and run the existing project workflow. The finalization step reapplies the selected template after integrating figures. For SANDBOX/EAG3R, edit the respective snapshot or explicitly recopy the original site. All old project and 4D-viewer URLs remain unchanged.\n')
 print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
