#!/usr/bin/env python3
"""Sync the existing quiet academic website from CV 02 without changing its design.

The 02 Robotics TeX is authoritative for the public resume, interests, skills,
awards, publication order and metadata. Research figures, original resource
links, personal inspiration, and the other tailored CVs remain untouched.
The root cv.tex must be an exact copy; the existing CV workflow builds its PDF.
"""
from pathlib import Path
from copy import deepcopy
import hashlib, html, json, re
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex'
PAGES = ['index.html', 'about.html', 'resume.html', 'research.html', 'publications.html']
DESIGN = 'quiet-academic-20261013'
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


def education_html(e, i):
    details=''.join('<p class="detail">'+d+'</p>' for d in e['details'])
    return '<div class="experience-row"'+(' id="experience"' if i==0 else '')+'><div><strong>'+html.escape(e['school'])+'</strong><p>'+html.escape(e['role'])+'</p>'+details+'</div><div class="dates">'+html.escape(e['dates'])+'<br>'+html.escape(e['location'])+'</div></div>'


def synchronize(docs, cv, data):
    interests=cv['interests'];theme='World models for generalizable robotic planning'
    if normalized(theme) not in normalized(interests[0]): raise ValueError('Review the website theme against the chosen CV')
    rows=[education_html(e,i) for i,e in enumerate(cv['education'])]
    # The source specifies a current visiting scholar, not the previous site's
    # expired visiting-researcher entry. No additional dates or roles are inferred.
    bio='I am a Ph.D. candidate at the University of Hong Kong, advised by <a href="https://xjqi.github.io/">Xiaojuan Qi</a>, and a Visiting Scholar at Harvard University, working with Yilun Du and Mengyu Wang.'
    data.update(resume_source=SOURCE,resume_source_blob=cv['source_git_blob'],bio='<p>'+bio+'</p>',direction='<p>'+interests[0]+'</p>',
                foundation='<p>'+interests[1]+' '+interests[2]+'</p>',future='<p>'+interests[3]+'</p>',experience=rows,
                awards='<ul class="awards">'+''.join('<li>'+a+'</li>' for a in cv['awards'])+'</ul>',skills=cv['skills'])
    home=docs['index.html'];copy=home.select_one('.academic-copy');contacts=deepcopy(copy.select_one('.contact-links'))
    set_inner(copy,'<p>'+bio+'</p>'+data['direction']+data['foundation']);copy.append(contacts)
    about=docs['about.html']
    set_inner(about.select_one('.about-profile .section-body'),'<p>'+bio+'</p><p>I received dual B.S. degrees in Computer Engineering through the ZJUI Institute at Zhejiang University and UIUC.</p>')
    perspective=about.find(id='perspective').find_next_sibling()
    old_links=deepcopy(perspective.select_one('.inline-links'))
    set_inner(perspective,data['direction']+data['foundation']+'<div class="future-note"><p class="section-label">Looking ahead</p>'+data['future']+'</div>')
    if old_links: perspective.append(old_links)
    set_inner(about.select_one('.page-heading > p'),theme+'.')
    resume=docs['resume.html'];main=resume.main
    heading=deepcopy(main.select_one('.page-heading'));download=deepcopy(main.select_one('.cv-download'))
    set_inner(heading.select_one('p'),'Research, education, experience, and selected awards.')
    def sec(id,title,body): return '<section class="resume-section" id="'+id+'"><h2>'+title+'</h2><div>'+body+'</div></section>'
    content=str(heading)+str(download)+'<div id="background">'+sec('education','Education',''.join(rows))
    content+=sec('research-interests','Research interests',''.join('<p>'+p+'</p>' for p in interests))
    content+=sec('skills','Technical skills',''.join('<p class="skill-list">'+p+'</p>' for p in cv['skills']))
    content+=sec('awards','Selected Awards',data['awards'])+'</div>'
    content+=sec('resume-publications','Publications &amp; preprints','<p>First- and co-first-author work, followed by collaborative work.</p><div class="inline-links"><a class="text-link" href="research.html#publications">View the complete publication record →</a></div>')
    set_inner(main,content)
    research=docs['research.html']
    set_inner(research.select_one('.page-heading > p'),theme+'.')
    set_inner(research.select_one('#direction'),''.join('<p>'+p+'</p>' for p in interests))
    # Resolve stable publication anchors by matching titles, not list positions.
    archive=research.select_one('#publications')
    lookup={normalized(x.select_one('.pub-title').get_text()):x for x in archive.select('.publication-list > li')}
    source_ids=[]
    for p in cv['papers']:
        key=normalized(p['title'])
        if key not in lookup: raise ValueError('Publication title not found on the current site: '+p['title'])
        li=lookup[key];source_ids.append(li['id'])
        for whitespace in list(li.children):
            if isinstance(whitespace, NavigableString) and not whitespace.strip(): whitespace.extract()
        title_node=li.select_one('.pub-title');anchor=title_node.select_one('a')
        set_inner(anchor if anchor else title_node,html.escape(p['title']))
        set_inner(li.select_one('.pub-authors'),p['authors'])
        detail=li.select_one('.pub-detail');links=deepcopy(detail.select_one('.paper-links'))
        set_inner(detail,'<span class="paper-venue">'+p['venue']+'</span>'+('<span class="pub-role">'+html.escape(p['role'])+'</span>' if p['role'] else ''))
        if links: detail.append(links)
        for old in li.select('.s4ndbox-tldr, .cv-source-summary'): old.decompose()
        if p['summary']: li.append(fragment('<p class="research-summary cv-source-summary">'+p['summary']+'</p>').p)
    groups=archive.select('.publication-list')
    for group in groups: group.clear()
    for i,p in enumerate(cv['papers']): groups[p['group']].append(lookup[normalized(p['title'])])
    projects=research.select_one('.project-grid');project_order=[]
    for p,id in zip(cv['papers'],source_ids):
        entry=research.find(id=id.replace('pub-','selected-',1))
        if not entry: continue
        set_inner(entry.select_one('h3 a'),html.escape(p['title'].split(': ',1)[1] if ': ' in p['title'] else p['title']))
        set_inner(entry.select_one('.research-authors'),p['authors'])
        set_inner(entry.select_one('.research-meta'),'<span>'+p['venue']+'</span><span>'+html.escape(p['role'])+'</span>')
        if p['summary']: set_inner(entry.select_one('.research-summary'),p['summary'])
        project_order.append(entry)
    if len(project_order)!=7: raise ValueError('Expected seven unchanged project routes')
    projects.clear()
    for entry in project_order: projects.append(entry)
    # Refresh Home from the canonical metadata but keep the same three projects,
    # figures, resources, and compact academic row layout.
    selected=home.select_one('.selected-list');selected.clear()
    for id in ['selected-world-action-model','selected-game','selected-eag3r']:
        item=deepcopy(research.find(id=id));del item['id'];item['class']=['research-entry','home-research-entry']
        if item.select_one('figcaption'):item.select_one('figcaption').decompose()
        selected.append(item)
    # Keep the no-JavaScript archive fallback synchronized as well.
    fallback=docs['publications.html']
    old_groups=fallback.select('.publication-group');new_groups=archive.select('.publication-group')
    if len(old_groups)!=2: raise ValueError('Missing publication fallback groups')
    for old,new in zip(old_groups,new_groups):old.replace_with(deepcopy(new))
    data['publications']=[str(g) for g in new_groups]
    for name,doc in docs.items():
        doc.body['data-resume-source']='cv02';doc.body['data-resume-source-blob']=cv['source_git_blob']
        title=('Xiaoshan Wu | '+theme) if name=='index.html' else doc.title.get_text()
        doc.title.string=title
        if doc.select_one('meta[property="og:title"]'):doc.select_one('meta[property="og:title"]')['content']=title
        description='Xiaoshan Wu — '+theme.lower()+', 4D world–action modeling, and sim-to-real transfer.'
        for m in doc.select('meta[name="description"],meta[property="og:description"]'):m['content']=description
    return source_ids


def main():
    protected={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'cv.tex',ROOT/'Xiaoshan_Wu_CV.pdf',*sorted((ROOT/'cv/2027-internships').glob('*.tex'))]}
    docs={name:fragment((ROOT/name).read_text()) for name in PAGES}
    inspiration=str(docs['about.html'].select_one('#inspiration'))
    cv=parse_cv();data=json.loads((ROOT/'_site_content/personal-site.json').read_text())
    ids=synchronize(docs,cv,data)
    assert str(docs['about.html'].select_one('#inspiration'))==inspiration
    assert len(docs['research.html'].select('.publication-list > li'))==15
    assert docs['resume.html'].select_one('#awards h2').get_text()=='Selected Awards'
    for name,doc in docs.items():
        assert doc.body['data-design']==DESIGN
        (ROOT/name).write_text(str(doc).rstrip()+'\n')
    (ROOT/'_site_content/personal-site.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    cv['publication_anchors']=ids
    (ROOT/'_site_content/resume-cv02.json').write_text(json.dumps(cv,ensure_ascii=False,indent=2)+'\n')
    for name,sha in protected.items():assert digest(ROOT/name)==sha,name
    report=dict(design=DESIGN,source=SOURCE,source_git_blob=cv['source_git_blob'],public_cv_matches_source=True,
                publication_count=15,project_count=7,separate_awards_section=True,protected_cv_files=len(protected),
                publication_anchors=ids,inspiration_preserved=True)
    Path('/tmp/personal-site-style-preservation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
