# -*- coding: utf-8 -*-
"""dedupe_0912.py — 去重 0912 块 results/evidence（按 no 保留首次出现）"""
import io, re, shutil, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习")
JS = R / "_发布_public" / "js"
BAK = R / "_backup" / "auto_bak"
TS = time.strftime("%Y%m%d_%H%M%S")
p = JS / "data-review.js"
dr = p.read_text(encoding="utf-8")
shutil.copy2(p, BAK / ("data-review.js_%s_prededupe.bak" % TS))
i = dr.index('"2026-09-12": {')
nx = re.search(r'\n  "2026-\d\d-\d\d": \{', dr[i + 10:])
end = (i + 10 + nx.start()) if nx else len(dr)
seg = dr[i:end]
res_head = seg.index("results: [") + len("results: [")
evi_head = seg.index("evidence: [") + len("evidence: [")
avoid = seg.index("avoidHigh:")

def dedupe(block):
    """block：条目文本（逗号分隔的 {...}）。返回（去重后文本, 数量）"""
    entries = re.findall(r'\{\s*no: "\d+"[\s\S]*?"\s*\}', block)
    seen, keep = set(), []
    for e in entries:
        no = re.search(r'no: "(\d+)"', e).group(1)
        if no in seen:
            continue
        seen.add(no)
        keep.append(e.rstrip())
    return ",\n".join("        " + k.strip() for k in keep), len(keep)

res_block = seg[res_head:seg.index("],\n      evidence: [")]
evi_block = seg[evi_head:avoid].rsplit("]", 1)[0]
new_res, n1 = dedupe(res_block)
new_evi, n2 = dedupe(evi_block)
print("results 去重后 %d 条｜evidence 去重后 %d 条" % (n1, n2))
assert n1 == n2 == 11, "去重后数量异常（期望 11）"

new_seg = (seg[:res_head] + "\n" + new_res + "\n      ],\n      evidence: [\n" + new_evi +
           "\n      ],\n      " + seg[avoid:])
dr2 = dr[:i] + new_seg + dr[end:]
p.write_text(dr2, encoding="utf-8", newline="\n")

# reviewedCount 机器回源
dp = JS / "data.js"
dj = dp.read_text(encoding="utf-8")
shutil.copy2(dp, BAK / ("data.js_%s_prededupe.bak" % TS))
j = dj.index('"2026-09-12": {')
m = re.search(r"reviewedCount: (\d+),", dj[j:])
dj = dj[:j + m.start()] + ("reviewedCount: %d," % n1) + dj[j + m.end():]
dp.write_text(dj, encoding="utf-8", newline="\n")
print("reviewedCount →", n1)
