# Personal website: one page, six sections

The main navigation is **Home · News · Research · Experience · Award · About**.
Every item on `index.html` is a native fragment link in the same document.
The cursive wordmark reads **Xiaoshan's Homepage** and returns to the top.

## Layout and sources

The homepage contains the approved Harvard-first biography, News, the existing
question-first Research overview and all 15 publications, a three-node
chronological Experience timeline, Awards, and the complete original About essay.
The timeline is **ZJU & UIUC → HKU → Harvard**. Institution names, roles, dates,
advisors, honors and GPAs come from CV02 without rewriting the underlying facts.
Technical skills are retained at the end of About; CV viewing/download remains
available beside Experience and in the introduction.

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex` is the source
of factual CV information. `cv.tex` must match it exactly. No TeX, PDF, paper,
research video, experiment data or individual project page is modified by this
layout update.

`site-presentation.json` supplies the approved biography, research directions,
short summaries, crops and resources. `personal-site.json` retains approved
news. `resume-cv02.json` is the generated factual cache. Navigation is structural:
its six labels/anchors are defined in `scripts/build-personal-site.py`, which
also updates the human-readable navigation cache in `site-presentation.json`.

The previous factual parser, research renderer and legacy-page renderers are
preserved verbatim in `scripts/personal_site_core.py`. The small
`build-personal-site.py` entry point assembles semantic HTML sections around
those unchanged research renderers. No client-side content hiding or page switcher
is used. All sections and publications are readable without JavaScript.

## Presentation

`assets/css/single-page.css` adds the cursive wordmark, six-link responsive
header, a thin vertical timeline, institution-icon tiles and section spacing.
The established white academic layout, portrait and research content remain.
The optional Allura web font has native cursive fallbacks. No font files are
bundled. Institution website icons are cached under `assets/institutions/`;
`sources.json` records their retrieval URLs and hashes. They identify
institutions, not institutional endorsement. The first build retrieves missing
icons; subsequent builds use the existing versioned local assets.

`assets/js/site-pages.js` progressively enhances active-section underlining,
measures the sticky header, and preserves native scrolling and browser history.
The original muted robot-video controls and figure enlargement behavior remain.
Scrolling never rewrites the URL or adds browser-history entries.

## Compatibility

Old `research.html`, `publications.html`, `resume.html` and `about.html` routes
redirect to the appropriate homepage anchor, preserving fragments and queries.
They retain their full no-JavaScript content as a fallback. Homepage aliases
`#resume`, `#education`, `#background`, `#skills`, `#awards` and `#inspiration`
remain valid. Top-level navigation never leads away from the homepage; paper,
project, advisor, profile and CV resource links keep their original destinations.

## Build and validation

Run `python scripts/build-personal-site.py`, then
`python scripts/test-personal-site.py` and `python scripts/test-sandbox-media.py`.
The media checker can run directly: it starts a temporary local HTTP server,
checks every original point-cloud frame, and opens all six interactive cases.
Its legacy-About test follows the redirect before exercising Research navigation.
The existing personal-site workflow installs dependencies, caches missing icons,
builds and checks the pages, verifies deterministic regeneration, and only then
commits generated HTML and requests GitHub Pages publication. The workflow name
is retained for compatibility with existing automation.

Checks cover the exact six navigation labels, same-document clicks with preserved
JS state, browser Back/Forward, manual-scroll active state, keyboard navigation,
visible anchor headings, no-JavaScript behavior, old routes, all internal links,
three chronological milestones, CV02 paper metadata and education preservation,
320/390/600/768/1024/1440 px layouts, portrait and figure decoding, original robot
video playback, and all six interactive 4D cases. Screenshots and reports are
saved in the `single-page-website-review` Actions artifact. The final workflow
step checks the public HTML, not only the repository version.
