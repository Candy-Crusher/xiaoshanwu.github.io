#!/usr/bin/env python3
"""Content, keyboard, no-JS and responsive checks for the personal website.

The existing personal-site workflow installs Playwright/Chromium and uploads
personal-site-qa. No CV or project microsite is modified by these tests.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit, unquote
from threading import Thread
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'personal-site-qa'
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html']
DESIGN = 'quiet-academic-20261013'
SLUGS = ['sandbox', 'game', 'eag3r', 'videossm', 'lifr-seg', 'lifr-v2', 'evsplat']


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def local_file(url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = (ROOT / unquote(parsed.path)).resolve()
    if path.is_dir():
        path /= 'index.html'
    return path


def static_checks():
    report = {}
    for name in PAGES:
        doc = BeautifulSoup((ROOT / name).read_text(), 'html.parser')
        assert doc.body.get('data-design') == DESIGN, name
        labels = [a.get_text(strip=True) for a in doc.select('nav[aria-label="Main navigation"] a')]
        assert labels == ['Home', 'About', 'Resume', 'Research'], (name, labels)
        assert len(doc.select('main')) == 1 and len(doc.select('h1')) == 1, name
        assert not doc.select('.cinematic-shell, .hero-scrim'), name
        for tag in doc.select('img[src], script[src], link[rel="stylesheet"][href]'):
            path = local_file(tag.get('src', tag.get('href', '')))
            assert path is None or path.is_file(), (name, str(path))
        report[name] = {'navigation': labels, 'heading': doc.h1.get_text(' ', strip=True)}
    doc = BeautifulSoup((ROOT / 'research.html').read_text(), 'html.parser')
    assert len(doc.select('.project-grid > .research-entry')) == 7
    assert len(doc.select('.publication-list > li')) == 15
    for item in doc.select('.publication-list > li'):
        assert 'X.Wu' in item.get_text().replace(' ', '').replace('\n', ''), item.get('id')
    for slug in SLUGS:
        assert (ROOT / 'projects' / slug / 'index.html').is_file(), slug
    resume = BeautifulSoup((ROOT / 'resume.html').read_text(), 'html.parser')
    assert any('award' in h.get_text().lower() or 'honor' in h.get_text().lower() for h in resume.select('h2'))
    assert (ROOT / 'Xiaoshan_Wu_CV.pdf').is_file()
    report['record'] = {'projects': 7, 'publications': 15, 'separate_awards_section': True}
    return report


def browser_checks(base):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(device_scale_factor=1, reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda exc: errors.append(str(exc)))
        for width in [320, 390, 768, 1024, 1440]:
            page.set_viewport_size({'width': width, 'height': 900})
            for name in PAGES:
                response = page.goto(base + name, wait_until='networkidle')
                assert response.status == 200, (name, response.status)
                page.locator('body[data-design="' + DESIGN + '"]').wait_for()
                for image in page.locator('img').all():
                    image.scroll_into_view_if_needed()
                    image.evaluate('(img) => img.decode().catch(() => {})')
                    assert image.evaluate('(img) => img.complete && img.naturalWidth > 0'), (name, image.get_attribute('src'))
                dimensions = page.evaluate('({viewport: innerWidth, document: document.documentElement.scrollWidth, body: document.body.scrollWidth})')
                assert max(dimensions['document'], dimensions['body']) <= width + 1, (name, width, dimensions)
                animations = page.evaluate('document.getAnimations().filter(a => a.playState === "running").length')
                assert animations == 0, (name, animations)
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(OUT / f'{Path(name).stem}-{width}.png'), full_page=True)
                results.append({'page': name, 'width': width, 'overflow_px': max(dimensions['document'], dimensions['body']) - width, 'loaded_images': page.locator('img').count(), 'animations': animations})
        page.set_viewport_size({'width': 1024, 'height': 900})
        page.goto(base + 'research.html', wait_until='networkidle')
        page.locator('#selected-world-action-model [data-figure]').first.click()
        page.locator('dialog[open]').wait_for()
        page.keyboard.press('Escape')
        assert page.locator('dialog[open]').count() == 0
        legacy = [
            ('index.html#selected-world-action-model', 'research.html#selected-world-action-model'),
            ('index.html#inspiration', 'about.html#inspiration'),
            ('publications.html#pub-game', 'research.html#pub-game'),
        ]
        for source, target in legacy:
            page.goto(base + source, wait_until='networkidle')
            page.wait_for_url(base + target)
        page.goto(base + 'research.html#pub-game', wait_until='networkidle')
        assert page.locator('#publications').get_attribute('open') is not None
        assert not errors, errors
        context.close()
        no_js = browser.new_context(java_script_enabled=False, viewport={'width':390, 'height':844})
        offline_page = no_js.new_page()
        offline_page.goto(base + 'research.html', wait_until='networkidle')
        offline_page.locator('.publication-archive > summary').click()
        assert offline_page.locator('.publication-list > li').count() == 15
        assert offline_page.locator('#pub-game').is_visible()
        no_js.close()
        browser.close()
    return {'responsive': results, 'dialog_keyboard': 'PASS', 'legacy_anchors': 'PASS', 'no_javascript_archive': 'PASS', 'javascript_errors': errors}


def main():
    OUT.mkdir(exist_ok=True)
    report = {'design': DESIGN, 'static': static_checks()}
    preservation = Path('/tmp/personal-site-style-preservation.json')
    if preservation.exists():
        report['preservation'] = json.loads(preservation.read_text())
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        report['browser'] = browser_checks(f'http://127.0.0.1:{server.server_port}/')
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc)
        raise
    finally:
        server.shutdown()
        server.server_close()
        (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
