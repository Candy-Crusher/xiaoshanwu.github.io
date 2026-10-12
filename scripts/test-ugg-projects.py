#!/usr/bin/env python3
"""Static preservation checks plus browser checks for the UGG project template."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from collections import Counter
import functools,threading,json,hashlib
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['sandbox','eag3r','videossm','game','lifr-seg','lifr-v2','evsplat']
OUT=ROOT/'ugg-qa';OUT.mkdir(exist_ok=True)
checks=[];errors=[]
def parse(p):return BeautifulSoup(p.read_text(),'html.parser')
def refs(d):
 return {(t.name,a,t[a]) for t in d.select('img,video,source,iframe') for a in ['src','srcset','poster'] if t.get(a)}
for slug in SLUGS:
 path=ROOT/'projects'/slug/'index.html';d=parse(path);source=parse(ROOT/'_site_content/project-sources'/f'{slug}.html')
 assert d.html.get('data-project-template')=='ugg',slug
 assert len(d.select('h1'))==1,slug
 ids=[t['id'] for t in d.select('[id]')]
 assert len(ids)==len(set(ids)),(slug,'duplicate IDs')
 assert [t.get_text(' ',strip=True) for t in source.select('table')]==[t.get_text(' ',strip=True) for t in d.select('table')],(slug,'table values changed')
 assert [t.get_text() for t in source.select('pre code')]==[t.get_text() for t in d.select('pre code')],(slug,'citation changed')
 missing=refs(source)-refs(d)
 assert not missing,(slug,'missing media references',missing)
 for a in d.select('.navlinks a,.ugg-header .links a'):
  u=urlsplit(a['href'])
  if not u.path and u.fragment:assert d.find(id=unquote(u.fragment)),(slug,'broken anchor',a['href'])
 for t in d.select('img[src],source[src],script[src],iframe[src],link[rel="stylesheet"]'):
  raw=t.get('src') or t.get('href');u=urlsplit(raw)
  if u.scheme or u.netloc:continue
  value=unquote(u.path)
  target=ROOT/value.removeprefix('/xiaoshanwu.github.io/').lstrip('/') if value.startswith('/') else path.parent/value
  assert target.is_file(),(slug,'missing local resource',raw)
 checks.append({'slug':slug,'content_preserved':True,'original_media_references':len(refs(source)),'tables':len(d.select('table'))})
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,p):return super().translate_path(p.removeprefix('/xiaoshanwu.github.io'))
 def log_message(self,*args):pass
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/xiaoshanwu.github.io/projects/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for width in [1440,390,320]:
   for slug in SLUGS:
    ctx=browser.new_context(viewport={'width':width,'height':960 if width==1440 else 844},color_scheme='light')
    page=ctx.new_page();js_errors=[];page.on('pageerror',lambda e:js_errors.append(str(e)))
    try:
     page.goto(BASE+slug+'/',wait_until='domcontentloaded',timeout=45000)
     page.wait_for_timeout(1200)
     page.evaluate('async()=>{for(let y=0;y<document.body.scrollHeight;y+=900){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0)}')
     page.wait_for_timeout(1000)
     state=page.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth,scrollWidth:document.documentElement.scrollWidth,broken:[...document.images].filter(i=>i.getBoundingClientRect().width>0&&!i.naturalWidth).map(i=>i.src),title:document.querySelector('h1').textContent,font:getComputedStyle(document.querySelector('h1')).fontFamily,wideElements:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&r.width>0}).slice(0,10).map(e=>({tag:e.tagName,class:String(e.className),width:e.getBoundingClientRect().width}))})''')
     checks.append({'slug':slug,'width':width,**state,'js_errors':js_errors})
     if state['overflow'] or state['broken'] or js_errors:errors.append(checks[-1])
     if width!=320:
      page.screenshot(path=str(OUT/f'{slug}-{width}-light.png'),full_page=True)
      if width==1440:page.screenshot(path=str(OUT/f'{slug}-hero-light.png'))
     if width==1440:
      before=page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')
      page.locator('.theme-toggle').click();page.wait_for_timeout(100)
      assert page.locator('html').get_attribute('data-theme')=='dark'
      after=page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor');assert before!=after
      page.screenshot(path=str(OUT/f'{slug}-hero-dark.png'))
      if page.locator('.figure-link').count():
       page.locator('.figure-link').first.click();assert page.locator('dialog[open]').count()==1;page.keyboard.press('Escape');assert page.locator('dialog[open]').count()==0
      if page.locator('[data-copy]').count():
       page.locator('[data-copy]').click();page.wait_for_function("document.querySelector('#copy-status').textContent.length>0")
      if slug=='eag3r':
       for slider in page.locator('input[type=range]').all():slider.evaluate("e=>{e.value=25;e.dispatchEvent(new Event('input',{bubbles:true}))}")
       checks.append({'eag3r_sliders':page.locator('input[type=range]').count(),'interaction':'passed'})
     if slug=='sandbox' and width==1440:
      controls=page.locator('[data-rdf-case]');assert controls.count()>=6
      controls.last.click();page.wait_for_timeout(1800)
      assert page.locator('iframe').count()>0
      checks.append({'sandbox_case_switch':'passed','case_controls':controls.count()})
    except Exception as exc:errors.append({'slug':slug,'width':width,'error':str(exc)})
    finally:ctx.close()
  # No JS: content, paper links, and figures must not be hidden by the template.
  ctx=browser.new_context(java_script_enabled=False);page=ctx.new_page()
  for slug in SLUGS:
   page.goto(BASE+slug+'/',wait_until='domcontentloaded');assert page.locator('h1').is_visible();assert page.locator('main').is_visible()
  ctx.close();browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2))
if errors:raise SystemExit(json.dumps(errors,indent=2))
print('PASS: 7 UGG pages, source preservation, 3 widths, 2 themes, copy/zoom and original gallery controls.')
