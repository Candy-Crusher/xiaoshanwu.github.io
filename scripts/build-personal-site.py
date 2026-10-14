#!/usr/bin/env python3
"""Assemble one academic homepage from the preserved CV02 parser/renderers.

personal_site_core.py preserves the previous factual parser and publication
renderer. This file owns the single-page layout. It never edits CVs, PDFs or
individual project pages. Legacy documents keep complete no-JavaScript content.
"""
from pathlib import Path
import hashlib
import json
import re
from bs4 import BeautifulSoup
import personal_site_core as core

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = 'teaser-covers-20261015-v1'
NAV = [('Home', 'top'), ('News', 'news'), ('Research', 'research'),
       ('Experience', 'experience'), ('Award', 'awards'), ('About', 'about')]
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html', 'publications.html']
plain = core.plain
MENTOR_PROFILES = core.MENTOR_PROFILES
# Share the verified advisor link with the timeline and legacy-page renderers.
MENTOR_PROFILES['Xiaojuan Qi'] = 'https://xjqi.github.io/'


def fragment(value):
    return BeautifulSoup(value, 'html.parser')


def publication_additions():
    """User-confirmed website additions, kept separate from downloadable CVs."""
    entries = json.loads((ROOT/'_site_content/publication-additions.json').read_text())['papers']
    ids = [entry['id'] for entry in entries]
    titles = [core.normalized(entry['paper']['title']) for entry in entries]
    if len(set(ids)) != len(ids) or len(set(titles)) != len(titles):
        raise ValueError('Duplicate supplemental publication')
    for entry in entries:
        if entry['paper']['group'] != 1 or not entry.get('source'):
            raise ValueError('Review supplemental collaborative publication metadata')
        if entry['presentation']['source_title'] != entry['paper']['title']:
            raise ValueError('Supplemental publication title mismatch')
    return entries


def parse_cv():
    """Read a website-only CV02 view without GPA, rank or review destinations.

    The underlying parser and all CV TeX/PDF files remain unchanged. Both the
    homepage and legacy resume use this view, as does the generated site cache.
    """
    cv = core.parse_cv()
    # Insert new collaborative work ahead of older collaborative records without
    # changing the order of the CV-backed papers or giving a coauthor a lead role.
    known = {core.normalized(p['title']) for p in cv['papers']}
    insert_at = next((i for i, p in enumerate(cv['papers']) if p['group'] == 1), len(cv['papers']))
    for entry in publication_additions():
        paper = entry['paper']
        title = core.normalized(paper['title'])
        if title not in known:
            cv['papers'].insert(insert_at, paper)
            insert_at += 1
            known.add(title)
    for entry in cv['education']:
        visible_details = []
        for detail in entry['details']:
            visible = re.sub(r'\s*<strong>GPA:</strong>[^<]*', ' ', detail).strip()
            visible = re.sub(r'\s*\(Rank\s+5\)', '', visible, flags=re.I)
            if re.search(r'\bGPA\b|\bRank\s+5\b', plain(visible), re.I):
                raise ValueError('Review GPA/rank field formatting before publishing')
            if visible:
                visible_details.append(visible)
        entry['details'] = visible_details
    # A public status is not a disclosure of the venue currently reviewing it.
    # Keep accepted venues, preprints, authors, order and all resource links.
    for paper in cv['papers']:
        if re.search(r'\bunder review\b', plain(paper['venue']), re.I):
            paper['venue'] = 'Under review'
    return cv


def news_feed(papers):
    """Render month-level milestones; retain source/date provenance in JSON."""
    data = json.loads((ROOT/'_site_content/news.json').read_text())
    entries = data['entries']
    if len({item['id'] for item in entries}) != len(entries):
        raise ValueError('Duplicate news event IDs')
    rows = []
    for item in sorted(entries, key=lambda item: item['month'], reverse=True):
        month = item['month']
        if not re.fullmatch(r'20\d{2}-(?:0[1-9]|1[0-2])', month):
            raise ValueError('News must use YYYY-MM dates: ' + month)
        if not item.get('sources') or not item.get('month_basis'):
            raise ValueError('News needs explicit source/date provenance')
        for paper_id in item['paper_ids']:
            if paper_id not in papers:
                raise ValueError('Unknown news paper: ' + paper_id)
            status = plain(papers[paper_id]['venue'])
            if 'acceptance' in item['kind']:
                if item['venue'] not in status or 'under review' in status.lower():
                    raise ValueError('Acceptance news conflicts with publication: ' + paper_id)
        markup = fragment(item['html'])
        for anchor in markup.select('a[href^="#pub-"]'):
            if anchor['href'][1:] not in item['paper_ids']:
                raise ValueError('Untracked paper in news: ' + anchor['href'])
        rows.append('<dt><time datetime="' + month + '">' + month.replace('-', '.') +
                    '</time></dt><dd data-news-id="' + core.esc(item['id']) + '">' +
                    core.mentor_links(item['html']) + '</dd>')
    return '<dl class="news news-monthly">' + ''.join(rows) + '</dl>'


def timeline(cv):
    """Three milestones, newest first; all dates and details come from CV02."""
    schools = cv['education']
    specs = [('harvard', 'Harvard', [('harvard', 'Harvard University')]),
             ('hku', 'Hong Kong', [('hku', 'The University of Hong Kong')]),
             ('zjui', 'ZJU', [('zju', 'Zhejiang University'), ('uiuc', 'UIUC')])]
    formats = {'zju': 'svg', 'uiuc': 'svg', 'hku': 'png', 'harvard': 'png'}
    entries = []
    for key, match, icons in specs:
        matches = [e for e in schools if match in e['school']]
        if len(matches) != 1:
            raise ValueError('Expected one CV02 education entry for ' + key)
        e = matches[0]
        logos = ''.join(f'<img src="assets/institutions/{name}.{formats[name]}" class="logo-{name}" alt="{core.esc(label)} emblem" width="64" height="64" loading="lazy" decoding="async">' for name, label in icons)
        details = ''.join('<p class="timeline-detail">' + core.mentor_links(d) + '</p>' for d in e['details'])
        entries.append(f'''<li class="timeline-entry" data-institution="{key}">
<div class="institution-tile {'institution-pair' if len(icons) == 2 else ''}">{logos}</div>
<div class="timeline-copy"><h3>{core.esc(e['school'])}</h3>
<p class="timeline-position">{core.esc(e['role'])}</p>
{details}<p class="timeline-dates">{core.esc(e['dates'])}<span>{core.esc(e['location'])}</span></p></div></li>''')
    return '''<section class="experience-record" id="experience" aria-labelledby="experience-title">
<span class="anchor-alias" id="resume"></span><span class="anchor-alias" id="background"></span><span class="anchor-alias" id="education"></span>
<header class="experience-heading"><h2 id="experience-title">Experience</h2><div class="download-links"><a href="Xiaoshan_Wu_CV.pdf" target="_blank" rel="noopener">View CV</a><a href="Xiaoshan_Wu_CV.pdf" download="Xiaoshan_Wu_CV.pdf">Download PDF</a></div></header>
<ol class="experience-timeline" aria-label="Education and research experience, newest first">''' + ''.join(entries) + '</ol></section>'


def compose_home(old_home, old_about, cv):
    """Build semantic, visible sections, not a client-side page switcher."""
    home = fragment(old_home)
    intro = home.select_one('.profile')
    news = home.select_one('.news-section')
    news['id'] = 'news'
    news['aria-labelledby'] = 'news-title'
    news.h2['id'] = 'news-title'
    news.h2.string = 'News'
    research = home.select_one('#research')
    publications = home.select_one('#publications')
    award = '<section class="award-record" id="awards" aria-labelledby="awards-title"><h2 id="awards-title">Awards</h2><ul class="awards">' + ''.join('<li>' + a.rstrip('.') + '</li>' for a in cv['awards']) + '</ul></section>'
    about = fragment(old_about).select_one('article')
    about.name = 'section'
    about['id'] = 'about'
    about['class'] = ['about-record', 'about-essay']
    about['aria-labelledby'] = 'about-title'
    for heading in about.select('h2'):
        heading.name = 'h3'
    about.h1.name = 'h2'
    about.h2['id'] = 'about-title'
    for a in about.select('a[href^="index.html#"]'):
        a['href'] = a['href'].removeprefix('index.html')
    skill = fragment('<section id="skills" aria-labelledby="skills-title"><h3 id="skills-title">Technical skills</h3>' + ''.join('<p class="skill-line">' + s + '</p>' for s in cv['skills']) + '</section>').section
    about.append(skill)
    return ''.join(map(str, [intro, news, research, publications])) + timeline(cv) + award + str(about)


def document(name, body, cfg, cv):
    doc = fragment(core.document(name, body, cfg, cv))
    doc.body['data-single-page'] = LAYOUT
    wordmark = doc.select_one('.wordmark')
    wordmark.string = "Xiaoshan's Homepage"
    wordmark['class'] = ['wordmark', 'wordmark-script']
    wordmark['href'] = '#top' if name == 'index.html' else 'index.html#top'
    wordmark['aria-label'] = "Xiaoshan's Homepage, return to top"
    for a in doc.select('.site-nav a, .site-footer nav a'):
        a.attrs.pop('aria-current', None)
    if name == 'index.html':
        doc.select_one('.site-nav a')['aria-current'] = 'location'
    doc.head.append(doc.new_tag('link', rel='stylesheet', href='assets/css/single-page.css?v=' + LAYOUT))
    if name == 'index.html':
        doc.head.append(doc.new_tag('link', rel='stylesheet', href='assets/css/news.css?v=' + LAYOUT))
    for node in doc.select('script[src^="assets/js/site-pages.js"]'):
        node['src'] = 'assets/js/site-pages.js?v=' + LAYOUT
    doc.head.append(doc.new_tag('link', rel='preconnect', href='https://fonts.googleapis.com'))
    doc.head.append(doc.new_tag('link', rel='preconnect', href='https://fonts.gstatic.com', crossorigin='anonymous'))
    doc.head.append(doc.new_tag('link', rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Allura&display=swap'))
    if name != 'index.html':
        doc.select_one('link[rel="canonical"]')['href'] = core.BASE + 'index.html'
    return str(doc) + '\n'


def main():
    protected_paths = [ROOT/'cv.tex', ROOT/'Xiaoshan_Wu_CV.pdf', ROOT/'ia8eshfzfsvn.pdf',
                       *sorted((ROOT/'cv/2027-internships').glob('*.tex')),
                       *sorted((ROOT/'projects').glob('*/index.html'))]
    protected = {str(p.relative_to(ROOT)): core.digest(p) for p in protected_paths if p.is_file()}
    cv = parse_cv()
    cfg = json.loads((ROOT/'_site_content/site-presentation.json').read_text())
    data = json.loads((ROOT/'_site_content/personal-site.json').read_text())
    for entry in publication_additions():
        cfg['papers'][entry['id']] = entry['presentation']
    cfg['navigation'] = [{'label': label, 'url': 'index.html#' + anchor} for label, anchor in NAV]
    cfg['layout'] = LAYOUT
    cfg['version'] = max(cfg.get('version', 0), 5)
    (ROOT/'_site_content/site-presentation.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
    lookup = {core.normalized(v['source_title']): key for key, v in cfg['papers'].items()}
    papers = {lookup[core.normalized(p['title'])]: p for p in cv['papers']}
    data['news'] = news_feed(papers)
    about = (ROOT/'_site_content/about-personal.html').read_text()
    assert fragment(about).select_one('article.about-essay[data-about-version]'), 'Missing personal About essay'
    bodies = {'index.html': compose_home(core.home_page(cfg, papers, cv, data), about, cv),
              'about.html': about, 'resume.html': core.resume_page(cfg, papers, cv),
              'research.html': core.research_page(cfg, papers, cv)}
    bodies['publications.html'] = bodies['research.html']
    for name, body in bodies.items():
        assert not re.search(r'\bGPA\b|\bRank\s+5\b', plain(body), re.I), 'GPA/rank leaked into ' + name
        (ROOT/name).write_text(document(name, body, cfg, cv))
    cv['publication_anchors'] = list(papers)
    (ROOT/'_site_content/resume-cv02.json').write_text(json.dumps(cv, ensure_ascii=False, indent=2) + '\n')
    assert all(core.digest(ROOT/name) == digest for name, digest in protected.items()), 'Protected research or CV content changed'
    report = {'layout': LAYOUT, 'navigation': NAV, 'experience_order': ['Harvard', 'HKU', 'ZJU & UIUC'],
              'publication_count': len(papers), 'source_git_blob': cv['source_git_blob'], 'protected_files': protected}
    Path('/tmp/personal-site-style-preservation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'protected_files'}, indent=2))


if __name__ == '__main__':
    main()
