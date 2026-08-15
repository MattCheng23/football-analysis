# -*- coding: utf-8 -*-
"""按批次统计命中率分层（7月旧模型 vs 8月V10+）"""
import re, io

src = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data.js", encoding="utf-8").read()

batches = {}
for m in re.finditer(r'"(\d{4}-\d{2}-\d{2})": \{[\s\S]*?stats: \{ dir: "([^"]+)", dirPct: "[^"]+", score: "([^"]+)", scorePct: "[^"]+", ht: "([^"]+)", htPct: "[^"]+"', src):
    date, d, s, h = m.group(1), m.group(2), m.group(3), m.group(4)
    if "-" in (d, s, h):
        continue
    def parts(x):
        a, b = x.split("/")
        return int(a), int(b)
    dn, dd = parts(d)
    sn, sd = parts(s)
    hn, hd = parts(h)
    batches[date] = (dn, dd, sn, sd, hn, hd)

# 按日期段汇总
seg = {"7月(V8-V9旧模型)": [], "8月(V10+)": []}
for date in sorted(batches):
    key = "7月(V8-V9旧模型)" if date < "2026-08-01" else "8月(V10+)"
    seg[key].append((date, batches[date]))

print("分段 | 场次 | 方向 | 比分 | 半全场")
alln = alld = alls = allh = 0
for label, items in seg.items():
    n = d = s = h = 0
    for date, (dn, dd, sn, sd, hn, hd) in items:
        n += dd; d += dn; s += sn; h += hn
    alln += n; alld += d; alls += s; allh += h
    print("%s | %d | %d/%d (%.1f%%) | %d/%d (%.1f%%) | %d/%d (%.1f%%)" % (
        label, n, d, n, 100*d/n, s, n, 100*s/n, h, n, 100*h/n))
print("合计(有stats批次) | %d | %d/%d (%.1f%%) | %d/%d (%.1f%%) | %d/%d (%.1f%%)" % (
    alln, alld, alln, 100*alld/alln, alls, alln, 100*alls/alln, allh, alln, 100*allh/alln))

# 逐批次明细（低命中率批次标注）
print("\n== 逐批次（按命中率排序）==")
rows = []
for date, (dn, dd, sn, sd, hn, hd) in batches.items():
    rows.append((date, 100*dn/dd, dn, dd))
for date, pct, dn, dd in sorted(rows, key=lambda x: x[1]):
    print("%s: 方向 %d/%d (%.0f%%)" % (date, dn, dd, pct))
