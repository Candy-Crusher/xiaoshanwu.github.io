#!/usr/bin/env python3
"""Build five static research sites. Only public figure URLs are downloaded.
Run: python scripts/build-project-pages.py --download-assets
Existing homepage/publication content is preserved; only project links are added.
"""
from __future__ import annotations
import argparse, html, json, re, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://candy-crusher.github.io/xiaoshanwu.github.io/'
PAPER = {'videossm':'2512.04519','lifr-seg':'2603.21115','lifr-v2':'2609.25803'}
PROJECTS = [
 dict(slug='videossm', name='VideoSSM', area='Generative models / Memory', color='#725045', tint='#f2eae4', status='arXiv · 2025',
 title='Autoregressive Long Video Generation with Hybrid State-Space Memory',
 authors=['Yifei Yu*','Xiaoshan Wu*','Xinting Hu','Tao Hu','Yangtian Sun','Xiaoyang Lyu','Bo Wang','Lin Ma','Yuewen Ma','Zhongrui Wang','Xiaojuan Qi'],
 affiliation='The University of Hong Kong · PICO, ByteDance · Southern University of Science and Technology', credit='* Equal contribution',
 statement='Long videos need memory that evolves.',
 tldr='A local attention cache preserves recent detail while recurrent state-space memory carries evolving context beyond the window.',
 synopsis='VideoSSM augments autoregressive diffusion with a hybrid memory: a sliding-window cache for local detail and an evolving state for longer-range context. It supports minute-long generation and prompt switching without retaining an ever-growing history of keys and values.',
 hero=dict(local='images/research/videossm-full.webp',caption='Original overview: hybrid memory, long-video examples and training. Figure 1 of the paper.'),
 method_title='Remember the past. Keep the scene moving.',
 steps=[('Local cache','Recent tokens retain fine motion and appearance.'),('Global state','Evicted tokens update a compact recurrent memory.'),('Adaptive fusion','A router combines local and global information.')],
 method_figure=dict(url='https://arxiv.org/html/2512.04519v1/memory_module.png',file='memory.webp',caption='Hybrid memory module. Original Figure 5.'),
 result_title='Consistency without freezing the video.',
 result_note='Selected metrics from Table 2, evaluated on 60-second videos. Higher is better. See the paper for the complete comparison and evaluation protocol.',
 table=dict(headers=['Metric','Self Forcing','LongLive','VideoSSM'],rows=[['Subject consistency','88.25','91.09','92.51'],['Background consistency','91.73','93.23','93.95'],['Dynamic degree','35.00','37.50','50.50']]),
 source='https://arxiv.org/html/2512.04519v1',year=2025,
 missing=['Original 60-second MP4s and their prompts; matched baseline clips.','Prompt-switching clips with switch timestamps.','Public code/checkpoint release URL and current submission status.']),
 dict(slug='game',name='GaMe',area='Spatial reasoning / Memory',color='#416659',tint='#eaf1eb',status='Under review · ICRA 2027',
 title='Geometry as Memory for Multi-View Spatial Reasoning',
 authors=['Xiaoshan Wu','Xiaoyang Lyu','Yifei Yu','Muxin Liu','S. Shi','Zhongrui Wang','Xiaojuan Qi'],affiliation='',credit='',
 statement='Give spatial reasoning a geometric working memory.',
 tldr='A compact geometric memory combines evidence across views and augments the original visual–language context for spatial question answering.',
 synopsis='GaMe investigates geometry as a working memory for multi-view spatial reasoning. Rather than replacing the original visual–language context, a 16-slot memory gathers geometric evidence across views and supplies an additional source of spatial context.',
 hero=dict(local='images/research/game-overview.webp',caption='Conceptual overview from the manuscript. The scene, point cloud and example answer illustrate the approach; they are not benchmark inputs or measured model predictions.'),
 method_title='Multiple views. A shared spatial context.',
 steps=[('Gather evidence','Combine visual and geometric information across views.'),('Form a memory','Condense the evidence into 16 working-memory slots.'),('Augment reasoning','Keep the original visual–language context alongside the memory.')],
 release_note='This page currently presents the project overview. A public manuscript and evaluated examples have not been posted here.',
 source=BASE+'publications.html#pub-game',year=2026,
 missing=['Publication-ready PDF or public preprint URL; confirm that public release is appropriate during review.','Full author spelling for S. Shi and author–affiliation mapping.','Approved method figure, benchmark table and real question–answer examples.','Public code/model URL when ready.']),
 dict(slug='lifr-seg',name='LiFR-Seg',area='Event vision / Dense perception',color='#28656b',tint='#e9f2f1',status='ICLR 2026',
 title='Anytime High-Frame-Rate Segmentation via Event-Guided Propagation',
 authors=['Xiaoshan Wu','Xiaoyang Lyu','Yifei Yu','Bo Wang','Zhongrui Wang','Xiaojuan Qi'],
 affiliation='The University of Hong Kong · Southern University of Science and Technology',credit='',
 statement='See what changes between RGB frames.',
 tldr='Event-guided, uncertainty-aware feature propagation updates semantic predictions at arbitrary query times without a new RGB frame.',
 synopsis='LiFR-Seg predicts interframe semantic maps from one past RGB frame and observed events. It transports semantic features using event-derived motion and learned confidence, then uses temporal memory to refine them. No future RGB frame is required at inference.',
 hero=dict(url='https://arxiv.org/html/2603.21115v1/figs/main_results.png',file='results.webp',caption='Interframe segmentation examples. Original Figure 4; target-time ground truth is a reference, not a model input.'),
 method_title='Move the features, not just the pixels.',
 steps=[('Anchor','Extract semantic features from the RGB keyframe.'),('Propagate','Use event motion and confidence to transport features.'),('Refine','Retrieve temporal context before decoding the semantic map.')],
 method_figure=dict(url='https://arxiv.org/html/2603.21115v1/net.png',file='method.webp',caption='Uncertainty-guided splatting and temporal memory. Original Figure 2; future observations shown for supervision are not inference inputs.'),
 result_title='Which representation should move?',
 result_note='DSEC, 50 ms query offset. Table 4, mIoU (%). Higher is better. The paper separately reports a target-RGB reference of 73.91% versus 73.82% for LiFR-Seg.',
 table=dict(headers=['Approach','mIoU'],rows=[['Image interpolation','70.38'],['Image warping','72.37'],['Segmentation warping','71.63'],['Feature warping · LiFR-Seg','73.82']]),
 source='https://arxiv.org/html/2603.21115v1',year=2026,
 related=('lifr-v2','LiFR v2 extends propagation with completion for newly visible content.'),
 missing=['Synchronized RGB / events / prediction / ground-truth MP4 demos with timestamps.','Confirm code release: Candy-Crusher/LiFR-Seg currently has no code.','The paper names the old /LiFR_Seg_Proj/ URL; update that link or enable a separate redirect repository.']),
 dict(slug='lifr-v2',name='LiFR v2',area='Event vision / Causal perception',color='#3d587b',tint='#ebeff6',status='Under review · IEEE TPAMI',
 title='Completion-Augmented Event Propagation for High-Rate Dense Prediction',
 authors=['Tao Wan*','Xiaoshan Wu*†','Yifei Yu','Bo Wang','Xiaoyang Lyu','Muxin Liu','Aoxuan Pan','Zhongrui Wang','Xiaojuan Qi'],
 affiliation='Southern University of Science and Technology · The University of Hong Kong',credit='* Equal contribution · † Project lead',
 statement='Transport the known. Complete the unseen.',
 tldr='Propagation reuses observed content, event-guided completion recovers missing source support, and memory retains inferred content for later queries.',
 synopsis='LiFR v2 supports causal anytime and streaming segmentation, depth and joint prediction. An Event-Guided Completion Module addresses regions missing from the RGB keyframe; a History Retrieval Module reuses completed features. SHF-Emerge tests rapid emergence and disocclusion.',
 hero=dict(url='https://arxiv.org/html/2609.25803v2/framework-v2.png',file='method.webp',caption='Streaming architecture, original Figure 2: propagate → retrieve history → complete → decode. Completed features update memory.'),
 method_title='Beyond propagation alone.',
 steps=[('Propagation','Transport reliable RGB-derived features with scene motion.'),('Completion','Recover event-supported content absent from the keyframe.'),('Retention','Preserve completed representations for subsequent queries.')],
 result_title='Recovering newly visible content.',
 result_note='SHF-Emerge, single-task evaluation. Tables I–II. Segmentation is mIoU (%); depth is 1–10 m RMSE (m). These are different task-specific models.',
 table=dict(headers=['Task','Baseline','Baseline score','LiFR v2'],rows=[['Segmentation ↑','LiFR-Seg','54.28','56.13'],['Depth ↓','LiFR propagation','1.564','1.118']]),
 result_figure=dict(url='https://arxiv.org/html/2609.25803v2/qualitative_comparison.png',file='results.webp',caption='Original Figure 8: segmentation, depth and multi-task comparisons. Target-time RGB and HFR outputs are visualization references, not LiFR v2 inputs.'),
 source='https://arxiv.org/html/2609.25803v2',year=2026,
 repository='https://github.com/TaoWan0610/LiFR-v2',repository_note='The public repository currently hosts paper materials; its README says code and pretrained models are being prepared.',
 related=('lifr-seg','Read the original LiFR-Seg conference paper.'),
 missing=['Streaming MP4s, especially emergence/disocclusion examples and the corresponding baselines.','Dataset/checkpoint download URLs when released.','Keep repository release wording in sync with TaoWan0610/LiFR-v2.']),
 dict(slug='evsplat',name='EVSplat',area='Event vision / 3D reconstruction',color='#755375',tint='#f1eaf3',status='Under review · AAAI 2027',
 title='Uncertainty-Aware Gaussian Splatting for Dynamic Scenes with Event Camera',
 authors=['Yifei Yu*','Xiaoshan Wu*†','Xiaoyang Lyu','Zhongrui Wang','Xiaojuan Qi'],affiliation='',credit='* Equal contribution · † Project lead',
 statement='Dynamic scenes through event-camera evidence.',
 tldr='Uncertainty-aware Gaussian splatting for dynamic-scene reconstruction with an event camera.',
 synopsis='EVSplat studies event-camera-based reconstruction of dynamic scenes using uncertainty-aware Gaussian splatting. This page presents the project identity and research focus; technical details and experimental media will be added with the public manuscript.',
 focus=['Event-camera observations','Dynamic-scene reconstruction','Uncertainty-aware Gaussian splatting'],
 release_note='A public manuscript, reconstruction videos and experimental results have not been posted here. No synthetic reconstruction demo or unverified benchmark scores are shown.',
 source=BASE+'publications.html#pub-evsplat',year=2026,
 missing=['Current manuscript/PDF, abstract and approved public-release status.','Teaser and method figures; reconstruction / novel-view / dynamic-scene MP4s.','Confirmed results table, dataset names and evaluation settings.','Author–affiliation mapping and public code/model URL.'])
]
CSS = r'''
:root{--ink:#202b33;--muted:#5b646a;--line:#dadeda;--paper:#fbfbf8;--accent:#28656b;--tint:#e9f2f1;font-family:Inter,"Avenir Next",Avenir,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper);font-synthesis:none;text-rendering:optimizeLegibility}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:100px}body{margin:0;font-size:17px;line-height:1.7}a{color:var(--accent);text-underline-offset:4px}a:hover{text-decoration-thickness:2px}button{font:inherit}button,a{-webkit-tap-highlight-color:transparent}:focus-visible{outline:3px solid var(--accent);outline-offset:5px}.wrap{width:min(1120px,calc(100% - 64px));margin-inline:auto}.skip{position:fixed;top:-100px;left:20px;z-index:99;background:white;padding:10px}.skip:focus{top:12px}.topbar{position:sticky;top:0;z-index:5;background:rgba(251,251,248,.96);border-bottom:1px solid var(--line)}.topbar .wrap{min-height:66px;display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{font-size:16px;font-weight:650;letter-spacing:-.3px;text-decoration:none;color:var(--ink)}.topnav{display:flex;gap:26px;align-items:center;font-size:13px}.topnav a{color:var(--muted);text-decoration:none}.topnav a[aria-current]{color:var(--accent);text-decoration:underline}.hero{padding:68px 0 32px;text-align:center}.eyebrow{font-size:12px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;color:var(--accent);margin:0 0 22px}.hero h1{font-size:clamp(56px,7vw,88px);letter-spacing:-5px;line-height:1.05;font-weight:650;margin:0 0 19px}.subtitle{font-size:clamp(23px,2.5vw,31px);font-weight:450;letter-spacing:-.8px;line-height:1.33;max-width:850px;margin:0 auto 20px;text-wrap:balance}.status{display:inline-block;font-size:12px;font-weight:650;letter-spacing:.4px;border:1px solid var(--line);padding:4px 14px;border-radius:30px;background:var(--tint);color:var(--accent);margin:0 0 26px}.authors{display:flex;justify-content:center;flex-wrap:wrap;gap:2px 16px;max-width:940px;margin:auto;font-size:15px;line-height:1.9}.authors span,.authors a{white-space:nowrap}.authors a{text-decoration:none}.authors sup{font-size:11px;margin-left:2px}.affiliation{max-width:800px;font-size:13px;color:var(--muted);margin:10px auto 0}.credit{font-size:11px;color:var(--muted);margin:7px 0 0}.actions{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin:25px 0 0}.button{display:inline-flex;align-items:center;justify-content:center;gap:12px;border:1px solid var(--ink);background:var(--ink);color:white;padding:8px 22px;border-radius:5px;font-size:13px;text-decoration:none;cursor:pointer}.button.secondary{color:var(--ink);background:transparent;border-color:var(--line)}.button:hover{background:var(--accent);border-color:var(--accent);color:white}.statement{font-size:clamp(23px,2.7vw,31px);line-height:1.35;letter-spacing:-.7px;text-align:center;font-weight:500;margin:22px auto 13px;text-wrap:balance}.tldr{max-width:850px;margin:0 auto 30px;text-align:center;color:var(--muted);font-size:17px;line-height:1.65}.tldr strong{color:var(--accent);font-size:11px;letter-spacing:1px;margin-right:9px}.figure{margin:20px 0 0}.figure-link{display:block;background:white;border:1px solid var(--line);border-radius:8px;padding:24px;cursor:zoom-in;overflow:hidden}.figure img{display:block;max-width:100%;height:auto;margin:auto;max-height:680px;object-fit:contain}.hero-figure img{max-height:520px}.hero-figure .figure-link{padding:26px}.figure figcaption{font-size:12px;line-height:1.65;color:var(--muted);padding:11px 3px}.figure figcaption a{color:var(--muted);margin-left:7px}.zoom-hint{float:right;margin-left:12px;color:var(--accent)}.section{display:grid;grid-template-columns:260px minmax(0,1fr);gap:64px;border-top:1px solid var(--line);padding:48px 0;margin-top:36px;scroll-margin-top:90px}.section .kicker{font-size:11px;letter-spacing:1.3px;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:12px}.section h2{font-size:28px;font-weight:500;line-height:1.24;letter-spacing:-.8px;margin:0;text-wrap:balance}.section p{margin:0 0 18px}.section p:last-child{margin-bottom:0}.copy{font-size:18px;color:#3e4a50;line-height:1.8}.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.step{border-top:2px solid var(--accent);padding-top:13px}.step .number{font-size:11px;color:var(--accent)}.step h3{font-size:17px;font-weight:600;margin:6px 0}.step p{font-size:14px;line-height:1.65;color:var(--muted)}.full{grid-column:1/-1}.section .full.figure{margin-top:2px}.table-wrap{overflow-x:auto}.results{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums;line-height:1.5}.results th,.results td{padding:15px 13px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}.results th:first-child,.results td:first-child{text-align:left;white-space:normal}.results thead th{font-size:12px;font-weight:600;background:var(--tint);color:var(--accent)}.results td:last-child{font-weight:650;color:var(--accent)}.table-note{font-size:12px;color:var(--muted);margin-top:17px!important;line-height:1.7}.source-link{font-size:13px;display:inline-block;margin-top:5px}.citation{position:relative}.citation pre{font-size:12px;line-height:1.75;background:var(--tint);padding:25px;margin:0;overflow-x:auto;white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid var(--line);border-radius:6px}.copy-button{margin-top:12px;background:transparent;color:var(--accent);border:1px solid var(--line);border-radius:4px;padding:6px 15px;font-size:12px;cursor:pointer}.copy-status{font-size:12px;margin-left:12px;color:var(--muted)}.related{font-size:14px;padding:22px 0;border-top:1px solid var(--line)}.related strong{font-weight:550}.focus{display:flex;justify-content:center;gap:0;background:var(--tint);border:1px solid var(--line);border-radius:7px;margin:36px 0 0;padding:40px 20px}.focus span{flex:1;text-align:center;font-size:18px;line-height:1.4;padding:12px 28px}.focus span+span{border-left:1px solid var(--line)}.release{background:var(--tint);padding:25px;border-left:3px solid var(--accent);font-size:15px;color:var(--muted)}footer{border-top:1px solid var(--line);padding:35px 0 28px;margin-top:45px;font-size:12px;color:var(--muted)}.footer-top{display:flex;justify-content:space-between;gap:20px;align-items:center}footer nav{display:flex;gap:20px;flex-wrap:wrap;margin-top:20px}footer a{color:var(--muted);text-decoration:none}footer a:hover{color:var(--accent)}.provenance{font-size:11px;max-width:800px;margin:20px 0 0}dialog{border:none;border-radius:8px;background:#fff;padding:46px 20px 20px;max-width:96vw;max-height:94vh;box-shadow:0 20px 100px #0005}dialog::backdrop{background:#15212cbb}dialog img{max-width:90vw;max-height:78vh;display:block;object-fit:contain}dialog .close{position:absolute;right:16px;top:8px;background:transparent;border:0;font-size:14px;padding:5px 12px;cursor:pointer}.hub-intro{padding:72px 0 36px}.hub-intro h1{font-size:52px;font-weight:550;letter-spacing:-2.5px;line-height:1.15;margin:0 0 15px}.hub-intro p{max-width:650px;color:var(--muted)}.project-list{list-style:none;padding:0;margin:0}.project-list li{border-top:1px solid var(--line);padding:25px 0}.project-list a{display:grid;grid-template-columns:210px 1fr 25px;gap:30px;text-decoration:none;color:var(--ink);align-items:start}.project-list strong{font-size:23px;letter-spacing:-.5px;font-weight:550}.project-list small{display:block;font-size:12px;color:var(--muted);margin-top:5px}.project-list span{font-size:16px;line-height:1.6}.project-list .arrow{color:var(--accent)}
@media(max-width:800px){.wrap{width:calc(100% - 40px)}.section{grid-template-columns:1fr;gap:25px;padding:33px 0;margin-top:25px}.section h2{max-width:600px}.hero{padding-top:42px}.hero h1{letter-spacing:-3px}.topnav{gap:16px}.topnav a:first-child{display:none}.hero-figure .figure-link,.figure-link{padding:12px}.statement{margin-top:20px}.steps{gap:18px}.project-list a{grid-template-columns:150px 1fr 18px;gap:18px}.focus span{font-size:16px;padding:10px 16px}.figure figcaption{font-size:11px}}
@media(max-width:480px){.topbar .wrap{min-height:58px;gap:12px}.brand{font-size:14px}.topnav{gap:13px;font-size:12px}.hero{padding:36px 0 20px}.hero h1{font-size:58px;letter-spacing:-3.5px}.subtitle{font-size:24px;line-height:1.3}.eyebrow{font-size:10px;letter-spacing:1.2px;margin-bottom:20px}.authors{gap:2px 12px;font-size:13px}.affiliation{font-size:11px}.status{margin-bottom:20px;font-size:11px}.button{padding:8px 17px}.statement{font-size:25px}.tldr{font-size:15px;margin-bottom:20px}.steps{grid-template-columns:1fr;gap:20px}.step{display:grid;grid-template-columns:28px 1fr;gap:0 8px}.step .number{grid-row:1/3;margin-top:8px}.step h3{margin:0 0 4px}.step p{grid-column:2}.copy{font-size:16px}.section h2{font-size:26px}.focus{flex-direction:column;padding:15px 25px}.focus span{padding:18px 0}.focus span+span{border-left:0;border-top:1px solid var(--line)}.footer-top{align-items:start}.hub-intro h1{font-size:40px}.project-list a{grid-template-columns:1fr 20px;gap:12px}.project-list a div{grid-column:1}.project-list a>span:not(.arrow){grid-column:1;grid-row:2}.project-list .arrow{grid-column:2;grid-row:1}.zoom-hint{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{.topbar,.actions,.copy-button,.zoom-hint,footer nav{display:none}.wrap{width:100%}.hero{padding-top:0}.section{break-inside:avoid}.hero h1{font-size:48px}.figure-link{border:0;padding:0}.figure img{max-height:400px}}
'''
JS = r'''
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
'''
def e(value):
 return html.escape(str(value),quote=True)
def author_html(names):
 result=[]
 for name in names:
  plain=name.rstrip('*†');marks=name[len(plain):]
  label=e(plain)+(f'<sup>{e(marks)}</sup>' if marks else '')
  result.append(f'<a href="{BASE}">{label}</a>' if plain=='Xiaoshan Wu' else f'<span>{label}</span>')
 return ''.join(result)
def download_figure(project,figure,enabled,report):
 if 'local' in figure:
  if not (ROOT/figure['local']).is_file():
   report.append({'project':project['slug'],'asset':figure['local'],'status':'missing_existing_asset'});return None
  return '../../'+figure['local']
 path=ROOT/'projects'/project['slug']/'assets'/figure['file']
 if path.is_file():return 'assets/'+figure['file']
 if not enabled:
  report.append({'project':project['slug'],'asset':figure['url'],'status':'download_not_requested'});return None
 from PIL import Image
 import io
 for attempt in range(2):
  try:
   request=urllib.request.Request(figure['url'],headers={'User-Agent':'ResearchProjectPages/1.0 (public academic figures)'})
   with urllib.request.urlopen(request,timeout=40) as response:raw=response.read(20_000_001)
   if len(raw)>20_000_000:raise ValueError('Figure exceeds 20 MB download limit')
   image=Image.open(io.BytesIO(raw));image.load()
   if image.mode not in ('RGB','RGBA'):image=image.convert('RGBA')
   if image.mode=='RGBA':
    bg=Image.new('RGBA',image.size,'white');bg.alpha_composite(image);image=bg.convert('RGB')
   path.parent.mkdir(parents=True,exist_ok=True);image.save(path,'WEBP',quality=94,method=6)
   report.append({'project':project['slug'],'asset':figure['url'],'status':'downloaded','path':str(path.relative_to(ROOT))})
   return 'assets/'+figure['file']
  except Exception as exc:
   if attempt==0:time.sleep(2)
   else:report.append({'project':project['slug'],'asset':figure['url'],'status':'unavailable','error':str(exc)})
 return None

def render_figure(figure,klass=''):
 if not figure or not figure.get('src'):return ''
 loading='eager' if klass=='hero-figure' else 'lazy'
 return f'<figure class="figure {klass}"><a class="figure-link" href="{e(figure["src"])}" aria-label="Enlarge figure: {e(figure["caption"])}"><img src="{e(figure["src"])}" alt="{e(figure["caption"])}" loading="{loading}" decoding="async"></a><figcaption>{e(figure["caption"])}<span class="zoom-hint">Click to enlarge ↗</span></figcaption></figure>'

def bibtex(p):
 slug=p['slug'];authors=' and '.join(n.rstrip('*†') for n in p['authors']);title=p['name']+': '+p['title']
 if slug=='lifr-seg':return f'@inproceedings{{wu2026lifrseg,\n  title = {{{title}}},\n  author = {{{authors}}},\n  booktitle = {{International Conference on Learning Representations}},\n  year = {{2026}},\n  url = {{https://arxiv.org/abs/{PAPER[slug]}}}\n}}'
 key='yu2025videossm' if slug=='videossm' else 'wan2026lifrv2'
 return f'@misc{{{key},\n  title = {{{title}}},\n  author = {{{authors}}},\n  year = {{{p["year"]}}},\n  eprint = {{{PAPER[slug]}}},\n  archivePrefix = {{arXiv}},\n  primaryClass = {{cs.CV}},\n  url = {{https://arxiv.org/abs/{PAPER[slug]}}}\n}}'

def footer(project=None):
 prefix='../' if project else ''
 links=''.join(f'<a href="{prefix}{p["slug"]}/">{e(p["name"])}</a>' for p in PROJECTS if not project or p['slug']!=project['slug'])
 return f'<footer><div class="wrap"><div class="footer-top"><span>Research by Xiaoshan Wu &amp; collaborators</span><a href="mailto:wuxiaoshan630@gmail.com">Contact ↗</a></div><nav aria-label="Other projects">{links}</nav><p class="provenance">Research figures belong to the respective authors. Figures and reported scores are identified by their paper locations; conceptual illustrations are labelled separately. This website does not run the research models.</p></div></footer>'

def page(p):
 slug=p['slug'];title=p['name']+': '+p['title'];canonical=BASE+'projects/'+slug+'/'
 nav='<a href="../">All projects</a><a href="#overview">Overview</a>'
 if p.get('steps'):nav+='<a href="#method">Method</a>'
 if p.get('table'):nav+='<a href="#results">Results</a>'
 actions=''
 if slug in PAPER:actions=f'<a class="button" href="https://arxiv.org/abs/{PAPER[slug]}">Paper <span aria-hidden="true">↗</span></a><a class="button secondary" href="https://arxiv.org/pdf/{PAPER[slug]}">PDF</a><a class="button secondary" href="#citation">BibTeX</a>'
 if p.get('repository'):actions+=f'<a class="button secondary" href="{e(p["repository"])}">Repository ↗</a>'
 if not actions:actions='<a class="button secondary" href="#overview">Project overview ↓</a>'
 sections=f'<section class="section" id="overview"><div><span class="kicker">Overview</span><h2>{e(p["statement"])}</h2></div><div class="copy"><p>{e(p["synopsis"])}</p></div></section>'
 if p.get('steps'):
  steps=''.join(f'<div class="step"><span class="number">0{i+1}</span><h3>{e(s[0])}</h3><p>{e(s[1])}</p></div>' for i,s in enumerate(p['steps']))
  sections+=f'<section class="section" id="method"><div><span class="kicker">The approach</span><h2>{e(p["method_title"])}</h2></div><div class="steps">{steps}</div>{render_figure(p.get("method_figure"),"full")}</section>'
 if p.get('table'):
  table=p['table'];head=''.join(f'<th scope="col">{e(x)}</th>' for x in table['headers']);rows=''
  for row in table['rows']:
   cells=f'<th scope="row">{e(row[0])}</th>'+''.join(f'<td>{e(x)}</td>' for x in row[1:]);rows+='<tr>'+cells+'</tr>'
  sections+=f'<section class="section" id="results"><div><span class="kicker">Paper results</span><h2>{e(p["result_title"])}</h2></div><div><div class="table-wrap" role="region" aria-label="Results table" tabindex="0"><table class="results"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div><p class="table-note">{e(p["result_note"])}</p><a class="source-link" href="{e(p["source"])}">Read the experimental protocol ↗</a></div>{render_figure(p.get("result_figure"),"full")}</section>'
 if p.get('release_note'):sections+=f'<section class="section" id="materials"><div><span class="kicker">Materials</span><h2>Project resources</h2></div><div class="release">{e(p["release_note"])}</div></section>'
 if slug in PAPER:sections+=f'<section class="section" id="citation"><div><span class="kicker">Reference</span><h2>Cite this work</h2></div><div class="citation"><pre><code id="bibtex">{e(bibtex(p))}</code></pre><button class="copy-button" type="button" data-copy>Copy BibTeX</button><span id="copy-status" class="copy-status" role="status" aria-live="polite"></span></div></section>'
 if p.get('repository_note'):sections+=f'<p class="table-note">{e(p["repository_note"])}</p>'
 if p.get('related'):sections+=f'<aside class="related"><strong>Related work.</strong> <a href="../{e(p["related"][0])}/">{e(p["related"][1])}</a></aside>'
 hero=render_figure(p.get('hero'),'hero-figure')
 if p.get('focus'):hero='<div class="focus" aria-label="Research focus">'+''.join(f'<span>{e(x)}</span>' for x in p['focus'])+'</div>'
 image_meta=''
 if p.get('hero',{}).get('src'):
  import urllib.parse
  image_meta=f'<meta property="og:image" content="{e(urllib.parse.urljoin(canonical,p["hero"]["src"]))}">'
 affiliation='<p class="affiliation">'+e(p['affiliation'])+'</p>' if p['affiliation'] else ''
 credit='<p class="credit">'+e(p['credit'])+'</p>' if p['credit'] else ''
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{e(title)}</title><meta name="description" content="{e(p['tldr'])}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(p['tldr'])}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}">{image_meta}<meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="../assets/project.css?v=1"><script defer src="../assets/project.js?v=1"></script></head>
<body style="--accent:{p['color']};--tint:{p['tint']}"><a class="skip" href="#main">Skip to content</a><header class="topbar"><div class="wrap"><a class="brand" href="../../">Xiaoshan Wu <span aria-hidden="true">/</span> Research</a><nav class="topnav" aria-label="On this page">{nav}</nav></div></header>
<main id="main" class="wrap"><header class="hero"><p class="eyebrow">{e(p['area'])}</p><h1>{e(p['name'])}</h1><p class="subtitle">{e(p['title'])}</p><p class="status">{e(p['status'])}</p><div class="authors">{author_html(p['authors'])}</div>{affiliation}{credit}<div class="actions">{actions}</div></header><p class="statement">{e(p['statement'])}</p><p class="tldr"><strong>TL;DR</strong>{e(p['tldr'])}</p>{hero}{sections}</main>{footer(p)}<dialog id="figure-dialog" aria-label="Enlarged research figure"><button type="button" class="close" aria-label="Close enlarged figure">Close ×</button><img alt=""></dialog></body></html>'''

def hub():
 items=''.join(f'<li><a href="{p["slug"]}/"><div><strong>{e(p["name"])}</strong><small>{e(p["status"])}</small></div><span>{e(p["tldr"])}</span><span class="arrow" aria-hidden="true">↗</span></a></li>' for p in PROJECTS)
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Research projects | Xiaoshan Wu</title><meta name="description" content="Project pages for VideoSSM, GaMe, LiFR-Seg, LiFR v2 and EVSplat."><link rel="canonical" href="{BASE}projects/"><link rel="stylesheet" href="assets/project.css?v=1"></head><body><a class="skip" href="#main">Skip to content</a><header class="topbar"><div class="wrap"><a class="brand" href="../">Xiaoshan Wu / Research</a><nav class="topnav" aria-label="Site navigation"><a href="../">Home</a><a href="../publications.html">Publications</a></nav></div></header><main id="main" class="wrap"><header class="hub-intro"><p class="eyebrow">Research projects</p><h1>Perception, geometry<br>and memory.</h1><p>Selected work on event-driven perception, spatial reasoning and generative memory. Each project has its own paper materials and research summary.</p></header><ul class="project-list">{items}</ul></main>{footer()}</body></html>'

def sync_links():
 """Patch only the known article IDs; idempotent and preserves all other text."""
 for filename in ('index.html','publications.html'):
  path=ROOT/filename
  if not path.is_file():continue
  text=path.read_text();original=text
  for p in PROJECTS:
   slug=p['slug'];anchor=('pub-' if filename=='publications.html' else 'selected-')+slug
   pattern=r'(<(?:li|article)\b[^>]*\bid="'+re.escape(anchor)+r'"[^>]*>)(.*?)(</(?:li|article)>)'
   def patch(m):
    inner=m.group(2)
    if f'projects/{slug}/' in inner:return m.group(0)
    link=f'<a href="projects/{slug}/">Project</a>'
    if 'class="paper-links"' in inner:inner=inner.replace('class="paper-links">','class="paper-links">'+link+' ',1)
    elif filename=='publications.html':
     pos=inner.rfind('</div>')
     if pos!=-1:inner=inner[:pos]+'<span class="paper-links">'+link+'</span>'+inner[pos:]
    else:inner+='<div class="paper-links">'+link+'</div>'
    return m.group(1)+inner+m.group(3)
   text=re.sub(pattern,patch,text,flags=re.S)
  if text!=original:path.write_text(text)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--download-assets',action='store_true');args=parser.parse_args()
 out=ROOT/'projects';(out/'assets').mkdir(parents=True,exist_ok=True)
 (out/'assets'/'project.css').write_text(CSS);(out/'assets'/'project.js').write_text(JS)
 report=[]
 for p in PROJECTS:
  folder=out/p['slug'];folder.mkdir(exist_ok=True)
  for key in ('hero','method_figure','result_figure'):
   if p.get(key):p[key]['src']=download_figure(p,p[key],args.download_assets,report)
  (folder/'index.html').write_text(page(p))
 (out/'index.html').write_text(hub())
 todo='# Project-page content checklist\n\nThe sites intentionally omit unavailable media, unpublished code buttons and unverified scores. No private repository visibility was changed.\n\n'
 for p in PROJECTS:
  todo+=f'## {p["name"]}\n\nPage: {BASE}projects/{p["slug"]}/\n\n'+''.join(f'- [ ] {x}\n' for x in p['missing'])+'\n'
 todo+='## Maintenance\n\nEdit `scripts/build-project-pages.py` and run `python scripts/build-project-pages.py --download-assets`. The build workflow regenerates the static pages. Research content is readable without JavaScript. JavaScript only enhances figure enlargement, navigation highlighting and citation copying.\n'
 (out/'CONTENT_CHECKLIST.md').write_text(todo);(out/'asset-report.json').write_text(json.dumps(report,indent=2))
 sync_links()
 print(json.dumps({'pages':[BASE+'projects/'+p['slug']+'/' for p in PROJECTS],'assets':report},indent=2))
if __name__=='__main__':main()
