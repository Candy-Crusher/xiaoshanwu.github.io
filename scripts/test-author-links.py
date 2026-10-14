#!/usr/bin/env python3
"""Check author link destinations and black normal/hover/focus presentation."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import json, os, sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from publication_style import load_details, load_profile_additions, VERSION, PROFILE_LABELS

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = load_details()
    additions = load_profile_additions()
    out = ROOT / 'author-links-review'
    out.mkdir(exist_ok=True)
    doc = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
    for key, record in data['papers'].items():
        authors = doc.select('#' + key + ' .pub-author')
        assert len(authors) == len(record['authors']), key
        for node, author in zip(authors, record['authors']):
            name = author['name']
            if name in additions:
                profile = additions[name]
                link = node.select_one('a')
                assert link and link['href'] == profile['url'], name
                assert link['data-profile-kind'] == profile['kind'], name
                assert link['title'] == name + ' — ' + PROFILE_LABELS[profile['kind']], name
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = sys.argv[1].rstrip('/') + '/' if len(sys.argv) > 1 else f'http://127.0.0.1:{server.server_port}/'
    report = {'version': VERSION, 'url': base, 'new_profiles': len(additions), 'views': []}
    report['unresolved_full_names'] = {k: [a['name'] for a in r['authors'] if a['full_name_pending']]
        for k, r in data['papers'].items() if any(a['full_name_pending'] for a in r['authors'])}
    try:
        with sync_playwright() as pw:
            executable = os.getenv('BROWSER_EXECUTABLE')
            browser = pw.chromium.launch(**({'executable_path': executable} if executable else {}))
            page = browser.new_page(reduced_motion='reduce')
            for width in [390, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.goto(base + 'index.html', wait_until='networkidle').status == 200
                assert page.locator('#publications').get_attribute('data-publication-style') == VERSION
                selector = '.pub-authors, .pub-authors .pub-author, .pub-authors a, .pub-authors strong, .pub-authors sup'
                wrong = page.locator(selector).evaluate_all("els => els.filter(e => getComputedStyle(e).color !== 'rgb(0, 0, 0)').map(e => e.textContent)")
                assert not wrong, wrong
                for selector in ['#pub-ugg .pub-author-self a', '#pub-videossm .pub-authors a[href="https://tau-yihouxiang.github.io/"]', '#pub-game .pub-authors a[href="https://github.com/mx-liu6"]']:
                    link = page.locator(selector)
                    link.hover()
                    assert link.evaluate('(e) => getComputedStyle(e).color') == 'rgb(0, 0, 0)'
                    assert 'underline' in link.evaluate('(e) => getComputedStyle(e).textDecorationLine')
                    link.focus()
                    assert link.evaluate('(e) => getComputedStyle(e).color') == 'rgb(0, 0, 0)'
                    link.evaluate('(e) => e.blur()')
                page.mouse.move(0, 0)
                assert page.locator('#pub-ugg .research-links a').first.evaluate('(e) => getComputedStyle(e).color') == 'rgb(0, 45, 114)'
                for key in ['world-action-model', 'eag3r', 'videossm', 'spiking-depth', 'game', 'neural-field-memory']:
                    entry = page.locator('#pub-' + key)
                    entry.scroll_into_view_if_needed()
                    for image in entry.locator('img').all():
                        image.evaluate('(e) => e.decode()')
                    entry.screenshot(path=str(out / f'{key}-{width}.png'), style='.site-topbar{visibility:hidden!important}')
                assert page.evaluate('document.documentElement.scrollWidth - innerWidth') <= 1
                report['views'].append({'width': width, 'author_normal_hover_focus': 'black', 'resource_links_unchanged': True})
            browser.close()
    finally:
        server.shutdown()
    report['status'] = 'PASS'
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
