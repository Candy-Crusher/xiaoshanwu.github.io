# Personal website: facts and presentation

Navigation: **Home → Research → Resume → About**.

- **Home**: a short identity and research introduction; S4NDBOX, GaMe, VideoSSM, EAG3R; existing news. Small author lists always retain X. Wu.
- **Research**: one open record of all 15 papers (8 first/co-first + 7 collaborative). Each paper appears once. No hidden publication accordion or duplicate project catalog.
- **Resume**: the CV02 PDF; research appointments; degrees; technical skills; a standalone Selected Awards section. Visiting Scholar is an appointment, not a degree.
- **About**: brief background, research motivation, the future co-evolution agenda, and the existing film inspiration.

## Sources

`cv/2027-internships/02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex` is the source of factual CV information. `cv.tex` must match it exactly; the existing CV workflow builds the public PDF. This update does not change either source or any tailored CV.

`site-presentation.json` is the editorial layer: homepage selection, concise descriptions, display titles, crops of existing figures, captions and resources. It deliberately does not mirror every CV paragraph. `source_title` matches each record to CV02; author lists, publication status, ordering and role labels are obtained from TeX, never retyped here. The full CV-derived cache is `resume-cv02.json`.

`personal-site.json` retains the existing news and earlier approved material. Its old cinematic fragment is archival, not rendered.

Media are existing research assets, not newly generated illustrations. GaMe's cropped scene is explicitly an illustrative example; VideoSSM's crop is the original Ours row at frames 0, 480 and 960. All image files remain unchanged. The former local robot-demo URL points to an absent file; the personal-page link now opens the original project site's demo instead.

## Build and validate

```sh
python -m pip install beautifulsoup4 playwright
python -m playwright install chromium
python scripts/build-personal-site.py
python scripts/test-personal-site.py
```

Tests check factual equivalence to CV02, one record per paper, all 15 visible without JavaScript, author-name retention, independent Awards, internal resources, 320/390/768/1024/1440 px layouts, image loading, keyboard figure closure and legacy anchors. Build repeatability and protected-file hashes are checked. Screenshots and report.json are saved under `personal-site-qa/`.

For an offline renderer with no navigation access, use `--inline-preview` and optionally `BROWSER_EXECUTABLE=/path/to/chromium`. This reports navigation testing as not performed; CI executes the full HTTP tests.

`publications.html` redirects to Research but retains a full no-JavaScript fallback. Existing `#pub-*`, `#selected-*`, `#projects`, `#publications`, Resume and inspiration anchors are preserved. Individual project microsites and their media are not rewritten.
