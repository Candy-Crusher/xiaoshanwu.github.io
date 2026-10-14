#!/usr/bin/env python3
"""Cache official vector emblems; retain existing Harvard/HKU raster marks.

The official ZJU .ai file has an empty PDF preview. Its Illustrator-private
streams contain the original vector paths. We export only the standalone blue
emblem, not a screenshot, tracing, or an upscaled favicon. Inputs and output are
pinned so an unexpected upstream design change requires explicit review.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from zipfile import ZipFile
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/institutions'
ZJU_ARCHIVE = 'https://www.zju.edu.cn/_upload/article/files/c3/98/1fb1d281492eb477a098ef7a2901/ee6d4e77-ffef-4e32-b76b-be8658698d98.zip'
ZJU_ARCHIVE_SHA256 = '04f8d224d03f4a16e2cdc889eb57cbf8cf23829fcc6ae4850468273944e87607'
VECTOR_SOURCES = {
    'zju': {'institution_domain': 'www.zju.edu.cn', 'source': ZJU_ARCHIVE,
            'source_page': 'https://www.zju.edu.cn/572/main.htm',
            'source_archive_sha256': ZJU_ARCHIVE_SHA256,
            'sha256': 'fa828fa2f07c54c08e061badbb2335c6e93768a1e2775b2ed4461d089cda7e07',
            'processing': 'Original 37 vector paths of the standalone emblem from xiaobiao.ai; official RGB #003f88; transparent background.'},
    'uiuc': {'institution_domain': 'illinois.edu',
             'source': 'https://cdn.brand.illinois.edu/logos/block-i.svg',
             'source_page': 'https://web.brand.illinois.edu/logos/',
             'sha256': '52d845d2bd8875782c9d095a74085f3c98e03802b2aa7522e95342be239b9995',
             'processing': 'Official Block I SVG, unchanged.'},
}


def fetch_bytes(url, limit=8_000_000):
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Unexpectedly large institution resource')
    return raw


def export_zju_svg(archive):
    if hashlib.sha256(archive).hexdigest() != ZJU_ARCHIVE_SHA256:
        raise ValueError('ZJU identity archive changed; review the original before exporting')
    with ZipFile(BytesIO(archive)) as source:
        ai = source.read('xiaobiao.ai')
    refs = sorted((int(n), int(ref)) for n, ref in
                  re.findall(rb'/AIPrivateData(\d+) (\d+) 0 R', ai))
    if len(refs) != 78:
        raise ValueError('Unexpected Illustrator private-stream layout')
    streams = []
    for _, ref in refs:
        match = re.search(rb'(?:\r\n|\r|\n)' + str(ref).encode() +
                          rb' 0 obj\s*<<(.*?)>>\s*stream(?:\r\n|\r|\n)', ai, re.S)
        if match is None or b'/Filter' in match[1]:
            raise ValueError('Unexpected Illustrator stream encoding')
        length = int(re.search(rb'/Length\s+(\d+)', match[1])[1])
        streams.append(ai[match.end():match.end()+length])
    private = b''.join(streams)
    program = zlib.decompress(private.split(b'%AI12_CompressedData', 1)[1]).decode('latin1')
    lines = program.splitlines()
    lines = lines[lines.index('%%EndSetup'):]
    paths, current, points = [], [], []
    compound, fill = 0, (0, 0, 0, 1)

    def finish(visible=True):
        nonlocal current, points
        if visible and current and points and fill == (1, .7, 0, .25):
            xs, ys = zip(*points)
            # The standalone, unannotated blue emblem on the second artboard.
            if min(xs) > -3800 and max(xs) < -3500 and min(ys) > 4700 and max(ys) < 5010:
                paths.append(' '.join(current))
        current, points = [], []

    for line in lines:
        if not line.strip() or line.startswith('%'):
            continue
        if line == '*u':
            compound += 1
            continue
        if line == '*U':
            compound -= 1
            if compound == 0:
                finish()
            continue
        values = line.split()
        command = values[-1]
        try:
            numbers = [float(n) for n in values[:-1]]
        except ValueError:
            continue
        if command == 'k' and len(numbers) == 4:
            fill = tuple(numbers)
        elif command in ('m', 'l', 'L', 'c', 'C') and len(numbers) in (2, 6):
            current.append(command.upper() + ' ' + ' '.join(values[:-1]))
            points.extend(zip(numbers[::2], numbers[1::2]))
        elif command in ('v', 'V') and len(numbers) == 4 and points:
            current.append('C ' + ' '.join(map(str, [*points[-1], *numbers])))
            points.extend(zip(numbers[::2], numbers[1::2]))
        elif command in ('y', 'Y') and len(numbers) == 4:
            current.append('C ' + ' '.join(map(str, [*numbers, *numbers[-2:]])))
            points.extend(zip(numbers[::2], numbers[1::2]))
        elif command == 'h':
            current.append('Z')
        elif command in ('f', 'F'):
            if command == 'f':
                current.append('Z')
            if not compound:
                finish()
        elif command in ('n', 'N', '*'):
            current, points = [], []
        elif command in ('S', 's', 'B', 'b'):
            if command in ('s', 'b'):
                current.append('Z')
            if not compound:
                finish(command not in ('S', 's'))
    if len(paths) != 37 or compound != 0:
        raise ValueError('Unexpected geometry in the selected university emblem')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 242.5747 242.5782" role="img">'
            '<title>Zhejiang University emblem</title><g fill="#003f88" fill-rule="nonzero" '
            'transform="translate(3777.292 4989.8765) scale(1,-1)">' +
            ''.join('<path d="' + path + '"/>' for path in paths) + '</g></svg>\n').encode()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT/'sources.json'
    sources = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name, metadata in VECTOR_SOURCES.items():
        target = OUT/(name + '.svg')
        if target.is_file():
            raw = target.read_bytes()
        else:
            raw = fetch_bytes(metadata['source'])
            if name == 'zju':
                raw = export_zju_svg(raw)
        if hashlib.sha256(raw).hexdigest() != metadata['sha256']:
            raise ValueError(name + ' vector asset changed; visual review is required')
        svg = ET.fromstring(raw)
        if not svg.get('viewBox') or svg.findall('.//{http://www.w3.org/2000/svg}image'):
            raise ValueError('Institution emblem must contain true vector geometry')
        target.write_bytes(raw)
        sources[name] = dict(metadata, format='svg', file='assets/institutions/' + name + '.svg',
                             usage='Affiliation identification only; no institutional endorsement.')
    # Existing Harvard and HKU files stay byte-for-byte unchanged.
    for name, domain in {'hku': 'www.hku.hk', 'harvard': 'www.harvard.edu'}.items():
        target = OUT/(name + '.png')
        if target.is_file():
            with Image.open(target) as image:
                image.verify()
            continue
        url = f'https://www.google.com/s2/favicons?domain={domain}&sz=128'
        with Image.open(BytesIO(fetch_bytes(url))) as image:
            image.load()
            if min(image.size) < 64:
                raise ValueError('Institution icon is too small')
            image = image.convert('RGBA')
            image.thumbnail((128, 128), Image.Resampling.LANCZOS)
            image.save(target, 'PNG', optimize=True)
        sources[name] = {'institution_domain': domain, 'source': url,
                         'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    manifest_path.write_text(json.dumps(sources, indent=2) + '\n')


if __name__ == '__main__':
    main()
