#!/usr/bin/env python3
"""Check static assets, desktop/mobile layout, figure dialogs, and citation controls."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote
import functools, threading, json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['videossm', 'game', 'lifr-seg', 'lifr-v2', 'evsplat']
output = ROOT / 'project-pages-qa'
output.mkdir(exist_ok=True)
errors, reports = [], []
for slug in SLUGS:
    path = ROOT / 'projects' / slug / 'index.html'
    soup = BeautifulSoup(path.read_text(), 'html.parser')
    ids = [tag['id'] for tag in soup.select('[id]')]
    if len(ids) != len(set(ids)):
        errors.append({'slug': slug, 'error': 'Duplicate HTML IDs'})
    for tag in soup.select('[href], [src]'):
        url = tag.get('href', tag.get('src', ''))
        parsed = urlparse(url)
        if parsed.scheme or parsed.netloc or not url:
            continue
        if not parsed.path:
            if parsed.fragment and parsed.fragment not in ids:
                errors.append({'slug': slug, 'error': 'Missing anchor', 'url': url})
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.exists():
            errors.append({'slug': slug, 'error': 'Missing local target', 'url': url})
handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width, height in [(1440, 1000), (390, 844)]:
            page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
            for slug in SLUGS:
                try:
                    url = f'http://127.0.0.1:{server.server_port}/projects/{slug}/'
                    page.goto(url, wait_until='networkidle')
                    page.evaluate('async () => {for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0)}')
                    page.wait_for_timeout(300)
                    check = page.evaluate('''() => ({title:document.title,h1:document.querySelectorAll('h1').length,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.querySelectorAll('main img')].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)})''')
                    if check['overflow'] or check['h1'] != 1 or check['brokenImages']:
                        errors.append({'slug': slug, 'width': width, **check})
                    page.screenshot(path=str(output / f'{slug}-{width}.png'), full_page=True)
                    if page.locator('.figure-link').count():
                        page.locator('.figure-link').first.click()
                        assert page.locator('dialog[open]').count() == 1, 'Figure dialog failed to open'
                        page.keyboard.press('Escape')
                        assert page.locator('dialog[open]').count() == 0, 'Figure dialog failed to close'
                    if page.locator('[data-copy]').count():
                        page.locator('[data-copy]').click()
                        page.wait_for_function("document.querySelector('#copy-status').textContent.length > 0")
                    reports.append({'slug': slug, 'width': width, **check})
                except Exception as exc:
                    errors.append({'slug': slug, 'width': width, 'error': str(exc)})
            page.close()
        browser.close()
finally:
    server.shutdown()
    (output / 'report.json').write_text(json.dumps({'checks': reports, 'errors': errors}, indent=2))
if errors:
    raise SystemExit(json.dumps(errors, indent=2))
print('PASS: five pages, desktop/mobile, local links, figures, dialogs, and citation controls.')
