# glossary — 术语参考

从《阿毗达摩进阶·第2级（心路 离心路 色）》（快乐戒尼 编译，2026，`assets/ref/阿毗达摩进阶-第2级.pdf`）提取的巴利—中文术语表，供翻译《概要缅疏》(Saṅgaha-bhāsāṭīkā) 时参考本书的中文译名。

## 文件

| 文件 | 内容 |
|---|---|
| `glossary.tsv` | **给 LLM 翻译用的参考**：只有 `pali`、`zh` 两栏，每个巴利词一个本书译名 |
| `glossary.md` | 同上加页码（PDF 页码），供人工查对；标 † 的巴利书中未见原样 |
| `glossary.json` | 同上，含 `pages`、`pali_in_book` |
| `source/阿毗达摩进阶-第2级.md` | PDF 全文转出的 markdown（`<!-- pN -->` 为 PDF 页码） |
| `chunks/chunk-NN.md` | 按章节切分的 12 块，供逐块提取 |
| `parts/chunk-NN.json` | 每块提取出的术语（合并前的原始结果） |
| `fill/batch-N.json`, `fill/out-N.json` | 书中未给巴利的中文术语，及按中文补拟的巴利（含 `confidence`） |
| `scripts/` | 转换与合并脚本 |

## 规则

- 中文只取本书的译名。同一巴利有多个译名时，取书中给出该巴利处的译名，其次取出现最多的。
- 书中未给巴利的术语，按中文补拟巴利（`fill/out-N.json`，低置信度的可在其中查到），合并后标 †。
- 由屈折形式还原的词干在书中也找不到原样，同样标 †。
- 书中个别笔误照录，如“利养(lobha)”（疑为 lābha）。

## 重新生成

```bash
python scripts/extract_pages.py ../assets/ref/阿毗达摩进阶-第2级.pdf /tmp/pages   # 需要 pypdf
python scripts/pdf_to_md.py /tmp/pages .
# 逐块提取术语到 parts/chunk-NN.json，补拟巴利到 fill/out-N.json（由 agent 完成）
python scripts/merge.py
```
