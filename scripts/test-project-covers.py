#!/usr/bin/env python3
"""Validate complete project covers, clickable links and EVSplat hero."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import hashlib,json,os,sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    covers=json.loads((ROOT/'_site_content/project-covers.json').read_text())['covers']
    out=ROOT/'cover-review';out.mkdir(exist_ok=True)
    for name in ['index.html','research.html','publications.html']:
        doc=BeautifulSoup((ROOT/name).read_text(),'html.parser')
        for key,m in covers.items():
            node=doc.select_one('#'+key+' .research-media img')
            assert node and node['src']==m['src'],(name,key)
            assert 'position:absolute' not in node.get('style','')
            assert int(node['width'])==m['width'] and int(node['height'])==m['height']
            assert hashlib.sha256((ROOT/m['src']).read_bytes()).hexdigest()==m['sha256']
        assert doc.select_one('#pub-world-action-model video source')['src']=='projects/sandbox/static/videos/disco_light_10x.mp4'
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    base=sys.argv[1].rstrip('/')+'/' if len(sys.argv)>1 else f'http://127.0.0.1:{server.server_port}/'
    report=[]
    try:
        with sync_playwright() as pw:
            exe=os.getenv('BROWSER_EXECUTABLE')
            browser=pw.chromium.launch(**({'executable_path':exe} if exe else {}))
            ctx=browser.new_context(reduced_motion='reduce');page=ctx.new_page();errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            for width in [390,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                page.goto(base+'index.html',wait_until='domcontentloaded')
                for key,m in covers.items():
                    entry=page.locator('#'+key);entry.scroll_into_view_if_needed()
                    image=entry.locator('.research-media img');image.evaluate('(i)=>i.decode()')
                    dims=image.evaluate('(i)=>({w:i.clientWidth,h:i.clientHeight,nw:i.naturalWidth,nh:i.naturalHeight})')
                    assert dims['nw']==m['width'] and dims['nh']==m['height'],(key,dims)
                    assert abs(dims['h']-dims['w']*m['height']/m['width'])<2,(key,dims)
                    assert entry.locator('a.media-link').get_attribute('href')
                    entry.screenshot(path=str(out/f'{key}-{width}.png'))
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                page.goto(base+'index.html#pub-ugg',wait_until='domcontentloaded')
                assert page.locator('#pub-ugg').evaluate('(e)=>getComputedStyle(e).outlineStyle')=='none'
                page.goto(base+'projects/evsplat/',wait_until='domcontentloaded')
                image=page.locator('#evsplat-method-figure img');image.evaluate('(i)=>i.decode()')
                assert image.evaluate('(i)=>i.naturalWidth>0')
                page.locator('#evsplat-method-figure').screenshot(path=str(out/f'evsplat-project-{width}.png'))
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                report.append({'width':width,'covers':len(covers),'uncropped':True,'evsplat_hero':True})
            assert not errors,errors
            browser.close()
    finally:server.shutdown()
    (out/'covers-report.json').write_text(json.dumps({'status':'PASS','checks':report,'sandbox_video_preserved':True},indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
