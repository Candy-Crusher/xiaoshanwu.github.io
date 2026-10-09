"""Change only the homepage cover markup; retain all research and CV content."""
from pathlib import Path
from bs4 import BeautifulSoup
import os
import sys
root = Path(os.environ.get('SITE_ROOT', Path(__file__).resolve().parents[1]))
file = root / 'index.html'
soup = BeautifulSoup(file.read_text(), 'html.parser')
if soup.select_one('.hero-navigation') and soup.select_one('.hero-media'):
    print('Hero markup already updated.')
    sys.exit(0)
head = soup.head
for link in list(head.find_all('link', rel='preload')):
    if link.get('as') == 'image' and '/theme/' in link.get('href', ''):
        link.decompose()
for node in list(head.find_all(['link','script'])):
    if 'hero-hd' in str(node): node.decompose()
head.append(soup.new_tag('link', rel='stylesheet', href='assets/css/hero-hd.css?v=20261010-hd'))
head.append(soup.new_tag('script', src='assets/js/hero-hd.js?v=20261010-hd', defer=''))
header = soup.select_one('.site-header')
header.extract()
header['class'] = ['hero-navigation']
inner = soup.new_tag('div', attrs={'class': 'header-inner'})
for child in list(header.contents): inner.append(child.extract())
header.append(inner)
cover = soup.select_one('.cinematic-shell')
cover.insert_before(header)
image = cover.select_one('.cinematic-image')
image['src'] = 'images/theme/shared-world-1920.webp'
image['srcset'] = 'images/theme/shared-world-1440.webp 1440w, images/theme/shared-world-1920.webp 1920w, images/theme/shared-world-2864.webp 2864w'
image['sizes'] = '(min-aspect-ratio: 239/100) 100vw, 258svh'
image['width'], image['height'] = '2864', '1200'
image['alt'] = 'A wide, violet-lit scene: a luminous figure reaches toward a person on a walkway.'
picture = soup.new_tag('picture', attrs={'class': 'hero-media'})
source = soup.new_tag('source', media='(max-width: 680px)', srcset='images/theme/shared-world-mobile-790.webp 790w, images/theme/shared-world-mobile-1580.webp 1580w', sizes='100vw')
picture.append(source)
image.replace_with(picture)
picture.append(image)
cover.insert(1, soup.new_tag('div', attrs={'class': 'hero-scrim', 'aria-hidden': 'true'}))
statement = soup.select_one('.hero-statement')
statement.clear(); statement.append('Intelligence for '); statement.append(soup.new_tag('br')); statement.append('the world we share.')
foot = cover.select_one('.hero-foot'); foot.clear()
cue = soup.new_tag('a', href='#direction', attrs={'class': 'scroll-cue'})
cue.append(soup.new_tag('span', attrs={'class':'scroll-chevron', 'aria-hidden':'true'})); cue.append('Explore the research'); foot.append(cue)
credit = soup.new_tag('a', href='#inspiration', attrs={'class':'inspiration-link'}); credit.string = 'On a shared world ↗'; foot.append(credit)
credit = soup.select_one('.image-credit'); credit.clear(); credit.append('Header film still: ')
cite = soup.new_tag('cite'); cite.string = 'Blade Runner 2049'; credit.append(cite)
credit.append(' (2017). All rights belong to the respective rights holders. ')
a = soup.new_tag('a', href='images/theme/shared-world-source.json', attrs={'target':'_blank','rel':'noopener'}); a.string='Image source'; credit.append(a)
credit.append('. Visual inspiration, not a research result.')
file.write_text(str(soup) + '\n')
