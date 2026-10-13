#!/usr/bin/env python3
"""Build a restrained homepage and refresh the shared personal-page shell.

Run from any directory with beautifulsoup4 installed. Existing About, Resume,
Research and publication content is preserved; CVs and project sites are never
written. The legacy cinematic fragment is kept as an archive, not rendered.
"""
from pathlib import Path
from copy import deepcopy
import json
import hashlib
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261012-four-pages-minimal-20261013'
DESIGN = 'quiet-academic-20261013'
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html', 'publications.html']


def read_page(name):
    return BeautifulSoup((ROOT / name).read_text(encoding='utf-8'), 'html.parser')


def fragment(html):
    return BeautifulSoup(html, 'html.parser')


def inner(html):
    doc = fragment(html)
    p = doc.find('p')
    if p is None:
        raise ValueError('Expected a paragraph in personal-site.json')
    return p.decode_contents()


def normalized_text(node):
    return ' '.join(node.stripped_strings) if node else ''


def shell(doc, page):
    """No scroll effects, external fonts, new analytics, or full-bleed imagery."""
    for tag in list(doc.select('link[href], script[src]')):
        attr = 'href' if tag.name == 'link' else 'src'
        value = tag.get(attr, '')
        if any(part in value for part in ('hero-hd.', 'shared-world.css')):
            tag.decompose()
        elif 'assets/css/site-pages.css' in value:
            tag[attr] = 'assets/css/site-pages.css?v=' + VERSION
    if not doc.select_one('link[href^="assets/css/site-pages.css"]'):
        doc.head.append(doc.new_tag('link', rel='stylesheet', href='assets/css/site-pages.css?v=' + VERSION))
    classes = doc.body.get('class', [])
    if 'site-layout' not in classes:
        classes.append('site-layout')
    doc.body['class'] = classes
    doc.body['data-design'] = DESIGN
    for nav in doc.select('nav[aria-label="Main navigation"]'):
        for a in nav.find_all('a'):
            a.attrs.pop('aria-current', None)
            if a.get('href') == page:
                a['aria-current'] = 'page'
    return doc


def homepage(current, about, research, data):
    main = current.select_one('main')
    header = deepcopy(about.select_one('header.site-topbar'))
    footer = deepcopy(about.select_one('footer.site-footer'))
    if not all((main, header, footer)):
        raise ValueError('Missing personal-page landmarks; refusing to replace content')
    for a in footer.select('a[aria-current]'):
        del a['aria-current']
    home_footer_link = footer.select_one('a[href="index.html"]')
    if home_footer_link:
        home_footer_link['aria-current'] = 'page'
    news = deepcopy(main.select_one('.news-section'))
    if news is None:
        raise ValueError('Missing existing news; refusing to drop updates')
    featured = []
    # Preserve the existing homepage selection and fetch author/status details
    # from the current research record instead of maintaining duplicate claims.
    for project_id in ['selected-world-action-model', 'selected-game', 'selected-eag3r']:
        source = research.find(id=project_id)
        if source is None:
            raise ValueError('Missing current research entry: ' + project_id)
        item = deepcopy(source)
        item.attrs.pop('id', None)
        item['class'] = ['research-entry', 'home-research-entry']
        # A compact preview; original figure and all resource links are retained.
        caption = item.select_one('figcaption')
        if caption:
            caption.decompose()
        featured.append(str(item))
    profile = '''<section class="academic-profile" id="welcome" aria-labelledby="name">
<div class="academic-identity"><h1 id="name">Xiaoshan Wu <span class="native-name" lang="zh">吴小山</span></h1></div>
<figure class="academic-portrait"><img src="images/research/profile.webp" alt="Xiaoshan Wu" width="160" height="214" decoding="async" fetchpriority="high"></figure>
<div class="academic-copy">
<p>I am a Ph.D. candidate at the University of Hong Kong, advised by <a href="https://xjqi.github.io/" rel="noopener" target="_blank">Prof. Xiaojuan Qi</a>.</p>
<p>''' + inner(data['direction']) + '''</p>
<p>''' + inner(data['foundation']) + '''</p>
<nav class="contact-links" aria-label="Contact and profiles"><a href="mailto:wuxiaoshan630@gmail.com">Email</a><a href="https://scholar.google.com/citations?user=9nsSKpsAAAAJ&amp;hl=en" rel="noopener" target="_blank">Google Scholar</a><a href="https://github.com/Candy-Crusher" rel="noopener" target="_blank">GitHub</a><a href="Xiaoshan_Wu_CV.pdf" rel="noopener" target="_blank">CV (PDF)</a></nav>
</div></section>'''
    selected = '''<section class="home-selected" aria-labelledby="home-selected-title"><div class="section-heading"><h2 id="home-selected-title">Selected research</h2><a href="research.html">All projects &amp; publications →</a></div><p class="section-note">Selected first- and co-first-author work. * Equal contribution.</p><div class="selected-list">''' + ''.join(featured) + '</div></section>'
    content = '<!doctype html>\n<html lang="en">' + str(current.head) + '<body class="site-layout" data-page="home" id="top"><a class="skip-link" href="#main">Skip to content</a>' + str(header) + '<main class="wrap" id="main">' + profile + selected + str(news) + '</main>' + str(footer) + '</body></html>\n'
    return shell(BeautifulSoup(content, 'html.parser'), 'index.html')


def main():
    docs = {name: read_page(name) for name in PAGES}
    data = json.loads((ROOT / '_site_content/personal-site.json').read_text(encoding='utf-8'))
    protected = {}
    for path in [ROOT / 'cv.tex', ROOT / 'Xiaoshan_Wu_CV.pdf', *sorted((ROOT / 'cv/2027-internships').glob('*.tex'))]:
        protected[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    before = {name: normalized_text(docs[name].select_one('main')) for name in PAGES[1:]}
    publication_count = len(docs['research.html'].select('.publication-list > li'))
    project_count = len(docs['research.html'].select('.project-grid > .research-entry'))
    if publication_count != 15 or project_count != 7:
        raise ValueError(f'Review the content counts before rebuilding: {publication_count} papers / {project_count} projects')
    output = {'index.html': homepage(docs['index.html'], docs['about.html'], docs['research.html'], data)}
    for name in PAGES[1:]:
        output[name] = shell(docs[name], name)
        assert normalized_text(output[name].select_one('main')) == before[name], name
    for name, doc in output.items():
        (ROOT / name).write_text(str(doc).rstrip() + '\n', encoding='utf-8')
    for name, digest in protected.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    report = {'design': DESIGN, 'pages': PAGES, 'publication_count': publication_count, 'project_count': project_count, 'subpage_text_preserved': True, 'protected_cv_files': len(protected)}
    (Path('/tmp') / 'personal-site-style-preservation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
