#!/usr/bin/env python3
"""Check original-site copies using their real local media at the Pages subpath."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import functools,threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'mirror-qa';OUT.mkdir(exist_ok=True)
CASES=['pose-1','pose-2','lighting-1','lighting-2','clutter-1','clutter-2']
checks=[];errors=[]
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):return super().translate_path(path.removeprefix('/xiaoshanwu.github.io'))
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/xiaoshanwu.github.io/projects/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for width in [1440,390,320]:
   page=browser.new_page(viewport={'width':width,'height':950})
   for slug in ['sandbox','eag3r']:
    if not (ROOT/'projects'/slug/'index.html').is_file():continue
    try:
     failed=[]
     def watch(r):
      if r.status>=400 and '127.0.0.1' in r.url:failed.append({'status':r.status,'url':r.url})
     page.on('response',watch)
     page.goto(BASE+slug+'/',wait_until='domcontentloaded',timeout=60000)
     page.wait_for_timeout(1300)
     page.evaluate('async()=>{for(let y=0;y<document.body.scrollHeight;y+=1000){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0)}')
     page.wait_for_timeout(2000)
     result=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth,scrollWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.naturalWidth&&i.getBoundingClientRect().width>0).map(i=>i.src),wideElements:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&r.width>0}).map(e=>({tag:e.tagName,id:e.id,class:typeof e.className==='string'?e.className:'',width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).slice(0,15)})''')
     checks.append({'slug':slug,'width':width,**result,'failed_resources':failed})
     page.screenshot(path=str(OUT/f'{slug}-{width}.png'),full_page=True)
     page.remove_listener('response',watch)
     if result['overflow'] or result['brokenImages'] or failed:errors.append({'slug':slug,'width':width,**result,'failed_resources':failed})
    except Exception as exc:errors.append({'slug':slug,'width':width,'error':str(exc)})
   page.close()
  if (ROOT/'projects/sandbox/index.html').is_file():
   page=browser.new_page(viewport={'width':1280,'height':900})
   failed=[]
   page.on('response',lambda r:failed.append({'status':r.status,'url':r.url}) if r.status>=400 and '127.0.0.1' in r.url else None)
   for case in CASES:
    try:
     page.goto(BASE+'sandbox/rdf-viewer.html?case='+case+'&view=compare',wait_until='domcontentloaded',timeout=60000)
     page.wait_for_function("document.querySelector('#loading') && document.querySelector('#loading').textContent.includes('time samples')",timeout=30000)
     initial=page.locator('body').inner_text()
     if case=='pose-1':page.screenshot(path=str(OUT/'sandbox-viewer.png'),full_page=True)
     page.locator('#seek').evaluate("e=>{e.value=e.max;e.dispatchEvent(new Event('input',{bubbles:true}));}")
     page.wait_for_timeout(2500)
     check={'case':case,'canvas_count':page.locator('canvas').count(),'initial':initial[:750],'last_sample':page.locator('body').inner_text()[:750],'error':page.locator('#error').inner_text()}
     checks.append(check)
     if check['canvas_count']!=2 or check['error'].strip():errors.append(check)
    except Exception as exc:errors.append({'case':case,'error':str(exc)})
   errors.extend(failed)
   page.goto(BASE+'sandbox/',wait_until='domcontentloaded')
   for path in sorted((ROOT/'projects/sandbox').rglob('*.mp4')):
    try:
     url=BASE+'sandbox/'+str(path.relative_to(ROOT/'projects/sandbox'))+'?metadata-probe=1'
     page.set_content('<video id="probe" muted preload="metadata"></video>')
     # SimpleHTTPRequestHandler does not implement byte-range requests. Decode a
     # complete, unchanged response blob so metadata-at-end MP4s are checked fairly.
     page.locator('#probe').evaluate('''async(v,url)=>{const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const data=await r.blob();v.src=URL.createObjectURL(data);v.load();}''',url)
     page.wait_for_function("document.querySelector('video').readyState>=1 || document.querySelector('video').error",timeout=20000)
     state=page.locator('#probe').evaluate('(v)=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,error:v.error?.code||null})')
     checks.append({'video':str(path.relative_to(ROOT)),**state})
     if state['error'] or not state['width']:errors.append({'video':str(path.relative_to(ROOT)),**state})
     page.locator('#probe').evaluate('(v)=>{const url=v.src;v.removeAttribute("src");v.load();URL.revokeObjectURL(url)}')
    except Exception as exc:errors.append({'video':str(path.relative_to(ROOT)),'error':str(exc)})
   page.close()
  browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2))
if errors:raise SystemExit(json.dumps(errors,indent=2))
print('PASS: mirror mobile widths, video metadata, six 4D viewers and late samples.')
