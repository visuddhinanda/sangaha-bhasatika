"""合并 parts/chunk-*.json（逐块提取）与 fill/out-*.json（补拟巴利），生成 glossary.json / .tsv / .md

- 每个巴利词只保留本书的一个中文译名（书中有巴利的优先，其次取出现最多的）
- 书中未给巴利的条目，用 fill/out-*.json 中按中文补拟的巴利
- 标 † 的巴利：书中找不到原样（补拟的，或从屈折形式还原的词干），使用前请核对
"""
import json, glob, os, re, unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ['a','ā','i','ī','u','ū','e','o','k','kh','g','gh','ṅ','c','ch','j','jh','ñ','ṭ','ṭh','ḍ','ḍh','ṇ',
         't','th','d','dh','n','p','ph','b','bh','m','y','r','l','ḷ','v','s','h','ṃ']
RANK = {c: i for i, c in enumerate(ORDER)}

def pali_key(s):
    s = unicodedata.normalize('NFC', s.lower()); out = []; i = 0
    while i < len(s):
        two = s[i:i+2]
        if len(two) == 2 and two in RANK: out.append(RANK[two]); i += 2; continue
        out.append(RANK.get(s[i], 100 + ord(s[i]) % 1000)); i += 1
    return out

def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', (s or '').strip()))

SRC = unicodedata.normalize('NFC', open(os.path.join(ROOT, 'source', '阿毗达摩进阶-第2级.md'), encoding='utf-8').read().lower())
SRC_NOSP = re.sub(r'\s+', '', SRC)
def in_book(p):
    p = p.lower()
    return p in SRC or re.sub(r'\s+', '', p) in SRC_NOSP

# 书中笔误：这些 (巴利, 中文) 对不收录
TYPOS = {('lobha', '利养')}  # 书中“利养(lobha)”，应为 lābha

# 1. 逐块提取的原始条目
items = []
for f in sorted(glob.glob(os.path.join(ROOT, 'parts', 'chunk-*.json'))):
    for e in json.load(open(f, encoding='utf-8')):
        p, zh = norm(e.get('pali')), norm(e.get('zh'))
        if zh and (p.lower(), zh) not in TYPOS:
            items.append(dict(pali=p, zh=zh, pages=[int(x) for x in e.get('pages') or [] if str(x).isdigit()],
                              from_book=bool(p)))

# 2. 书中有巴利的中文 → 巴利（唯一时）；其余用补拟表
book_map = defaultdict(set)
for it in items:
    if it['pali']: book_map[it['zh']].add(it['pali'].lower())
fill = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'fill', 'out-*.json'))):
    for e in json.load(open(f, encoding='utf-8')):
        if norm(e.get('pali')): fill[norm(e['zh'])] = norm(e['pali'])
canon = {}  # 小写巴利 → 书中写法
for it in items:
    if it['pali']: canon.setdefault(it['pali'].lower(), it['pali'])
for it in items:
    if it['pali']: continue
    if len(book_map.get(it['zh'], ())) == 1:
        it['pali'] = canon[next(iter(book_map[it['zh']]))]
    elif it['zh'] in fill:
        it['pali'] = fill[it['zh']]

# 3. 按巴利合并；每个巴利只留一个中文
groups = defaultdict(list)
for it in items:
    groups[('p', it['pali'].lower()) if it['pali'] else ('z', it['zh'])].append(it)
rows = []
for (kind, _), es in groups.items():
    pool = [e for e in es if e['from_book']] or es
    zh = Counter(e['zh'] for e in pool).most_common(1)[0][0]
    pali = Counter(e['pali'] for e in pool).most_common(1)[0][0]
    pages = sorted({p for e in es for p in e['pages']})
    rows.append(dict(pali=pali, zh=zh, pages=pages, pali_in_book=bool(pali) and in_book(pali)))

with_p = sorted([r for r in rows if r['pali']], key=lambda r: pali_key(r['pali']))
no_p = sorted([r for r in rows if not r['pali']], key=lambda r: r['zh'])
rows = with_p + no_p

json.dump(rows, open(os.path.join(ROOT, 'glossary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cell = lambda s: str(s).replace('\t', ' ').replace('\n', ' ')
pg = lambda r: ','.join(map(str, r['pages']))
with open(os.path.join(ROOT, 'glossary.tsv'), 'w', encoding='utf-8') as f:
    f.write('pali\tzh\n')  # 供 LLM 翻译参考：只放巴利、中文
    for r in with_p:
        f.write(f"{cell(r['pali'])}\t{cell(r['zh'])}\n")
md = lambda s: cell(s).replace('|', '\\|')
with open(os.path.join(ROOT, 'glossary.md'), 'w', encoding='utf-8') as f:
    f.write('# 术语表（巴利—中文）\n\n来源：《阿毗达摩进阶·第2级》（快乐戒尼 编译，2026）。中文为本书译名，页码为 PDF 页码。\n\n'
            '标 † 的巴利书中未见原样（按中文补拟，或由屈折形式还原），使用前请核对。\n\n'
            f'共 {len(with_p)} 条。\n\n| 巴利 | 中文 | 页码 |\n|---|---|---|\n')
    for r in with_p:
        f.write(f"| {md(r['pali'])}{'' if r['pali_in_book'] else ' †'} | {md(r['zh'])} | {pg(r)} |\n")
    if no_p:
        f.write(f'\n## 未补出巴利（{len(no_p)} 条）\n\n| 中文 | 页码 |\n|---|---|\n')
        for r in no_p:
            f.write(f"| {md(r['zh'])} | {pg(r)} |\n")
print(f'{len(with_p)} with Pali ({sum(not r["pali_in_book"] for r in with_p)} †), {len(no_p)} without')
