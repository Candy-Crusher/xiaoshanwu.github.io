# Project-page content checklist

The sites intentionally omit unavailable media, unpublished code buttons and unverified scores. No private repository visibility was changed.

## VideoSSM

Page: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/videossm/

- [ ] Original 60-second MP4s and their prompts; matched baseline clips.
- [ ] Prompt-switching clips with switch timestamps.
- [ ] Public code/checkpoint release URL and current submission status.

## GaMe

Page: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/game/

- [ ] Publication-ready PDF or public preprint URL; confirm that public release is appropriate during review.
- [ ] Full author spelling for S. Shi and author–affiliation mapping.
- [ ] Approved method figure, benchmark table and real question–answer examples.
- [ ] Public code/model URL when ready.

## LiFR-Seg

Page: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-seg/

- [ ] Synchronized RGB / events / prediction / ground-truth MP4 demos with timestamps.
- [ ] Confirm code release: Candy-Crusher/LiFR-Seg currently has no code.
- [ ] The paper names the old /LiFR_Seg_Proj/ URL; update that link or enable a separate redirect repository.

## LiFR v2

Page: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/lifr-v2/

- [ ] Streaming MP4s, especially emergence/disocclusion examples and the corresponding baselines.
- [ ] Dataset/checkpoint download URLs when released.
- [ ] Keep repository release wording in sync with TaoWan0610/LiFR-v2.

## EVSplat

Page: https://candy-crusher.github.io/xiaoshanwu.github.io/projects/evsplat/

- [ ] Current manuscript/PDF, abstract and approved public-release status.
- [ ] Teaser and method figures; reconstruction / novel-view / dynamic-scene MP4s.
- [ ] Confirmed results table, dataset names and evaluation settings.
- [ ] Author–affiliation mapping and public code/model URL.

## Maintenance

Edit `scripts/build-project-pages.py` and run `python scripts/build-project-site.py --download-assets`. The build workflow regenerates the static pages. Research content is readable without JavaScript. JavaScript only enhances figure enlargement, navigation highlighting and citation copying.
