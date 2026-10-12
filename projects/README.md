# Research project pages

Five independent static project pages, hosted in the existing personal-site repository.

| Work | Project page | Current coverage |
| --- | --- | --- |
| VideoSSM | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/videossm/ | Overview, original figures, selected paper results, paper/PDF and BibTeX |
| GaMe | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/game/ | Public project identity and conceptual overview; manuscript and evaluated examples pending |
| LiFR-Seg | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-seg/ | Overview, original figures, selected paper results, paper/PDF and BibTeX |
| LiFR v2 | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-v2/ | Overview, original figures, selected paper results, paper/PDF, BibTeX and repository link |
| EVSplat | https://candy-crusher.github.io/xiaoshanwu.github.io/projects/evsplat/ | Project identity and research focus; technical manuscript and experimental media pending |

Project directory: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/

## Updating the sites

- Edit project metadata, prose, figure definitions and reported tables in `scripts/build-project-pages.py`.
- Use `python scripts/build-project-site.py --download-assets` to regenerate. The site entry point also maintains homepage/publication links and responsive table layout.
- Generated HTML is under `projects/<slug>/index.html`; shared presentation code is under `projects/assets/`. Direct changes to generated files can be overwritten on the next build.
- The `Build research project pages` workflow regenerates pages, checks desktop/mobile layout and local links in Chromium, saves screenshots, commits generated content, and requests a fresh build of the existing GitHub Pages site.
- Figure assets are stored locally in the repository. Existing figures are reused; only verified public paper-image URLs are downloaded. No private manuscript or code repository is made public by this workflow.

## Outstanding content

See [CONTENT_CHECKLIST.md](CONTENT_CHECKLIST.md) for the per-project list. The highest-priority additions are approved GaMe/EVSplat manuscripts and genuine experimental MP4s. Unavailable paper/code/video buttons are intentionally omitted. Conceptual figures are labelled separately from evaluated outputs.

LiFR v2 links to a **repository**, not to a completed code release: its current README says code and pretrained models are being prepared.

## LiFR-Seg legacy URL

The public LiFR-Seg manuscript names `https://candy-crusher.github.io/LiFR_Seg_Proj/`. This is outside this repository's GitHub Pages path. The new canonical page is the `/xiaoshanwu.github.io/projects/lifr-seg/` route above. The manuscript link should be updated, or a separately configured `LiFR_Seg_Proj` Pages repository should redirect to the new page. This change does not claim to configure that separate legacy URL.

## Design reference

The old SANDBOX preview URL was not accessible during this build. These pages use a restrained academic-project layout with paper figures, concise summaries, labelled results and source links; they are not represented as an exact visual copy of that inaccessible deployment.
