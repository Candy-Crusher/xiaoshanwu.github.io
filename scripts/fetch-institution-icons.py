#!/usr/bin/env python3
"""Cache institution website icons locally; existing assets are never replaced."""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/institutions'
SCHOOLS = {'zju': 'www.zju.edu.cn', 'uiuc': 'illinois.edu',
           'hku': 'www.hku.hk', 'harvard': 'www.harvard.edu'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT/'sources.json'
    sources = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for key, domain in SCHOOLS.items():
        target = OUT/(key + '.png')
        if target.is_file():
            with Image.open(target) as image:
                image.verify()
            continue
        urls = [f'https://www.google.com/s2/favicons?domain={domain}&sz=128',
                f'https://{domain}/favicon.ico']
        failures = []
        for url in urls:
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as response:
                    raw = response.read(2_000_000)
                with Image.open(BytesIO(raw)) as image:
                    image.load()
                    if min(image.size) < 16:
                        raise ValueError('Icon is too small')
                    image = image.convert('RGBA')
                    image.thumbnail((128, 128), Image.Resampling.LANCZOS)
                    image.save(target, 'PNG', optimize=True)
                sources[key] = {'institution_domain': domain, 'source': url,
                                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                                'usage': 'Website icon identifying education/research affiliation; not an endorsement.'}
                break
            except Exception as exc:
                failures.append(str(exc))
        else:
            raise RuntimeError(f'Unable to retrieve {key} institution icon: {failures}')
    manifest_path.write_text(json.dumps(sources, indent=2) + '\n')


if __name__ == '__main__':
    main()
