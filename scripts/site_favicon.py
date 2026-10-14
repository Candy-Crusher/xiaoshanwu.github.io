"""Local mountain emoji favicon; only head metadata, never page bodies."""
from pathlib import Path
from html.parser import HTMLParser
import os,re
ROOT=Path(__file__).resolve().parents[1]
START='<!-- favicon:mountain:start -->'
END='<!-- favicon:mountain:end -->'
VERSION='mountain-20261015'

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__();self.icon=False
    def handle_starttag(self,tag,attrs):
        if tag=='link':
            self.icon=bool(set(dict(attrs).get('rel','').lower().split()) & {'icon','apple-touch-icon','apple-touch-icon-precomposed','mask-icon'})

def apply_favicon(document,page_path):
    head=re.search(r'(<head\b[^>]*>)(.*?)(</head\s*>)',document,re.I|re.S)
    if not head:raise ValueError('No document head in '+page_path)
    inside=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',head[2],flags=re.S)
    def strip_icon(match):
        parser=LinkParser();parser.feed(match[0]);return '' if parser.icon else match[0]
    inside=re.sub(r'<link\b[^>]*>',strip_icon,inside,flags=re.I)
    prefix=os.path.relpath(ROOT/'assets/icons',(ROOT/page_path).parent).replace(os.sep,'/')
    links=(f'<link rel="icon" type="image/x-icon" sizes="16x16 32x32 48x48 64x64" href="{prefix}/mountain.ico?v={VERSION}">'
           f'<link rel="icon" type="image/png" sizes="32x32" href="{prefix}/mountain-32.png?v={VERSION}">'
           f'<link rel="icon" type="image/svg+xml" sizes="any" href="{prefix}/mountain.svg?v={VERSION}">'
           f'<link rel="apple-touch-icon" sizes="180x180" href="{prefix}/mountain-180.png?v={VERSION}">')
    return document[:head.start()]+head[1]+inside+START+links+END+head[3]+document[head.end():]

def build_assets():
    import cairosvg
    from PIL import Image
    icons=ROOT/'assets/icons';source=(icons/'mountain.svg').read_bytes()
    for size in (32,64,180):
        path=icons/f'mountain-{size}.png'
        cairosvg.svg2png(bytestring=source,output_width=size,output_height=size,write_to=str(path))
        with Image.open(path) as image:assert image.size==(size,size) and image.getbbox()
    with Image.open(icons/'mountain-64.png') as image:
        image.save(icons/'mountain.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64)])
    with Image.open(icons/'mountain.ico') as image:assert len(image.ico.sizes())==4

if __name__=='__main__':build_assets()
