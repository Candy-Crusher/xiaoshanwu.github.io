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

# Grid children must be allowed to shrink below a table's min-content width.
# The table itself stays legible and scrolls inside its labelled container.
pages.CSS += '\n.section > *{min-width:0}.table-wrap{max-width:100%;min-width:0}\n'

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
                # Clean up an earlier generator's outside-the-grid link, if present.
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
    checklist = ROOT / 'projects/CONTENT_CHECKLIST.md'
    if checklist.is_file():
        checklist.write_text(checklist.read_text().replace('python scripts/build-project-pages.py --download-assets', 'python scripts/build-project-site.py --download-assets'))
