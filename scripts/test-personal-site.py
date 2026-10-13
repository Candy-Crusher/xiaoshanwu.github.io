#!/usr/bin/env python3
"""Validate IA, factual preservation, links, responsive layouts and old anchors.

Default: local HTTP + Playwright (CI). --inline-preview: offline visual rendering
for a sandbox without browser navigation; functional navigation stays unclaimed.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlsplit, unquote
from collections import Counter
import argparse, base64, hashlib, importlib.util, json, mimetypes, os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'personal-site-qa'
PAGES=['index.html','research.html','resume.html','about.html']
DESIGN='academic-ia-20261014'
NAV=['Home','Research','Resume','About']


def text(node): return ' '.join(node.stripped_strings)
def norm(s): return ''.join(s.split()).rstrip('.')


def static_checks():
    spec=importlib.util.spec_from_file_location('site_builder',ROOT/'scripts/build-personal-site.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    cv=builder.parse_cv()
    before={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in PAGES+['publications.html']}
    builder.main()
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in before.items()), 'Build is not idempotent'
    docs={n:BeautifulSoup((ROOT/n).read_text(),'html.parser') for n in PAGES+['publications.html']}
    for name,doc in docs.items():
        assert doc.body['data-design']==DESIGN
        assert [text(a) for a in doc.select('nav[aria-label="Main navigation"] a')]==NAV
        assert len(doc.select('h1'))==1 and len(doc.select('main'))==1
        ids=[n['id'] for n in doc.select('[id]')]
        assert len(ids)==len(set(ids)), (name,'duplicate IDs')
        assert not doc.select('.cinematic-shell, .hero-scrim, details'), name
        for a in doc.select('a[href], main img[src], script[src], link[rel="stylesheet"][href]'):
            url=urlsplit(a.get('href',a.get('src','')))
            if url.scheme or url.netloc:continue
            local=ROOT/unquote(url.path or name)
            if local.is_dir():local/='index.html'
            assert local.is_file(), (name,str(url))
            if url.fragment and local.suffix=='.html':
                target=BeautifulSoup(local.read_text(),'html.parser')
                assert target.find(id=unquote(url.fragment)), (name,str(url))
    r=docs['research.html'];items=r.select('.publication-list > li')
    assert len(items)==15
    assert len(r.select('.lead-papers > li'))==8 and len(r.select('.collaborative-papers > li'))==7
    for item,paper in zip(items,cv['papers']):
        assert text(item.select_one('h3'))==paper['title']
        assert norm(text(item.select_one('.pub-authors')))==norm(builder.plain(paper['authors']))
        assert 'X.Wu' in norm(text(item.select_one('.pub-authors')))
        assert norm(text(item.select_one('.research-meta > span')))==norm(builder.plain(paper['venue']))
        if paper['role']:assert text(item.select_one('.research-role'))==paper['role']
    assert len(docs['index.html'].select('.selected-entry'))==4
    assert docs['index.html'].select_one('[data-paper="pub-videossm"]')
    assert docs['resume.html'].select_one('#experience h2').get_text()=='Research Experience'
    assert 'Harvard' in text(docs['resume.html'].select_one('#experience'))
    assert 'Harvard' not in text(docs['resume.html'].select_one('#education'))
    assert docs['resume.html'].select_one('#awards h2').get_text()=='Selected Awards'
    for award in cv['awards']:assert norm(builder.plain(award)) in norm(text(docs['resume.html'].select_one('#awards')))
    for skill in cv['skills']:assert norm(builder.plain(skill)) in norm(text(docs['resume.html'].select_one('#skills')))
    for name in ['index.html','resume.html','research.html']:
        assert 'agent–world model co-evolution' not in text(docs[name].main), name
    assert 'agent–world model co-evolution' in text(docs['about.html'].main)
    return {'navigation':NAV,'unique_publications':15,'first_author_work':8,'collaborative_work':7,'home_features':4,'metadata_matches_cv02':True,'standalone_awards':True,'duplicate_cv_paragraphs_removed':True,'internal_resources':'PASS','repeat_build':'PASS'}


def inline_doc(name):
    d=BeautifulSoup((ROOT/name).read_text(),'html.parser')
    for old in d.select('link[rel="stylesheet"]'):
        new=d.new_tag('style');new.string=(ROOT/old['href'].split('?')[0]).read_text();old.replace_with(new)
    for script in d.select('script'):script.decompose()
    for img in d.select('main img[src]'):
        path=ROOT/img['src'];img['src']='data:'+mimetypes.guess_type(path)[0]+';base64,'+base64.b64encode(path.read_bytes()).decode();img['loading']='eager'
    return str(d)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def browser_checks(base,inline=False):
    report={'mode':'inline offline render' if inline else 'HTTP + browser','responsive':[]}
    with sync_playwright() as pw:
        executable=os.getenv('BROWSER_EXECUTABLE')
        browser=pw.chromium.launch(**({'executable_path':executable} if executable else {}))
        ctx=browser.new_context(reduced_motion='reduce');page=ctx.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':900})
            for name in PAGES:
                if inline:page.set_content(inline_doc(name),wait_until='load')
                else:assert page.goto(base+name,wait_until='networkidle').status==200
                for img in page.locator('main img').all():
                    # The visible crop, not the entire off-canvas source image,
                    # is what should be scrolled into view.
                    if not inline:img.evaluate('(i)=>{i.loading="eager";}')
                    img.evaluate('(i)=>i.decode()')
                    assert img.evaluate('(i)=>i.complete && i.naturalWidth>0')
                overflow=page.evaluate('document.documentElement.scrollWidth-innerWidth')
                assert overflow<=1,(name,width,overflow)
                assert page.evaluate('document.getAnimations().filter(a=>a.playState==="running").length')==0
                if name=='research.html':
                    assert all(i.is_visible() for i in page.locator('.publication-list > li').all())
                page.evaluate('scrollTo(0,0)')
                page.screenshot(path=str(OUT/f'{Path(name).stem}-{width}.png'),full_page=True)
                report['responsive'].append({'page':name,'width':width,'overflow_px':overflow,'images_loaded':page.locator('main img').count()})
        if not inline:
            page.goto(base+'research.html',wait_until='networkidle')
            page.locator('a[data-figure]').first.click();page.locator('dialog[open]').wait_for()
            page.locator('dialog[open] img').evaluate('(i)=>i.decode()')
            page.keyboard.press('Escape');assert not page.locator('dialog[open]').count()
            for source,target in [('index.html#pub-game','research.html#pub-game'),('index.html#selected-world-action-model','research.html#selected-world-action-model'),('index.html#awards','resume.html#awards'),('publications.html#pub-game','research.html#pub-game'),('index.html#inspiration','about.html#inspiration')]:
                page.goto(base+source);page.wait_for_url(base+target)
                assert page.locator('#'+target.split('#')[1]).count()==1
            page.goto(base+'index.html');page.keyboard.press('Tab')
            assert page.evaluate('document.activeElement.classList.contains("skip-link")')
            nojs=browser.new_context(java_script_enabled=False);np=nojs.new_page()
            np.goto(base+'research.html');assert all(x.is_visible() for x in np.locator('.publication-list > li').all())
            assert np.locator('.publication-list > li').count()==15
            nojs.close();report['navigation_and_keyboard']='PASS';report['no_javascript_record']='PASS'
        else:
            report['navigation_and_keyboard']='Not exercised in offline preview; checked by CI'
        assert not errors,errors
        ctx.close();browser.close()
    return report


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inline-preview',action='store_true');args=ap.parse_args()
    OUT.mkdir(exist_ok=True);report={'design':DESIGN,'static':static_checks()}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        report['browser']=browser_checks(f'http://127.0.0.1:{server.server_port}/',args.inline_preview);report['status']='PASS'
        report['preservation']=json.loads(Path('/tmp/personal-site-style-preservation.json').read_text())
    except Exception as exc:
        report['status']='FAIL';report['error']=str(exc);raise
    finally:
        server.shutdown();server.server_close();(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
