#!/usr/bin/env python3
"""Small compatibility repairs to COPIES only; original project sites are untouched."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
ROOT=Path(__file__).resolve().parents[1]
CSS={
'eag3r': '''
/* Keep original layout and colours; contain full-resolution figures on phones. */
.content-image.half-width{max-width:min(600px,100%);box-sizing:border-box}
.content-image.full-width{box-sizing:border-box}
.method-grid>*{min-width:0}
.video-compare-container,.vis-comparison-container,pre{max-width:100%;box-sizing:border-box}
@media(max-width:650px){.content-block{padding:1.3rem}.teaser-grid{min-width:0}.teaser-grid>*{min-width:0}}
''',
'sandbox': '''
/* Native horizontal scrolling retains every table column without widening the page. */
.mirror-table-scroll{max-width:100%;min-width:0;overflow-x:auto;-webkit-overflow-scrolling:touch}
.rdf-frame{box-sizing:border-box;max-width:100%}
@media(max-width:768px){
  .container,.columns,.column,.rdf-panel,.rdf-panel-body{min-width:0}
  .cover-content,.cover-title,.cover-subtitle{max-width:100%;box-sizing:border-box}
  .button{max-width:100%}
  pre{max-width:100%;box-sizing:border-box}
}
'''
}
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
    if link.get_text(strip=True).lower() in ['arxiv','paper']:
     link['href']='https://arxiv.org/abs/2512.00771'
  path.write_text(str(soup))
 provenance=ROOT/'projects/media-provenance.json'
 if provenance.is_file():
  data=json.loads(provenance.read_text());data['copy_repairs']=['Kept original layouts; made EAG3R fixed-width figures responsive.','Wrapped SANDBOX result tables in labelled horizontal-scroll regions.','Disabled the unused Nerfies interpolation preloader when its target element is absent; this prevents 240 requests to files that do not exist on the original source site.']
  data['notes']=[s for s in data.get('notes',[]) if 'Some resources also failed' not in s]
  data['notes'].append('The source audit records historical unused-template failures; the copied site guards the unused interpolation preloader. The promotional cover retrieved from the EAG3R code repository is not presented as a measured reconstruction output.')
  provenance.write_text(json.dumps(data,indent=2))
if __name__=='__main__':main()
