# Personal website: one page, six sections

The main navigation is **Home · News · Research · Experience · Award · About**.
Every homepage item is a native same-document fragment link. The cursive
wordmark reads **Xiaoshan's Homepage** and returns to the top.

## Layout and factual sources

The homepage contains the approved Harvard-first biography, News, the existing
question-first Research overview and all 15 publications, Experience, Awards,
and the complete original About essay. Technical skills remain at the end of
About; the introduction and Experience heading retain their CV links.

**Experience is newest first: Harvard → HKU → ZJU & UIUC.** Keep the dual-degree
institutions together as one node. All institution names, roles, dates,
advisors, honors and GPAs remain sourced from CV02.

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex` is the factual
CV source; `cv.tex` must match it. Layout changes never modify TeX, PDF files,
research media, experiment data, or individual project pages.

`site-presentation.json` supplies the approved biography, research directions,
short descriptions, crops and resources. `personal-site.json` retains approved
news. `resume-cv02.json` is the generated factual cache. Navigation and layout
are defined by `scripts/build-personal-site.py`, which updates the presentation
cache. The unchanged factual parser and research renderers live in
`scripts/personal_site_core.py`.

## Timeline logos and styling

`assets/css/single-page.css` controls the cursive wordmark, responsive six-link
header and timeline. The optional Allura web font has native cursive fallbacks;
no font files are bundled.

ZJU and UIUC now use **true SVG vector paths**, not favicons or enlarged PNGs:

- `assets/institutions/zju.svg`: the original standalone emblem paths extracted
  from the official ZJU identity archive (`xiaobiao.ai`), with the university's
  official RGB color #003f88 and a transparent background.
- `assets/institutions/uiuc.svg`: the official Illinois Block I SVG, unchanged.

`scripts/fetch-institution-icons.py` creates missing assets from the official
sources. Input and output SHA-256 checks require review if the upstream identity
files change. Subsequent builds use versioned local assets. `sources.json`
records URLs, hashes, formats and processing. The Harvard/HKU PNGs remain
unchanged; old ZJU/UIUC PNG URLs remain available but are not used by the timeline.
The paired emblems are slightly larger and stack vertically on narrow screens.

## Navigation and compatibility

`assets/js/site-pages.js` enhances active-section underlining and measures the
sticky header without replacing native scrolling or browser history. Original
robot-video controls and figure enlargement remain unchanged.

Legacy `research.html`, `publications.html`, `resume.html` and `about.html` URLs
redirect to homepage anchors, preserving fragments and queries. Complete
no-JavaScript fallback content remains. Homepage aliases `#resume`, `#education`,
`#background`, `#skills`, `#awards` and `#inspiration` remain valid. Paper, project,
advisor, profile and CV resource links keep their original destinations.

## Build and validation

Run `python scripts/fetch-institution-icons.py`,
`python scripts/build-personal-site.py`, `python scripts/test-personal-site.py`,
and `python scripts/test-sandbox-media.py`.

The existing personal-site workflow caches assets, builds and validates pages,
checks repeatability, commits generated HTML/assets, requests GitHub Pages
publication, and checks the public HTML. Its existing name is retained for
compatibility with other automation.

Tests cover the exact six navigation labels, same-document clicks, Back/Forward,
manual-scroll active state, keyboard navigation, anchor visibility, no-JavaScript
behavior, legacy routes, all internal resources, Harvard-first order, CV02
metadata preservation, 320–1440 px layouts, original robot playback and all six
interactive 4D cases. Logo checks reject raster images wrapped in SVG, verify
source hashes and render a 3x-density mobile screenshot. Screenshots/reports are
saved in the `single-page-website-review` Actions artifact.
