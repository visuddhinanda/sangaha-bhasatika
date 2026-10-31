---
name: translate-sangaha
description: 把缅文《概要缅疏》(Saṅgaha-bhāsāṭīkā, assets/markdown/saṅgaha-bhāsāṭīkā.md) 逐节翻译成现代汉语简体中文，按 glossary/glossary.tsv 统一术语，佛教术语首次出现时用 () 标注巴利。用户说“翻译概要缅疏”“翻译下一节”“翻译第 N 节”“继续翻译”“检查译文”“合并译文”时使用。
---

# 翻译《概要缅疏》

## 材料

| 路径 | 用途 |
|---|---|
| `assets/markdown/saṅgaha-bhāsāṭīkā.md` | 缅文原文（只读） |
| `glossary/glossary.tsv` | 术语表（`pali`、`zh`），术语译名的首选依据 |
| `translation/zh/terms.tsv` | 术语表里没有、翻译中新定的译名（`pali`、`zh`、节号） |
| `translation/zh/annotated.tsv` | 已经标注过巴利的术语（`pali`、`zh`、节号），用来判断“首次出现” |
| `translation/zh/PP/SS.md` | 每节译文，按原文层级分目录（见下） |

辅助脚本（在仓库根目录运行）：

```bash
S=.claude/skills/translate-sangaha/scripts/sections.py
python3 $S list          # 全部节：节号、行号、字数、块数、是否已译（✓）
python3 $S next          # 下一个未译的节
python3 $S show 06/01    # 某节原文；大节分块，用 show 06/01 K 看第 K 块
python3 $S check 06/01   # 检查译文：段落数、缅文残留、文言虚词
python3 $S assemble      # 合并为 translation/zh/saṅgaha-bhāsāṭīkā.md
```

译文按原文层级切分成文件，节号写作 `PP/SS`：

- 每个 `##` 篇是一个目录 `PP`（01、02……）；`#` 书名为 `00/00`
- 篇目录里 `00.md` 是 `##` 标题及其引言，`01.md`、`02.md`……依次是该篇的各个 `###` 节
- `####` 小节留在所属 `###` 节的文件里，保持 `####`

例：`## စိတ်ပိုင်းဘာသာဋီကာ` → `translation/zh/06/00.md`，其第一个 `###` 节 → `translation/zh/06/01.md`。

## 翻译要求

1. **简体中文，现代汉语。** 不要古汉语，不要半文半白。不用“之、其、乃、则、矣、焉、谓、者、若、此、彼、故”等文言虚词和句式（术语本身含这些字的照用，如“彼所缘”“不来者”）。
2. **术语以 `glossary/glossary.tsv` 为准。** 表里没有的，先查 `translation/zh/terms.tsv`；都没有的，自定译名（与术语表风格一致），登记到 `terms.tsv`，全书统一。
3. **佛教术语在全书第一次出现时标注巴利，用半角 `()` 包裹**：`有分(bhavaṅga)`。之后再出现只写中文。是否第一次以 `annotated.tsv` 为准，标注后立即登记。
4. **忠实完整。** 不漏译、不总结、不发挥。原文一个段落对应译文一个段落；标题保持原有的 `#` 级别（`##`、`###`、`####`）。

## 流程

1. 用户指定节号就译那一节，否则 `next`。按顺序译，不跳节，不并行（首次标注依赖前文）。
2. 读入 `glossary.tsv`、`terms.tsv`、`annotated.tsv`（后两个不存在就建，首行为表头）。
3. `show PP/SS` 读原文，大节逐块读、逐块译，按顺序写入同一个 `translation/zh/PP/SS.md`。
   超大的节可以在块边界切开分次译：先写到 `PP/SS.part.md`，首行写 `<!-- 已译到第 K 块 -->`（每译完一块更新 K），`next` 会提示从第 K+1 块继续。整节译完后删掉首行标记，改名为 `PP/SS.md`。
4. 更新 `annotated.tsv`、`terms.tsv`。
5. `check PP/SS`，⚠ 必须改到通过，ℹ 逐项确认。
6. 向用户汇报：译了哪一节，新定了哪些译名，哪些地方拿不准（附原文行号）。
