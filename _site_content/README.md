# Personal website: a combined introduction and research record

Navigation: **Home → Resume → About**. Home contains the Harvard-first introduction and the complete research record; there is no second featured-project catalog.

- **Home**: exactly two introductory paragraphs, followed by all 15 papers (8 first/co-first-author + 7 collaborative) and the existing news. Every paper appears once; X. Wu remains visible in every author list.
- **Resume**: CV02 PDF, research appointments, degrees, technical skills and an independent Selected Awards section.
- **About**: research motivation, future interests and the existing film inspiration.
- **research.html / publications.html**: compatibility routes. JavaScript redirects to the relevant homepage anchor; without JavaScript the complete research record remains readable. Do not remove these files while project sites and CVs still link to them.

## Content sources

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex` remains the factual CV source. `cv.tex` must match it exactly; its existing workflow builds the public PDF. This update changes neither file nor any other tailored CV.

`site-presentation.json` separates presentation from CV facts. `home.identity` is the user's approved Harvard-first biography, including fourth-year status and HKPFS/HKUPS. `home.interest_indices` selects sentences 1, 2 and 4 from CV02 as the second introductory paragraph. Do not silently promote the future co-evolution agenda into completed work.

Paper author order, status, contribution labels and order come from TeX. Project summaries, resource links and existing image crops remain unchanged. `_site_content/resume-cv02.json` is the generated CV cache. `personal-site.json` retains the news and archived material.

## Build and validation

Run `python scripts/build-personal-site.py` and `python scripts/test-personal-site.py` with BeautifulSoup and Playwright/Chromium installed. Tests cover 320, 390, 768, 1024 and 1440 px, all 15 paper anchors, legacy redirects, keyboard access, figure viewing, no-JavaScript research access, and exact CV metadata preservation. `--inline-preview` is a visual-only fallback for restricted runtimes; navigation must still be tested by CI.

The existing workflow reads expected navigation and the design marker from the presentation configuration. No new workflow or permission is introduced. CV PDFs, all 13 tailored TeX files, project microsites and image assets are outside the generator's write scope.
