"""《概要缅疏》翻译辅助脚本。

用法（在仓库根目录运行）：
  python3 .claude/skills/translate-sangaha/scripts/sections.py list            # 列出全部章节及翻译状态
  python3 .claude/skills/translate-sangaha/scripts/sections.py next            # 下一个未翻译的节
  python3 .claude/skills/translate-sangaha/scripts/sections.py show ID [K]     # 显示某节原文（大节分块，K 为块号）
  python3 .claude/skills/translate-sangaha/scripts/sections.py check ID        # 检查某节译文（段落数、缅文残留、文言虚词）
  python3 .claude/skills/translate-sangaha/scripts/sections.py assemble        # 合并全部译文为一个文件

节的划分保持原文层级：
  - 每个 `##` 篇是一个目录 PP（01、02……；`#` 书名及其前的内容为 00）
  - 篇目录里 00.md 是 `##` 标题及其引言，01.md、02.md……依次是该篇的各个 `###` 节
  - `####` 小节留在所属 `###` 节的文件里
节号 ID 写作 PP/SS，如 07/01。译文：translation/zh/PP/SS.md
"""
import os, re, sys

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'assets', 'markdown', 'saṅgaha-bhāsāṭīkā.md')
OUT = os.path.join(ROOT, 'translation', 'zh')
PART_CHARS = 6000          # 每块大约字数（缅文字符）
HEADING = re.compile(r'^#{1,3} ')    # 切分文件的标题级别；#### 留在所属文件内
MYANMAR = re.compile(r'[က-႟ꩠ-ꩿ]')
# 原样保留、不译的行（维基文库来源链接、时间戳、占位符、分隔线）
PASSTHRU = re.compile(r'(<a href|wikisource|^YZYZ|^---\s*$|\(\+0630\))')
CLASSICAL = ['之', '其', '乃', '则', '矣', '焉', '於', '曰', '谓', '故', '亦', '皆', '若', '此', '彼', '者']


def sections():
    lines = open(SRC, encoding='utf-8').read().split('\n')
    starts = [i for i, l in enumerate(lines) if HEADING.match(l)]
    out, pp, ss = [], 0, 0
    for n, s in enumerate(starts):
        e = starts[n + 1] if n + 1 < len(starts) else len(lines)
        level = len(lines[s].split(' ')[0])
        if level == 2: pp, ss = pp + 1, 0
        elif level == 3: ss += 1
        out.append(dict(id=f'{pp:02d}/{ss:02d}', title=lines[s], start=s + 1, end=e, lines=lines[s:e]))
    return out


def paragraphs(sec):
    return [l for l in sec['lines'] if l.strip()]


def parts(sec):
    """按段落切块，每块不超过 PART_CHARS（单段超长时单独成块）。"""
    chunks, cur, size = [], [], 0
    for l in sec['lines']:
        if cur and size + len(l) > PART_CHARS and l.strip():
            chunks.append(cur); cur, size = [], 0
        cur.append(l); size += len(l)
    if cur: chunks.append(cur)
    return chunks


def norm_id(x):
    m = re.fullmatch(r'(\d+)/(\d+)', x.strip())
    if not m: sys.exit(f'节号应写作 PP/SS，如 07/01：{x}')
    return f'{int(m[1]):02d}/{int(m[2]):02d}'


def out_path(sid):
    return os.path.join(OUT, *sid.split('/')) + '.md'


def get(sid):
    sid = norm_id(sid)
    for s in sections():
        if s['id'] == sid: return s
    sys.exit(f'没有这一节：{sid}（用 list 查看全部节号）')


def cmd_list():
    for s in sections():
        done = '✓' if os.path.exists(out_path(s['id'])) else ' '
        size = sum(len(l) for l in s['lines'])
        print(f"{done} {s['id']}  L{s['start']}-{s['end']}  {size:>6}字  {len(parts(s))}块  {s['title']}")


def cmd_next():
    for s in sections():
        if not os.path.exists(out_path(s['id'])):
            print(f"{s['id']}  {s['title']}  ({len(parts(s))} 块)"); return
    print('全部章节已翻译')


def cmd_show(sid, k=None):
    s = get(sid); n = s['id']; ps = parts(s)
    if k is None and len(ps) > 1:
        print(f"<!-- 第 {n} 节共 {len(ps)} 块，请用 show {n} 1 … show {n} {len(ps)} 逐块查看 -->")
        k = 1
    k = k or 1
    if not 1 <= k <= len(ps): sys.exit(f'块号应在 1–{len(ps)} 之间')
    first = s['start'] + sum(len(p) for p in ps[:k - 1])
    print(f"<!-- 第 {n} 节「{s['title']}」 第 {k}/{len(ps)} 块，原文自第 {first} 行起 -->")
    print('\n'.join(ps[k - 1]))


def cmd_check(sid):
    s = get(sid); p = out_path(s['id'])
    if not os.path.exists(p): sys.exit(f'没有译文：{p}')
    tgt = open(p, encoding='utf-8').read().split('\n')
    src_paras, tgt_paras = paragraphs(s), [l for l in tgt if l.strip()]
    problems = 0
    if len(src_paras) != len(tgt_paras):
        problems += 1
        print(f'⚠ 段落数不一致：原文 {len(src_paras)} 段，译文 {len(tgt_paras)} 段（应一段对一段）')
    level = s['title'].split(' ')[0]
    if not tgt_paras or tgt_paras[0].split(' ')[0] != level:
        problems += 1; print(f'⚠ 译文第一行应为与原文同级的标题（{level}）')
    left = [i for i, l in enumerate(tgt, 1) if not PASSTHRU.search(l) and MYANMAR.search(l)]
    if left:
        print(f'ℹ 含缅文字母的行（确认是有意保留，而不是漏译）：{" ".join(map(str, left[:30]))}')
    text = '\n'.join(l for l in tgt if not PASSTHRU.search(l))
    text_zh = re.sub(r'\([^)]*\)|\*\*[^*]*[A-Za-zāīūṃṇñṭḍḷṅ][^*]*\*\*', '', text)  # 去掉巴利，只看中文
    hits = {c: text_zh.count(c) for c in CLASSICAL if text_zh.count(c)}
    if hits:
        print('ℹ 文言虚词出现次数（逐个确认是否必要；术语中的如“彼所缘”“不来者”无妨）：',
              '，'.join(f'{c}×{v}' for c, v in sorted(hits.items(), key=lambda x: -x[1])))
    print('✓ 结构检查通过' if not problems else f'共 {problems} 处需要处理')


def cmd_assemble():
    secs = sections(); body = []; missing = []
    for s in secs:
        p = out_path(s['id'])
        if os.path.exists(p):
            body.append(open(p, encoding='utf-8').read().rstrip('\n'))
        else:
            missing.append(s['id'])
    dst = os.path.join(OUT, 'saṅgaha-bhāsāṭīkā.md')
    open(dst, 'w', encoding='utf-8').write('\n\n'.join(body) + '\n')
    print(f'已合并 {len(body)}/{len(secs)} 节 → {dst}')
    if missing: print('未翻译：', ' '.join(missing))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'list': cmd_list()
    elif a[0] == 'next': cmd_next()
    elif a[0] == 'show': cmd_show(a[1], int(a[2]) if len(a) > 2 else None)
    elif a[0] == 'check': cmd_check(a[1])
    elif a[0] == 'assemble': cmd_assemble()
    else: sys.exit(__doc__)
