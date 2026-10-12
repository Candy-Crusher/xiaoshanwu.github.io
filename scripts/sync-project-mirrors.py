#!/usr/bin/env python3
"""Copy public project sites; preserve originals and record all media provenance.
Run on the existing website checkout. This does not expose private repositories.
"""
from __future__ import annotations
import io,json,re,time,shutil,hashlib,posixpath,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlsplit,unquote,quote
from bs4 import BeautifulSoup
from PIL import Image
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'projects'
SITE='https://candy-crusher.github.io/xiaoshanwu.github.io/'
SOURCE='https://demo1-indol-gamma.vercel.app/'
CASES=['pose-1','pose-2','lighting-1','lighting-2','clutter-1','clutter-2']
REPORT={'mirrors':{},'high_resolution':[],'notes':[]}
MAX_FILE=95_000_000
TEXT={'.html','.css','.js','.json','.svg'}
MEDIA={'.html','.css','.js','.json','.svg','.png','.jpg','.jpeg','.webp','.gif','.mp4','.webm','.bin','.gz','.br','.ply','.npz','.npy','.wasm','.pdf'}

def get(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'ResearchProjectArchive/1.0'}),timeout=65) as response:
                if int(response.headers.get('Content-Length','0'))>MAX_FILE:raise ValueError('File exceeds 95 MB repository limit')
                raw=response.read(MAX_FILE+1)
                if len(raw)>MAX_FILE:raise ValueError('File exceeds 95 MB repository limit')
                return raw
        except Exception:
            if attempt==2:raise
            time.sleep(attempt+1)

def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

def record_image(path):
    im=Image.open(path)
    return {'path':str(path.relative_to(ROOT)),'pixels':list(im.size),'bytes':path.stat().st_size}

def hd_pdf(source,slug,name,width=3600):
    folder=OUT/slug/'assets';folder.mkdir(parents=True,exist_ok=True)
    target=folder/(name+'.pdf')
    if source.resolve()!=target.resolve():shutil.copy2(source,target)
    with fitz.open(source) as doc:
        page=doc[0];pix=page.get_pixmap(matrix=fitz.Matrix(width/page.rect.width,width/page.rect.width),alpha=False)
        full=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        images=[]
        for w in (min(1440,width),width):
            im=full if w==width else full.resize((w,round(full.height*w/full.width)),Image.Resampling.LANCZOS)
            path=folder/(name+('-hd' if w==width else '')+'.webp');im.save(path,'WEBP',quality=96,method=6);images.append(record_image(path))
        REPORT['high_resolution'].append({'source':str(source.relative_to(ROOT)),'output':images,'vector_paths':len(page.get_drawings()),'pdf':str(target.relative_to(ROOT))})
    return name+'.webp',name+'-hd.webp',name+'.pdf'

def mirror_eag3r():
    repo='Candy-Crusher/EAG3R_Proj';ref='b5df173e9125f97c4d4cacad2aac524f1f5b466f'
    tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1'))['tree']
    folder=OUT/'eag3r';count=0
    for item in tree:
        if item['type']!='blob':continue
        path=item['path']
        if not (Path(path).suffix.lower() in MEDIA or Path(path).name.startswith(('LICENSE','README'))):continue
        put(folder/path,get(f'https://raw.githubusercontent.com/{repo}/{ref}/'+quote(path)));count+=1
    REPORT['mirrors']['eag3r']={'source':f'https://github.com/{repo}','commit':ref,'files':count,'mode':'Original HTML, stylesheet and research assets copied; original site unchanged.'}
    # This original PDF matches the concept/optimization overview in the old site.
    hd_pdf(ROOT/'images/1_eag3r.pdf','eag3r','concept',3600)
    # Keep the code repository's original teaser for review; use only after inspecting it.
    source=folder/'assets/code-repository-teaser.png'
    put(source,get('https://raw.githubusercontent.com/Candy-Crusher/EAG3R/main/assets/teaser.png'))
    REPORT['high_resolution'].append({'source':'Candy-Crusher/EAG3R/assets/teaser.png','original':record_image(source),'status':'Retrieved original; not substituted for a different figure.'})

def mirror_sandbox():
    folder=OUT/'sandbox';folder.mkdir(parents=True,exist_ok=True)
    urls={SOURCE,urljoin(SOURCE,'rdf-viewer.html')}
    # Observe actual public viewer requests, including runtime-generated binary paths.
    observed=set();browser_errors=[]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        context=browser.new_context(viewport={'width':1280,'height':900})
        context.on('request',lambda request:observed.add(request.url) if urlsplit(request.url).netloc==urlsplit(SOURCE).netloc else None)
        page=context.new_page()
        try:
            page.goto(SOURCE,wait_until='domcontentloaded',timeout=60000)
            page.evaluate('async()=>{for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}}')
            page.wait_for_timeout(3500)
            for case in CASES:
                button=page.locator('[data-rdf-case="'+case+'"]')
                if button.count():button.click();page.wait_for_timeout(1800)
        except Exception as exc:browser_errors.append(str(exc))
        for case in CASES:
            try:
                page.goto(urljoin(SOURCE,'rdf-viewer.html?case='+case+'&view=compare'),wait_until='networkidle',timeout=60000)
                page.wait_for_timeout(1800)
            except Exception as exc:browser_errors.append(case+': '+str(exc))
        browser.close()
    urls.update(observed)
    for case in CASES:
        for filename in ['tracking.mp4','tracking-poster.jpg','tracking.json']:
            urls.add(urljoin(SOURCE,'static/rdf/'+case+'/'+filename))
    seen=set();failed=[];saved=[]
    def normalize(url):
        parts=urlsplit(url)
        if parts.netloc!=urlsplit(SOURCE).netloc:return None
        path=unquote(parts.path).lstrip('/') or 'index.html'
        if '..' in Path(path).parts:return None
        if Path(path).suffix.lower() not in MEDIA:return None
        return urljoin(SOURCE,quote(path,safe='/'))
    def references(text,base):
        found=[]
        if Path(urlsplit(base).path).suffix in ('','.html'):
            soup=BeautifulSoup(text,'html.parser')
            for attr in ('src','href','poster','data-src'):
                for tag in soup.select('['+attr+']'):found.append(urljoin(base,tag[attr]))
            for tag in soup.select('[srcset]'):
                for spec in tag['srcset'].split(','):found.append(urljoin(base,spec.strip().split(' ')[0]))
        for value in re.findall(r'''["'`]([^"'`\n<>]{1,300}\.(?:html|css|js|json|svg|png|jpe?g|webp|gif|mp4|webm|bin|gz|ply|wasm))(?:\?[^"'`\s]*)?["'`]''',text):
            if '${' in value or '+' in value:continue
            found.append(urljoin(base,value))
        for value in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)',text):found.append(urljoin(base,value))
        return found
    while urls:
        batch=sorted(set(filter(None,(normalize(u) for u in urls)))-seen);urls=set()
        if not batch:break
        if len(seen)+len(batch)>1800:raise RuntimeError('Unexpectedly large source site; review the asset list')
        def download(url):
            try:return url,get(url),None
            except Exception as exc:return url,None,str(exc)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for url,raw,error in pool.map(download,batch):
                seen.add(url)
                if error:failed.append({'url':url,'error':error});continue
                path=unquote(urlsplit(url).path).lstrip('/');dest=folder/path;put(dest,raw)
                saved.append({'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                if Path(path).suffix.lower() in TEXT:
                    try:urls.update(references(raw.decode('utf-8'),url))
                    except UnicodeDecodeError:pass
    # Runtime requests are authoritative. Missing guessed string references are logged,
    # whereas failed actual resource requests fail the mirror rather than faking a copy.
    actual={normalize(u) for u in observed};critical=[f for f in failed if f['url'] in actual]
    REPORT['mirrors']['sandbox']={'source':SOURCE,'mode':'Public deployed site mirror, not original Git repository','files':saved,'unresolved':failed,'browser_inspection':browser_errors,'failed_actual_resources':critical}
    if not (folder/'index.html').is_file() or not (folder/'rdf-viewer.html').is_file():raise RuntimeError('Original SANDBOX site unavailable')
    if critical:REPORT['notes'].append('Some resources also failed on the original site; inspect failed_actual_resources before claiming a full offline mirror.')
    # Root-relative resource paths must point inside the GitHub Pages project subpath.
    prefix='/xiaoshanwu.github.io/projects/sandbox/'
    for path in folder.rglob('*'):
        if path.suffix not in TEXT:continue
        text=path.read_text()
        text=text.replace(SOURCE,SITE+'projects/sandbox/')
        text=re.sub(r'''(["'`])/(static/|rdf-viewer\.html)''',lambda m:m.group(1)+prefix+m.group(2),text)
        path.write_text(text)

def main():
    try:
        mirror_eag3r();mirror_sandbox()
        hd_pdf(ROOT/'images/videossm.pdf','videossm','overview',3600)
        hd_pdf(ROOT/'images/SegmentAnytime.pdf','lifr-seg','teaser',3200)
        source=OUT/'lifr-v2/assets/repository-teaser.pdf'
        put(source,get('https://raw.githubusercontent.com/TaoWan0610/LiFR-v2/main/assets/teaser.pdf'))
        hd_pdf(source,'lifr-v2','teaser',3600)
    finally:
        OUT.mkdir(exist_ok=True)
        (OUT/'media-provenance.json').write_text(json.dumps(REPORT,indent=2))
        print(json.dumps(REPORT,indent=2))
if __name__=='__main__':main()
