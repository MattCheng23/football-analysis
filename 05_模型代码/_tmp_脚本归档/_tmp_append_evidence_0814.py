# -*- coding: utf-8 -*-
"""追加合并 evidence_2026-08-14.md 到已有 evidence 数组（8/14 批已有 6 条）"""
import re, io

data_path = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
md_path = r"D:\Cola\足球分析学习\05_模型代码\_tmp_脚本归档\evidence_2026-08-14.md"
src = io.open(data_path, encoding="utf-8").read()
md = io.open(md_path, encoding="utf-8").read()

lines = []
for line in md.splitlines():
    s = line.strip()
    if s.startswith("{ no:") and (s.endswith("}") or s.endswith("},")):
        lines.append(s.rstrip(","))
print("新增 evidence 行数:", len(lines))

m = re.search(r'^\s*"2026-08-14": \{', src, re.M)
blk_start = m.start()
nxt = re.search(r'^\s*"\d{4}-\d{2}-\d{2}": \{', src[m.start()+12:], re.M)
blk_end = m.start() + 12 + (nxt.start() if nxt else len(src) - m.start() - 12)
blk = src[blk_start:blk_end]

# 定位 evidence 数组：evidence: [ ... ] 或 evidence: []（可能带换行多行）
m_ev = re.search(r'evidence:\s*\[(.*?)\]', blk, re.S)
if not m_ev:
    print("!! 未找到 evidence 数组")
else:
    inner = m_ev.group(1)
    if inner.strip():
        # 已有内容：追加（去掉尾部换行/缩进后接新行）
        new_inner = inner.rstrip() + ",\n        " + ",\n        ".join(lines) + "\n      "
    else:
        new_inner = "\n        " + ",\n        ".join(lines) + "\n      "
    new_blk = blk[:m_ev.start()] + "evidence: [" + new_inner + "]" + blk[m_ev.end():]
    src = src[:blk_start] + new_blk + src[blk_end:]
    io.open(data_path, "w", encoding="utf-8").write(src)
    print("8/14 evidence 追加完成")
