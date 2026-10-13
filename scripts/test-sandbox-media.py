#!/usr/bin/env python3
"""Check real media, not just HTML links: original demo + all six RDF cases.

Called by test-personal-site.py after its ordinary responsive/content checks.
Requires a local HTTP server, Chromium and the original restored assets.
"""
from pathlib import Path
import gzip
import json
import os
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
CASES = ['pose-1', 'pose-2', 'lighting-1', 'lighting-2', 'clutter-1', 'clutter-2']
STATIC = ROOT / 'projects/sandbox/static'


def validate_files():
    for name in ['viewer.js', 'gallery.js', 'vendor/three.module.js', 'vendor/OrbitControls.js']:
        assert (STATIC / 'rdf' / name).is_file(), f'Missing viewer dependency: {name}'
    frame_counts = {}
    for case in CASES:
        directory = STATIC / 'rdf' / case
        manifest = json.loads((directory / 'manifest.json').read_text())
        assert manifest['id'] == case
        expected_size = manifest['width'] * manifest['height'] * 6
        frame_counts[case] = {}
        for kind in ['pred', 'obs']:
            frames = manifest['streams'][kind]['frames']
            assert frames, (case, kind, 'empty stream')
            for frame in frames:
                file = directory / frame['file']
                assert file.is_file(), f'Missing frame: {file.relative_to(ROOT)}'
                with gzip.open(file, 'rb') as handle:
                    data = handle.read()
                assert len(data) == expected_size, (str(file), len(data), expected_size)
            frame_counts[case][kind] = len(frames)
        # Gallery playback is a separate resource from the 3D viewer.
        for name in ['tracking.mp4', 'tracking-poster.jpg', 'tracking.json']:
            assert (directory / name).is_file(), (case, name)
    doc = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
    entry = doc.select_one('#pub-world-action-model')
    video = entry.select_one('video.research-video')
    assert video is not None
    assert all(key in video.attrs for key in ['muted', 'loop', 'controls', 'playsinline'])
    assert video['poster'].endswith('/poster_disco_light.jpg')
    source = video.select_one('source')['src']
    assert source.endswith('/disco_light_10x.mp4')
    assert (ROOT / source).is_file() and (ROOT / video['poster']).is_file()
    assert not entry.select('a video, video a[data-figure]')
    assert not any('Robot demo' in a.get_text() for a in entry.select('.research-links a'))
    return {'manifest_frames': frame_counts, 'all_frame_sizes_valid': True,
            'original_video': source, 'video_cover_has_native_controls': True,
            'standalone_robot_demo_link_removed': True}


def run(base, out):
    out = Path(out)
    report = {'files': validate_files(), 'cases': [], 'navigation': []}
    (out / 'sandbox-files-report.json').write_text(json.dumps(report['files'], indent=2))
    with sync_playwright() as pw:
        args = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']
        executable = os.getenv('BROWSER_EXECUTABLE')
        browser = pw.chromium.launch(args=args, **({'executable_path': executable} if executable else {}))
        context = browser.new_context(reduced_motion='reduce')
        failures, errors = [], []
        context.on('response', lambda response: failures.append({'status': response.status, 'url': response.url})
                   if response.status >= 400 and response.url.startswith(base) else None)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        for width in [390, 1440]:
            print(f'Testing Research navigation and video at {width}px', flush=True)
            page.set_viewport_size({'width': width, 'height': 900})
            page.goto(base + 'index.html', wait_until='domcontentloaded')
            page.evaluate('window.__researchSentinel = "same-document"')
            page.locator('.site-nav a[href="#research"]').click()
            page.wait_for_url(base + 'index.html#research')
            assert page.evaluate('window.__researchSentinel') == 'same-document'
            expect(page.locator('.site-nav a[href="#research"]')).to_have_attribute('aria-current', 'location')
            header = page.locator('.site-topbar').bounding_box()['height']
            assert page.locator('#research-title').bounding_box()['y'] >= header
            page.screenshot(path=str(out / f'research-navigation-{width}.png'))
            video = page.locator('#pub-world-action-model video')
            video.scroll_into_view_if_needed()
            page.wait_for_function('document.querySelector(".research-video").readyState >= 2')
            assert video.evaluate('(v) => v.paused'), 'Reduced-motion cover unexpectedly autoplayed'
            video.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".research-video").currentTime > 0.1')
            info = video.evaluate('(v) => ({width:v.videoWidth,height:v.videoHeight,duration:v.duration,error:v.error?.code||null,muted:v.muted})')
            assert info['width'] > 0 and info['height'] > 0 and not info['error'] and info['muted'], info
            video.evaluate('(v) => v.pause()')
            page.locator('#pub-world-action-model').screenshot(path=str(out / f'sandbox-video-cover-{width}.png'))
            page.locator('.site-nav a[href="#top"]').click()
            assert page.evaluate('window.__researchSentinel') == 'same-document'
            page.go_back();page.wait_for_url(base + 'index.html#research')
            assert page.evaluate('window.__researchSentinel') == 'same-document'
            page.goto(base + 'about.html', wait_until='domcontentloaded')
            page.locator('.site-nav a[href="index.html#research"]').click()
            page.wait_for_url(base + 'index.html#research')
            report['navigation'].append({'width': width, 'same_document': True, 'back_button': True,
                                         'heading_clear_of_header': True, 'from_about': True, 'video': info})
        page.set_viewport_size({'width': 1440, 'height': 1000})
        for case in CASES:
            print(f'Testing point clouds: {case}', flush=True)
            page.goto(base + f'projects/sandbox/rdf-viewer.html?case={case}&view=compare', wait_until='domcontentloaded')
            page.wait_for_function('!document.getElementById("play").disabled')
            assert page.locator('canvas[aria-label]').count() == 2
            assert not page.locator('#error').inner_text().strip()
            counts = [page.locator('#count-' + kind).inner_text() for kind in ['pred', 'obs']]
            assert all(re.search(r'[1-9][0-9,]* /', value) for value in counts), (case, counts)
            for image in page.locator('.rgb').all():
                image.evaluate('(i) => i.decode()')
                assert image.evaluate('(i) => i.naturalWidth > 0')
            first = page.locator('#stamp').inner_text()
            page.locator('#next').click()
            page.wait_for_function('!document.getElementById("loading").textContent.startsWith("Loading")')
            assert page.locator('#stamp').inner_text() != first
            page.locator('#prev').click()
            page.wait_for_function('!document.getElementById("loading").textContent.startsWith("Loading")')
            assert page.locator('#stamp').inner_text() == first
            page.locator('#oblique').click()
            page.screenshot(path=str(out / f'interactive-4d-{case}.png'), full_page=True)
            report['cases'].append({'case': case, 'canvas_count': 2, 'points': counts,
                                    'timeline_next_previous': True, 'rgb_insets_loaded': True, 'error': None})
        # Both single-stream modes must also initialize and remain usable.
        for mode in ['pred', 'obs']:
            print(f'Testing single-stream mode: {mode}', flush=True)
            page.goto(base + f'projects/sandbox/rdf-viewer.html?case=pose-1&view={mode}', wait_until='domcontentloaded')
            page.wait_for_function('!document.getElementById("play").disabled')
            assert page.locator('canvas[aria-label]').count() == 1
            assert re.search(r'[1-9][0-9,]* /', page.locator('#count-' + mode).inner_text())
        page.set_viewport_size({'width': 390, 'height': 900})
        page.goto(base + 'projects/sandbox/rdf-viewer.html?case=pose-1', wait_until='domcontentloaded')
        page.wait_for_function('!document.getElementById("play").disabled')
        assert page.evaluate('document.documentElement.scrollWidth - innerWidth') <= 1
        first = page.locator('#stamp').inner_text()
        page.locator('#play').click()
        page.wait_for_function('(first) => document.getElementById("stamp").textContent !== first', arg=first)
        page.locator('#play').click()
        assert page.locator('#play').inner_text() == 'Play'
        page.screenshot(path=str(out / 'interactive-4d-mobile.png'), full_page=True)
        # Check all six in-page gallery choices, not just the full-screen link.
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(base + 'projects/sandbox/#rdf-single-view', wait_until='domcontentloaded')
        report['project_gallery_cases'] = []
        for case in CASES:
            print(f'Testing project gallery: {case}', flush=True)
            page.locator(f'[data-rdf-case="{case}"]').click()
            frame = page.frame_locator('#rdf-cloud')
            frame.locator('#play:not([disabled])').wait_for()
            assert page.locator('#rdf-cloud').get_attribute('src').find('case=' + case) >= 0
            page.wait_for_function('document.getElementById("rdf-metrics").textContent.startsWith("Prediction:")')
            page.wait_for_function('document.getElementById("rdf-tracking").readyState >= 2')
            assert frame.locator('canvas[aria-label]').count() == 2
            report['project_gallery_cases'].append({'case': case, 'viewer': True, 'tracking_video': True, 'metrics': True})
        assert not failures, failures
        assert not errors, errors
        context.close()
        # Autoplay with normal preferences, off-screen pause, and manual pause.
        normal = browser.new_context(reduced_motion='no-preference')
        p = normal.new_page();p.goto(base + 'index.html', wait_until='domcontentloaded')
        v = p.locator('.research-video');v.scroll_into_view_if_needed()
        p.wait_for_function('!document.querySelector(".research-video").paused')
        v.evaluate('(v) => v.pause()')
        p.evaluate('scrollTo(0,0)');p.wait_for_timeout(250)
        v.scroll_into_view_if_needed();p.wait_for_timeout(300)
        assert v.evaluate('(v) => v.paused'), 'Manual pause was overridden'
        normal.close();browser.close()
    report.update({'status': 'PASS', 'single_stream_modes': True, 'mobile_playback': True,
                   'motion_preferences_respected': True, 'manual_pause_preserved': True,
                   'http_errors': failures, 'javascript_errors': errors})
    (out / 'sandbox-media-report.json').write_text(json.dumps(report, indent=2))
    return report
