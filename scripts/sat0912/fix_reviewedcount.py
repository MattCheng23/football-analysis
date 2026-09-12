# -*- coding: utf-8 -*-
"""fix_reviewedcount.py — 机器回源校正 reviewedCount = 0912 块 results 实际条目数（防漂移/防 0）"""
import io, re, shutil, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习")
JS = R / "_发布_public" / "js"
BAK = R / "_backup" / "auto_bak"
TS = time.strftime("%Y%m%d_%H%M%S")
dr = (JS / "data-review.js").read_text(encoding="utf-8")
i = dr.index('"2026-09-12": {')
nx = re.search(r'\n  "2026-\d\d-\d\d": \{', dr[i + 10:])
seg = dr[i:(i + 10 + nx.start()) if nx else len(dr)]
# 直接数 results 段里的 score 字段（results 在 evidence 之前）
res_seg = seg[:seg.index("evidence: [")] if "evidence: [" in seg else seg
nos = re.findall(r'no: "(\d+)", teams: "[^"]*"', res_seg)
print("0912 results 条目：%d 场 %s" % (len(nos), ",".join(sorted(set(nos)))))
print("片段样例：", res_seg[:180].replace("\n", " "))
dj_path = JS / "data.js"
dj = dj_path.read_text(encoding="utf-8")
shutil.copy2(dj_path, BAK / ("data.js_%s_prerevcnt.bak" % TS))
j = dj.index('"2026-09-12": {')
m = re.search(r"reviewedCount: (\d+),", dj[j:])
old = int(m.group(1))
new = len(set(nos))
dj = dj[:j + m.start()] + ("reviewedCount: %d," % new) + dj[j + m.end():]
dj_path.write_text(dj, encoding="utf-8", newline="\n")
print("reviewedCount %d → %d" % (old, new))
# 校验 reviewed 标志
mm = re.search(r"reviewed: (true|false),", dj[j:])
print("reviewed 标志 =", mm.group(1) if mm else "未找到")
