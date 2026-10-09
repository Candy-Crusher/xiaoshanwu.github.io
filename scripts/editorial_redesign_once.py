from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'index.html').read_bytes()
assert hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()=='56a7d5f837d1a738da7cf602c76b883a004b2dad', 'Homepage changed; review before regenerating.'
old=BeautifulSoup(source.decode(),'html.parser')
pubs=old.select_one('section[aria-labelledby="publications"]')
original_pub_ids=[x['id'] for x in pubs.select('li[id]')]
original_records={x['id']:{sel:x.select_one(sel).get_text(' ',strip=True) for sel in ['.pub-title','.pub-authors','.pub-detail']} for x in pubs.select('li[id]')}
head='''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Xiaoshan Wu">
  <meta name="color-scheme" content="light">
  <meta name="description" content="Xiaoshan Wu — world models and memory for embodied intelligence. Research in 3D/4D vision, video generation, and spatial reasoning.">
  <title>{title}</title>
  <link rel="canonical" href="https://candy-crusher.github.io/xiaoshanwu.github.io/{path}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="World models and memory for embodied intelligence.">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="assets/css/editorial.css?v=20261010">
  <script defer src="assets/js/editorial.js?v=20261010"></script>
</head>'''
def nav(home=True):
    base='' if home else 'index.html'
    return f'''<header class="site-header wrap">
  <a class="wordmark" href="index.html" aria-label="Xiaoshan Wu, homepage">Xiaoshan Wu<span lang="zh" aria-hidden="true">小山</span></a>
  <nav class="site-nav" aria-label="Main navigation">
    <a href="{base}#selected-research">Research</a>
    <a href="publications.html"{' aria-current="page"' if not home else ''}>Publications</a>
    <a href="{base}#background">Background</a>
    <a href="Xiaoshan_Wu_CV.pdf" target="_blank" rel="noopener">CV <span aria-hidden="true">↗</span></a>
  </nav>
</header>'''
footer='''<footer class="site-footer wrap">
  <span>© 2026 Xiaoshan Wu</span>
  <div><a href="mailto:wuxiaoshan630@gmail.com">Email</a><a href="https://github.com/Candy-Crusher" target="_blank" rel="noopener">GitHub</a><a href="#top">Back to top ↑</a></div>
</footer>'''
modal='''<dialog class="figure-dialog" id="research-figure" aria-labelledby="figure-title" aria-describedby="figure-caption">
  <div class="figure-dialog-bar"><p id="figure-title">Research figure</p><button type="button" class="figure-close" aria-label="Close figure">Close <span aria-hidden="true">×</span></button></div>
  <img class="figure-dialog-image" alt="">
  <p class="figure-dialog-caption" id="figure-caption"></p>
</dialog>'''
summaries={
 'selected-world-action-model':'S4NDBOX predicts appearance, geometry, and motion before generating actions. Agreement between the predicted future and its paired action provides a geometric signal for candidate selection before execution.',
 'selected-game':'A 16-slot geometric working memory combines evidence across views and augments the original visual–language context for spatial question answering.',
 'selected-videossm':'Local attention preserves recent detail while recurrent state-space memory retains long-range context, supporting autoregressive long-video generation without an ever-growing KV cache.',
 'selected-eag3r':'Reliability-aware RGB–event fusion and event-based photometric constraints recover geometry in dynamic, low-light scenes, including daytime-to-nighttime transfer.',
 'selected-lifr-seg':'Event-guided propagation and temporal memory keep semantic predictions up to date between RGB frames, without requiring an image at each query time.'}
figcaptions={
 'selected-world-action-model':'4D prediction & geometric verification',
 'selected-game':'Geometric working memory · conceptual overview',
 'selected-videossm':'Local detail & long-range memory',
 'selected-eag3r':'RGB input / RGB-only / EAG3R',
 'selected-lifr-seg':'Semantic prediction between RGB frames'}
entries=[]
for article in old.select('article.research-entry'):
    id=article['id'];article['class']=['research-entry']
    for category in article.select('.research-area'):category.decompose()
    article.select_one('.research-summary').string=summaries[id]
    article.select_one('figcaption').string=figcaptions[id]
    label=article.select_one('.figure-expand');label.clear();label.append('↗')
    article.select_one('.figure-preview img')['loading']='lazy'
    result=article.select_one('.s4ndbox-result')
    if result:
        result['class']=['research-result'];result.clear()
        result.append(BeautifulSoup('<strong>+13.3 percentage points</strong> on RoboTwin Hard over RGB-only after clean-only task training; zero-shot sim-to-real on a Franka Research 3.','html.parser'))
    extra=article.select_one('.s4ndbox-figure-links')
    if extra:
        links=article.select_one('.research-links')
        for a in extra.find_all('a'):links.append(a.extract())
        extra.decompose()
    for a in article.select('a[href^="#pub-"]'):
        a['href']='publications.html'+a['href'];a.string='Details'
    entries.append(str(article))
bio='''<section class="profile" aria-labelledby="name">
  <div class="profile-copy">
    <h1 id="name">Xiaoshan Wu <span class="native-name" lang="zh">吴小山</span></h1>
    <p class="affiliation">Ph.D. candidate · The University of Hong Kong</p>
    <p class="research-statement">World models and memory<br>for embodied intelligence.</p>
    <p>I connect <strong>3D/4D perception, video generation, and spatial reasoning</strong> to help robots understand and act in the physical world. My longer-term goal is to build agents that improve through interaction and feedback.</p>
    <p class="biography">At HKU, I am advised by <a href="https://xjqi.github.io/" target="_blank" rel="noopener">Prof. Xiaojuan Qi</a>. Previously, I visited Harvard University, working with Yilun Du and Mengyu Wang.</p>
    <nav class="contact-links" aria-label="Contact and profiles">
      <a href="mailto:wuxiaoshan630@gmail.com">Email</a>
      <a href="https://scholar.google.com/citations?user=9nsSKpsAAAAJ&amp;hl=en" target="_blank" rel="noopener">Google Scholar</a>
      <a href="https://github.com/Candy-Crusher" target="_blank" rel="noopener">GitHub</a>
      <a href="Xiaoshan_Wu_CV.pdf" target="_blank" rel="noopener">CV</a>
    </nav>
  </div>
  <figure class="portrait"><img src="images/research/profile.webp" width="480" height="720" alt="Xiaoshan Wu" fetchpriority="high" decoding="async"></figure>
</section>'''
background=old.select_one('section[aria-labelledby="background"]');background['class']=['background-section']
for exp in background.select('.experience'):exp['class']=['experience-row']
background.select_one('h2').string='Background';background.select_one('h3').string='Selected honors'
news=old.select_one('section[aria-labelledby="news"]');news['class']=['news-section'];news.select_one('h2').string='Recent updates'
for a in news.select('a[href^="#pub-"]'):a['href']='publications.html'+a['href']
home=head.format(title='Xiaoshan Wu | World Models &amp; Embodied AI',path='')+f'''
<body id="top" data-page="home">
<a class="skip-link" href="#main">Skip to content</a>
{nav()}
<main id="main" class="wrap">
{bio}
<section class="selected-section" aria-labelledby="selected-research">
  <div class="section-heading"><h2 id="selected-research">Selected research</h2><a href="publications.html">All publications <span aria-hidden="true">→</span></a></div>
  <p class="section-note">First- and co-first-author work. <span>* Equal contribution.</span></p>
  {''.join(entries)}
  <p class="publication-index" id="publications"><a href="publications.html">View the complete publication list <span aria-hidden="true">→</span></a></p>
</section>
{news}
{background}
</main>
{footer}
{modal}
</body>
</html>
'''
(ROOT/'index.html').write_text(home,encoding='utf-8')
pubs.select_one('h2').decompose()
for group in pubs.select('section'):
    group['class']=sorted(set(group.get('class',[])+['publication-group']))
    for item in group.select('li'):
        paper_link=item.select_one('.paper-links a')
        if paper_link:
            title=item.select_one('.pub-title')
            a=old.new_tag('a',href=paper_link['href'],target='_blank',rel='noopener')
            a.string=title.get_text();title.clear();title.append(a)
assert original_pub_ids==[x['id'] for x in pubs.select('li[id]')]
publications=head.format(title='Publications | Xiaoshan Wu',path='publications.html')+f'''
<body id="top" data-page="publications">
<a class="skip-link" href="#main">Skip to content</a>
{nav(False)}
<main id="main" class="wrap publications-page">
  <header class="page-intro"><a class="back-link" href="index.html#selected-research">← Selected research</a><h1>Publications &amp; preprints</h1><p>World models, spatial reasoning, and visual perception.</p></header>
{pubs}
</main>
{footer}
</body>
</html>
'''
(ROOT/'publications.html').write_text(publications,encoding='utf-8')
new=BeautifulSoup(publications,'html.parser')
for id,record in original_records.items():
    item=new.select_one('#'+id)
    for sel,value in record.items():assert item.select_one(sel).get_text(' ',strip=True)==value,(id,sel)
print('Preserved all 15 titles, author lists, status labels and original resource links.')
for name in ['index.html','publications.html','assets/css/editorial.css','assets/js/editorial.js']:
    b=(ROOT/name).read_bytes();print(name,hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest())
