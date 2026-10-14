#!/usr/bin/env python3
"""Cache institution marks locally, upgrading undersized website icons once."""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/institutions'
SCHOOLS = {'zju': 'www.zju.edu.cn', 'uiuc': 'illinois.edu',
           'hku': 'www.hku.hk', 'harvard': 'www.harvard.edu'}
# Official emblem download linked from https://www.zju.edu.cn/572/main.htm.
ZJU_EMBLEM = 'https://www.zju.edu.cn/_upload/article/images/c3/98/1fb1d281492eb477a098ef7a2901/05966b26-ab45-470d-94c1-99b1e02d12f4.png'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT/'sources.json'
    sources = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for key, domain in SCHOOLS.items():
        target = OUT/(key + '.png')
        if target.is_file():
            with Image.open(target) as image:
                adequate = min(image.size) >= 64
                image.verify()
            if adequate:
                continue
        urls = ([ZJU_EMBLEM] if key == 'zju' else []) + [
                f'https://www.google.com/s2/favicons?domain={domain}&sz=128',
                f'https://{domain}/favicon.ico']
        failures = []
        for url in urls:
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as response:
                    raw = response.read(2_000_000)
                with Image.open(BytesIO(raw)) as image:
                    image.load()
                    if min(image.size) < 64:
                        raise ValueError('Icon is too small for the timeline')
                    if url == ZJU_EMBLEM:
                        rgb = image.convert('RGB')
                        bounds = ImageChops.difference(rgb, Image.new('RGB', rgb.size, 'white')).getbbox()
                        if bounds:
                            image = image.crop(bounds)
                    image = image.convert('RGBA')
                    image.thumbnail((128, 128), Image.Resampling.LANCZOS)
                    image.save(target, 'PNG', optimize=True)
                sources[key] = {'institution_domain': domain, 'source': url,
                                'source_page': 'https://www.zju.edu.cn/572/main.htm' if key == 'zju' else 'https://' + domain,
                                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                                'processing': 'Blank outer margins cropped and resized; mark itself unchanged.' if url == ZJU_EMBLEM else 'Resized website icon.',
                                'usage': 'Institution mark identifying education/research affiliation; not an endorsement.'}
                break
            except Exception as exc:
                failures.append(str(exc))
        else:
            raise RuntimeError(f'Unable to retrieve a clear {key} institution mark: {failures}')
    manifest_path.write_text(json.dumps(sources, indent=2) + '\n')


if __name__ == '__main__':
    main()
