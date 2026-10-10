"""Apply the three requested CV edits to exact, pre-verified source snapshots."""
from pathlib import Path
import hashlib
import json
import re


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def revise(text, paragraph, main):
    marker = '\\cvsection{Research Interests}\n'
    start = text.index(marker) + len(marker)
    end = text.index('\\cvsection{Publications', start)
    comments = ''.join(line + '\n' for line in text[start:end].splitlines() if line.startswith('%'))
    text = text[:start] + paragraph + '\n\n' + comments + text[end:]
    wam = re.search(r'\\item \\textbf\{Verifiable 4D World.*?(?=\\item|\\end\{enumerate\})', text, re.S)
    assert wam and r'\textbf{X. Wu*}, R. Cai*' in wam.group()
    block = wam.group()
    assert block.count(r'\textit{Co-first author}') == 1
    text = text[:wam.start()] + block.replace(r'\textit{Co-first author}', r'\textit{First author}') + text[wam.end():]
    text = text.replace(r'\textbf{X. Wu}, W. He, M. Yao, et al. \hfill \textbf{IEEE TCDS}', r'\textbf{X. Wu}, W. He, M. Yao, et al.\par' + '\n' + r'\textbf{IEEE TCDS}')
    if main:
        # Both settings already render at 9pt; remove ignored options/substitution warnings.
        text = text.replace(r'\documentclass[9pt,a4paper]{article}', r'\documentclass[a4paper]{article}')
        text = text.replace(r'\fontsize{8.55}{9.65}', r'\fontsize{9}{9.65}')
    else:
        text = text.replace('% Standalone file;', '% Revised 2026-10-10: author-role labels, TCDS layout, and research-interest framing.\n% Standalone file;', 1)
    assert text.count(r'\textit{First author}') == 5
    assert text.count(r'\textit{Co-first author}') == 1
    assert text.count(r'\textit{Co-first author; project lead}') == 2
    assert r'\textbf{X. Wu*}, R. Cai*' in text
    assert r'\textbf{X. Wu}, W. He, M. Yao, et al.\par' + '\n' + r'\textbf{IEEE TCDS}' in text
    assert r'\textbf{Self-Improving Physical Agents' not in text
    return text


edits = json.loads(Path('.cv-clarity/edits.json').read_text())
assert len(edits) == 14
prepared = []
for edit in edits:
    path = Path(edit['path'])
    original = path.read_bytes()
    assert blob(original) == edit['before'], f'Source changed: {path}'
    revised = revise(original.decode('utf-8'), edit['paragraph'], edit['main']).encode('utf-8')
    assert blob(revised) == edit['after'], f'Revision does not match locally compiled version: {path}'
    prepared.append((path, revised))
readme = Path('cv/2027-internships/README.md')
original = readme.read_text()
assert blob(original.encode()) == 'e197222626ad69265abc76fb28fb193a7733b366'
old = '本目录的 `.tex` 与 2026-10-10 对话中交付的版本逐字节一致。导入时已逐份核对 SHA-256，没有重新改写研究内容或署名。'
new = '初始版本于 2026-10-10 逐份校验后导入。本次按作者反馈更新了贡献标签、TCDS 条目排版和研究兴趣；以下文件是修订版，不再与最初交付的附件逐字节一致。\n\n**修订约定：** 第一署名显示 `First author`，但保留共同一作的 `*` 与 equal-contribution 说明；非第一署名的共同一作仍显示 `Co-first author`。TCDS 的标题、作者、期刊与贡献分三行。研究兴趣先介绍已有工作，最后一句将 self-improving agents / agent–world model co-evolution 明确作为新兴趣。'
assert old in original
prepared.append((readme, original.replace(old, new).encode()))
for path, content in prepared:
    path.write_bytes(content)
    print(f'{blob(content)}  {path}')
print('All 14 TeX outputs match the locally compiled revision; authors, order and publication status are preserved.')
