#!/usr/bin/env python3
"""Link the seven CV research titles to their canonical project pages.

Only hyperlink destinations/wrappers change. Visible text, author roles, paper
links, contact information and layout settings are preserved. --compile also
builds all before/after PDFs, checks their links, and compares rendered pages.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, re, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://candy-crusher.github.io/xiaoshanwu.github.io/'
PROJECTS = {
    'sandbox': 'Verifiable 4D World--Action Model for Robust Robot Control.',
    'game': 'GaMe: Geometry as Memory for Multi-View Spatial Reasoning.',
    'videossm': 'VideoSSM: Autoregressive Long Video Generation with Hybrid State-Space Memory.',
    'eag3r': 'EAG3R: Event-Augmented 3D Geometry Estimation for Dynamic and Extreme-Lighting Scenes.',
    'lifr-seg': 'LiFR-Seg: Anytime High-Frame-Rate Segmentation via Event-Guided Propagation.',
    'evsplat': 'EVSplat: Uncertainty-Aware Gaussian Splatting for Dynamic Scenes with Event Camera.',
    'lifr-v2': 'LiFR v2: Completion-Augmented Event Propagation for High-Rate Dense Prediction.',
}
URLS = {slug: BASE + 'projects/' + slug + '/' for slug in PROJECTS}
ALIASES = {
    'https://demo1-indol-gamma.vercel.app/': URLS['sandbox'],
    'https://candy-crusher.github.io/EAG3R_Proj/': URLS['eag3r'],
    'https://candy-crusher.github.io/LiFR_Seg_Proj/': URLS['lifr-seg'],
}
for slug in PROJECTS:
    anchor = 'world-action-model' if slug == 'sandbox' else slug
    ALIASES[BASE + 'publications.html#pub-' + anchor] = URLS[slug]
    ALIASES[BASE + 'research.html#pub-' + anchor] = URLS[slug]


def group(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != '{':
        raise ValueError('Expected a LaTeX argument at offset ' + str(start))
    depth, i = 1, start + 1
    while i < len(text):
        if text[i] == '\\' and i + 1 < len(text) and text[i + 1] in '{}':
            i += 2
            continue
        if text[i] == '{': depth += 1
        if text[i] == '}': depth -= 1
        if depth == 0: return text[start + 1:i], i + 1
        i += 1
    raise ValueError('Unclosed LaTeX argument')


def transform_hrefs(text: str, visible_only: bool = False) -> str:
    output, cursor = [], 0
    for_match = re.compile(r'\\href\s*\{')
    while match := for_match.search(text, cursor):
        output.append(text[cursor:match.start()])
        url, end_url = group(text, match.end() - 1)
        body_start = end_url
        while body_start < len(text) and text[body_start].isspace(): body_start += 1
        body, end_body = group(text, body_start)
        body = transform_hrefs(body, visible_only)
        if visible_only:
            output.append(body)
        else:
            destination = ALIASES.get(url.replace('\\#', '#'), url)
            for slug, title in PROJECTS.items():
                if body == '\\textbf{' + title + '}': destination = URLS[slug]
            output.append('\\href{' + destination + '}{' + body + '}')
        cursor = end_body
    output.append(text[cursor:])
    return ''.join(output)


def update(text: str) -> str:
    revised = transform_hrefs(text)
    for slug, title in PROJECTS.items():
        title_tex = '\\textbf{' + title + '}'
        if revised.count(title_tex) != 1:
            raise ValueError('Expected exactly one publication title: ' + title)
        linked = '\\href{' + URLS[slug] + '}{' + title_tex + '}'
        if linked not in revised: revised = revised.replace(title_tex, linked, 1)
    if transform_hrefs(text, True) != transform_hrefs(revised, True):
        raise ValueError('A non-link source change was detected')
    return revised


def compile_one(path: Path) -> Path:
    for pass_no in (1, 2):
        result = subprocess.run(
            ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode',
             '-halt-on-error', '-file-line-error', path.name],
            cwd=path.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=90,
        )
        path.with_suffix('.pass' + str(pass_no) + '.txt').write_text(result.stdout)
        if result.returncode:
            raise RuntimeError('Compilation failed: ' + str(path) + '\n' + result.stdout[-5000:])
    return path.with_suffix('.pdf')


def compare_pdf(before: Path, after: Path) -> dict:
    import fitz
    with fitz.open(before) as old, fitz.open(after) as new:
        if len(old) != len(new): raise ValueError('Page count changed: ' + after.name)
        old_text = '\n'.join(p.get_text() for p in old)
        new_text = '\n'.join(p.get_text() for p in new)
        if old_text != new_text: raise ValueError('PDF text changed: ' + after.name)
        visual = []
        for i, (a, b) in enumerate(zip(old, new)):
            pa = a.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            pb = b.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            identical = pa.width == pb.width and pa.height == pb.height and pa.samples == pb.samples
            visual.append({'page': i + 1, 'identical_pixels': identical})
            if not identical: raise ValueError('Rendered layout changed: ' + after.name + ', page ' + str(i + 1))
        old_uris = {link['uri'] for p in old for link in p.get_links() if link.get('uri')}
        new_uris = {link['uri'] for p in new for link in p.get_links() if link.get('uri')}
        missing = set(URLS.values()) - new_uris
        if missing: raise ValueError('Missing project PDF links: ' + repr(missing))
        bad = set(ALIASES).intersection(new_uris)
        if bad: raise ValueError('Legacy project links remain: ' + repr(bad))
        preserved = old_uris - set(ALIASES)
        if not preserved.issubset(new_uris): raise ValueError('An unrelated PDF link was removed')
        return {'pdf': after.name, 'pages': len(new), 'project_urls': sorted(set(URLS.values())),
                'preserved_other_links': sorted(preserved), 'visual_comparison': visual,
                'sha256': hashlib.sha256(after.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile', action='store_true', help='Build and compare all before/after PDFs')
    args = parser.parse_args()
    sources = [ROOT / 'cv.tex', *sorted((ROOT / 'cv/2027-internships').glob('*.tex'))]
    if not sources[0].is_file(): raise FileNotFoundError('Primary CV source not found')
    review = ROOT / 'cv-link-review'
    report = {'project_urls': URLS, 'sources': [], 'pdf_checks': []}
    pairs = []
    for source in sources:
        original = source.read_text()
        revised = update(original)
        relative = source.relative_to(ROOT)
        old_path, new_path = review / 'before' / relative, review / 'after' / relative
        old_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.write_text(original); new_path.write_text(revised)
        source.write_text(revised)
        report['sources'].append({'path': str(relative), 'changed': original != revised,
                                  'visible_content_unchanged': True,
                                  'before_sha256': hashlib.sha256(original.encode()).hexdigest(),
                                  'after_sha256': hashlib.sha256(revised.encode()).hexdigest()})
        pairs.append((old_path, new_path))
    if args.compile:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(compile_one, [path for pair in pairs for path in pair]))
        for old_path, new_path in pairs:
            report['pdf_checks'].append(compare_pdf(old_path.with_suffix('.pdf'), new_path.with_suffix('.pdf')))
        shutil.copy2(review / 'after/cv.pdf', ROOT / 'Xiaoshan_Wu_CV.pdf')
        shutil.copy2(review / 'after/cv.pdf', ROOT / 'ia8eshfzfsvn.pdf')
        delivery = review / 'updated-cvs'
        delivery.mkdir(exist_ok=True)
        shutil.copy2(review / 'after/cv.pdf', delivery / 'Xiaoshan_Wu_CV.pdf')
        shutil.copy2(ROOT / 'cv.tex', delivery / 'cv.tex')
        for source in sources[1:]:
            built = review / 'after' / source.relative_to(ROOT)
            shutil.copy2(built, delivery / source.name)
            shutil.copy2(built.with_suffix('.pdf'), delivery / built.with_suffix('.pdf').name)
    (review / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
