#!/usr/bin/env python3
"""Full bylines, venue format, one-sentence summaries, links, fonts and favicon."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json,os,sys
from publication_style import load_details,authors_markup,venue_markup,VERSION
from site_favicon import apply_favicon
ROOT=Path(__file__).resolve().parents[1]
SANDBOX_AUTHORS = ['Xiaoshan Wu', 'Ruojin Cai', 'Yiming Bao', 'Zihan Su',
                   'Anne Wu', 'Feiyang Wu', 'Zhiyi Li', 'Zhenting Qi',
                   'Haonan Chen', 'Weirui Ye', 'Jing Zhang', 'Kaichen Zhou',
                   'Mengyu Wang', 'Yilun Du']

def compact(text):return ''.join(text.split())
def check_document(doc):
    data=load_details()
    for path in ['mountain.svg','mountain-32.png','mountain.ico']:
        assert doc.select_one('head link[rel="icon"][href*="'+path+'"]'),path
    record=doc.select_one('.publications-record')
    if record is None:return
    assert record['data-publication-style']==VERSION
    assert [e['id'] for e in record.select('.publication-entry')]==list(data['papers'])
    for key,r in data['papers'].items():
        e=record.find(id=key)
        expected=BeautifulSoup(authors_markup(r,data['profiles']),'html.parser').get_text()
        assert compact(e.select_one('.pub-authors').get_text())==compact(expected),key
        nodes=e.select('.pub-author');assert len(nodes)==len(r['authors'])
        for node,a in zip(nodes,r['authors']):
            if a['name'] in data['profiles']:
                href='#top' if a['name']=='Xiaoshan Wu' else data['profiles'][a['name']]
                assert node.select_one('a')['href']==href,(key,a)
            else:assert not node.select('a'),(key,a)
        assert e.select_one('.pub-author-self strong').get_text()=='Xiaoshan Wu'
        assert len(e.select('.pub-tldr'))==1
        assert e.select_one('.pub-tldr').get_text()=='TL;DR: '+r['tldr'],key
        assert e.select_one('.pub-tldr').find_next_sibling().get('class')==['research-links']
        expected=BeautifulSoup(venue_markup(r),'html.parser').get_text()
        assert compact(e.select_one('.research-meta').get_text())==compact(expected),key
        labels=[a.get_text() for a in e.select('.research-links a')]
        assert len(labels)==len(set(labels)) and labels
        if 'Project' in labels:assert labels[0]=='Project'
        if 'Paper' in labels:assert labels.index('Paper')==(1 if 'Project' in labels else 0)
        assert not e.select('[data-full-name-pending]'),key
    # The author's supplied OpenReview record resolves the last nine initials.
    sandbox=data['papers']['pub-world-action-model']
    assert [a['name'] for a in sandbox['authors']]==SANDBOX_AUTHORS
    assert list(sandbox['openreview_author_profiles'])==SANDBOX_AUTHORS
    assert [a['marks'] for a in sandbox['authors']]==['*','*']+['']*12
    assert len(record.select('#pub-world-action-model .pub-author a'))==14
    for name in ['Feiyang Wu','Jing Zhang']:
        assert data['profiles'][name]==sandbox['openreview_author_profiles'][name]
    assert not record.select('[data-full-name-pending]')
    assert not record.select('.research-evidence, .research-role')
    assert 'Oral' not in record.get_text() and 'top 1%' not in record.get_text()
    assert len(record.select('.pub-distinction'))==1
    assert record.select_one('#pub-eag3r .pub-distinction').get_text()=='Spotlight'

def main():
    out=ROOT/'publication-style-review';out.mkdir(exist_ok=True)
    for name in ['index.html','about.html','resume.html','research.html','publications.html']:
        raw=(ROOT/name).read_text();check_document(BeautifulSoup(raw,'html.parser'))
        assert apply_favicon(raw,name)==raw
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    base=sys.argv[1].rstrip('/')+'/' if len(sys.argv)>1 else f'http://127.0.0.1:{server.server_port}/'
    report={'status':'PASS','url':base,'views':[],
            'author_entries':sum(len(r['authors']) for r in load_details()['papers'].values()),
            'full_name_pending':{},'sandbox_full_names':SANDBOX_AUTHORS,'sandbox_author_links':14}
    try:
        with sync_playwright() as pw:
            exe=os.getenv('BROWSER_EXECUTABLE')
            browser=pw.chromium.launch(**({'executable_path':exe} if exe else {}))
            page=browser.new_page(reduced_motion='reduce')
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            for width in [390,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                response=page.goto(base+'index.html',wait_until='networkidle');assert response.status==200
                check_document(BeautifulSoup(page.content(),'html.parser'))
                page.evaluate("document.fonts.load('15px Lato')")
                assert page.evaluate("document.fonts.check('15px Lato')")
                assert page.locator('#pub-eag3r .pub-title').evaluate('(e)=>getComputedStyle(e).fontFamily').startswith('Lato')
                assert page.locator('#pub-eag3r .pub-title').evaluate('(e)=>getComputedStyle(e).fontSize')=='15px'
                colors=page.locator('#pub-world-action-model .pub-authors, #pub-world-action-model .pub-authors *').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).color)')
                assert all(c=='rgb(0, 0, 0)' for c in colors),colors
                page.locator('#publications .research-media img').evaluate_all('(images)=>images.forEach(i=>i.loading="eager")')
                for image in page.locator('#publications .research-media img').all():
                    image.evaluate('(i)=>i.decode()')
                    d=image.evaluate('(i)=>({w:i.clientWidth,h:i.clientHeight,nw:i.naturalWidth,nh:i.naturalHeight})')
                    assert abs(d['h']-d['w']*d['nh']/d['nw'])<2
                page.locator('#publications').screenshot(path=str(out/f'publications-{width}.png'))
                for key in ['world-action-model','lifr-seg','eag3r','ugg','neural-field-memory']:
                    page.locator('#pub-'+key).screenshot(path=str(out/f'{key}-{width}.png'),style='.site-topbar{visibility:hidden!important}')
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                if width==1440:
                    for entry in page.locator('.publication-entry').all():
                        ys=[a.bounding_box()['y'] for a in entry.locator('.research-links a').all()]
                        assert max(ys)-min(ys)<2,'Resource links must fit on one desktop line'
                for node in page.locator('head link[rel="icon"]').all():
                    url=node.evaluate('(e)=>e.href')
                    r=page.request.get(url);assert r.status==200,url
                svg=page.request.get(base+'assets/icons/mountain.svg')
                assert '<title>⛰️</title>' in svg.text()
                report['views'].append({'width':width,'font':'Lato','icons_loaded':True,'uncropped_covers':True,'resource_rows':True,'sandbox_names_all_black':True})
            assert not errors,errors
            browser.close()
    finally:server.shutdown()
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
