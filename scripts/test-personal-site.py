#!/usr/bin/env python3
"""Test the new personal-site pages at their actual GitHub Pages subpath."""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit,unquote
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,threading,functools,hashlib
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'personal-site-qa';OUT.mkdir(exist_ok=True)
FILES=['index.html','about.html','resume.html','research.html']
EXPECTED=['Home','About','Resume','Research']
SLUGS=['sandbox','eag3r','game','videossm','lifr-seg','lifr-v2','evsplat']
errors=[];checks=[]
for filename in FILES:
    path=ROOT/filename;doc=BeautifulSoup(path.read_text(),'html.parser')
    links=doc.select('nav[aria-label="Main navigation"] a')
    assert [a.get_text(strip=True) for a in links]==EXPECTED, 'Incorrect navigation: '+filename
    assert len([a for a in links if a.get('aria-current')=='page'])==1, 'Active page marker: '+filename
    assert len(doc.select('h1'))==1, 'Heading structure: '+filename
    ids=[t['id'] for t in doc.select('[id]')]
    assert len(ids)==len(set(ids)), 'Duplicate IDs: '+filename
    for tag in doc.select('a[href],img[src],script[src],link[rel="stylesheet"]'):
        raw=tag.get('href') or tag.get('src');u=urlsplit(raw)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/'index.html'
        if not target.is_file():errors.append({'page':filename,'missing_target':raw});continue
        if u.fragment and target.suffix=='.html':
            other=BeautifulSoup(target.read_text(),'html.parser')
            if other.find(id=unquote(u.fragment)) is None:errors.append({'page':filename,'missing_anchor':raw})
research=BeautifulSoup((ROOT/'research.html').read_text(),'html.parser')
assert len(research.select('.project-grid > article'))==7
assert len(research.select('.publication-list > li'))==15
for slug in SLUGS:assert research.find('a',href='projects/'+slug+'/'),slug
assert (ROOT/'Xiaoshan_Wu_CV.pdf').is_file()
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):return super().translate_path(path.removeprefix('/xiaoshanwu.github.io'))
    def log_message(self,*args):pass
    def copyfile(self,source,output):
        try:super().copyfile(source,output)
        except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/xiaoshanwu.github.io/'
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for width,height in [(1440,1000),(390,844),(320,800)]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            for filename in FILES:
                try:
                    page_errors=[];page.on('pageerror',lambda exc:page_errors.append(str(exc)))
                    response=page.goto(BASE+filename,wait_until='networkidle',timeout=30000)
                    page.evaluate('async()=>{for(let y=0;y<document.body.scrollHeight;y+=800){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}window.scrollTo(0,0)}')
                    page.wait_for_timeout(250)
                    result=page.evaluate('''()=>({title:document.title,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(i=>i.getBoundingClientRect().width>0&&!i.naturalWidth).map(i=>i.src),navigation:[...document.querySelectorAll('nav[aria-label="Main navigation"] a')].map(a=>({label:a.textContent.trim(),visible:a.getBoundingClientRect().width>0}))})''')
                    result.update(page=filename,width=width,status=response.status,script_errors=page_errors)
                    checks.append(result)
                    if result['overflow'] or result['brokenImages'] or page_errors or response.status!=200:errors.append(result)
                    if any(not a['visible'] for a in result['navigation']):errors.append({'hidden_navigation':result})
                    if width!=320:page.screenshot(path=str(OUT/(filename[:-5]+'-'+str(width)+'.png')),full_page=True)
                    page.remove_all_listeners('pageerror')
                except Exception as exc:errors.append({'page':filename,'width':width,'error':str(exc)})
            page.close()
        page=browser.new_page(viewport={'width':1440,'height':1000})
        for original,target in [('index.html#background','resume.html#background'),('index.html#inspiration','about.html#inspiration'),('index.html#selected-world-action-model','research.html#selected-world-action-model'),('publications.html#pub-lifr-v2','research.html#pub-lifr-v2'),('publications.html','research.html#publications')]:
            try:
                page.goto(BASE+original,wait_until='networkidle')
                page.wait_for_url(BASE+target,timeout=10000)
                checks.append({'legacy':original,'target':target,'passed':True})
            except Exception as exc:errors.append({'legacy':original,'error':str(exc)})
        try:
            page.goto(BASE+'research.html#pub-lifr-v2',wait_until='networkidle')
            assert page.locator('#publications').evaluate('(e)=>e.open'), 'Publication archive did not open'
            assert page.locator('#pub-lifr-v2').is_visible()
            page.goto(BASE+'research.html',wait_until='networkidle')
            page.locator('.figure-preview').first.click()
            assert page.locator('#research-figure[open]').count()==1,'Figure enlargement failed'
            page.keyboard.press('Escape')
            assert page.locator('#research-figure[open]').count()==0,'Figure close failed'
            checks.append({'publication_hash_and_figure_dialog':'passed'})
        except Exception as exc:errors.append({'interaction':str(exc)})
        # Without JavaScript, all main pages and the legacy publication archive
        # remain readable. Publication disclosure is a native details element.
        context=browser.new_context(java_script_enabled=False)
        static=context.new_page()
        for filename in FILES+['publications.html']:
            static.goto(BASE+filename)
            assert static.locator('nav[aria-label="Main navigation"] a').count()==4
        static.goto(BASE+'research.html');static.locator('#publications > summary').click()
        assert static.locator('#pub-lifr-v2').is_visible()
        context.close();browser.close()
finally:
    server.shutdown()
    (OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'cv_sha256':hashlib.sha256((ROOT/'Xiaoshan_Wu_CV.pdf').read_bytes()).hexdigest()},indent=2))
if errors:raise SystemExit(json.dumps(errors,indent=2))
print('PASS: four pages, 3 screen widths, 7 project links, 15 publication entries, old links, CV and no-JS fallback.')
