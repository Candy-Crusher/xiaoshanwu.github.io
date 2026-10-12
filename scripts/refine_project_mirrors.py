#!/usr/bin/env python3
"""Small compatibility repairs to COPIES only; original project sites are untouched."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
CSS={
'eag3r': '''
.content-image.half-width{max-width:min(600px,100%);box-sizing:border-box}
.content-image.full-width{box-sizing:border-box}
.method-grid>*{min-width:0}
.video-compare-container,.vis-comparison-container,pre{max-width:100%;box-sizing:border-box}
@media(max-width:650px){.content-block{padding:1.3rem}.teaser-grid{min-width:0}.teaser-grid>*{min-width:0}}
''',
'sandbox': '''
.mirror-table-scroll{max-width:100%;min-width:0;overflow-x:auto;-webkit-overflow-scrolling:touch}
.rdf-frame{box-sizing:border-box;max-width:100%}
mjx-container:not([display="true"]){display:inline-block;max-width:100%;overflow-x:auto;overflow-y:hidden;padding:.2em 0;vertical-align:middle}
@media(max-width:768px){
  .container,.columns,.column,.rdf-panel,.rdf-panel-body{min-width:0}
  .cover-content,.cover-title,.cover-subtitle{max-width:100%;box-sizing:border-box}
  .button{max-width:100%}
  pre{max-width:100%;box-sizing:border-box}
}
'''
}
def game_figures():
 folder=ROOT/'projects/game';path=folder/'index.html'
 if not path.is_file() or not (folder/'assets/teaser-hd.webp').is_file():return
 soup=BeautifulSoup(path.read_text(),'html.parser')
 def image(figure,name,caption):
  im=figure.find('img');w,h=Image.open(folder/'assets'/f'{name}-hd.webp').size
  sw,_=Image.open(folder/'assets'/f'{name}.webp').size
  im['src']=f'assets/{name}.webp';im['srcset']=f'assets/{name}.webp {sw}w, assets/{name}-hd.webp {w}w';im['sizes']='(max-width:800px) calc(100vw - 40px),1120px';im['width']=w;im['height']=h;im['alt']=caption
  figure.find('a')['href']=f'assets/{name}-hd.webp'
  cap=figure.find('figcaption');cap.clear();cap.append(caption+' ')
  link=soup.new_tag('a',href=f'assets/{name}.pdf');link['target']='_blank';link['rel']='noopener';link.string='Original PDF ↗';cap.append(link)
 hero=soup.select_one('.hero-figure')
 if hero:image(hero,'teaser','Conceptual project overview from the original manuscript figure. The scenes, point cloud and example answer illustrate the approach; they are not evaluated predictions.')
 if (folder/'assets/method-hd.webp').is_file():
  figure=soup.find(id='game-original-method')
  if figure is None:
   figure=soup.new_tag('figure',id='game-original-method');figure['class']='figure full'
   a=soup.new_tag('a',href='assets/method-hd.webp');a['class']='figure-link';a['aria-label']='Enlarge original GaMe method figure';a.append(soup.new_tag('img',loading='lazy',decoding='async'));figure.append(a);figure.append(soup.new_tag('figcaption'));soup.find(id='method').append(figure)
  image(figure,'method','Original method diagram: visual and geometric features, geometric working memory, and answer generation.')
 path.write_text(str(soup))
 checklist=ROOT/'projects/CONTENT_CHECKLIST.md'
 if checklist.is_file():checklist.write_text(checklist.read_text().replace('Approved method figure, benchmark table and real question–answer examples.','Benchmark table and real evaluated question–answer examples. The original teaser and method figure have been imported.'))
def main():
 for slug,css in CSS.items():
  folder=ROOT/'projects'/slug;path=folder/'index.html'
  if not path.is_file():continue
  soup=BeautifulSoup(path.read_text(),'html.parser')
  style=soup.find('style',id='mirror-compatibility')
  if style is None:style=soup.new_tag('style',id='mirror-compatibility');soup.head.append(style)
  style.string=css
  if slug=='sandbox':
   for table in soup.select('table'):
    if table.parent.get('class')==['mirror-table-scroll']:continue
    wrapper=soup.new_tag('div');wrapper['class']='mirror-table-scroll';wrapper['tabindex']='0';wrapper['role']='region';wrapper['aria-label']='Research result table, scroll horizontally on small screens';table.wrap(wrapper)
   js=folder/'static/js/index.js'
   if js.is_file():
    text=js.read_text()
    for call in ['preloadInterpolationImages();','setInterpolationImage(0);']:
     guarded="if (document.getElementById('interpolation-image-wrapper')) "+call
     if guarded not in text:text=text.replace(call,guarded)
    js.write_text(text)
  else:
   for link in soup.find_all('a',href='#'):
    if link.get_text(strip=True).lower() in ['arxiv','paper']:link['href']='https://arxiv.org/abs/2512.00771'
  path.write_text(str(soup))
 game_figures()
 provenance=ROOT/'projects/media-provenance.json'
 if provenance.is_file():
  data=json.loads(provenance.read_text());data['copy_repairs']=['Kept original layouts; made EAG3R fixed-width figures responsive.','Contained SANDBOX long inline equations and result tables within horizontal-scroll regions.','Disabled the unused Nerfies interpolation preloader when its target element is absent; this prevents 240 requests to files that do not exist on the original source site.']
  data['notes']=[s for s in data.get('notes',[]) if 'Some resources also failed' not in s and 'The source audit records' not in s]
  data['notes'].append('The source audit records historical unused-template failures; the copied site guards the unused interpolation preloader. The promotional cover retrieved from the EAG3R code repository is not presented as a measured reconstruction output.')
  data['game_figures']='See projects/game/assets/sources.json for hashes and original-source render dimensions.'
  provenance.write_text(json.dumps(data,indent=2))
if __name__=='__main__':main()
