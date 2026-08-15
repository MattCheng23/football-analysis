# -*- coding: utf-8 -*-
"""从 data.js 提取联赛级实测数据：命中率/场均进球/平局率/大小球"""
import re, io, json

src = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data.js", encoding="utf-8").read()
keys = [(m.group(1), m.start()) for m in re.finditer(r'^\s*"(\d{4}-\d{2}-\d{2})":\s*\{', src, re.M)]

leagues = {}  # league -> {n, d, s, h, goals, over25, draws, home_win}
for i, (k, s) in enumerate(keys):
    e = keys[i+1][1] if i+1 < len(keys) else len(src)
    blk = src[s:e]
    rev = blk.split("review:")[-1]
    for m in re.finditer(r'\{ no: "[^"]+", teams: "[^"]+", league: "([^"]+)", lg: "[^"]*", score: "([^"]*)"\s*, d: "([^"]+)", s: "([^"]+)", h: "([^"]+)"', rev):
        lg, score, d, s_, h = m.groups()
        L = leagues.setdefault(lg, {"n":0,"d":0,"s":0,"h":0,"goals":0,"over25":0,"draws":0,"hw":0})
        L["n"] += 1
        if d == "ok": L["d"] += 1
        if s_ == "ok": L["s"] += 1
        if h == "ok": L["h"] += 1
        # 比分解析
        mm = re.search(r'(\d+)-(\d+)', score)
        if mm:
            g1, g2 = int(mm.group(1)), int(mm.group(2))
            L["goals"] += g1 + g2
            if g1 + g2 > 2.5: L["over25"] += 1
            if g1 == g2: L["draws"] += 1
            elif g1 > g2: L["hw"] += 1

print("联赛 | 场次 | 方向% | 比分% | 半全场% | 场均进球 | 大2.5% | 平局% | 主胜%")
out = io.open(r"D:\Cola\足球分析学习\05_模型代码\_tmp_脚本归档\_league_stats_out.txt", "w", encoding="utf-8")
out.write("联赛 | 场次 | 方向% | 比分% | 半全场% | 场均进球 | 大2.5% | 平局% | 主胜%\n")
for lg, L in sorted(leagues.items(), key=lambda x: -x[1]["n"]):
    n = L["n"]
    line = "%s | %d | %.0f%% | %.0f%% | %.0f%% | %.2f | %.0f%% | %.0f%% | %.0f%%" % (
        lg, n, 100*L["d"]/n, 100*L["s"]/n, 100*L["h"]/n, L["goals"]/n,
        100*L["over25"]/n, 100*L["draws"]/n, 100*L["hw"]/n)
    print(line)
    out.write(line + "\n")
out.close()
