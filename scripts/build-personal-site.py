#!/usr/bin/env python3
"""Build a combined Home/Research page, Resume and About from CV02 facts.

The TeX parser preserves authors, statuses, dates, skills and awards. The separate
site-presentation.json controls short summaries, existing-image crops, and page
selection. Never write the CVs, PDFs, or individual research project pages.
"""
from pathlib import Path
from copy import deepcopy
import hashlib, html, json, re
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex'
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html', 'publications.html']
DESIGN = 'academic-home-research-20261014'
BASE = 'https://candy-crusher.github.io/xiaoshanwu.github.io/'


def group(s, i):
    while i < len(s) and s[i].isspace(): i += 1
    if i >= len(s) or s[i] != '{': raise ValueError('Missing TeX argument: ' + s[i:i+60])
    start, depth, i = i + 1, 1, i + 1
    while i < len(s):
        if s[i] == '\\' and i+1 < len(s) and s[i+1] in '{}': i += 2; continue
        if s[i] == '{': depth += 1
        if s[i] == '}': depth -= 1
        if not depth: return s[start:i], i+1
        i += 1
    raise ValueError('Unclosed TeX argument')


def inline(s, graduation=''):
    out, i = [], 0
    while i < len(s):
        if s[i] == '{':
            arg, i = group(s, i); out.append(inline(arg, graduation)); continue
        if s[i] != '\\':
            out.append(html.escape(' ' if s[i] == '~' else s[i])); i += 1; continue
        m = re.match(r'\\([A-Za-z]+|.)', s[i:])
        if not m: raise ValueError('Incomplete TeX command')
        cmd = m[1]; i += len(m[0])
        if cmd in ('textbf', 'textit', 'underline', 'pubnote'):
            arg, i = group(s, i); value = inline(arg, graduation)
            tag = {'textbf':'strong', 'textit':'em', 'underline':'span', 'pubnote':'span'}[cmd]
            out.append(f'<{tag}>{value}</{tag}>')
        elif cmd == 'textcolor':
            color, i = group(s, i); arg, i = group(s, i); value = inline(arg, graduation)
            out.append('<span class="highlight">'+value+'</span>' if color == 'cvred' else value)
        elif cmd == 'href':
            url, i = group(s, i); label, i = group(s, i)
            out.append('<a href="'+html.escape(url.replace(r'\&','&'), quote=True)+'">'+inline(label, graduation)+'</a>')
        elif cmd == 'fontsize':
            _, i = group(s, i); _, i = group(s, i)
        elif cmd == 'ExpectedGraduation': out.append(graduation)
        elif cmd in ('selectfont','bfseries','dashitem','relax'): pass
        elif cmd in ('par','quad','hfill','enspace',' ', ',', ';'): out.append(' ')
        elif cmd in ('textdagger','ldots','textperiodcentered'): out.append({'textdagger':'†','ldots':'…','textperiodcentered':'·'}[cmd])
        elif cmd in ('&','%','_','#','$','{','}'): out.append(html.escape(cmd))
        else: raise ValueError('Unsupported TeX command: ' + cmd)
    return re.sub(r'\s+', ' ', ''.join(out).replace('---','—').replace('--','–')).strip()


def plain(s): return BeautifulSoup(s, 'html.parser').get_text(' ', strip=True)
def fragment(s): return BeautifulSoup(s, 'html.parser')
def set_inner(node, content):
    if node is None: raise ValueError('Missing existing website element')
    node.clear()
    for c in list(fragment(content).contents): node.append(c)
def normalized(s): return re.sub(r'[^a-z0-9]', '', plain(s).lower())
def section(s, name):
    start = s.index('\\cvsection{'+name+'}') + len('\\cvsection{'+name+'}')
    return s[start:].split('\\cvsection{', 1)[0].split('\\end{document}',1)[0].strip()
def no_comments(s): return '\n'.join(re.sub(r'(?<!\\)%.*', '', l) for l in s.splitlines())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_cv():
    raw = (ROOT/SOURCE).read_bytes()
    if (ROOT/'cv.tex').read_bytes() != raw:
        raise ValueError('Public cv.tex is not CV 02. Copy '+SOURCE+' to cv.tex and rebuild the public PDF before publishing.')
    s = no_comments(raw.decode())
    match = re.search(r'\\newcommand\{\\ExpectedGraduation\}\{',s)
    graduation = inline(group(s, match.end()-1)[0])
    interests = [inline(l) for l in section(s,'Research Interests').splitlines() if l.strip()]
    if len(interests) != 4: raise ValueError('Review the Research Interests paragraph structure')
    education = []
    for m in re.finditer(r'\\begin\{tabularx\}[^\n]*\n(.*?)\\end\{tabularx\}(.*?)(?=\\begin\{tabularx\}|\Z)', section(s,'Education'), re.S):
        rows = re.split(r'\\\\\[[^]]*\]', m[1])
        school, location = re.split(r'(?<!\\)\s&\s', rows[0], maxsplit=1)
        role, dates = re.split(r'(?<!\\)\s&\s', rows[1], maxsplit=1)
        detail = re.search(r'\\begin\{tabular\}[^\n]*\n(.*?)\\end\{tabular\}',m[2],re.S)
        details = [inline(x, graduation) for x in re.split(r'\\\\\[[^]]*\]',detail[1]) if x.strip()]
        education.append(dict(school=plain(inline(school)),location=plain(inline(location)),role=plain(inline(role)),dates=plain(inline(dates)),details=details))
    if len(education)!=3: raise ValueError('Expected the three education/research entries in CV 02')
    skills = [inline(x) for x in section(s,'Technical Skills').split(r'\par') if x.strip()]
    awards = [inline(x) for x in section(s,'Selected Awards').replace(r'\par',';').split(';') if x.strip()]
    papers=[]
    blocks=re.findall(r'\\begin\{enumerate\}\[[^]]*\](.*?)\\end\{enumerate\}',section(s,r'Publications \& Preprints'),re.S)
    for bi, block in enumerate(blocks):
        for item in re.split(r'\\item\s+',block)[1:]:
            title, end=group(item,item.index(r'\textbf')+len(r'\textbf'))
            first, rest=item[end:].split(r'\par',1)
            link_match=re.search(r'\\href\{([^}]+)\}', first)
            lines=[l.strip() for l in rest.splitlines() if l.strip()]
            if bi==0:
                author=lines[0].removesuffix(r'\par')
                venue, role=lines[1].split(r'\hfill',1)
                note=' '.join(lines[2:])
            else:
                author, venue=lines[0].split(r'\hfill',1);role='';note=''
            authors=inline(author)
            authors=re.sub(r'([*†]+)',r'<sup>\1</sup>',authors)
            papers.append(dict(title=plain(inline(title)).rstrip('.'),authors=authors,venue=inline(venue),role=plain(inline(role)),summary=inline(note),project_url=link_match[1] if link_match else None,group=bi))
    if len(papers)!=15 or sum(p['group']==0 for p in papers)!=8: raise ValueError('Review the paper counts')
    for paper in papers:
        if 'X.Wu' not in plain(paper['authors']).replace(' ',''): raise ValueError('Author name missing')
    return dict(source=SOURCE,source_git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                graduation=graduation,interests=interests,education=education,skills=skills,awards=awards,papers=papers)


# Facts are parsed above. Page-specific editorial choices live separately in
# site-presentation.json; changing the CV never expands every page into the CV.
STYLE = 'assets/css/site-pages.css?v=academic-home-research-20261014'
SCRIPT = 'assets/js/site-pages.js?v=academic-home-research-20261014'


# Verified personal pages. These are presentation links, not edits to CV02.
MENTOR_PROFILES = {
    'Yilun Du': 'https://yilundu.github.io/',
    'Mengyu Wang': 'https://wang.hms.harvard.edu/team/dr-wang/',
}


def mentor_links(content):
    """Link plain mentor names without changing text or nesting existing links."""
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, MENTOR_PROFILES)) + r')\b')
    doc = fragment(content)
    before = doc.get_text()
    for node in list(doc.find_all(string=pattern)):
        if node.find_parent(['a', 'script', 'style', 'code', 'pre']):
            continue
        text, cursor, parts = str(node), 0, []
        for match in pattern.finditer(text):
            parts.append(NavigableString(text[cursor:match.start()]))
            anchor = doc.new_tag('a', href=MENTOR_PROFILES[match[0]], target='_blank', rel='noopener')
            anchor.string = match[0]
            parts.append(anchor)
            cursor = match.end()
        parts.append(NavigableString(text[cursor:]))
        node.replace_with(*parts)
    assert doc.get_text() == before, 'Mentor linking changed visible text'
    assert not doc.select('a a'), 'Nested mentor links'
    return str(doc)


def esc(value):
    return html.escape(str(value), quote=True)


def link(url, label, extra=''):
    external = ' target="_blank" rel="noopener"' if url.startswith(('https://', 'http://')) else ''
    return f'<a href="{esc(url)}"{external}{extra}>{label}</a>'


def navigation(cfg, page):
    current = 'index.html' if page in ('research.html', 'publications.html') else page
    return ''.join(link(n['url'], esc(n['label']), ' aria-current="page"' if n['url'] == current else '') for n in cfg['navigation'])


def document(name, content, cfg, cv):
    title = 'Xiaoshan Wu' if name == 'index.html' else name.split('.')[0].title() + ' | Xiaoshan Wu'
    canonical = 'index.html' if name in ('research.html', 'publications.html') else name
    description = 'Xiaoshan Wu — world models for generalizable robotic planning, spatial perception, and embodied intelligence.'
    nav = navigation(cfg, name)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="author" content="Xiaoshan Wu"><meta name="color-scheme" content="light">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{BASE}{canonical}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:url" content="{BASE}{canonical}">
<link rel="stylesheet" href="{STYLE}"><script defer src="{SCRIPT}"></script>
</head>
<body class="site-layout" data-page="{name.split('.')[0]}" data-design="{DESIGN}" data-resume-source="cv02" data-resume-source-blob="{cv['source_git_blob']}" id="top">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-topbar"><div class="site-header wrap">{link('index.html','Xiaoshan Wu',' class="wordmark" aria-label="Xiaoshan Wu, Home"')}<nav class="site-nav" aria-label="Main navigation">{nav}</nav></div></header>
<main class="wrap" id="main">{content}</main>
<footer class="site-footer wrap"><span>© 2026 Xiaoshan Wu</span><nav aria-label="Footer navigation">{nav}{link('mailto:wuxiaoshan630@gmail.com','Email')}</nav></footer>
<dialog class="figure-dialog" id="research-figure" aria-labelledby="figure-heading"><div class="dialog-bar"><p id="figure-heading">Research figure</p><button type="button" class="figure-close">Close ×</button></div><img class="figure-dialog-image" alt=""><p class="figure-dialog-caption"></p></dialog>
</body></html>
'''


def media(view, url):
    m = view.get('media')
    if not m:
        return ''
    crop = m.get('crop')
    style = ''
    if crop:
        x, y, w, h = crop
        frame_style = f'aspect-ratio:{w}/{h}'
        style = f'position:absolute;width:{m["width"] / w * 100:.5f}%;max-width:none;height:auto;left:{-x / w * 100:.5f}%;top:{-y / h * 100:.5f}%'
    else:
        frame_style = f'aspect-ratio:{m["width"]}/{m["height"]}'
    image = f'<span class="media-frame" style="{frame_style}"><img src="{esc(m["src"])}" alt="{esc(m["alt"])}" width="{m["width"]}" height="{m["height"]}" loading="lazy" decoding="async" style="{style}"></span>'
    return '<figure class="research-media">' + link(url, image, ' class="media-link" aria-label="Open project"') + '<figcaption>' + esc(m['caption']) + '</figcaption></figure>'


def resource_links(view, home=False):
    links = []
    for r in view.get('resources', []):
        if home and not r.get('home'):
            continue
        extra = ' data-figure' if r.get('figure') else ''
        links.append(link(r['url'], esc(r['label']), extra))
    return '<nav class="research-links" aria-label="Research resources">' + ''.join(links) + '</nav>' if links else ''


def authors_short(authors):
    parts = authors.rstrip('. ').split(', ')
    if len(parts) <= 3:
        return authors
    selected = parts[:3]
    if not any('X. Wu' in p for p in selected):
        # Never let abbreviation hide the site's author.
        selected = parts[:2] + [next(p for p in parts if 'X. Wu' in p)]
    return ', '.join(selected) + ', et al.'


def metadata(paper):
    venue = paper['venue'].rstrip('.')
    role = '<span class="research-role">' + esc(paper['role']) + '</span>' if paper['role'] else ''
    return '<p class="research-meta"><span>' + venue + '</span>' + role + '</p>'


def home_page(cfg, papers, cv, data):
    contacts = ''.join(link(u,l) for l,u in [('Email','mailto:wuxiaoshan630@gmail.com'),('Google Scholar','https://scholar.google.com/citations?user=9nsSKpsAAAAJ&hl=en'),('GitHub','https://github.com/Candy-Crusher'),('CV (PDF)','Xiaoshan_Wu_CV.pdf')])
    # The first paragraph is explicitly supplied by the user. The second uses
    # CV02 verbatim, without upgrading future interests into completed work.
    interests = ' '.join(cv['interests'][i] for i in cfg['home']['interest_indices'])
    content = f'''<section class="profile" id="welcome" aria-labelledby="name">
<div class="profile-heading"><h1 id="name">Xiaoshan Wu <span lang="zh">吴小山</span></h1></div>
<figure class="portrait"><img src="images/research/profile.webp" alt="Xiaoshan Wu" width="170" height="222" decoding="async" fetchpriority="high"></figure>
<div class="profile-copy"><p class="biography">{mentor_links(cfg['home']['identity'])}</p><p class="research-lead" id="research-interests">{interests}</p><nav class="contact-links" aria-label="Contact and profiles">{contacts}</nav></div>
</section>'''
    # One visible record replaces both the former featured list and Research.
    content += research_page(cfg, papers, cv, embedded=True)
    content += '<section class="news-section" aria-labelledby="news"><h2 id="news">Recent updates</h2>'
    content += data['news'].replace('publications.html#','#').replace('research.html#','#') + '</section>'
    return content


def research_page(cfg, papers, cv, embedded=False):
    # Legacy research.html/publications.html keep a complete no-JS fallback.
    level = 2 if embedded else 1
    content = f'<section class="research-record" id="research" aria-labelledby="research-title"><header class="research-heading"><h{level} id="research-title">Research &amp; Publications</h{level}></header>'
    if not embedded:
        content += '<p class="legacy-notice">Research now lives on the '+link('index.html#research','homepage')+'. This page preserves previously shared links.</p>'
    content += '<nav class="section-links" aria-label="Research sections">' + link('#first-author-work','First- &amp; co-first-author work') + link('#collaborative-work','Collaborative work') + '</nav>'
    content += '<div id="publications"><span class="anchor-alias" id="direction"></span><span class="anchor-alias" id="projects"></span><span class="anchor-alias" id="selected-research"></span>'
    for group_idx, heading, anchor in [(0,'First- and Co-first-author Work','first-author-work'),(1,'Collaborative Work','collaborative-work')]:
        content += f'<section class="publication-group" aria-labelledby="{anchor}"><h{level+1} class="publication-group-title" id="{anchor}">{heading}</h{level+1}>'
        if group_idx == 0:
            content += '<p class="section-note">* Equal contribution · † Project lead. Publication and review status are indicated for each work.</p>'
        content += '<ol class="publication-list '+('lead-papers' if group_idx == 0 else 'collaborative-papers')+'" start="'+('1' if group_idx==0 else '9')+'">'
        for id, p in papers.items():
            if p['group'] != group_idx:
                continue
            v = cfg['papers'][id]
            dest = p['project_url'] or next((x['url'] for x in v['resources'] if x['label']=='Paper'), None)
            title = link(dest, esc(p['title'])) if dest else esc(p['title'])
            image = media(v, dest) if dest else ''
            summary = '<p class="research-summary">'+esc(v['summary'])+'</p>' if v.get('summary') else ''
            evidence = '<p class="research-evidence">'+v['evidence']+'</p>' if v.get('evidence') else ''
            alias = '<span class="anchor-alias" id="'+id.replace('pub-','selected-',1)+'"></span>' if p['project_url'] else ''
            content += f'<li id="{id}" data-paper="{id}" class="publication-entry '+('with-media' if image else 'text-only')+f'">{alias}<div class="publication-layout">{image}<div class="research-copy"><h{level+2} class="pub-title">{title}</h{level+2}>{metadata(p)}<p class="pub-authors research-authors">{p["authors"]}</p>{summary}{evidence}{resource_links(v)}</div></div></li>'
        content += '</ol></section>'
    return content + '</div></section>'


def experience_row(e):
    return '<div class="experience-row"><div><h3>'+esc(e['school'])+'</h3><p class="position">'+esc(e['role'])+'</p>'+''.join('<p class="detail">'+mentor_links(x)+'</p>' for x in e['details'])+'</div><p class="dates">'+esc(e['dates'])+'<br><span>'+esc(e['location'])+'</span></p></div>'


def resume_page(cfg, papers, cv):
    def sec(id,heading,body):
        return f'<section class="resume-section" id="{id}"><h2>{heading}</h2><div>{body}</div></section>'
    content = '<header class="page-heading resume-heading"><h1>Resume</h1><div class="download-links">'+link('Xiaoshan_Wu_CV.pdf','View CV (PDF)',' target="_blank" rel="noopener"')+link('Xiaoshan_Wu_CV.pdf','Download PDF',' download="Xiaoshan_Wu_CV.pdf"')+'</div></header>'
    content += '<p class="resume-intro">World models for generalizable robotic planning. '+link('index.html#research','Browse research &amp; publications →')+'</p><div id="background">'
    experience = [e for e in cv['education'] if 'Visiting' in e['role']]
    education = [e for e in cv['education'] if 'Visiting' not in e['role']]
    content += sec('experience','Research Experience',''.join(experience_row(e) for e in experience))
    content += sec('education','Education',''.join(experience_row(e) for e in education))
    content += sec('skills','Technical Skills',''.join('<p class="skill-line">'+s+'</p>' for s in cv['skills']))
    content += sec('awards','Selected Awards','<ul class="awards">'+''.join('<li>'+s.rstrip('.')+'</li>' for s in cv['awards'])+'</ul>')
    return content + '</div>'


def about_page(cfg, papers, cv):
    a=cfg['about']
    content='<article class="about-essay"><header class="page-heading"><h1>About</h1><p>'+mentor_links(esc(a['background']))+'</p><p class="about-background-link">'+link('resume.html','Education &amp; experience →')+'</p></header>'
    content+='<section aria-labelledby="perspective"><h2 id="perspective">Research perspective</h2>'+''.join('<p>'+esc(s)+'</p>' for s in a['perspective'])+'</section>'
    content+='<section aria-labelledby="future"><h2 id="future">Looking ahead</h2><p>'+cv['interests'][3]+'</p></section>'
    content+='<section id="inspiration" aria-labelledby="inspiration-title"><h2 id="inspiration-title">A personal inspiration</h2><p>'+a['inspiration']+'</p><figure class="inspiration-figure"><img src="images/theme/shared-world-1440.webp" alt="Film still from Blade Runner 2049" width="1440" height="603" loading="lazy" decoding="async"><figcaption><cite>Blade Runner 2049</cite> (2017). Visual inspiration, not a research result. '+link('images/theme/shared-world-source.json','Image source')+'. All rights belong to the respective rights holders.</figcaption></figure></section></article>'
    return content


def main():
    paths=[ROOT/'cv.tex',ROOT/'Xiaoshan_Wu_CV.pdf',ROOT/'ia8eshfzfsvn.pdf',*sorted((ROOT/'cv/2027-internships').glob('*.tex')),*sorted((ROOT/'projects').glob('*/index.html'))]
    protected={str(p.relative_to(ROOT)):digest(p) for p in paths if p.is_file()}
    cv=parse_cv()
    cfg=json.loads((ROOT/'_site_content/site-presentation.json').read_text())
    data=json.loads((ROOT/'_site_content/personal-site.json').read_text())
    lookup={normalized(v['source_title']):id for id,v in cfg['papers'].items()}
    papers={lookup[normalized(p['title'])]:p for p in cv['papers']}
    assert len(papers)==15 and cfg['home']['interest_indices']==[0,1,3]
    assert cfg['navigation']==[{'label':l,'url':u} for l,u in [('Home','index.html'),('Resume','resume.html'),('About','about.html')]]
    bodies={'index.html':home_page(cfg,papers,cv,data),'research.html':research_page(cfg,papers,cv),'resume.html':resume_page(cfg,papers,cv),'about.html':about_page(cfg,papers,cv)}
    # Legacy URLs redirect to Home and preserve all paper anchors; no-JS fallback remains.
    bodies['publications.html']=bodies['research.html']
    for name,body in bodies.items():
        (ROOT/name).write_text(document(name,body,cfg,cv))
    cv['publication_anchors']=list(papers)
    (ROOT/'_site_content/resume-cv02.json').write_text(json.dumps(cv,ensure_ascii=False,indent=2)+'\n')
    assert all(digest(ROOT/n)==h for n,h in protected.items()), 'A protected CV or project page changed'
    report={'design':DESIGN,'source':SOURCE,'source_git_blob':cv['source_git_blob'],'publication_count':15,'first_author_count':8,'collaborative_count':7,'homepage_publications':len(papers),'intro_paragraphs':2,'publications_visible_without_javascript':True,'separate_awards_section':True,'protected_files':protected,'page_roles':{'Home':'Harvard-first biography, CV02 interests and the complete research record','Resume':'Experience, education, skills and awards','About':'Motivation and future interests','Legacy Research/Publications':'Hash-preserving redirect to Home with a no-JS record'}}
    Path('/tmp/personal-site-style-preservation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='protected_files'},indent=2))


if __name__=='__main__':
    main()
