"""Website-only publication typography and complete, source-checked bylines."""
from __future__ import annotations
from copy import deepcopy
from functools import lru_cache
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'recent-projects-20261015-v1'

@lru_cache(maxsize=1)
def load_details():
    data = json.loads((ROOT/'_site_content/publication-details.json').read_text())
    for key, record in data['papers'].items():
        record['authors'] = []
        for value in record['byline'].split(' | '):
            name = value.rstrip('*†')
            record['authors'].append({'name': name, 'marks': value[len(name):],
                                      'full_name_pending': bool(re.match(r'^[A-Z]\. ', name))})
        assert record['authors'] and record['sources'] and record['tldr'], key
        assert sum(a['name'] == 'Xiaoshan Wu' for a in record['authors']) == 1, key
        assert not re.search(r'et\s+al|…', ' '.join(a['name'] for a in record['authors'])), key
        if record['status'] == 'under_review':
            assert record['venue'] is None and record['year'] is None, key
        else:
            assert record['venue'] and isinstance(record['year'], int), key
        assert record.get('distinction') in (None, 'Spotlight'), key
        assert not record.get('percentile'), key
    for name, url in data['profiles'].items():
        assert urlsplit(url).scheme == 'https' and urlsplit(url).netloc, name
    return data

def authors_markup(record, profiles):
    authors = []
    for author in record['authors']:
        name = author['name']
        label = html.escape(name)
        classes = ['pub-author']
        if name == 'Xiaoshan Wu':
            label = '<strong>' + label + '</strong>'
            classes.append('pub-author-self')
        url = profiles.get(name)
        if url:
            href = '#top' if name == 'Xiaoshan Wu' else url
            external = '' if name == 'Xiaoshan Wu' else ' target="_blank" rel="noopener"'
            label = f'<a href="{html.escape(href, quote=True)}"{external}>' + label + '</a>'
        if author.get('marks'):
            label += '<sup>' + html.escape(author['marks']) + '</sup>'
        pending = ' data-full-name-pending="true"' if author.get('full_name_pending') else ''
        authors.append(f'<span class="{" ".join(classes)}"{pending}>{label}</span>')
    return ', '.join(authors) + '.'

def venue_markup(record):
    if record['status'] == 'under_review':
        return 'Under review'
    value = '<strong>' + html.escape(record['venue']) + '</strong>, ' + str(record['year']) + '.'
    if record.get('distinction'):
        value += ' <strong class="pub-distinction">' + html.escape(record['distinction']) + '</strong>.'
    return value

def resource_records(view, record):
    resources = deepcopy(view.get('resources', []))
    for extra in record.get('resources', []):
        resources = [r for r in resources if r['label'] != extra['label']]
        resources.append(extra)
    order = {'Project': 0, 'Paper': 1, 'Code': 2, 'Interactive 4D': 3, 'BibTeX': 4}
    resources.sort(key=lambda r: order.get(r['label'], 5))
    seen = set(); unique = []
    for r in resources:
        pair = (r['label'], r['url'])
        if pair not in seen:
            seen.add(pair); unique.append(r)
    return unique

def resource_markup(resources):
    links = []
    for r in resources:
        external = ' target="_blank" rel="noopener"' if urlsplit(r['url']).scheme else ''
        figure = ' data-figure' if r.get('figure') else ''
        links.append(f'<a href="{html.escape(r["url"], quote=True)}"{external}{figure}>' + html.escape(r['label']) + '</a>')
    return ''.join(links)

def apply_publication_style(doc, cfg):
    """Change publication text blocks only; preserve all media, IDs and other sections."""
    record = doc.select_one('.publications-record')
    if record is None:
        return doc
    data = load_details()
    entries = record.select('.publication-entry')
    assert [e['id'] for e in entries] == list(data['papers']), 'Publication membership/order changed'
    record['data-publication-style'] = VERSION
    note = record.select_one('.section-note')
    if note:
        note.string = '* Equal contribution · † Project lead.'
    for entry in entries:
        key = entry['id']; details = data['papers'][key]; view = cfg['papers'][key]
        assert entry.select_one('.pub-title').get_text(' ', strip=True) == details['source_title'], key
        media_before = str(entry.select_one('.research-media'))
        byline = entry.select_one('.pub-authors')
        byline.clear()
        byline.append(BeautifulSoup(authors_markup(details, data['profiles']), 'html.parser'))
        meta = entry.select_one('.research-meta')
        old_role = meta.select_one('.research-role')
        if old_role:
            entry['data-author-role'] = old_role.get_text(' ', strip=True)
        meta.clear()
        meta.append(BeautifulSoup('<span>' + venue_markup(details) + '</span>', 'html.parser'))
        for old in entry.select('.research-summary, .research-evidence'):
            old.decompose()
        tldr = doc.new_tag('p', attrs={'class': ['research-summary', 'pub-tldr']})
        marker = doc.new_tag('span', attrs={'class': 'tldr-label'})
        marker.string = 'TL;DR: '
        tldr.append(marker); tldr.append(details['tldr'])
        meta.insert_after(tldr)
        links = entry.select_one('.research-links')
        if links is None:
            links = doc.new_tag('nav', attrs={'class': 'research-links', 'aria-label': 'Research resources'})
        else:
            links.extract(); links.clear()
        links.append(BeautifulSoup(resource_markup(resource_records(view, details)), 'html.parser'))
        tldr.insert_after(links)
        assert str(entry.select_one('.research-media')) == media_before, key
    if not doc.select_one('link[href^="assets/css/publications-classic.css"]'):
        doc.head.append(doc.new_tag('link', rel='stylesheet', href='assets/css/publications-classic.css?v=' + VERSION))
        doc.head.append(doc.new_tag('link', rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap'))
    return doc
