#!/usr/bin/env python3
"""Idempotent post-build integration; preserves the two original website layouts."""
from pathlib import Path
from bs4 import BeautifulSoup
import re,json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'projects'
BASE='https://candy-crusher.github.io/xiaoshanwu.github.io/'
MIRRORS=[('sandbox','S4NDBOX','Verifiable 4D World–Action Model for Robust Robot Control'),('eag3r','EAG3R','Event-Augmented 3D Geometry Estimation for Dynamic and Extreme-Lighting Scenes')]

def responsive(soup,img,slug,name):
    folder=P/slug/'assets'
    if not (folder/(name+'-hd.webp')).is_file():return
    from PIL import Image
    w,h=Image.open(folder/(name+'-hd.webp')).size
    sw,sh=Image.open(folder/(name+'.webp')).size
    img['src']='assets/'+name+'.webp';img['srcset']=f'assets/{name}.webp {sw}w, assets/{name}-hd.webp {w}w';img['sizes']='(max-width: 800px) calc(100vw - 40px), 1120px'
    img['width']=w;img['height']=h;img['style']='width:100%;height:auto;object-fit:contain'
    if img.parent.name=='a':img.parent['href']='assets/'+name+'-hd.webp'
    else:
        a=soup.new_tag('a',href='assets/'+name+'-hd.webp');a['target']='_blank';a['rel']='noopener';a['aria-label']='Open original figure in high resolution';img.wrap(a)
    figure=img.find_parent('figure')
    if figure and not figure.select('.source-pdf'):
        caption=figure.find('figcaption')
        if caption:
            a=soup.new_tag('a',href='assets/'+name+'.pdf');a['class']='source-pdf';a.string='Original PDF ↗';a['target']='_blank';a['rel']='noopener';caption.append(' ');caption.append(a)

def main():
    if not P.exists():return
    for slug,name,title in MIRRORS:
        path=P/slug/'index.html'
        if not path.is_file():continue
        soup=BeautifulSoup(path.read_text(),'html.parser')
        canonical=soup.find('link',rel='canonical')
        if canonical is None:canonical=soup.new_tag('link',rel='canonical');soup.head.append(canonical)
        canonical['href']=BASE+'projects/'+slug+'/'
        if soup.find(id='project-directory-nav') is None:
            nav=soup.new_tag('nav',id='project-directory-nav');nav['aria-label']='Research project directory';nav['style']='font-family:system-ui,sans-serif;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:10px 24px;font-size:12px;background:#f7f8f9;border-bottom:1px solid #e2e5e8;position:relative;z-index:30;'
            a=soup.new_tag('a',href='../');a.string='← All research projects';nav.append(a)
            a=soup.new_tag('a',href='../../');a.string='Xiaoshan Wu · Homepage';nav.append(a)
            soup.body.insert(0,nav)
        if slug=='eag3r':
            img=soup.find('img',src='assets/fig1_concept.png') or soup.find('img',src='assets/concept.webp')
            if img:responsive(soup,img,'eag3r','concept')
        path.write_text(str(soup))
    path=P/'videossm/index.html'
    if path.is_file():
        soup=BeautifulSoup(path.read_text(),'html.parser');img=soup.select_one('.hero-figure img')
        if img:responsive(soup,img,'videossm','overview')
        path.write_text(str(soup))
    for slug,name,caption in [('lifr-seg','teaser','Original LiFR-Seg teaser: semantic predictions at interframe query times.'),('lifr-v2','teaser','Original project teaser from the official LiFR v2 repository.')]:
        path=P/slug/'index.html'
        if not path.is_file() or not (P/slug/'assets'/f'{name}-hd.webp').is_file():continue
        soup=BeautifulSoup(path.read_text(),'html.parser')
        figure=soup.find(id='repository-hd-teaser')
        if figure is None:
            figure=soup.new_tag('figure',id='repository-hd-teaser');figure['class']='figure hero-figure'
            a=soup.new_tag('a',href=f'assets/{name}-hd.webp');a['class']='figure-link';a['aria-label']='Enlarge original project teaser'
            img=soup.new_tag('img',src=f'assets/{name}.webp',alt=caption);img['decoding']='async';a.append(img);figure.append(a)
            cap=soup.new_tag('figcaption');cap.string=caption;figure.append(cap)
            tldr=soup.select_one('.tldr');tldr.insert_after(figure)
        responsive(soup,figure.find('img'),slug,name)
        other=soup.select_one('.hero-figure:not(#repository-hd-teaser)')
        if other:
            target=soup.find(id='results' if slug=='lifr-seg' else 'method')
            if target:
                other['class']='figure full';target.append(other.extract())
        path.write_text(str(soup))
    for path in [P/'index.html',*[P/slug/'index.html' for slug in ['videossm','game','lifr-seg','lifr-v2','evsplat']]]:
        if not path.is_file():continue
        soup=BeautifulSoup(path.read_text(),'html.parser');is_hub=path==P/'index.html'
        for slug,name,title in MIRRORS:
            if not (P/slug/'index.html').is_file():continue
            href=('' if is_hub else '../')+slug+'/'
            nav=soup.select_one('footer nav')
            if nav and not nav.find('a',href=href):
                a=soup.new_tag('a',href=href);a.string=name;nav.append(a)
            listing=soup.select_one('.project-list') if is_hub else None
            if listing and not listing.find('a',href=href):
                li=soup.new_tag('li');a=soup.new_tag('a',href=href);li.append(a);d=soup.new_tag('div');a.append(d)
                strong=soup.new_tag('strong');strong.string=name;d.append(strong)
                small=soup.new_tag('small');small.string='Original project website · Local copy';d.append(small)
                summary=soup.new_tag('span');summary.string=title;a.append(summary)
                arrow=soup.new_tag('span');arrow['class']='arrow';arrow['aria-hidden']='true';arrow.string='↗';a.append(arrow)
                listing.insert(0,li)
        path.write_text(str(soup))
    for filename in ['index.html','publications.html']:
        path=ROOT/filename
        if not path.is_file():continue
        text=path.read_text()
        if (P/'sandbox/index.html').is_file():text=text.replace('https://demo1-indol-gamma.vercel.app/','projects/sandbox/')
        if (P/'eag3r/index.html').is_file():
            text=text.replace('https://candy-crusher.github.io/EAG3R_Proj/','projects/eag3r/')
            if filename=='publications.html':
                pattern=r'(<li id="pub-eag3r">)(.*?)(</li>)'
                def fix(m):
                    inner=m.group(2)
                    if 'projects/eag3r/' not in inner:inner=inner.replace('class="paper-links">','class="paper-links"><a href="projects/eag3r/">Project</a> ',1)
                    return m.group(1)+inner+m.group(3)
                text=re.sub(pattern,fix,text,flags=re.S)
        path.write_text(text)
    from refine_project_mirrors import main as refine
    refine()
    print('Integrated available mirrors and original-source high-resolution figures.')
if __name__=='__main__':main()
