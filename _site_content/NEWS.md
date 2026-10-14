# Publication status and monthly News (2026-10-15)

The website-only `parse_cv()` view reduces every pending venue label to
**Under review**. Accepted conference/journal labels and preprint entries are
unchanged; TeX, downloadable CVs, and individual project pages are not rewritten.
The generated public website cache uses the same venue-neutral labels.

`news.json` now owns the homepage News milestones, rendered by `news_feed()`.
Events are sorted newest first and displayed as `YYYY.MM`; each source entry
records the relevant paper anchors, provenance, and month basis. Conference
months use the official main-track decision-notification months, not conference
or arXiv-publication months. Counts use the confirmed papers in the current
CV02-backed catalog; VideoSSM is not counted as an accepted conference paper.
Nature's article history records acceptance on 12 May 2026 and publication on
10 June 2026: the news item is an acceptance milestone in May. Harvard's May
arrival is the user's explicit update, separate from the April appointment start
in the unchanged CV. The old year-only news fragment in `personal-site.json` is
archival and is no longer rendered. `assets/css/news.css` provides the wider
month column without changing the surrounding layout.

## UGG update

UGG: Unified Generative Geometry Model is a user-confirmed NeurIPS 2026
collaborative paper. Its complete supplied BibTeX is preserved at
`assets/bibtex/kiruga2026ugg.bib`. The website supplement
`publication-additions.json` supplies the title, all seven authors in order,
venue, and project link without changing any CV TeX or PDF. It is inserted at
the top of Collaborative Work; all original 15 records retain their order.
The new September 2026 News item is distinct from EAG3R's September 2025
acceptance. Its month follows the official September 24, 2026 notification
schedule; it is not a claim about the date of an individual email.
