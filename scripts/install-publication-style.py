"""Install publication-only presentation and update the matching regressions."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def main():
    before={}
    def save(path,value):
        p=ROOT/path;before[path]=hashlib.sha256(p.read_bytes()).hexdigest();p.write_text(value)
    p=ROOT/'scripts/build-personal-site.py';s=p.read_text()
    if 'from publication_style import apply_publication_style' not in s:
        needle='import personal_site_core as core'
        assert s.count(needle)==1
        s=s.replace(needle,needle+'\nfrom publication_style import apply_publication_style\nfrom site_favicon import apply_favicon')
        needle="    return str(doc) + '\\n'"
        assert s.count(needle)==1,'Review current document renderer'
        s=s.replace(needle,"    doc = apply_publication_style(doc, cfg)\n    return apply_favicon(str(doc) + '\\n', name)")
    s,n=re.subn(r"^LAYOUT = '[^']+'","LAYOUT = 'recent-projects-20261015-v1'",s,count=1,flags=re.M);assert n==1
    save('scripts/build-personal-site.py',s)
    p=ROOT/'scripts/test-personal-site.py';s=p.read_text()
    if 'from publication_style import load_details' not in s:
        needle='from playwright.sync_api import sync_playwright'
        assert needle in s
        s=s.replace(needle,needle+'\nfrom publication_style import load_details, authors_markup, venue_markup')
        replacements={
            "assert norm(text(item.select_one('.pub-authors'))) == norm(builder.plain(paper['authors']))":
            "assert norm(text(item.select_one('.pub-authors'))) == norm(builder.plain(authors_markup(load_details()['papers'][item['id']], load_details()['profiles'])))",
            "assert norm(text(item.select_one('.research-meta > span'))) == norm(builder.plain(paper['venue']))":
            "assert norm(text(item.select_one('.research-meta > span'))) == norm(builder.plain(venue_markup(load_details()['papers'][item['id']])))",
            "assert text(item.select_one('.research-role')) == paper['role']":
            "assert item.get('data-author-role') == paper['role']",
            "assert norm(text(ugg.select_one('.pub-authors'))) == norm('A. Kiruga, Z. Li, R. Cai, H. Lillemark, X. Wu, A. Tewari, and Y. Du.')":
            "assert norm(text(ugg.select_one('.pub-authors'))) == norm(builder.plain(authors_markup(load_details()['papers']['pub-ugg'], load_details()['profiles'])))",
            "assert text(ugg.select_one('.research-meta')) == 'NeurIPS 2026'":
            "assert norm(text(ugg.select_one('.research-meta'))) == norm('NeurIPS, 2026.')",
            "assert not ugg.select('.research-role, .pub-authors sup')":
            "assert not ugg.select('.research-role, .pub-author-self sup')"
        }
        for old,new in replacements.items():
            assert s.count(old)==1,old
            s=s.replace(old,new)
    s,n=re.subn(r"^LAYOUT = '[^']+'","LAYOUT = 'recent-projects-20261015-v1'",s,count=1,flags=re.M);assert n==1
    save('scripts/test-personal-site.py',s)
    print(json.dumps({'source_hashes_before':before},indent=2))
if __name__=='__main__':main()
