#!/usr/bin/env python3
"""Validate the single-page site, original research metadata and legacy routes."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlsplit, unquote
import hashlib
import importlib.util
import json
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'personal-site-qa'
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html', 'publications.html']
NAV = [('Home', 'top'), ('News', 'news'), ('Research', 'research'),
       ('Experience', 'experience'), ('Award', 'awards'), ('About', 'about')]
LAYOUT = 'monthly-news-review-20261015-v1'


def text(node):
    return ' '.join(node.stripped_strings)


def norm(value):
    return ''.join(value.split()).rstrip('.')


def static_checks():
    spec = importlib.util.spec_from_file_location('site_builder', ROOT/'scripts/build-personal-site.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    cv = builder.parse_cv()
    raw_cv = builder.core.parse_cv()
    for visible, original in zip(cv['papers'], raw_cv['papers']):
        expected = 'Under review' if 'under review' in builder.plain(original['venue']).lower() else original['venue']
        assert visible['venue'] == expected
        assert {k:v for k,v in visible.items() if k!='venue'} == {k:v for k,v in original.items() if k!='venue'}

    before = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in PAGES}
    builder.main()
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest() == h for n, h in before.items()), 'Build is not idempotent'
    docs = {n: BeautifulSoup((ROOT/n).read_text(), 'html.parser') for n in PAGES}
    cfg = json.loads((ROOT/'_site_content/site-presentation.json').read_text())
    for name, doc in docs.items():
        assert doc.body['data-single-page'] == LAYOUT
        assert doc.body['data-resume-source-blob'] == cv['source_git_blob']
        assert len(doc.select('h1')) == 1 and len(doc.select('main')) == 1
        ids = [n['id'] for n in doc.select('[id]')]
        assert len(ids) == len(set(ids)), (name, 'Duplicate IDs')
        assert text(doc.select_one('.wordmark')) == "Xiaoshan's Homepage"
        assert [text(a) for a in doc.select('.site-nav a')] == [label for label, _ in NAV]
        prefix = '' if name == 'index.html' else 'index.html'
        assert [a['href'] for a in doc.select('.site-nav a')] == [prefix+'#'+anchor for _, anchor in NAV]
        assert not any(a.get('target') for a in doc.select('.site-nav a'))
        assert doc.select_one('link[rel=canonical]')['href'].endswith('/index.html')
        for element in doc.select('a[href], main img[src], main source[src], script[src], link[rel=stylesheet][href]'):
            url = urlsplit(element.get('href', element.get('src', '')))
            if url.scheme or url.netloc:
                continue
            local = ROOT/unquote(url.path or name)
            if local.is_dir():
                local /= 'index.html'
            assert local.is_file(), (name, str(url), 'Missing internal resource')
            if url.fragment and local.suffix == '.html':
                assert BeautifulSoup(local.read_text(), 'html.parser').find(id=unquote(url.fragment)), (name, str(url), 'Missing anchor')
    home = docs['index.html']
    assert not home.select('a[href^="about.html"], a[href^="resume.html"]')
    sections = [n.get('id') for n in home.select('main > section')]
    assert sections == ['welcome', 'news', 'research', 'publications', 'experience', 'awards', 'about'], sections
    biography = home.select_one('.biography')
    assert text(biography).startswith('I am a Visiting Scholar at Harvard University')
    assert norm(text(biography)) == norm(builder.plain(cfg['home']['identity']))
    assert norm(text(home.select_one('.research-lead'))) == norm(builder.plain(cfg['home']['research_statement']))
    assert 'Looking ahead, I aim to explore' in text(home.select_one('.research-lead'))
    assert len(home.select('.profile-copy > p')) == 2
    for label, url in builder.MENTOR_PROFILES.items():
        assert any(text(a) == label and a['href'] == url for a in biography.select('a'))
    for url in ['https://www.ugc.edu.hk/eng/rgc/hkphd/', 'https://gradsch.hku.hk/prospective_students/fees_scholarships_and_financial_support/hku_presidential_phd_scholar_programme']:
        assert biography.find('a', href=url)
    assert home.select_one('.contact-links a[href="Xiaoshan_Wu_CV.pdf"]').get_text() == 'CV'
    for name in ['index.html', 'research.html', 'publications.html']:
        doc = docs[name]
        items = doc.select('.publication-list > li')
        assert len(items) == 15 and len(doc.select('.lead-papers > li')) == 8 and len(doc.select('.collaborative-papers > li')) == 7
        for item, paper in zip(items, cv['papers']):
            assert text(item.select_one('.pub-title')) == paper['title']
            assert norm(text(item.select_one('.pub-authors'))) == norm(builder.plain(paper['authors']))
            assert norm(text(item.select_one('.research-meta > span'))) == norm(builder.plain(paper['venue']))
            if paper['role']:
                assert text(item.select_one('.research-role')) == paper['role']
        assert text(doc.select_one('.research-question')) == cfg['research']['question']
        assert len(doc.select('.research-direction')) == 3
        for item, topic in zip(doc.select('.research-direction'), cfg['research']['directions']):
            assert item.find(id=topic['id']).get_text() == topic['title']
            assert text(item.select_one('div > p')) == topic['text']
        assert doc.select_one('video.research-video source')['src'] == 'projects/sandbox/static/videos/disco_light_10x.mp4'
        assert doc.select_one('a[href="projects/sandbox/rdf-viewer.html?case=pose-1"]')
    news = json.loads((ROOT/'_site_content/news.json').read_text())
    events = sorted(news['entries'], key=lambda e:e['month'], reverse=True)
    assert [time['datetime'] for time in home.select('#news time')] == [event['month'] for event in events]
    assert [time.get_text() for time in home.select('#news time')] == [event['month'].replace('-', '.') for event in events]
    assert [dd['data-news-id'] for dd in home.select('#news dd')] == [event['id'] for event in events]
    for row, event in zip(home.select('#news dd'), events):
        assert norm(text(row)) == norm(builder.plain(event['html']))
        assert event['sources'] and event['month_basis']
        if event['kind'] == 'conference_acceptance':
            assert len(event['paper_ids']) == 1 and 'One paper accepted' in text(row)
    assert next(e for e in events if e['id']=='harvard-arrival')['month'] == '2026-05'
    assert next(e for e in events if e['id']=='nature-acceptance')['month'] == '2026-05'
    assert not any('pub-videossm' in e['paper_ids'] for e in events)
    assert len(home.select('.publication-list .research-meta > span:first-child')) == 15
    for node in home.select('.publication-list .research-meta > span:first-child'):
        if 'under review' in text(node).lower():
            assert text(node) == 'Under review'
    entries = home.select('.experience-timeline > li')
    assert [e['data-institution'] for e in entries] == ['harvard', 'hku', 'zjui']
    assert len(home.select('.institution-tile img')) == 4
    manifest = json.loads((ROOT/'assets/institutions/sources.json').read_text())
    for school in ['zju', 'uiuc']:
        node = home.select_one('.logo-' + school)
        assert node['src'] == 'assets/institutions/' + school + '.svg'
        raw = (ROOT/node['src']).read_bytes()
        svg = ET.fromstring(raw)
        assert svg.tag.endswith('}svg') and svg.get('viewBox')
        assert len(svg.findall('.//{http://www.w3.org/2000/svg}path')) >= 2
        assert not svg.findall('.//{http://www.w3.org/2000/svg}image')
        assert not svg.findall('.//{http://www.w3.org/2000/svg}script')
        assert hashlib.sha256(raw).hexdigest() == manifest[school]['sha256']
        assert manifest[school]['format'] == 'svg'
    for entry, school in zip(entries, cv['education']):
        assert text(entry.h3) == school['school']
        assert text(entry.select_one('.timeline-position')) == school['role']
        assert school['dates'] in text(entry.select_one('.timeline-dates'))
        for detail in school['details']:
            assert norm(builder.plain(detail)) in norm(text(entry))
    for award in cv['awards']:
        assert norm(builder.plain(award)) in norm(text(home.select_one('#awards')))
    for skill in cv['skills']:
        assert norm(builder.plain(skill)) in norm(text(home.select_one('#skills')))
    for anchor in ['resume', 'education', 'background', 'inspiration', 'skills']:
        assert home.find(id=anchor)
    # Website-only omissions must not remove the surrounding honors or advisor.
    for name in ['index.html', 'resume.html']:
        visible = text(docs[name].main)
        assert 'GPA' not in visible and 'Rank 5' not in visible
        assert 'Outstanding Graduate' in visible and "Dean's List" in visible
    advisor = home.select_one('[data-institution="hku"] a[href="https://xjqi.github.io/"]')
    assert advisor and text(advisor) == 'Xiaojuan Qi'
    about_source = BeautifulSoup((ROOT/'_site_content/about-personal.html').read_text(), 'html.parser')
    for name in ['index.html', 'about.html']:
        about = docs[name].select_one('[data-about-version="science-fiction-to-physical-agents-v1"]')
        assert about is not None
        story = about.select_one('.about-story')
        assert text(story) == text(about_source.select_one('.about-story'))
        assert not about.select('.about-background-link')
        assert not any(text(h) in ['Research perspective', 'Looking ahead'] for h in about.select('h2,h3'))
        assert 'Visiting Scholar' not in text(about) and 'fourth-year' not in text(about)
        assert 'Science fiction has fascinated me since childhood.' in text(story)
        assert 'I believe that LLM-based AGI may arrive soon.' in text(story)
        assert 'not be tied to a single body' in text(story)
        assert 'under human supervision' in text(story)
        assert all(title in text(story) for title in ['Hyperion', 'Foundation', 'WALL-E', 'Interstellar', 'Ready Player One', 'Pantheon', 'The Matrix', 'Blade Runner 2049'])
        assert len(story.select('p')) == 6
    assert 'Blade Runner 2049' in text(home.select_one('#about'))
    assert not home.select('details, .selected-entry')
    return {'static': 'PASS', 'publication_metadata': 'CV02: 15 papers, authors/status/order unchanged',
            'experience_order': ['Harvard', 'HKU', 'ZJU & UIUC'], 'repeatable_build': True,
            'internal_links': 'PASS', 'source_git_blob': cv['source_git_blob']}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def browser_checks(base):
    report = {'responsive': [], 'native_navigation': [], 'legacy_routes': []}
    with sync_playwright() as pw:
        executable = os.getenv('BROWSER_EXECUTABLE')
        browser = pw.chromium.launch(**({'executable_path': executable} if executable else {}))
        ctx = browser.new_context(reduced_motion='reduce')
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        for width in [320, 390, 600, 768, 1024, 1440]:
            page.set_viewport_size({'width': width, 'height': 1000})
            assert page.goto(base+'index.html', wait_until='networkidle').status == 200
            page.locator('main img').evaluate_all('(images)=>images.forEach(i=>i.loading="eager")')
            for image in page.locator('main img').all():
                image.evaluate('(i)=>i.decode()')
            overflow = page.evaluate('document.documentElement.scrollWidth-innerWidth')
            assert overflow <= 1, (width, overflow)
            assert page.locator('.site-nav a').count() == 6
            page.evaluate('window.__sameDocument = "preserved"')
            page.screenshot(path=str(OUT/f'homepage-{width}.png'), full_page=True)
            for label, anchor in NAV:
                page.locator('.site-nav a').filter(has_text=label).click()
                page.wait_for_timeout(120)
                assert urlsplit(page.url).path.endswith('/index.html') and urlsplit(page.url).fragment == anchor
                assert page.evaluate('window.__sameDocument') == 'preserved', (label, 'Document reloaded')
                assert page.locator('.site-nav a[aria-current]').inner_text() == label
                if anchor != 'top':
                    top = page.locator('#'+anchor).bounding_box()['y']
                    header_bottom = page.locator('.site-topbar').bounding_box()['height']
                    assert top >= header_bottom-2, (width, label, 'Heading obscured', top, header_bottom)
                if label == 'News':
                    page.locator('#news').screenshot(path=str(OUT/f'news-{width}.png'))
                if label == 'About':
                    page.locator('#about').screenshot(path=str(OUT/f'about-{width}.png'))
                if label == 'Experience':
                    page.screenshot(path=str(OUT/f'experience-{width}.png'))
                report['native_navigation'].append({'width': width, 'section': label, 'same_document': True})
            page.locator('.wordmark').click()
            assert page.evaluate('scrollY') < 4
            page.screenshot(path=str(OUT/f'header-{width}.png'))
            report['responsive'].append({'width': width, 'overflow_px': overflow, 'loaded_images': page.locator('main img').count()})
        retina = browser.new_context(viewport={'width': 390, 'height': 1000},
                                     device_scale_factor=3, reduced_motion='reduce')
        rp = retina.new_page()
        rp.goto(base+'index.html#experience', wait_until='networkidle')
        for logo in rp.locator('.institution-pair img').all():
            logo.evaluate('(i)=>i.decode()')
            assert logo.evaluate('(i)=>i.complete && i.naturalWidth>0')
            assert logo.get_attribute('src').endswith('.svg')
        rp.screenshot(path=str(OUT/'experience-mobile-retina.png'))
        assert rp.evaluate('document.documentElement.scrollWidth-innerWidth') <= 1
        retina.close()
        report['retina_vector_logos'] = 'PASS: 3x mobile display'
        # Back/forward, deep anchors, manually scrolling, keyboard, figure dialog.
        page.locator('.site-nav a[href="#news"]').click()
        page.locator('.site-nav a[href="#experience"]').click()
        page.go_back()
        assert urlsplit(page.url).fragment == 'news'
        page.go_forward()
        assert urlsplit(page.url).fragment == 'experience'
        page.locator('#awards').evaluate('(e)=>e.scrollIntoView()')
        page.wait_for_timeout(100)
        assert page.locator('.site-nav a[aria-current]').inner_text() == 'Award'
        page.locator('a[data-figure]').first.click()
        assert page.locator('dialog').is_visible()
        page.keyboard.press('Escape')
        assert not page.locator('dialog').is_visible()
        page.goto(base+'index.html#inspiration', wait_until='networkidle')
        assert '/index.html#inspiration' in page.url
        for legacy, target in [('about.html','#about'),('about.html#inspiration','#inspiration'),('resume.html','#experience'),('resume.html#education','#education'),('research.html#pub-game','#pub-game'),('publications.html','#research')]:
            page.goto(base+legacy, wait_until='networkidle')
            assert page.url == base+'index.html'+target, (legacy, page.url)
            report['legacy_routes'].append({'source': legacy, 'destination': target})
        page.goto(base+'index.html', wait_until='networkidle')
        page.keyboard.press('Tab')
        assert page.locator('.skip-link').evaluate('(e)=>e===document.activeElement')
        page.keyboard.press('Enter')
        assert urlsplit(page.url).fragment == 'main'
        assert not errors, errors
        ctx.close()
        nojs = browser.new_context(java_script_enabled=False, reduced_motion='reduce', viewport={'width':390,'height':1000})
        p = nojs.new_page()
        p.goto(base+'index.html', wait_until='networkidle')
        assert p.locator('.publication-list > li').count() == 15
        for label, anchor in NAV:
            p.locator('.site-nav a').filter(has_text=label).click()
            assert p.url == base+'index.html#'+anchor
        for legacy in PAGES[1:]:
            p.goto(base+legacy, wait_until='networkidle')
            assert p.locator('main').inner_text().strip()
        nojs.close()
        browser.close()
    report['no_javascript'] = 'PASS'
    report['back_forward_keyboard_dialog'] = 'PASS'
    return report


def main():
    OUT.mkdir(exist_ok=True)
    report = static_checks()
    server = ThreadingHTTPServer(('127.0.0.1',0), partial(QuietHandler,directory=str(ROOT)))
    thread = Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        report.update(browser_checks(f'http://127.0.0.1:{server.server_port}/'))
    finally:
        server.shutdown()
    (OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
