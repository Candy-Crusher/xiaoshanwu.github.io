# Personal website: facts and presentation

Navigation: **Home → Resume → About**. Home and Resume are positions on the
same document, not separate pages. About remains a short personal essay.

- **Home**: Harvard-first biography and CV02 research interests, followed by
  all 15 papers (8 first/co-first + 7 collaborative), the full Resume, and news.
- **Resume (`index.html#resume`)**: research appointments, degrees, technical
  skills, a standalone Selected Awards section, and CV PDF links. The navigation
  uses native `#resume` / `#top` anchors, including without JavaScript.
- **About**: background, research motivation, future co-evolution interests,
  and the existing film inspiration. Its Resume link leads to the homepage.

## Sources

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex` is the source
of factual CV information. `cv.tex` must match it exactly; the existing CV
workflow builds the public PDF. This layout update changes no TeX, PDF, or
individual research project page.

`site-presentation.json` controls concise research descriptions, existing-image
crops and resources. It does not mirror every CV paragraph. `source_title`
matches each record to CV02; authors, status, order and role labels are parsed
from TeX. `resume-cv02.json` is the generated factual cache. The user-approved
biography, corrected official scholarship links and mentor links are retained.

`personal-site.json` retains news and earlier approved material. The old
cinematic fragment is archival, not rendered. Media are existing research
assets; captions distinguish illustrative material from measured results.

## Compatibility and checks

`research.html` and `publications.html` redirect to the matching homepage
research anchor. `resume.html` redirects to `index.html#resume`, preserving
old fragment links such as `#education`, `#experience`, `#skills`, `#awards`,
and `#background`. All three legacy routes retain their complete content as a
no-JavaScript fallback. Homepage anchors no longer redirect out to Resume.

The modest sticky navigation stays accessible while reading. Header offsets
keep anchor headings visible. There are no decorative or scrolling animations.
CSS and JavaScript have a new cache key; the page-family marker and existing
GitHub workflow stay unchanged.

Run `python scripts/build-personal-site.py` and
`python scripts/test-personal-site.py` to build and validate. Tests cover CV02
metadata preservation, unique headings and anchors, 320–1440 px layouts,
no-JavaScript content, native Resume navigation, browser Back, old routes,
keyboard navigation and image enlargement. `--inline-preview` provides only
static/offline visual validation; full navigation tests run in CI.

## Research narrative

The homepage keeps the Harvard-first biography and uses a shorter, web-specific
paraphrase of CV02 for the second introduction paragraph. Research then presents
one central question and three connected lines of work, each with links to its
actual publications. Publications remain a single, fully visible record below.
This borrows the problem-first organization of https://yilundu.github.io/, not
its prose, research claims or taxonomy. CV02 and its PDF are not rewritten.

Edit `home.research_statement` and `research.question/directions` in
`site-presentation.json`. Each direction records its supporting source and
references publication anchors instead of duplicating entries. The short CV
link label is `CV`; the destination remains `Xiaoshan_Wu_CV.pdf`.

`assets/css/research-overview.css` styles only the new overview and its adjacent
publication heading. Existing personal-page navigation and resume layout stay
unchanged. Tests check the overview, real example links, metadata/order
preservation, plain CV labels and the future-only co-evolution framing.
