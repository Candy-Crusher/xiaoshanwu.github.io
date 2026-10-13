from pathlib import Path
import json
r=Path('.')
p=r/'_site_content/site-presentation.json';cfg=json.loads(p.read_text());cfg['navigation'].insert(1,{'label':'Research','url':'index.html#research'})
v=cfg['papers']['pub-world-action-model'];v['resources']=[x for x in v['resources'] if not x['label'].startswith('Robot demo')]
v['media']={'kind':'video','src':'projects/sandbox/static/videos/disco_light_10x.mp4','poster':'projects/sandbox/static/images/poster_disco_light.jpg','width':1920,'height':1080,'alt':'Stack Cups on a Franka Research 3 under moving coloured lighting, played at 10× speed','caption':'Franka Research 3 · robot demo (10×)'}
v['media_source']='Original cover-video source and poster from projects/sandbox/index.html; restored byte-for-byte from pre-deletion Git history.'
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
p=r/'scripts/build-personal-site.py';s=p.read_text();s=s.replace("STYLE = 'assets/css/site-pages.css?v=academic-home-research-20261014'", "STYLE = 'assets/css/site-pages.css?v=research-media-20261014'").replace("SCRIPT = 'assets/js/site-pages.js?v=academic-home-research-20261014'", "SCRIPT = 'assets/js/site-pages.js?v=research-media-20261014'")
s=s.replace("    crop = m.get('crop')",'''    if m.get('kind') == 'video':
        # Native controls are not nested inside a project link. The title and
        # Project resource remain clickable; the cover itself plays the demo.
        video = (f'<span class="media-frame video-frame">'
                 f'<video class="research-video" controls muted loop playsinline '
                 f'preload="metadata" poster="{esc(m["poster"])}" '
                 f'aria-label="{esc(m["alt"])}" data-autoplay-on-view>'
                 f'<source src="{esc(m["src"])}" type="video/mp4">'
                 f'{link(m["src"], "Open robot demonstration")}</video></span>')
        return ('<figure class="research-media research-video-media">' + video +
                '<figcaption>' + esc(m['caption']) + '</figcaption></figure>')
    crop = m.get('crop')''')
s=s.replace("[('Home','index.html#top'),('Resume','index.html#resume'),('About','about.html')]", "[('Home','index.html#top'),('Research','index.html#research'),('Resume','index.html#resume'),('About','about.html')]")
p.write_text(s)
p=r/'assets/css/site-pages.css';s=p.read_text()+'''\n/* Research navigation and an inline, accessible original robot demo. */
.video-frame{aspect-ratio:16/9;background:#111;overflow:hidden}
.research-video{display:block;width:100%;height:100%;object-fit:contain}
.research-video:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media(max-width:360px){.site-nav{gap:19px}}
''';p.write_text(s)
p=r/'assets/js/site-pages.js';s=p.read_text();s=s.replace("    const resumeSelected = resumeAnchors.has(id);", "    const resumeSelected = resumeAnchors.has(id);\n    const targetNode = document.getElementById(id);\n    const researchSelected = !!targetNode?.closest('#research, #publications');")
s=s.replace("      if (target === '#top' && !resumeSelected) a.setAttribute('aria-current', 'location');", "      if (target === '#research' && researchSelected) a.setAttribute('aria-current', 'location');\n      if (target === '#top' && !resumeSelected && !researchSelected) a.setAttribute('aria-current', 'location');")
s=s.replace("  const dialog = document.getElementById('research-figure');",'''  // Play the original muted demo only while visible. Reduced-motion and
  // data-saving users keep native click-to-play controls. A manual pause is
  // respected until the user chooses to play again.
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('video[data-autoplay-on-view]').forEach(video => {
    let visible = false, manuallyPaused = false;
    const play = () => {
      if (visible && !document.hidden && !manuallyPaused && !motion.matches && !navigator.connection?.saveData) {
        video.play().catch(() => {});
      }
    };
    video.addEventListener('pause', () => {
      if (visible && !document.hidden && !motion.matches) manuallyPaused = true;
    });
    video.addEventListener('play', () => { manuallyPaused = false; });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        if (visible) play(); else video.pause();
      }, {threshold: 0.3}).observe(video);
    }
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) video.pause(); else play();
    });
    motion.addEventListener('change', () => {
      if (motion.matches) video.pause(); else play();
    });
  });
  const dialog = document.getElementById('research-figure');''')
p.write_text(s)
p=r/'scripts/test-personal-site.py';s=p.read_text().replace("NAV=['Home','Resume','About']","NAV=['Home','Research','Resume','About']")
s=s.replace("a[href], main img[src], script[src], link[rel=\"stylesheet\"][href]", "a[href], main img[src], main source[src], script[src], link[rel=\"stylesheet\"][href]")
s=s.replace("    assert home.select_one('nav[aria-label=\"Main navigation\"] a[href=\"#resume\"]')", "    assert home.select_one('nav[aria-label=\"Main navigation\"] a[href=\"#research\"]')\n    assert docs['about.html'].select_one('nav[aria-label=\"Main navigation\"] a[href=\"index.html#research\"]')\n    assert home.select_one('nav[aria-label=\"Main navigation\"] a[href=\"#resume\"]')")
s=s.replace("        report['browser']=browser_checks(f'http://127.0.0.1:{server.server_port}/',args.inline_preview);report['status']='PASS'", "        report['browser']=browser_checks(f'http://127.0.0.1:{server.server_port}/',args.inline_preview)\n        if not args.inline_preview:\n            spec=importlib.util.spec_from_file_location('sandbox_media',ROOT/'scripts/test-sandbox-media.py')\n            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\n            report['sandbox_media']=module.run(f'http://127.0.0.1:{server.server_port}/',OUT)\n        report['status']='PASS'")
p.write_text(s)
p=r/'_site_content/README.md';s=p.read_text();s += '''\n## Research navigation and S4NDBOX media (2026-10-14)

Navigation is now **Home → Research → Resume → About**, with the first three
using native homepage anchors. The S4NDBOX publication cover uses the original
`disco_light_10x.mp4` and its matching poster, with native play/pause controls.
The redundant Robot demo resource link is removed. Quiet, reduced-motion and
data-saving behavior are handled without changing the clip or its playback speed.

The missing S4NDBOX static assets were restored from commit
`0ac8073ef92ce5f84828f8a9f4a4c3e398f55793`, before the Overleaf sync deletion
in `5e0e4d52cd34e42c34f745380df937d45fb047af`. Existing static files were
verified unchanged; no paper prose, experiments or research data were rewritten.
`test-sandbox-media.py` validates every manifest frame and exercises all six
interactive cases, both point-cloud streams, timeline navigation, source RGB
insets, and the inline video's decode/playback. It runs as part of personal-site
validation so a surviving HTML shell alone can no longer pass the media check.
''';p.write_text(s)
