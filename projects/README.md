# Research project pages

Seven project websites in the existing personal-site repository.

Directory: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/

| Work | Website | Coverage |
| --- | --- | --- |
| S4NDBOX | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/sandbox/ | Copy of the original deployed website, including 14 MP4 files and six interactive 4D cases. |
| EAG3R | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/eag3r/ | Original project HTML, CSS and research figures, including comparison sliders; the concept figure uses its original PDF at higher resolution. |
| VideoSSM | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/videossm/ | Paper overview, original figures, selected results and citation. |
| GaMe | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/game/ | Conceptual overview and original method diagram. Full public manuscript and evaluated examples remain pending. |
| LiFR-Seg | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-seg/ | Original teaser, method, paper results and citation. |
| LiFR v2 | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-v2/ | Original repository teaser, architecture, results, citation and repository link. |
| EVSplat | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/evsplat/ | Project identity and research focus. Manuscript and experimental media remain pending. |

## Original sites remain unchanged

The copied S4NDBOX site comes from `https://demo1-indol-gamma.vercel.app/`; EAG3R comes from `Candy-Crusher/EAG3R_Proj`. Their original deployments and source repositories have not been replaced or redirected. The new copies retain the original designs and include directory/home navigation.

S4NDBOX research media, viewer scripts, Three.js modules, case manifests and compressed point-cloud frames are stored under `projects/sandbox/`, not embedded as an iframe pointing at the old deployment. Six cases are available: pose-1, pose-2, lighting-1, lighting-2, clutter-1 and clutter-2. Some presentation dependencies, such as remote fonts and MathJax, still use their original public CDNs.

## Higher-resolution source figures

These images were rendered from original PDF figures, not AI-upscaled or redrawn. Responsive pages use smaller previews and provide larger images and/or the original PDFs.

| Project | Original source | Large render |
| --- | --- | --- |
| VideoSSM | `images/videossm.pdf` | 3600 × 1185 |
| GaMe teaser | Selected manuscript figure `fig_01_teaser.pdf` | 3600 × 1256 |
| GaMe method | Selected manuscript figure `fig02_method.pdf` | 3600 × 1450 |
| LiFR-Seg | `images/SegmentAnytime.pdf` | 3200 × 1919 |
| LiFR v2 | `TaoWan0610/LiFR-v2/assets/teaser.pdf` | 3600 × 1138 |
| EAG3R concept | `images/1_eag3r.pdf`, matching the original concept figure | 3600 × 799 |

The public GaMe page includes only the two selected figure PDFs and their renders; the full private manuscript and author notes were not imported. The teaser remains labelled as conceptual, not as measured predictions. Figure hashes are in `game/assets/sources.json`.

The larger `assets/` images in the VideoSSM code checkout belong to the inherited **LongLive** README and are not used as VideoSSM outputs. The promotional cover found in the EAG3R code repository is likewise not substituted for a measured reconstruction comparison.

## Maintenance

1. Edit the five generated projects' data and prose in `scripts/build-project-pages.py`.
2. Run `python scripts/build-project-site.py --download-assets`, followed by `python scripts/finalize-project-pages.py`. The latter preserves mirror links, source-based HD figures, and compatibility fixes.
3. Run `python scripts/test-project-pages.py` and `python scripts/test-project-mirrors.py` with Playwright/Chromium installed.
4. The `Build research project pages` workflow performs these steps, saves screenshots/reports, commits generated pages, and requests an existing GitHub Pages rebuild.

`Mirror original project sites` is a separate manual/source-update workflow for re-copying the original public sites. `scripts/sync-project-mirrors.py` records source hashes and download provenance. No repository visibility is changed.

## Validation and template repairs

Browser checks cover desktop and 390-/320-pixel mobile mirror layouts, image loading, all six 4D viewer routes, later time samples, and MP4 metadata decoding. The other five pages are checked for local links, image dialogs, citation controls and desktop/mobile containment.

Compatibility fixes only affect the local copies: EAG3R fixed-width figures become responsive; SANDBOX tables and long inline equations stay in local horizontal-scroll regions. An unused Nerfies interpolation preloader is guarded when its target is absent, preventing 240 requests to nonexistent source-template frames. These missing template files were never research results.

## Remaining inputs

EVSplat still needs its exact repository or source-material location. VideoSSM and LiFR projects would benefit from genuine experimental MP4s with prompts/timestamps and matched baselines. GaMe still needs a public manuscript/version decision, author affiliation details and evaluated question-answer examples. See `CONTENT_CHECKLIST.md` for release-related items.

LiFR v2 uses a **Repository** button, not a claim that code/checkpoints have been released; its repository README still describes those as being prepared.

The legacy LiFR-Seg manuscript address `/LiFR_Seg_Proj/` is outside this repository's Pages path and has not been redirected.
