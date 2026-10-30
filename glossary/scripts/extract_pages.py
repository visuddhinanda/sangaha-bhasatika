"""把 PDF 每页文字导出为 pN.txt（需要 pypdf）。用法: python extract_pages.py 输入.pdf 输出目录"""
import sys, os
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
os.makedirs(sys.argv[2], exist_ok=True)
for i, p in enumerate(r.pages):
    open(os.path.join(sys.argv[2], f'p{i+1:03d}.txt'), 'w', encoding='utf-8').write(p.extract_text() or '')
