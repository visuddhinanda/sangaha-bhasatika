"""把 extract_pages.py 导出的逐页文字清理后合成 markdown，并按章节切成 chunks。用法: python pdf_to_md.py 页面目录 glossary目录"""
import sys,os,re
src,out=sys.argv[1],sys.argv[2]
L='a-zāīūṃṇñṭḍḷṅ'
def page(n):
    t=open(os.path.join(src,f'p{n:03d}.txt'),encoding='utf-8').read()
    t=re.sub(rf'ñ (?=[{L}])','ñ',t)                 # ñ never ends a Pali word
    t=re.sub(rf'(?<=[{L}]) (?=[ṇṃṅ])','',t)          # ṇ ṃ ṅ never begin a Pali word
    lines=[l.rstrip() for l in t.split('\n')]
    # drop running header "第X章 …  N" / bare page number
    while lines and (not lines[0].strip() or re.fullmatch(r'\s*(第.章.*|前言|参考答案)?\s*\d*\s*',lines[0])): lines.pop(0)
    while lines and re.fullmatch(r'\s*(\d+|第.章.*)?\s*',lines[-1]): lines.pop()
    return '\n'.join(lines)
chunks=[  # (id, title, first_pdf_page, last_pdf_page)
 ('01','前言', 5, 12),
 ('02','第四章 心路 · 一、类别列举 / 二、五门心路（上）', 13, 24),
 ('03','第四章 心路 · 二、五门心路（下）/ 三、意门心路', 25, 44),
 ('04','第四章 心路 · 四、安止速行时分', 45, 58),
 ('05','第四章 心路 · 五、彼所缘定律 / 六、速行定律', 59, 73),
 ('06','第四章 心路 · 七、依人分类 / 八、依地分别 / 概述', 74, 90),
 ('07','第五章 离心路 · 一、四地', 91, 110),
 ('08','第五章 离心路 · 二、四结生', 111, 125),
 ('09','第五章 离心路 · 三、四业（上）', 126, 140),
 ('10','第五章 离心路 · 三、四业（下）', 141, 161),
 ('11','第五章 离心路 · 四、死生次第', 162, 183),
 ('12','第六章 色 / 89心分析表 / 参考答案 / 参考资料', 184, 199),
]
full=[]
for cid,title,a,b in chunks:
    body=[f'# {title}\n\n<!-- 《阿毗达摩进阶·第2级》PDF 第 {a}–{b} 页 -->\n']
    for n in range(a,b+1):
        body.append(f'\n<!-- p{n} -->\n\n{page(n)}\n')
    s=''.join(body)
    open(os.path.join(out,'chunks',f'chunk-{cid}.md'),'w',encoding='utf-8').write(s)
    full.append(s); print(cid,a,b,len(s))
open(os.path.join(out,'source','阿毗达摩进阶-第2级.md'),'w',encoding='utf-8').write('\n\n'.join(full))
