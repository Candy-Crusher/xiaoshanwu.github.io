# Personal website information architecture

Home (`index.html`): original cinematic cover, a short introduction, three project highlights and recent updates.
About (`about.html`): biography, one research perspective, future interests and the existing personal inspiration.
Resume (`resume.html`): CV PDF, education, research experience, honors and technical skills.
Research (`research.html`): seven project summaries and the complete publication record.

`personal-site.json` preserves the pre-migration sections as editable source. Edit those fragments for biography, dates, awards, news, authors or publication statuses. Do not delete the source file: the short homepage intentionally no longer contains the full record. Project descriptions for LiFR v2 and EVSplat are read from their current project pages during a build.

Run `python scripts/build-personal-site.py` and `python scripts/test-personal-site.py`. The personal-site workflow also runs after successful project-page builds, so updates do not restore the old navigation. It serializes with other site writers.

The original CV PDF and LaTeX are unchanged. All seven project URLs are unchanged. `publications.html#pub-*` redirects to the same anchor on Research, with a full no-JavaScript archive fallback. Old homepage research, background and inspiration anchors have explicit redirects.
