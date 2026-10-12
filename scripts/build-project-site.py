#!/usr/bin/env python3
"""Site integration for the research-page data/template module.

Run this entry point to preserve homepage navigation and apply responsive fixes:
    python scripts/build-project-site.py --download-assets
"""
from pathlib import Path
import importlib.util
import re
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('research_pages', ROOT / 'scripts/build-project-pages.py')
if spec is None or spec.loader is None:
    raise RuntimeError('Research-page template module is missing')
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)

# Keep grid children within the viewport. On phones, wrap table headers so
# the proposed method's scores remain visible instead of falling off-screen.
pages.CSS += '''
.section > *{min-width:0}.table-wrap{max-width:100%;min-width:0}
@media(max-width:600px){
  .results{font-size:12px}
  .results th,.results td{padding:12px 7px;white-space:normal}
  .results thead th{font-size:11px}
}
'''
OVERVIEW_HEADINGS = {
    'videossm': 'A finite cache, a longer history.',
    'game': 'A geometric reference across views.',
    'lifr-seg': 'An up-to-date scene between frames.',
    'lifr-v2': 'When motion alone is not enough.',
    'evsplat': 'Event-based 3D reconstruction.',
}

def sync_links():
    """Make narrowly scoped text edits without reformatting the existing site."""
    for filename in ('index.html', 'publications.html'):
        path = ROOT / filename
        if not path.is_file():
            continue
        text = path.read_text()
        original = text
        for project in pages.PROJECTS:
            slug = project['slug']
            anchor = ('pub-' if filename == 'publications.html' else 'selected-') + slug
            pattern = r'(<(?:li|article)\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>)(.*?)(</(?:li|article)>)'
            link = f'<a href="projects/{slug}/">Project</a>'
            def patch(match):
                inner = match.group(2)
                inner = inner.replace('<div class="paper-links">' + link + '</div>', '')
                if f'projects/{slug}/' in inner:
                    return match.group(1) + inner + match.group(3)
                research_nav = r'(<nav\b[^>]*class="research-links"[^>]*>)'
                if re.search(research_nav, inner):
                    inner = re.sub(research_nav, lambda m: m.group(1) + link, inner, count=1)
                elif 'class="paper-links"' in inner:
                    inner = inner.replace('class="paper-links">', 'class="paper-links">' + link + ' ', 1)
                elif filename == 'publications.html':
                    position = inner.rfind('</div>')
                    if position < 0:
                        raise ValueError(f'Cannot locate resource row for {anchor}')
                    inner = inner[:position] + '<span class="paper-links">' + link + '</span>' + inner[position:]
                else:
                    raise ValueError(f'Cannot locate existing research navigation for {anchor}')
                return match.group(1) + inner + match.group(3)
            text = re.sub(pattern, patch, text, flags=re.S)
        if filename == 'index.html' and 'href="projects/"' not in text:
            pattern = r'(<p\b[^>]*id="publications"[^>]*>.*?)(</p>)'
            text = re.sub(pattern, lambda m: m.group(1) + ' <span aria-hidden="true"> · </span><a href="projects/">Project pages →</a>' + m.group(2), text, count=1, flags=re.S)
        if text != original:
            path.write_text(text)

pages.sync_links = sync_links
if __name__ == '__main__':
    pages.main()
    for project in pages.PROJECTS:
        path = ROOT / 'projects' / project['slug'] / 'index.html'
        old = '<h2>' + pages.e(project['statement']) + '</h2>'
        new = '<h2>' + pages.e(OVERVIEW_HEADINGS[project['slug']]) + '</h2>'
        path.write_text(path.read_text().replace(old, new, 1))
    checklist = ROOT / 'projects/CONTENT_CHECKLIST.md'
    if checklist.is_file():
        checklist.write_text(checklist.read_text().replace('python scripts/build-project-pages.py --download-assets', 'python scripts/build-project-site.py --download-assets'))
