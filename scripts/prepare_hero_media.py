"""Prepare a verified high-resolution film still without upscaling or generative editing."""
from pathlib import Path
from io import BytesIO
from urllib.request import Request, urlopen
import hashlib
import json
import os
from PIL import Image, ImageOps

ROOT = Path(os.environ.get('SITE_ROOT', Path(__file__).resolve().parents[1]))
OUT = ROOT / 'images/theme'
SOURCE_URL = 'https://wallup.net/wp-content/uploads/2018/09/25/571291-Officer_K-blue_hair-finger_pointing-eye_contact-Ana_de_Armas-women-Joi-Blade_Runner_2049-hologram-bridge-neon_glow-coats-futuristic-cyberpunk-Blade_Runner.jpg'
SOURCE_PAGE = 'https://wallup.net/officer-k-blue-hair-finger-pointing-eye-contact-ana-de-armas-women-joi-blade-runner-2049-hologram-bridge-neon-glow-coats-futuristic-cyberpunk-blade-runner/'
source_path = os.environ.get('HERO_SOURCE_FILE')
if source_path:
    raw = Path(source_path).read_bytes()
else:
    with urlopen(Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as response:
        raw = response.read()
if hashlib.sha256(raw).hexdigest() != 'f98bc14c4df8eeef63ccbd6e923dcff0525008bad02afccab716e5bf255930e0':
    raise ValueError('Source has changed; review before using a new image.')
im = ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert('RGB')
if im.size != (2864, 1200):
    raise ValueError(f'Unexpected source size: {im.size}; expected 2864 x 1200.')
OUT.mkdir(parents=True, exist_ok=True)
manifest = {
    'source_url': SOURCE_URL,
    'source_page': SOURCE_PAGE,
    'source_dimensions': list(im.size),
    'source_sha256': hashlib.sha256(raw).hexdigest(),
    'processing': 'Downsampling and WebP encoding only. Mobile preview is a crop of the same source. No upscaling, synthetic detail, sharpening, or color filters.',
    'credit': 'Film still from Blade Runner 2049 (2017). All rights remain with the respective rights holders. The source page is not a reuse license.',
    'files': {}
}

def save(image, filename, width):
    if width > image.width:
        raise ValueError('Upscaling is not permitted.')
    if image.width != width:
        image = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
    image.save(OUT / filename, format='WEBP', quality=91, method=6)
    manifest['files'][filename] = {'width': image.width, 'height': image.height, 'bytes': (OUT/filename).stat().st_size}

for width in (1440, 1920, 2864):
    save(im.copy(), f'shared-world-{width}.webp', width)
# Preserve the face, reaching hand, and distant standing figure in a narrow viewport.
crop = (535, 0, 2115, 1200)
mobile = im.crop(crop)
for width in (790, 1580):
    save(mobile.copy(), f'shared-world-mobile-{width}.webp', width)
manifest['mobile_crop_xyxy'] = list(crop)
(OUT / 'shared-world-source.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
