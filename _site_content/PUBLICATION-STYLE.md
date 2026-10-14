# Publications presentation

Typography and hierarchy follow Jieneng Chen's Recent Projects section: Lato; 15px bold titles, 13px author bylines, short venue/year metadata, a 14px one-sentence TL;DR, and a compact Project / Paper / other-resources row. Existing teaser images stay complete; S4NDBOX retains its original video. Styling is limited to Publications, and mobile layouts retain the cover figures.

`publication-details.json` contains source-checked complete author lists and personal-homepage mappings. Author order is not truncated to et al. Xiaoshan Wu is bold; confirmed equal-contribution/project-lead markers remain. S4NDBOX's nine unconfirmed full names deliberately retain their original CV initials until the author supplies the complete byline. The Science Advances digital-twin paper contains two different authors named Yi Li, both retained. Ambiguous or unverified personal websites are not guessed.

Published items use **Venue**, YYYY. **Distinction**. EAG3R is Spotlight; no unverified oral designation or ranking percentage is added. Pending papers show only Under review; VideoSSM remains arXiv, 2025. Public article/project URLs are preserved or supplemented with verified primary sources; a missing public paper link is not replaced with a placeholder.

The main document builder calls `publication_style.py` and `site_favicon.py`. Downloadable CVs, the factual CV parser, all project pages, media files, News, Experience and About text are unchanged. Lato is loaded from Google Fonts; no font files are bundled. The mountain emoji favicon is a locally served Twemoji SVG with PNG/ICO fallbacks and attribution under assets/icons/.
