# -*- coding: utf-8 -*-
"""extract_versions.py — 从 git 各版本提取 0912 批 30 场票面（机器回源·供赛果对照）"""
import io, json, re, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = r"D:\Cola\足球分析学习"
REVS = [("afa4ca1", "1841 首发（001-010 定稿 + 011-030 首发）"),
        ("c2c2a71", "1900 首轮过审"),
        ("1575797", "1937 四类全覆盖"),
        ("b3acc10", "1957 五维终审"),
        ("62ce0e7", "2121 连续性改判（8 场）"),
        ("26e1751", "2138 五维复核 + 一致性收口（最终·上线）")]
PAT = (r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)", league: "([^"]+)", lg: "[^"]+", '
       r'time: "([^"]+)", dir: "([^"]+)", dc: "[^"]+", scores: "([^"]+)", ht: "([^"]+)", '
       r'ou: "([^"]+)", risk: (\d+),')
out = {}
for rev, label in REVS:
    r = subprocess.run(["git", "show", "%s:_发布_public/js/data.js" % rev], cwd=REPO,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    src = r.stdout
    if not src:
        print("  ❌ %s 取不到" % rev); continue
    si = src.index('"2026-09-12": {')
    se = src.index("/* 红黑总榜", si)
    seg = src[si:se]
    d = {}
    for m in re.finditer(PAT, seg):
        d[m.group(1)] = {"home": m.group(2), "away": m.group(3), "time": m.group(5),
                         "dir": m.group(6), "scores": m.group(7), "ht": m.group(8), "ou": m.group(9)}
    out[rev] = {"label": label, "matches": d, "n": len(d)}
    print("  %s %-34s 场次 %d" % (rev, label, len(d)))
json.dump(out, io.open(r"D:\Cola\_tmp_football\sat0912\versions.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
# 差异摘要：与最终版对比，列出票面不同的场次
fin = out["26e1751"]["matches"]
print("\n各版本 ↔ 最终版票面差异：")
for rev, label in REVS[:-1]:
    diff = [no for no in sorted(fin) if out[rev]["matches"].get(no, {}).get("scores") != fin[no]["scores"]]
    print("  %s: %2d 场 %s" % (rev, len(diff), ",".join(diff)))
print("\n已写 versions.json")
