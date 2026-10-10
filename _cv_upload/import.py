"""Import the 13 user-approved standalone CV files without changing their bytes.

This one-time transfer uses a shared text plus literal line replacements only
for transport. Every output .tex is standalone. The SHA-256 checks are from the
original conversation attachments. No template dependency is introduced.
"""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
source = root / '_cv_upload'
base = (source / 'base.tex').read_bytes().decode('utf-8').splitlines(keepends=True)
variants = json.loads((source / 'variants.json').read_text(encoding='utf-8'))
if len(variants) != 13:
    raise ValueError('Expected exactly 13 CV files')
outputs = {}
for variant in variants:
    name = variant['name']
    if not re.fullmatch(r'\d{2}_Xiaoshan_Wu_[A-Za-z0-9_]+\.tex', name):
        raise ValueError(f'Unexpected filename: {name}')
    if name in outputs:
        raise ValueError(f'Duplicate filename: {name}')
    lines = list(base)
    previous_end = 0
    for start, end, replacement in variant['edits']:
        if not (previous_end <= start <= end <= len(base)):
            raise ValueError(f'Invalid replacement coordinates: {name}')
        previous_end = end
    for start, end, replacement in reversed(variant['edits']):
        lines[start:end] = replacement.splitlines(keepends=True)
    content = ''.join(lines).encode('utf-8')
    digest = hashlib.sha256(content).hexdigest()
    if digest != variant['sha256']:
        raise ValueError(f'Content checksum mismatch: {name}: {digest}')
    outputs[name] = content
out = root / 'cv' / '2027-internships'
out.mkdir(parents=True, exist_ok=True)
for name, content in outputs.items():
    path = out / name
    if path.exists() and path.read_bytes() != content:
        raise FileExistsError(f'Refusing to overwrite changed file: {path}')
    path.write_bytes(content)
    print(f'Verified {name}: {hashlib.sha256(content).hexdigest()}')
print('All 13 standalone TeX files match their original attachments byte-for-byte.')
