#!/usr/bin/env python3
"""Build the four personal-site pages without changing project research content.

The first run preserves the existing homepage sections and publication record in
_site_content/personal-site.json. Later runs read that editable source, rather
than trying to recover content from the new, shorter homepage. Existing project
URLs and the CV PDF stay unchanged. No network requests are made by this builder.
"""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import html,json,re
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE='https://candy-crusher.github.io/xiaoshanwu.github.io/'
DATA=ROOT/'_site_content/personal-site.json'
VERSION='20261012-four-pages'
PAGES=[('home','index.html','Home'),('about','about.html','About'),('resume','resume.html','Resume'),('research','research.html','Research')]
SLUGS=['sandbox','game','videossm','eag3r','lifr-seg','lifr-v2','evsplat']
PUBIDS={'sandbox':'world-action-model',**{s:s for s in SLUGS if s!='sandbox'}}
NAMES={'sandbox':'S4NDBOX','game':'GaMe','videossm':'VideoSSM','eag3r':'EAG3R','lifr-seg':'LiFR-Seg','lifr-v2':'LiFR v2','evsplat':'EVSplat'}
CSS=r'''
/* Information architecture: one shared navigation, four distinct page roles. */
html{scroll-padding-top:108px;scroll-behavior:smooth}.site-layout{--paper:#fbfaf7;--accent:#355f68}.site-layout .wrap{width:min(1120px,100%);padding-inline:40px}.site-topbar{position:sticky;top:0;z-index:40;background:rgba(251,250,247,.97);border-bottom:1px solid var(--line)}.site-topbar .site-header{min-height:78px;padding-block:17px}.site-layout .site-nav{gap:29px}.site-layout .site-nav a{font-size:11px;text-transform:uppercase;letter-spacing:.10em;white-space:nowrap}.site-layout .site-nav a[aria-current=page]{text-decoration:underline;text-underline-offset:8px;text-decoration-thickness:1px}.site-layout .hero-navigation .site-nav a[aria-current=page]{color:#fff}.site-layout .hero-navigation.is-scrolled .site-nav a[aria-current=page]{color:var(--ink)}.site-layout .hero-navigation{z-index:40}.site-layout .skip-link{z-index:60}.site-layout main{min-height:45vh}.page-heading{padding:65px 0 38px;border-bottom:1px solid var(--line);margin-bottom:42px}.page-label{display:block;font-size:11px;color:var(--accent);letter-spacing:.14em;text-transform:uppercase;margin-bottom:16px}.page-heading h1{font:58px/1.08 var(--serif);letter-spacing:-1.8px}.page-heading>p{max-width:680px;font-size:17px;color:var(--muted);line-height:1.75;margin-top:18px}.page-heading .inline-links{margin-top:22px}.inline-links{display:flex;gap:12px 25px;flex-wrap:wrap;align-items:center;font-size:13px}.text-link{text-decoration:underline;text-decoration-color:#b8c6c5}.action-link{display:inline-flex;align-items:center;gap:14px;padding:11px 20px;border:1px solid var(--ink);background:var(--ink);color:var(--paper);font-size:13px;border-radius:2px}.action-link:hover{background:var(--accent);border-color:var(--accent);color:#fff;text-decoration:none}.action-link.secondary{background:none;color:var(--ink);border-color:var(--line)}.section-label{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}.section-lead{font:31px/1.35 var(--serif);letter-spacing:-.5px}.section-body{font-size:16px;line-height:1.85;color:#4d5759}.section-body p+p{margin-top:18px}.site-layout .site-footer{margin-top:72px;font-size:12px;padding-block:24px 32px}.site-layout .site-footer::before{left:40px;right:40px}.site-layout .site-footer>div{flex-wrap:wrap;gap:12px 22px}.site-layout .site-footer a[aria-current=page]{color:var(--accent)}
/* Home: cover, a short introduction, three highlights, recent updates. */
.home-intro{display:grid;grid-template-columns:1fr 1.1fr;gap:64px;padding:60px 0;border-bottom:1px solid var(--line)}.home-intro .section-lead{font-size:33px;max-width:430px}.home-intro .section-body{font-size:15px}.home-intro .inline-links{margin-top:23px}.home-highlights{padding:45px 0 0}.home-highlights .section-heading h2{font-size:28px}.home-highlights .section-heading>a{font-size:13px}.highlight-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:27px;margin-top:27px}.highlight-item{display:block;color:var(--ink);min-width:0}.highlight-item:hover{text-decoration:none}.highlight-image{height:150px;background:#fff;border:1px solid var(--line);padding:12px;display:flex;align-items:center;justify-content:center;margin-bottom:17px}.highlight-image img{max-height:100%;width:100%;object-fit:contain;display:block}.highlight-item .section-label{font-size:10px;margin-bottom:7px}.highlight-item h3{font:23px/1.3 var(--serif);margin-bottom:8px}.highlight-item>p{font-size:13px;line-height:1.75;color:var(--muted)}.highlight-item .read-more{display:inline-block;font-size:12px;color:var(--accent);margin-top:13px;text-decoration:underline;text-underline-offset:4px}.site-layout .news-section{margin-top:47px;padding-top:34px;border-top:1px solid var(--line)}.site-layout .news{font-size:13px;grid-template-columns:46px 1fr;gap:13px 25px}.home-cover-credit{font-size:10px;color:var(--muted);margin-top:22px;text-align:right}.home-cover-credit a{color:inherit}
/* About: the person and the long-term question, not another CV. */
.about-profile{display:grid;grid-template-columns:minmax(0,1fr) 235px;gap:75px;align-items:start}.about-profile .section-lead{max-width:650px;margin-bottom:24px}.about-profile .section-body{max-width:670px}.about-portrait img{display:block;width:235px;height:318px;object-fit:cover;object-position:center 55%;border-radius:2px}.about-portrait figcaption{font-size:12px;color:var(--muted);margin-top:12px}.about-profile .inline-links{margin-top:26px}.editorial-section{display:grid;grid-template-columns:235px minmax(0,1fr);gap:60px;margin-top:53px;padding-top:38px;border-top:1px solid var(--line)}.editorial-section h2{font-size:27px}.editorial-section .section-body{max-width:690px}.future-note{margin-top:28px;padding-left:21px;border-left:2px solid #a9bfc1}.future-note .section-label{color:var(--accent);margin-bottom:9px}.inspiration-image{width:100%;max-height:325px;object-fit:cover;object-position:50% 45%;margin-top:24px;border-radius:2px}.image-credit{font-size:11px;color:var(--muted);line-height:1.7;margin-top:11px}.about-contact{margin-top:35px;font-size:14px}
/* Resume: the downloadable document and a scannable academic record. */
.cv-download{display:flex;align-items:center;justify-content:space-between;gap:25px;padding:25px 29px;background:#eef1ed;border:1px solid #dce2da;margin-bottom:44px}.cv-download h2{font:25px/1.3 var(--serif);margin:0 0 6px}.cv-download p{font-size:13px;color:var(--muted)}.cv-download .inline-links{gap:12px}.resume-section{display:grid;grid-template-columns:235px minmax(0,1fr);gap:60px;padding:32px 0;border-top:1px solid var(--line)}.resume-section>h2{font-size:26px}.resume-section .experience-row{font-size:14px;gap:15px;line-height:1.8;margin:0 0 26px;grid-template-columns:minmax(0,1fr) auto}.resume-section .experience-row:last-child{margin-bottom:0}.resume-section .experience-row strong{font-size:16px}.resume-section .experience-row .detail{font-size:13px}.resume-section .experience-row .dates{font-size:12px;white-space:nowrap}.resume-section .awards{grid-template-columns:1fr;gap:11px;font-size:14px;list-style:none}.resume-section .skill-list{font-size:15px;line-height:1.9;color:var(--muted)}.resume-section p{font-size:14px;color:var(--muted)}
/* Research: all seven projects, then one expandable publication record. */
.research-summary-top{max-width:810px;color:var(--muted);font-size:16px;line-height:1.85;margin-bottom:29px}.research-subnav{display:flex;flex-wrap:wrap;gap:23px;font-size:13px;margin-bottom:35px}.research-subnav a{text-decoration:underline;text-decoration-color:#c1cecb}.project-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:40px}.site-layout .project-grid .research-entry{display:flex;flex-direction:column;gap:19px;padding:30px 0 31px;border-top:1px solid var(--line);border-bottom:0;min-width:0;scroll-margin-top:110px}.project-grid .research-visual{width:100%;padding:0;margin:0}.project-grid .figure-preview{height:205px;min-height:0;padding:15px;border:1px solid #e4e6df}.project-grid .figure-preview img{width:100%;height:100%;max-height:100%;object-fit:contain}.project-grid .research-visual figcaption{font-size:10.5px}.project-grid .research-copy{flex:1;width:100%;display:flex;flex-direction:column}.project-grid .project-name{font-size:11px;text-transform:uppercase;letter-spacing:.10em;color:var(--accent);margin-bottom:9px}.project-grid .research-copy h3{font:24px/1.3 var(--serif);letter-spacing:-.45px;margin-bottom:12px}.project-grid .research-copy h3 a{color:var(--ink)}.project-grid .research-authors{font-size:12px}.project-grid .research-meta{font-size:12px;line-height:1.75;margin:5px 0 13px;gap:2px 12px}.project-grid .research-meta>span+span::before{margin-right:12px}.project-grid .research-summary{font-size:14px;line-height:1.8;margin-bottom:13px}.project-grid .research-links{margin-top:auto;padding-top:7px;font-size:12px;gap:8px 18px}.project-grid .research-links a{padding-block:5px}.project-identity{min-height:205px;padding:30px;background:#eff0ed;border:1px solid #e4e6df;display:flex;flex-direction:column;justify-content:center}.project-identity strong{font:41px/1.2 var(--serif);font-weight:400;letter-spacing:-1px}.project-identity span{font-size:13px;color:var(--muted);margin-top:13px;max-width:260px}.publication-archive{margin-top:40px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:28px 0;scroll-margin-top:100px}.publication-archive>summary{cursor:pointer;font:29px/1.35 var(--serif);list-style-position:inside;color:var(--ink)}.publication-archive>summary .archive-caption{display:block;font:13px/1.7 var(--sans);color:var(--muted);margin:8px 0 0 25px}.publication-archive[open]>summary{margin-bottom:32px}.publication-archive .publication-group{margin-top:32px}.publication-archive .publication-list li{scroll-margin-top:110px}.publication-archive .pub-title{font-size:15px}.publication-archive .pub-authors{font-size:13px}.publication-archive .paper-links{display:inline-flex;gap:12px}.publication-archive .section-note{margin:0;font-size:12px}.site-layout .figure-dialog{z-index:80}.site-layout .figure-dialog-image{max-width:100%;height:auto}
@media(max-width:850px){.site-layout .wrap{padding-inline:30px}.home-intro{gap:32px}.about-profile{grid-template-columns:minmax(0,1fr) 185px;gap:35px}.about-portrait img{width:185px;height:260px}.editorial-section,.resume-section{grid-template-columns:185px minmax(0,1fr);gap:32px}.resume-section .experience-row{grid-template-columns:1fr;gap:5px}.resume-section .experience-row .dates{text-align:left}.cv-download{flex-wrap:wrap}.project-grid{column-gap:28px}.highlight-grid{gap:20px}.highlight-image{height:125px}.site-layout .site-footer::before{left:30px;right:30px}}
@media(max-width:600px){html{scroll-padding-top:116px}.site-layout .wrap{padding-inline:23px}.site-topbar .site-header{gap:8px;padding-block:14px 9px;flex-wrap:wrap}.site-layout .site-nav{gap:25px;flex-basis:100%;width:100%}.site-layout .site-nav a{font-size:10px;letter-spacing:.065em;padding-block:7px}.page-heading{padding:37px 0 28px;margin-bottom:31px}.page-heading h1{font-size:44px;letter-spacing:-1.1px}.page-heading>p{font-size:15px;margin-top:15px}.page-label{font-size:10px;margin-bottom:13px}.home-intro{grid-template-columns:1fr;gap:22px;padding:39px 0}.home-intro .section-lead{font-size:29px}.home-intro .section-body{font-size:14px}.highlight-grid{grid-template-columns:1fr;gap:25px}.highlight-item{display:grid;grid-template-columns:115px minmax(0,1fr);column-gap:19px}.highlight-image{grid-row:1/span 4;height:110px;margin:0;padding:8px}.highlight-item .section-label{font-size:9px}.highlight-item h3{font-size:22px}.highlight-item>p{grid-column:2;font-size:12px}.highlight-item .read-more{grid-column:2;margin-top:7px}.home-highlights{padding-top:32px}.home-highlights .section-heading{gap:11px}.site-layout .news{grid-template-columns:34px 1fr;gap:12px 14px;font-size:12px}.site-layout .news-section{margin-top:34px}.about-profile{grid-template-columns:1fr;gap:28px}.about-portrait{display:flex;align-items:flex-end;gap:20px}.about-portrait img{width:140px;height:190px}.about-portrait figcaption{max-width:170px;font-size:11px}.about-profile .section-lead{font-size:29px}.section-body{font-size:14px}.editorial-section,.resume-section{grid-template-columns:1fr;gap:23px;margin-top:35px;padding-top:29px}.resume-section{margin-top:0;padding-bottom:29px}.editorial-section h2,.resume-section>h2{font-size:26px}.inspiration-image{max-height:210px}.cv-download{padding:22px;gap:19px;margin-bottom:28px}.cv-download .inline-links{gap:11px}.action-link{padding:10px 15px;font-size:12px}.resume-section .experience-row strong{font-size:15px}.resume-section .awards{font-size:13px}.research-summary-top{font-size:14px}.research-subnav{gap:17px;font-size:12px}.project-grid{grid-template-columns:1fr}.site-layout .project-grid .research-entry{gap:18px;padding:25px 0}.project-grid .figure-preview{height:200px}.project-grid .research-copy h3{font-size:24px}.project-grid .research-summary{font-size:13.5px}.project-grid .research-meta{font-size:11.5px}.publication-archive>summary{font-size:26px}.publication-archive>summary .archive-caption{font-size:12px}.site-layout .site-footer{margin-top:43px;font-size:11px;gap:16px}.site-layout .site-footer::before{left:23px;right:23px}.site-layout .site-footer>div{gap:12px 21px}.home-cover-credit{text-align:left}}
@media(max-width:360px){.site-layout .site-nav{gap:18px}.highlight-item{grid-template-columns:100px minmax(0,1fr);gap:12px}.site-layout .wrap{padding-inline:20px}.site-layout .site-footer::before{left:20px;right:20px}.project-grid .figure-preview{height:174px}.about-portrait img{width:120px;height:168px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}}
@media print{.site-topbar,.inline-links,.site-footer,.research-subnav,.hero-navigation{display:none!important}.site-layout .wrap{width:100%;padding:0}.page-heading{padding-top:0}.page-heading h1{font-size:32px}.resume-section{break-inside:avoid}.project-grid{display:block}.research-entry{break-inside:avoid}.cv-download{background:none}.site-layout .cinematic-shell{height:auto;min-height:0}}
'''
JS=r'''
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
'''

def soup(text):return BeautifulSoup(text,'html.parser')
def esc(value):return html.escape(str(value),quote=True)
def seed():
    if DATA.is_file():return json.loads(DATA.read_text())
    old=soup((ROOT/'index.html').read_text());pub=soup((ROOT/'publications.html').read_text())
    required=['.cinematic-shell','.bio-compact','.direction-intro','.direction-pair','.experience-row','.news','#inspiration']
    for selector in required:
        if old.select_one(selector) is None:raise RuntimeError('Cannot safely migrate missing source section: '+selector)
    groups=pub.select('.publication-group')
    if not groups:raise RuntimeError('Original publication groups not found')
    data={'version':1,'hero':str(old.select_one('.cinematic-shell')),'bio':str(old.select_one('.bio-compact')),'direction':str(old.select_one('.direction-intro')),'foundation':str(old.select_one('#agent-heading').find_next_sibling('p')),'future':str(old.select_one('#model-heading').find_next_sibling('p')),'experience':[str(x) for x in old.select('.experience-row')],'awards':str(old.select_one('.awards')),'news':str(old.select_one('.news')),'inspiration':str(old.select_one('#inspiration')),'publications':[str(g) for g in groups],'publication_note':str(pub.select_one('main .section-note')),'research':[str(a) for a in old.select('article.research-entry')]}
    DATA.parent.mkdir(parents=True,exist_ok=True);DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return data

def nav(page,prefix=''):
    return ''.join(f'<a href="{prefix+file}"'+(' aria-current="page"' if key==page else '')+f'>{label}</a>' for key,file,label in PAGES)
def header(page):
    mark='<a class="wordmark" href="index.html" aria-label="Xiaoshan Wu, Home">Xiaoshan Wu<span lang="zh" aria-hidden="true">小山</span></a>'
    links='<nav class="site-nav" aria-label="Main navigation">'+nav(page)+'</nav>'
    if page=='home':return '<header class="hero-navigation"><div class="header-inner">'+mark+links+'</div></header>'
    return '<header class="site-topbar"><div class="site-header wrap">'+mark+links+'</div></header>'
def footer(page):
    return '<footer class="site-footer wrap"><span>© 2026 Xiaoshan Wu</span><div>'+nav(page)+'<a href="mailto:wuxiaoshan630@gmail.com">Email ↗</a></div></footer>'
def document(page,body,description,hero=''):
    title='Xiaoshan Wu | Spatial Intelligence for Physical Agents' if page=='home' else page.title()+' | Xiaoshan Wu'
    canonical=BASE+('' if page=='home' else page+'.html')
    extra=''
    if page=='home':extra='<link rel="stylesheet" href="assets/css/shared-world.css?v=20261010"><link rel="stylesheet" href="assets/css/hero-hd.css?v=20261010-hd"><script defer src="assets/js/hero-hd.js?v=20261010-hd"></script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="Xiaoshan Wu"><meta name="color-scheme" content="light"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website"><link rel="stylesheet" href="assets/css/editorial.css?v=20261010">{extra}<link rel="stylesheet" href="assets/css/site-pages.css?v={VERSION}"><script defer src="assets/js/editorial.js?v=20261010"></script><script defer src="assets/js/site-pages.js?v={VERSION}"></script></head>
<body class="site-layout" data-page="{page}" id="top"><a class="skip-link" href="#main">Skip to content</a>{header(page)}{hero}<main class="wrap" id="main">{body}</main>{footer(page)}{figure_dialog() if page=='research' else ''}</body></html>'''
def figure_dialog():
    return '<dialog class="figure-dialog" id="research-figure" aria-labelledby="figure-title" aria-describedby="figure-caption"><div class="figure-dialog-bar"><p id="figure-title">Research figure</p><button class="figure-close" type="button" aria-label="Close figure">Close <span aria-hidden="true">×</span></button></div><img class="figure-dialog-image" alt=""><p class="figure-dialog-caption" id="figure-caption"></p></dialog>'
def heading(label,title,subtitle,links=''):
    return f'<header class="page-heading"><span class="page-label">{label}</span><h1>{title}</h1><p>{subtitle}</p>{links}</header>'
def paragraph(fragment):
    doc=soup(fragment)
    return ''.join(str(x) for x in doc.find('p').contents)
def update_links(fragment):
    doc=soup(fragment)
    for a in doc.select('a[href]'):
        href=a['href']
        if href.startswith('publications.html'):a['href']='research.html'+(href.split('publications.html',1)[1] or '#publications')
        if href.startswith('index.html#background'):a['href']='resume.html#background'
        if href.startswith('index.html#selected-research'):a['href']='research.html#selected-research'
    return str(doc)

def record(data,slug):
    return soup(''.join(data['publications'])).find(id='pub-'+PUBIDS[slug])
def research_article(data,slug):
    original=next((x for x in data['research'] if 'id="selected-'+PUBIDS[slug]+'"' in x),None)
    if original:doc=soup(update_links(original));article=doc.find('article')
    else:
        pub=record(data,slug)
        if pub is None:raise RuntimeError('Missing publication identity '+slug)
        title=pub.select_one('.pub-title').get_text(' ',strip=True)
        authors=pub.select_one('.pub-authors').decode_contents()
        venue=pub.select_one('.paper-venue').decode_contents();role=pub.select_one('.pub-role').decode_contents()
        project=soup((ROOT/'projects'/slug/'index.html').read_text())
        text=project.select_one('.tldr');tldr=text.get_text(' ',strip=True).removeprefix('TL;DR').strip() if text else ''
        paper=''.join(str(a) for a in pub.select('.paper-links a') if a.get_text(strip=True).lower()!='project')
        media='<div class="project-identity"><strong>EVSplat</strong><span>Uncertainty-aware reconstruction of dynamic scenes.</span></div>'
        if slug=='lifr-v2':media='<figure class="research-visual"><a class="figure-preview" href="projects/lifr-v2/assets/teaser-hd.webp" data-figure data-caption="Original LiFR v2 teaser from the project repository."><img src="projects/lifr-v2/assets/teaser.webp" alt="LiFR v2: propagate, complete and retain interframe evidence" loading="lazy" decoding="async"><span class="figure-expand" aria-hidden="true">↗</span></a><figcaption>Causal, high-rate dense prediction</figcaption></figure>'
        doc=soup(f'<article class="research-entry" id="selected-{PUBIDS[slug]}">{media}<div class="research-copy"><h3>{esc(title)}</h3><p class="research-authors">{authors}</p><p class="research-meta"><span>{venue}</span><span>{role}</span></p><p class="research-summary">{esc(tldr)}</p><nav class="research-links" aria-label="{esc(NAMES[slug])} resources"><a href="projects/{slug}/">Project</a>{paper}</nav></div></article>');article=doc.article
    # Use the original HD assets already imported during the project-page work.
    source={'game':('projects/game/assets/teaser.webp','projects/game/assets/teaser-hd.webp'),'videossm':('projects/videossm/assets/overview.webp','projects/videossm/assets/overview-hd.webp'),'lifr-seg':('projects/lifr-seg/assets/teaser.webp','projects/lifr-seg/assets/teaser-hd.webp')}.get(slug)
    if source and article.select_one('.research-visual img'):
        im=article.select_one('.research-visual img');im['src']=source[0]
        im.attrs.pop('width',None);im.attrs.pop('height',None)
        im.find_parent('a')['href']=source[1]
    for old in article.select('.research-result'):old.decompose()
    h=article.find('h3');label=doc.new_tag('p');label['class']='project-name';label.string=NAMES[slug];h.insert_before(label)
    title=h.get_text(' ',strip=True)
    if title.startswith(NAMES[slug]+':'):title=title[len(NAMES[slug])+1:].strip()
    h.clear();a=doc.new_tag('a',href=f'projects/{slug}/');a.string=title;h.append(a)
    if slug=='sandbox':article.select_one('.research-summary').string='Explicit 4D prediction connects visual imagination to robot control, guiding action generation and checking geometric agreement before execution.'
    for a in article.select('.research-links a'):
        if a.get_text(strip=True)=='Details':a.decompose();continue
        if a['href'].startswith('projects/'):
            a.attrs.pop('target',None);a.attrs.pop('rel',None)
    return str(article)

def build_home(data):
    hero=soup(data['hero']);hero.select_one('.scroll-cue')['href']='#welcome'
    hero.select_one('.scroll-cue').contents[-1].replace_with('A brief introduction')
    hero.select_one('.inspiration-link')['href']='about.html#inspiration'
    for a in hero.select('.hero-links a'):
        if 'CV' in a.get_text():a['href']='resume.html';a.string='Resume';a.attrs.pop('target',None);a.attrs.pop('rel',None)
    items=[]
    highlight_data=[('sandbox','World models & action','4D futures that connect visual prediction with robot control.','images/research/s4ndbox-overview.webp'),('game','Spatial reasoning','Geometric working memory for reasoning across multiple views.','projects/game/assets/teaser.webp'),('eag3r','Robust world understanding','Recovering scene geometry in motion and challenging light.','images/research/eag3r-night-depth.webp')]
    for slug,area,text,image in highlight_data:
        items.append(f'<a class="highlight-item" href="projects/{slug}/"><div class="highlight-image"><img src="{image}" alt="{esc(NAMES[slug])} project figure" loading="lazy" decoding="async"></div><div class="section-label">{esc(area)}</div><h3>{NAMES[slug]}</h3><p>{text}</p><span class="read-more">View project ↗</span></a>')
    body=f'''<section class="home-intro" id="welcome" aria-labelledby="welcome-title"><div><p class="section-label">Hello, I’m Xiaoshan.</p><h2 class="section-lead" id="welcome-title">Understanding the physical world.<br>Acting beyond the familiar.</h2></div><div class="section-body"><p>I am a Ph.D. candidate at the University of Hong Kong, advised by <a href="https://xjqi.github.io/">Prof. Xiaojuan Qi</a>.</p><p>I study spatial intelligence for physical agents: how a coherent understanding of the world can support reliable action in unfamiliar environments.</p><div class="inline-links"><a class="text-link" href="about.html">About me →</a><a class="text-link" href="research.html">Explore my research →</a></div></div></section><section class="home-highlights" aria-labelledby="highlights-title"><div class="section-heading"><h2 id="highlights-title">A few recent projects</h2><a href="research.html#projects">All seven projects →</a></div><div class="highlight-grid">{''.join(items)}</div></section><section class="news-section" aria-labelledby="news"><h2 id="news">Recent updates</h2>{update_links(data['news'])}</section><p class="home-cover-credit">Cover: <cite>Blade Runner 2049</cite>. <a href="about.html#inspiration">The inspiration behind it ↗</a></p>'''
    return document('home',body,'Xiaoshan Wu — spatial intelligence for physical agents, world understanding and reliable action.',str(hero))

def build_about(data):
    inspiration=soup(data['inspiration']);copy=inspiration.find_all('p')[1].decode_contents();credit=inspiration.select_one('.image-credit').decode_contents()
    body=heading('The person & the perspective','About','A coherent understanding of the world, in service of meaningful action.')
    body+=f'''<section class="about-profile" aria-labelledby="about-name"><div><h2 class="section-lead" id="about-name">I’m Xiaoshan Wu <span lang="zh">（吴小山）</span>.</h2><div class="section-body"><p>{paragraph(data['bio'])}</p><p>I received my dual bachelor’s degrees in Computer Engineering from Zhejiang University and the University of Illinois Urbana-Champaign through the ZJUI Institute.</p></div><div class="inline-links"><a class="text-link" href="resume.html">Education & experience →</a><a class="text-link" href="mailto:wuxiaoshan630@gmail.com">Email ↗</a></div></div><figure class="about-portrait"><img src="images/research/profile.webp" alt="Xiaoshan Wu" width="235" height="318" decoding="async"><figcaption>Xiaoshan Wu<br>Ph.D. candidate · HKU</figcaption></figure></section><section class="editorial-section" aria-labelledby="perspective"><h2 id="perspective">Research perspective</h2><div class="section-body"><p>{paragraph(data['direction'])}</p><p>{paragraph(data['foundation'])}</p><div class="future-note"><p class="section-label">Looking ahead</p><p>{paragraph(data['future'])}</p></div><div class="inline-links" style="margin-top:25px"><a class="text-link" href="research.html">Projects & publications →</a></div></div></section><section class="editorial-section" id="inspiration" aria-labelledby="inspiration-title"><h2 id="inspiration-title">A personal inspiration</h2><div class="section-body"><p>{copy}</p><img class="inspiration-image" src="images/theme/shared-world-1440.webp" alt="Joi and K in a scene from Blade Runner 2049" loading="lazy" decoding="async"><p class="image-credit">{credit}</p></div></section>'''
    return document('about',body,'About Xiaoshan Wu: background, research perspective, and the inspiration behind physical agents that share our world.')

def build_resume(data):
    edu=[];vis=[]
    for raw in data['experience']:
        if 'Harvard University' in soup(raw).get_text():vis.append(raw)
        else:edu.append(raw)
    body=heading('Academic background','Resume','Education, research experience, and selected honors. The full publication record is on the Research page.')
    body+='''<section class="cv-download" aria-labelledby="cv-title"><div><h2 id="cv-title">Curriculum vitae</h2><p>The full academic CV, including publications and technical skills.</p></div><div class="inline-links"><a class="action-link" href="Xiaoshan_Wu_CV.pdf" target="_blank" rel="noopener">View CV <span aria-hidden="true">↗</span></a><a class="action-link secondary" href="Xiaoshan_Wu_CV.pdf" download="Xiaoshan_Wu_CV.pdf">Download PDF ↓</a></div></section>'''
    body+='<div id="background"><section class="resume-section" id="education"><h2>Education</h2><div>'+''.join(edu)+'</div></section><section class="resume-section" id="experience"><h2>Research experience</h2><div>'+''.join(vis)+'</div></section><section class="resume-section" id="awards"><h2>Selected honors</h2><div>'+data['awards']+'</div></section></div>'
    body+='<section class="resume-section"><h2>Technical skills</h2><p class="skill-list">PyTorch · CUDA · Diffusers · Open3D · OpenCV</p></section><section class="resume-section"><h2>Publications</h2><div><p>First- and co-first-author research, collaborative work, and preprints.</p><div class="inline-links" style="margin-top:15px"><a class="text-link" href="research.html#publications">View the complete publication record →</a></div></div></section>'
    return document('resume',body,'Xiaoshan Wu’s academic resume: education, research experience, honors, technical skills, and downloadable CV.')

def build_research(data):
    body=heading('World understanding → reliable action','Research','Spatial intelligence for physical agents.')
    body+=f'<section id="direction" class="research-summary-top"><p>{paragraph(data["foundation"])}</p></section><nav class="research-subnav" aria-label="Research page sections"><a href="#projects">Research projects</a><a href="#publications">Complete publication record</a></nav><section id="projects" aria-labelledby="selected-research"><div class="section-heading"><h2 id="selected-research">Research projects</h2><span class="section-note">Seven projects · First- and co-first-author work</span></div><div class="project-grid">'+''.join(research_article(data,s) for s in SLUGS)+'</div></section>'
    body+='<details class="publication-archive" id="publications"><summary>Complete publication record<span class="archive-caption">All publications and preprints, with authors, venues, and contribution roles.</span></summary>'+data['publication_note']+update_links(''.join(data['publications']))+'</details>'
    return document('research',body,'Research by Xiaoshan Wu: S4NDBOX, EAG3R, VideoSSM, GaMe, LiFR-Seg, LiFR v2, EVSplat, and the complete publication record.')

def legacy_publications(data):
    # Keep every old article anchor usable, with a full no-JavaScript fallback.
    body=heading('Publication archive','Publications','The publication record is now part of Research.','<div class="inline-links"><a class="text-link" href="research.html#publications">Continue to Research →</a></div>')+data['publication_note']+update_links(''.join(data['publications']))
    text=document('research',body,'Publication archive for Xiaoshan Wu.')
    return text.replace('</head>','<script>location.replace("research.html"+(location.hash||"#publications"));</script></head>',1)

def integrate_project_navigation():
    # Preserve every project website; change only links back to the personal site.
    for slug in SLUGS:
        path=ROOT/'projects'/slug/'index.html'
        if not path.is_file():raise RuntimeError('Existing project page missing: '+slug)
        doc=soup(path.read_text())
        for a in doc.select('.topnav a, #project-directory-nav a'):
            if a.get_text(' ',strip=True) in ['All projects','← All research projects','← Research']:
                a['href']='../../research.html#projects';a.string='← Research'
        path.write_text(str(doc))
    path=ROOT/'projects/index.html';doc=soup(path.read_text());n=doc.select_one('.topnav')
    if n:
        n.clear()
        for element in list(soup(nav('research','../')).contents):n.append(element)
        fix=doc.find('style',id='personal-site-hub-nav')
        if fix is None:fix=doc.new_tag('style',id='personal-site-hub-nav');doc.head.append(fix)
        fix.string='.topbar .wrap{flex-wrap:wrap;padding-block:10px;gap:8px 20px}.topnav a:first-child{display:inline!important}@media(max-width:480px){.topnav{width:100%;gap:22px}}'
    path.write_text(str(doc))

def main():
    data=seed()
    (ROOT/'assets/css/site-pages.css').write_text(CSS)
    (ROOT/'assets/js/site-pages.js').write_text(JS)
    builders={'index.html':build_home,'about.html':build_about,'resume.html':build_resume,'research.html':build_research,'publications.html':legacy_publications}
    for filename,build in builders.items():(ROOT/filename).write_text(build(data))
    integrate_project_navigation()
    (ROOT/'_site_content/README.md').write_text('''# Personal website information architecture\n\nHome (`index.html`): original cinematic cover, a short introduction, three project highlights and recent updates.\nAbout (`about.html`): biography, one research perspective, future interests and the existing personal inspiration.\nResume (`resume.html`): CV PDF, education, research experience, honors and technical skills.\nResearch (`research.html`): seven project summaries and the complete publication record.\n\n`personal-site.json` preserves the pre-migration sections as editable source. Edit those fragments for biography, dates, awards, news, authors or publication statuses. Do not delete the source file: the short homepage intentionally no longer contains the full record. Project descriptions for LiFR v2 and EVSplat are read from their current project pages during a build.\n\nRun `python scripts/build-personal-site.py` and `python scripts/test-personal-site.py`. The personal-site workflow also runs after successful project-page builds, so updates do not restore the old navigation. It serializes with other site writers.\n\nThe original CV PDF and LaTeX are unchanged. All seven project URLs are unchanged. `publications.html#pub-*` redirects to the same anchor on Research, with a full no-JavaScript archive fallback. Old homepage research, background and inspiration anchors have explicit redirects.\n''')
    print('Built Home / About / Resume / Research; preserved 7 projects and all publication anchors.')
if __name__=='__main__':main()
