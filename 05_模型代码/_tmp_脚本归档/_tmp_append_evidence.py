# -*- coding: utf-8 -*-
"""通用追加合并：按 no 去重，把 md 的 evidence 行追加到 data.js 对应批次"""
import re, io, sys

data_path = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
md_path = sys.argv[1]
key = sys.argv[2]
src = io.open(data_path, encoding="utf-8").read()
md = io.open(md_path, encoding="utf-8").read()

lines = []
for line in md.splitlines():
    s = line.strip()
    if s.startswith("{ no:") and (s.endswith("}") or s.endswith("},")):
        lines.append(s.rstrip(","))
print("md evidence 行数:", len(lines))

m = re.search(r'^\s*"%s": \{' % key, src, re.M)
blk_start = m.start()
nxt = re.search(r'^\s*"\d{4}-\d{2}-\d{2}": \{', src[m.start()+12:], re.M)
blk_end = m.start() + 12 + (nxt.start() if nxt else len(src) - m.start() - 12)
blk = src[blk_start:blk_end]

m_ev = re.search(r'evidence:\s*\[(.*?)\]', blk, re.S)
inner = m_ev.group(1)
# 已有 no 集合
existing = set(re.findall(r'no: "(\d+)"', inner))
new_lines = [l for l in lines if re.search(r'no: "(\d+)"', l).group(1) not in existing]
print("待追加:", len(new_lines), "跳过重复:", len(lines) - len(new_lines))
if new_lines:
    if inner.strip():
        new_inner = inner.rstrip() + ",\n        " + ",\n        ".join(new_lines) + "\n      "
    else:
        new_inner = "\n        " + ",\n        ".join(new_lines) + "\n      "
    new_blk = blk[:m_ev.start()] + "evidence: [" + new_inner + "]" + blk[m_ev.end():]
    src = src[:blk_start] + new_blk + src[blk_end:]
    io.open(data_path, "w", encoding="utf-8").write(src)
    print("%s evidence 追加完成" % key)
else:
    print("%s 无新增" % key)
