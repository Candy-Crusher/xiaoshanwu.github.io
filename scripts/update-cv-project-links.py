#!/usr/bin/env python3
"""Use only one [Project] link immediately after each plain research title.

Remove [Paper] links consistently across the main and tailored CVs. Preserve
publication metadata, ordinary text and unrelated links. --compile validates
all before/after PDFs and checks exactly which text each project link covers.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, re, shutil, subprocess
from collections import Counter
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
    for name in ('publications', 'research'):
        ALIASES[BASE + name + '.html#pub-' + anchor] = URLS[slug]
LABEL = r'\textcolor{cvblue}{[Project]}'
TITLES = {r'\textbf{' + title + '}' for title in PROJECTS.values()}
LINK_START = re.compile(r'\\href\s*\{')


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


def hrefs(text: str):
    cursor = 0
    while match := LINK_START.search(text, cursor):
        url, end_url = group(text, match.end() - 1)
        start_body = end_url
        while start_body < len(text) and text[start_body].isspace():
            start_body += 1
        body, end = group(text, start_body)
        yield match.start(), end, url, body
        cursor = end


def is_paper_label(body: str) -> bool:
    # Match the label, not the destination: unrelated arXiv links or metadata
    # are not removed simply because they refer to a paper.
    plain = re.sub(r'\\textcolor\{[^{}]+\}', '', body)
    plain = re.sub(r'\\(?:textbf|textit|textrm|textsf|texttt|underline|mbox)', '', plain)
    plain = plain.replace('{', '').replace('}', '').strip()
    return plain.casefold() == '[paper]'


def strip_paper_links(text: str) -> str:
    output, cursor = [], 0
    for start, end, _, body in hrefs(text):
        prefix = text[cursor:start]
        if is_paper_label(body):
            prefix = re.sub(r'(?:\\quad|\\enspace|\\,|~|[ \t])+$', '', prefix)
            replacement = ''
        else:
            replacement = text[start:end]
        output.extend((prefix, replacement))
        cursor = end
    output.append(text[cursor:])
    return ''.join(output)


def strip_project_links(text: str) -> str:
    """Remove only project-title wrappers and old/new project labels."""
    output, cursor = [], 0
    for start, end, url, body in hrefs(text):
        prefix = text[cursor:start]
        destination = ALIASES.get(url.replace(r'\#', '#'), url)
        if body in TITLES:
            replacement = body
        elif destination in URLS.values() and re.fullmatch(
            r'(?:\\textcolor\{cvblue\}\{)?\[(?:Project|Porject|Details)\]\}?', body
        ):
            prefix = re.sub(r'(?:\\quad|\\enspace|\\,|~|[ \t])+$', '', prefix)
            replacement = ''
        else:
            replacement = text[start:end]
        output.extend((prefix, replacement))
        cursor = end
    output.append(text[cursor:])
    return ''.join(output)


def update(text: str) -> str:
    base = strip_project_links(strip_paper_links(text))
    revised = base
    for slug, title in PROJECTS.items():
        title_tex = r'\textbf{' + title + '}'
        if revised.count(title_tex) != 1:
            raise ValueError('Expected exactly one publication title: ' + title)
        label = r'~\href{' + URLS[slug] + '}{' + LABEL + '}'
        revised = revised.replace(title_tex, title_tex + label, 1)
    if strip_project_links(revised) != base:
        raise ValueError('An unrelated source change was detected')
    if re.search(r'\[paper\]', revised, re.IGNORECASE):
        raise ValueError('A [Paper] label remains in the source')
    found = [(url, body) for _, _, url, body in hrefs(revised) if url in URLS.values()]
    if Counter(url for url, _ in found) != Counter(URLS.values()):
        raise ValueError('Expected exactly one project link per publication')
    if any(body != LABEL for _, body in found):
        raise ValueError('A project link still wraps a title or another label')
    if any(body in TITLES for _, _, _, body in hrefs(revised)):
        raise ValueError('A publication title is still clickable')
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


def normalized_text(doc) -> str:
    text = '\n'.join(page.get_text() for page in doc)
    text = re.sub(r'\[(?:Project|Porject|Details|Paper)\]', '', text, flags=re.IGNORECASE)
    return ''.join(text.split())


def link_text(page, link) -> str:
    import fitz
    rect = fitz.Rect(link['from'])
    # Hyperref pads its annotations: word centres avoid adjacent-line glyphs.
    covered = [w for w in page.get_text('words') if rect.contains(
        fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))]
    return ''.join(w[4] for w in covered)


def compare_pdf(before: Path, after: Path) -> dict:
    import fitz
    with fitz.open(before) as old, fitz.open(after) as new:
        if len(old) != len(new):
            raise ValueError('Page count changed: ' + after.name)
        if normalized_text(old) != normalized_text(new):
            raise ValueError('PDF content changed beyond resource labels: ' + after.name)
        old_links = {l['uri'] for p in old for l in p.get_links() if l.get('uri')}
        new_links = {l['uri'] for p in new for l in p.get_links() if l.get('uri')}
        paper_links = {l['uri'] for p in old for l in p.get_links()
                       if l.get('uri') and link_text(p, l).casefold() == '[paper]'}
        preserved = old_links - set(ALIASES) - set(URLS.values()) - paper_links
        if not preserved.issubset(new_links):
            raise ValueError('An unrelated link was removed: ' + after.name)
        if set(ALIASES).intersection(new_links):
            raise ValueError('Legacy project destinations remain: ' + after.name)
        if any(re.search(r'\[paper\]', p.get_text(), re.IGNORECASE) for p in new):
            raise ValueError('A [Paper] label remains in the PDF: ' + after.name)
        labels, seen = [], Counter()
        for page_no, page in enumerate(new):
            for link in page.get_links():
                uri = link.get('uri')
                if uri not in URLS.values(): continue
                text = link_text(page, link)
                if text != '[Project]':
                    raise ValueError('Project link must cover only [Project]: ' + after.name + ': ' + repr(text))
                seen[uri] += 1
                labels.append({'page': page_no + 1, 'url': uri, 'clickable_text': text,
                               'rectangle_pt': list(link['from'])})
            for word in page.get_text('words'):
                if word[0] < 0 or word[1] < 0 or word[2] > page.rect.width or word[3] > page.rect.height:
                    raise ValueError('Text exceeds page bounds: ' + after.name)
        if seen != Counter(URLS.values()):
            raise ValueError('Missing or duplicated PDF project links: ' + after.name)
        if sum(p.get_text().count('[Project]') for p in new) != len(PROJECTS):
            raise ValueError('Incorrect number of visible project labels: ' + after.name)
        return {'pdf': after.name, 'pages': len(new), 'project_links': labels,
                'content_preserved_except_resource_labels': True, 'paper_labels_remaining': 0,
                'removed_paper_destinations': sorted(paper_links - new_links),
                'preserved_other_links': sorted(preserved),
                'sha256': hashlib.sha256(after.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile', action='store_true', help='Build and compare before/after PDFs')
    args = parser.parse_args()
    sources = [ROOT / 'cv.tex', *sorted((ROOT / 'cv/2027-internships').glob('*.tex'))]
    if not sources[0].is_file(): raise FileNotFoundError('Primary CV source not found')
    review = ROOT / 'cv-link-review'
    review.mkdir(exist_ok=True)
    report = {'project_urls': URLS, 'placement': 'One [Project] immediately after each plain title; no [Paper] labels',
              'sources': [], 'pdf_checks': []}
    pairs = []
    # Stage every source first. No source or stable PDF is published on failure.
    for source in sources:
        original = source.read_text()
        revised = update(original)
        if update(revised) != revised: raise ValueError('Update is not idempotent')
        relative = source.relative_to(ROOT)
        old_path, new_path = review / 'before' / relative, review / 'after' / relative
        old_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.write_text(original); new_path.write_text(revised)
        report['sources'].append({'path': str(relative), 'changed': original != revised,
                                  'titles_are_plain_text': True, 'project_labels_after_titles': 7,
                                  'paper_labels_removed': sum(is_paper_label(body) for _, _, _, body in hrefs(original)),
                                  'non_link_source_preserved': True,
                                  'before_sha256': hashlib.sha256(original.encode()).hexdigest(),
                                  'after_sha256': hashlib.sha256(revised.encode()).hexdigest()})
        pairs.append((old_path, new_path))
    try:
        if args.compile:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(compile_one, [path for pair in pairs for path in pair]))
            for old_path, new_path in pairs:
                report['pdf_checks'].append(compare_pdf(old_path.with_suffix('.pdf'), new_path.with_suffix('.pdf')))
        for source, (_, new_path) in zip(sources, pairs):
            source.write_text(new_path.read_text())
        if args.compile:
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
            import fitz
            previews = review / 'previews'; previews.mkdir(exist_ok=True)
            for _, new_path in pairs:
                with fitz.open(new_path.with_suffix('.pdf')) as doc:
                    for number, page in enumerate(doc):
                        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(
                            previews / (new_path.stem + '-' + str(number + 1) + '.png'))
        report['status'] = 'passed'
    except Exception as exc:
        report['status'] = 'failed'; report['error'] = str(exc)
        raise
    finally:
        (review / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
