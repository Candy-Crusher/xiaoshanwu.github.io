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
PAGES=['index.html','about.html']
ALIASES=['research.html','publications.html','resume.html']
DESIGN='academic-home-research-20261014'
NAV=['Home','Resume','About']


def text(node): return ' '.join(node.stripped_strings)
def norm(s): return ''.join(s.split()).rstrip('.')


def static_checks():
    spec=importlib.util.spec_from_file_location('site_builder',ROOT/'scripts/build-personal-site.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    cv=builder.parse_cv()
    before={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in PAGES+ALIASES}
    builder.main()
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in before.items()), 'Build is not idempotent'
    docs={n:BeautifulSoup((ROOT/n).read_text(),'html.parser') for n in PAGES+ALIASES}
    for name,doc in docs.items():
        assert doc.body['data-design']==DESIGN
        assert doc.body['data-research-presentation']=='question-first-20261014'
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
    r=docs['index.html'];items=r.select('.publication-list > li')
    assert len(items)==15
    assert len(r.select('.lead-papers > li'))==8 and len(r.select('.collaborative-papers > li'))==7
    for item,paper in zip(items,cv['papers']):
        assert text(item.select_one('.pub-title'))==paper['title']
        assert norm(text(item.select_one('.pub-authors')))==norm(builder.plain(paper['authors']))
        assert 'X.Wu' in norm(text(item.select_one('.pub-authors')))
        assert norm(text(item.select_one('.research-meta > span')))==norm(builder.plain(paper['venue']))
        if paper['role']:assert text(item.select_one('.research-role'))==paper['role']
    assert not docs['index.html'].select('.selected-entry')
    assert len(docs['index.html'].select('[data-paper]')) == 15
    assert len(docs['index.html'].select('.profile-copy > p')) == 2
    biography = docs['index.html'].select_one('.biography')
    bio = text(biography)
    assert bio.startswith('I am a Visiting Scholar at Harvard University')
    assert bio.index('Harvard') < bio.index('University of Hong Kong') < bio.index('Zhejiang University')
    assert all(x in bio for x in ['Yilun Du', 'Mengyu Wang', 'fourth year', 'HKPFS', 'HKUPS', 'University of Illinois Urbana-Champaign'])
    assert 'I am also a fourth-year' not in bio
    # These names must lead to the programmes, not back to our own awards list.
    award_urls = {
        'Hong Kong PhD Fellowship (HKPFS)': 'https://www.ugc.edu.hk/eng/rgc/hkphd/',
        'HKU Presidential Scholarship (HKUPS)': 'https://gradsch.hku.hk/prospective_students/fees_scholarships_and_financial_support/hku_presidential_phd_scholar_programme',
    }
    for label, destination in award_urls.items():
        anchors = [a for a in biography.select('a') if text(a) == label]
        assert len(anchors) == 1 and anchors[0]['href'] == destination, label
        assert anchors[0].get('target') == '_blank' and 'noopener' in anchors[0].get('rel', []), label
    for label, destination in builder.MENTOR_PROFILES.items():
        assert any(text(a) == label and a['href'] == destination for a in biography.select('a')), label
    cfg=json.loads((ROOT/'_site_content/site-presentation.json').read_text())
    interests = text(docs['index.html'].select_one('.research-lead'))
    assert norm(interests) == norm(builder.plain(cfg['home']['research_statement']))
    assert 'Looking ahead, I aim to explore' in interests
    assert docs['index.html'].select_one('.contact-links a[href="Xiaoshan_Wu_CV.pdf"]').get_text()=='CV'
    for doc in docs.values():
        assert all('(PDF)' not in text(a) for a in doc.select('a[href="Xiaoshan_Wu_CV.pdf"]'))
    for name in ['index.html','research.html','publications.html']:
        doc=docs[name]
        assert doc.select_one('#research-title').get_text()=='Research'
        assert doc.select_one('#publications-title').get_text()=='Publications'
        assert text(doc.select_one('.research-question'))==cfg['research']['question']
        assert len(doc.select('.research-direction'))==3
        for node,topic in zip(doc.select('.research-direction'),cfg['research']['directions']):
            assert node.find(id=topic['id']).get_text()==topic['title']
            assert text(node.select_one('div > p'))==topic['text']
            for a,example in zip(node.select('.direction-examples a'),topic['examples']):
                assert a['href']=='#'+example['paper'] and a.get_text()==example['label']
                assert doc.find(id=example['paper']) is not None
        assert not doc.select('#research [data-paper]')
        for item in doc.select('.publication-list > li'):
            nodes=[n.get('class',[]) for n in item.select_one('.research-copy').find_all(recursive=False)]
            assert nodes.index(['pub-title']) < nodes.index(['pub-authors','research-authors']) < nodes.index(['research-meta'])
    for name in ['research.html','publications.html']:
        assert len(docs[name].select('.publication-list > li')) == 15
    for name in ALIASES:
        assert docs[name].select_one('link[rel=canonical]')['href'].endswith('/index.html')
    assert docs['index.html'].select_one('[data-paper="pub-videossm"]')
    home = docs['index.html']
    assert home.body['data-resume-placement'] == 'home'
    assert home.select_one('#resume h2').get_text() == 'Resume'
    assert len(home.select('#resume')) == 1
    assert home.select_one('#experience h3').get_text()=='Research Experience'
    assert 'Harvard' in text(home.select_one('#experience'))
    assert 'Harvard' not in text(home.select_one('#education'))
    assert home.select_one('#awards h3').get_text()=='Selected Awards'
    assert home.select_one('nav[aria-label="Main navigation"] a[href="#resume"]')
    assert home.select_one('nav[aria-label="Main navigation"] a[href="#top"]')
    assert docs['about.html'].select_one('nav[aria-label="Main navigation"] a[href="index.html#resume"]')
    assert not home.select('a[href^="resume.html"]')
    sections=[n.get('id') for n in home.select('main > section')]
    assert sections.index('research') < sections.index('publications') < sections.index('resume')
    for name in ['index.html','resume.html']:
        for award in cv['awards']:assert norm(builder.plain(award)) in norm(text(docs[name].select_one('#awards')))
        for skill in cv['skills']:assert norm(builder.plain(skill)) in norm(text(docs[name].select_one('#skills')))
        for anchor in ['experience','education','skills','awards']:
            assert norm(text(home.select_one('#'+anchor))) == norm(text(docs['resume.html'].select_one('#'+anchor)))
        assert len(docs[name].select('#resume a[href="Xiaoshan_Wu_CV.pdf"]')) == 2
    for name in ['resume.html','research.html','publications.html']:
        assert 'agent–world model co-evolution' not in text(docs[name].main), name
    assert 'agent–world model co-evolution' in text(docs['about.html'].main)
    assert 'agent–world model co-evolution' in text(docs['index.html'].select_one('.research-lead'))
    return {'navigation':NAV,'unique_publications':15,'first_author_work':8,'collaborative_work':7,'homepage_research_records':15,'intro_paragraphs':2,'harvard_first':True,'resume_on_home':True,'native_resume_navigation':True,'resume_content_matches_cv02':True,'official_scholarship_links':True,'mentor_links_preserved':True,'research_interest_source':'Web-specific paraphrase grounded in CV02','research_overview':'Central question + three connected lines of work with linked examples','cv_label':'CV','metadata_matches_cv02':True,'standalone_awards':True,'no_duplicate_project_list':True,'legacy_fallbacks':True,'internal_resources':'PASS','repeat_build':'PASS'}


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
                if name=='index.html':
                    assert all(i.is_visible() for i in page.locator('.publication-list > li').all())
                page.evaluate('scrollTo(0,0)')
                page.screenshot(path=str(OUT/f'{Path(name).stem}-{width}.png'),full_page=True)
                report['responsive'].append({'page':name,'width':width,'overflow_px':overflow,'images_loaded':page.locator('main img').count()})
        if not inline:
            page.goto(base+'index.html',wait_until='networkidle')
            for anchor in page.locator('.research-jump, .direction-examples a').all():
                expected=anchor.get_attribute('href');anchor.click();page.wait_for_url(base+'index.html'+expected)
                assert page.locator(expected).count()==1
            page.goto(base+'index.html',wait_until='networkidle')
            page.locator('a[data-figure]').first.click();page.locator('dialog[open]').wait_for()
            page.locator('dialog[open] img').evaluate('(i)=>i.decode()')
            page.keyboard.press('Escape');assert not page.locator('dialog[open]').count()
            routes=[('research.html','index.html#research'),('publications.html','index.html#research'),('index.html#pub-game','index.html#pub-game'),('research.html#pub-game','index.html#pub-game'),('publications.html#pub-game','index.html#pub-game'),('index.html#selected-world-action-model','index.html#selected-world-action-model'),('research.html#projects','index.html#projects'),('index.html#awards','index.html#awards'),('index.html#inspiration','about.html#inspiration'),('resume.html','index.html#resume'),('resume.html#awards','index.html#awards'),('resume.html#experience','index.html#experience'),('resume.html#education','index.html#education'),('resume.html#skills','index.html#skills'),('resume.html?from=old#awards','index.html?from=old#awards'),('resume.html#research-interests','index.html#research-interests'),('resume.html#resume-publications','index.html#publications')]
            for source,target in routes:
                page.goto(base+source);page.wait_for_url(base+target)
                assert page.locator('#'+target.split('#')[1]).count()==1
            # Every previously shared paper anchor reaches the same record.
            for item in BeautifulSoup((ROOT/'index.html').read_text(),'html.parser').select('.publication-list > li'):
                page.goto(base+'research.html#'+item['id'])
                page.wait_for_url(base+'index.html#'+item['id'])
                assert page.locator('#'+item['id']).count()==1
            page.goto(base+'index.html');page.keyboard.press('Tab')
            assert page.evaluate('document.activeElement.classList.contains("skip-link")')
            nojs=browser.new_context(java_script_enabled=False);np=nojs.new_page()
            for name in ['index.html','research.html','publications.html']:
                np.goto(base+name)
                assert np.locator('.publication-list > li').count()==15
                assert all(x.is_visible() for x in np.locator('.publication-list > li').all())
            np.goto(base+'resume.html')
            assert np.locator('#awards li').count() == 4
            np.goto(base+'index.html')
            np.locator('.site-nav a[href="#resume"]').click()
            assert np.url == base+'index.html#resume'
            assert np.locator('#resume-title').is_visible()
            nojs.close();report['navigation_and_keyboard']='PASS';report['no_javascript_record']='PASS';report['no_javascript_resume']='PASS'
            # Confirm these controls only change the hash, not the document.
            report['native_anchor_checks']=[]
            for width in [390,1440]:
                page.set_viewport_size({'width':width,'height':900})
                page.goto(base+'index.html',wait_until='networkidle')
                page.evaluate('window.__resumeNavigationSentinel = "same-document"')
                page.locator('.site-nav a[href="#resume"]').click()
                page.wait_for_url(base+'index.html#resume')
                assert page.evaluate('window.__resumeNavigationSentinel') == 'same-document'
                header_bottom=page.locator('.site-topbar').bounding_box()['height']
                heading=page.locator('#resume-title').bounding_box()
                assert header_bottom <= heading['y'] < 400, (width, header_bottom, heading)
                assert page.locator('.site-nav a[href="#resume"]').get_attribute('aria-current') == 'location'
                page.screenshot(path=str(OUT/f'resume-section-{width}.png'))
                page.locator('.site-nav a[href="#top"]').click()
                assert page.evaluate('window.__resumeNavigationSentinel') == 'same-document'
                assert page.evaluate('scrollY') < 5
                page.go_back()
                page.wait_for_url(base+'index.html#resume')
                assert page.evaluate('window.__resumeNavigationSentinel') == 'same-document'
                page.locator('nav[aria-label="Resume sections"] a[href="#awards"]').click()
                page.wait_for_url(base+'index.html#awards')
                awards=page.locator('#awards').bounding_box()
                assert awards['y'] >= header_bottom, (width, awards, header_bottom)
                assert page.evaluate('window.__resumeNavigationSentinel') == 'same-document'
                report['native_anchor_checks'].append({'width':width,'same_document':True,'heading_below_navigation':True,'back_navigation':True,'awards_jump':True})

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
