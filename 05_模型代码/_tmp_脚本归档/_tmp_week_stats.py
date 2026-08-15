# -*- coding: utf-8 -*-
"""最近一周(8/9-8/15)命中率统计"""
import re, io

src = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data.js", encoding="utf-8").read()

# 8/9-8/14 用批次 stats；8/15 用 results 实算
dates = ["2026-08-07","2026-08-08","2026-08-09","2026-08-10","2026-08-11","2026-08-12","2026-08-13","2026-08-14"]
rows = []
for m in re.finditer(r'"(\d{4}-\d{2}-\d{2})": \{[\s\S]*?stats: \{ dir: "([^"]+)", dirPct: "[^"]+", score: "([^"]+)", scorePct: "[^"]+", ht: "([^"]+)", htPct: "[^"]+"', src):
    if m.group(1) in dates:
        def p(x):
            a, b = x.split("/")
            return int(a), int(b)
        dn, dd = p(m.group(2)); sn, sd = p(m.group(3)); hn, hd = p(m.group(4))
        rows.append((m.group(1), dn, dd, sn, sd, hn, hd))

# 8/15 批 results
idx = src.index('"2026-08-15": {')
seg = src[idx:]
nxt = re.search(r'"2026-\d{2}-\d{2}": \{', seg[10:])
blk = seg[:10 + nxt.start()] if nxt else seg
rev = blk.index("results: [")
ev = blk.index("evidence: [")
res = blk[rev:ev]
dn = sn = hn = n = 0
for r in re.finditer(r'd: "(\w+)", s: "(\w+)", h: "(\w+)"', res):
    n += 1
    if r.group(1) == "ok": dn += 1
    if r.group(2) == "ok": sn += 1
    if r.group(3) == "ok": hn += 1
rows.append(("2026-08-15", dn, n, sn, n, hn, n))

print("批次 | 场次 | 方向 | 比分 | 半全场")
tn = td = ts = th = 0
for date, dn, dd, sn, sd, hn, hd in rows:
    tn += dd; td += dn; ts += sn; th += hn
    print("%s | %d | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %d/%d (%.0f%%)" % (
        date, dd, dn, dd, 100*dn/dd, sn, dd, 100*sn/dd, hn, dd, 100*hn/dd))
print("== 合计(8/9-8/15) ==")
print("场次 %d | 方向 %d/%d (%.1f%%) | 比分 %d/%d (%.1f%%) | 半全场 %d/%d (%.1f%%)" % (
    tn, td, tn, 100*td/tn, ts, tn, 100*ts/tn, th, tn, 100*th/tn))
