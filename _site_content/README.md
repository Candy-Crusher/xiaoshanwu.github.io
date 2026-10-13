# Personal website

The personal pages use a quiet academic layout: white background, compact typography, modest portrait, text links and research rows. The cinematic assets remain available, but are no longer loaded on Home. The existing film-inspiration section stays on About.

## Page roles and editable content

- `index.html`: generated introduction, three selected projects and existing news. The selected projects remain S4NDBOX, GaMe and EAG3R; authors, statuses, summaries, figures and resources are copied from the current Research page.
- `about.html`: biography, research perspective, future interests and personal inspiration.
- `resume.html`: CV PDF, education, experience, a separate honors/awards section, and skills.
- `research.html`: all seven project summaries and all 15 publication records.
- `publications.html`: legacy URL compatibility and no-JavaScript publication fallback.

Edit About, Resume and Research content in their HTML files. `scripts/build-personal-site.py` preserves their main-text content exactly and only refreshes the shared shell. Home uses the approved `direction` and `foundation` paragraphs in `personal-site.json`, the existing Home news, and selected entries from `research.html`. Other fragments in `personal-site.json`, including the old `hero`, are retained as an archive rather than silently restored over newer content.

## Build and checks

```sh
python -m pip install beautifulsoup4 playwright
python -m playwright install chromium
python scripts/build-personal-site.py
python scripts/test-personal-site.py
```

The existing `.github/workflows/build-personal-site.yml` runs these commands, verifies repeatable generation, uploads screenshots and test results, commits validated HTML and requests a Pages rebuild. No workflow-file change is needed for this design update.

Responsive checks cover 320, 390, 768, 1024 and 1440 px, image loading, navigation, keyboard dismissal of figures, the no-JavaScript publication archive and legacy anchors. Screenshots and `report.json` are written to `personal-site-qa/` and included in the existing review artifact.

The CV PDF, main LaTeX, all 13 tailored CVs and every project microsite remain outside this generator's write scope. Existing project routes, paper links and contribution labels are preserved.
