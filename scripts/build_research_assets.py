"""Render original research figures for the homepage; never redraw research results."""
from pathlib import Path
import json
import fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images/research"
OUT.mkdir(parents=True, exist_ok=True)


def webp(image: Image.Image, name: str, width: int, quality: int = 88) -> None:
    image = image.convert("RGB")
    if image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
    image.save(OUT / name, format="WEBP", quality=quality, method=6)


def pdf_image(path: str, width: int, crop=None) -> Image.Image:
    with fitz.open(ROOT / path) as doc:
        page = doc[0]
        rect = fitz.Rect(crop) if crop else page.rect
        pix = page.get_pixmap(matrix=fitz.Matrix(width / rect.width, width / rect.width), clip=rect, alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


# All crops retain the original figure content. Larger versions are available on click.
wam = pdf_image("images/research/source/s4ndbox-architecture.pdf", 1680)
webp(wam, "s4ndbox-architecture-full.webp", 1680, 92)
webp(wam, "s4ndbox-architecture.webp", 720, 92)
video = pdf_image("images/videossm.pdf", 1800)
webp(video, "videossm-full.webp", 1800, 92)
webp(pdf_image("images/videossm.pdf", 680, (320, 0, 603, 286)), "videossm-memory.webp", 680, 92)
lifr = pdf_image("images/SegmentAnytime.pdf", 1440)
webp(lifr, "lifr-seg-full.webp", 1440, 91)
webp(lifr, "lifr-seg-overview.webp", 720, 90)
eag3r = Image.open(ROOT / "images/EAG3R_poster.png")
webp(eag3r.crop((2720, 1194, 3568, 1478)), "eag3r-night-depth.webp", 848, 92)
webp(pdf_image("images/1_eag3r.pdf", 1800), "eag3r-pipeline-full.webp", 1800, 91)
photo = ImageOps.exif_transpose(Image.open(ROOT / "images/photo.jpg"))
webp(photo, "profile.webp", 480, 88)
manifest = {}
for path in sorted(OUT.glob("*.webp")):
    with Image.open(path) as image:
        manifest[path.name] = {"width": image.width, "height": image.height, "bytes": path.stat().st_size}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
