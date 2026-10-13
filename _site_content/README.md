# Personal website — CV 02 content, quiet academic design

## Canonical resume source

The user-selected source is:

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex`

The public `cv.tex` is an exact copy of that source. The existing `Build CV PDF` workflow compiles it to both stable public names, `Xiaoshan_Wu_CV.pdf` and `ia8eshfzfsvn.pdf`. Every existing CV download link therefore serves the selected Robotics version. The 13 application sources themselves are not rewritten by the website generator.

`python scripts/build-personal-site.py` reads CV 02 and synchronizes:

- Resume: education/research entries, dates, advisers, GPAs, research interests, technical skills and a separate Selected Awards section.
- Home and About: the matching biography and research direction, with current work and future co-evolution clearly separated.
- Research and the legacy publication fallback: publication order, author lists, venues, contribution labels and project notes available in the source.
- `_site_content/resume-cv02.json`: parsed content and the exact source Git blob SHA for auditability.
- `_site_content/personal-site.json`: matching editable/archive fragments so older website content does not return on rebuild.

Figures, project URLs, paper/code/demo links, detailed summaries not supplied by the CV, news and the personal inspiration remain in the existing pages. No new publication status, training scale, award criterion or employment date is invented. In particular, the current source's Tools / Methods wording is copied as written rather than replaced with a different proposed Skills line.

## Updating the selected resume

After editing CV 02, copy it to `cv.tex`, commit the copy, and let the existing CV workflow finish before publishing the website update. The website generator refuses to publish when the source and public TeX differ.

```sh
cp cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex cv.tex
python -m pip install beautifulsoup4 playwright
python -m playwright install chromium
python scripts/build-personal-site.py
python scripts/test-personal-site.py
```

The parser is scoped to the current standalone CV format and fails on unsupported LaTeX commands or changed publication/entry counts instead of silently dropping text. Rebuilding twice must yield identical output.

The existing personal-site workflow performs the responsive and functional checks, uploads screenshots and `report.json`, commits the generated pages, and requests the Pages rebuild. No `.github/workflows/` changes are needed for this update.

## Design and preservation

The white background, typography, modest portrait, four-page navigation and research-row layout remain unchanged. The standalone Selected Awards section is retained in both PDF and HTML. The cinematic image remains only in the existing personal-inspiration section. CV 02 and the other 12 application TeX files, all seven project microsites, CSS and JavaScript files are outside this content synchronization's write scope.
