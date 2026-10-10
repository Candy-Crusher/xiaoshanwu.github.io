"""Add the abstract-grounded S4NDBOX summary to all CVs and the personal site.
This is a targeted, idempotent edit; other projects and research interests are unchanged.
"""
from pathlib import Path
import hashlib
import re
import sys

CV_TLDR = ('S4NDBOX bridges visual imagination and robot control through explicit 4D prediction, '
           'guiding action generation and candidate selection by geometric agreement before execution.')
CV_RESULT = (r'RoboTwin Hard: \textbf{+13.3 pp} success over RGB-only after clean-only training; '
             r'zero-shot sim-to-real on Stack Cups.')
WEB_TLDR = ('S4NDBOX bridges visual imagination and robot control through explicit 4D prediction of '
            'appearance, geometry, and motion. These predictions guide action generation and enable '
            'candidate selection through geometric agreement with paired actions before execution, '
            'improving robustness over RGB-only control under scene shifts and in zero-shot sim-to-real transfer.')
WEB_RESULT = ('<strong>+13.3 percentage points</strong> in RoboTwin Hard success over RGB-only after '
              'clean-only training. Zero-shot Stack Cups transfer from simulation to a Franka Research 3, '
              'without real-world task demonstrations or fine-tuning.')
TITLE = r'\item \textbf{Verifiable 4D World--Action Model for Robust Robot Control.}\par'


def once(text, old, new):
    if old == new or (old not in text and new in text):
        return text
    if text.count(old) != 1:
        raise ValueError(f'Expected one match for {old[:100]!r}, got {text.count(old)}')
    return text.replace(old, new, 1)


def update_cv(text, main=False):
    start = text.index(TITLE)
    end = text.index(r'\item ', start + len(TITLE))
    block = text[start:end]
    base = '\n'.join(line for line in block.splitlines() if not line.startswith(r'\pubnote{')).rstrip()
    note = '\n'+r'\pubnote{'+CV_TLDR+'}\n'+r'\pubnote{'+CV_RESULT+'}\n'
    text = text[:start]+base+note+text[end:]
    if main and r'\newcommand{\pubnote}' not in text:
        macros = (r'\definecolor{cvgray}{RGB}{66,66,66}'+'\n'+
                  r'\newcommand{\pubnote}[1]{\par{\color{cvgray}#1}}'+'\n\n')
        text = once(text, r'\begin{document}', macros+r'\begin{document}')
    if main:
        text = text.replace('itemsep=4.1pt', 'itemsep=2.4pt', 1)
        text = text.replace(r'\par\vspace{5.5pt}', r'\par\vspace{4.5pt}', 1)
    return text


def update_web(text, home=False):
    element = 'article' if home else 'li'
    ident = 'selected-world-action-model' if home else 'pub-world-action-model'
    pat = rf'(<{element}\b[^>]*\bid="{ident}"[^>]*>)(.*?)(</{element}>)'
    matches = list(re.finditer(pat, text, re.S))
    if len(matches) != 1: raise ValueError(f'Expected one {ident}')
    m = matches[0]; body = m.group(2)
    # Align the role badge with the author's requested convention, retaining both * markers.
    body = body.replace('>Co-first author</span>', '>First author</span>', 1)
    if home:
        for cls, copy in [('research-summary', '<strong>TL;DR.</strong> '+WEB_TLDR),('research-result',WEB_RESULT)]:
            p = rf'<p class="{cls}">.*?</p>'
            body, n = re.subn(p, lambda _:f'<p class="{cls}">{copy}</p>', body, count=1, flags=re.S)
            if n != 1: raise ValueError(f'Missing {cls}')
    else:
        p = '<p class="pub-authors s4ndbox-tldr"><strong>TL;DR.</strong> '+CV_TLDR+'</p>'
        if 's4ndbox-tldr' in body:
            body = re.sub(r'<p class="pub-authors s4ndbox-tldr">.*?</p>', lambda _:p, body, flags=re.S)
        else: body=body.rstrip()+'\n'+p+'\n'
    return text[:m.start()]+m.group(1)+body+m.group(3)+text[m.end():]


def main(root):
    root=Path(root)
    paths = [root/'cv.tex', *sorted((root/'cv/2027-internships').glob('*.tex'))]
    if len(paths)!=14: raise RuntimeError(f'Expected main plus 13 variants, found {len(paths)}')
    for p in paths:
        old=p.read_text(encoding='utf-8');new=update_cv(old,main=p==root/'cv.tex')
        if old.count(r'\item ')!=new.count(r'\item '): raise ValueError('Publication count changed')
        p.write_text(new, encoding='utf-8')
        print(p.relative_to(root))
    for fn in ['index.html','publications.html']:
        p=root/fn; p.write_text(update_web(p.read_text(encoding='utf-8'),home=fn=='index.html'),encoding='utf-8')
        print(fn)

if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else '.')
