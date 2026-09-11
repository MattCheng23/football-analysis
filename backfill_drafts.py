# -*- coding: utf-8 -*-
"""backfill_drafts.py — 回填历史批次的初稿快照（可复原者）·2026-09-12
  0911 批 ← HANDOFF_260911.md §一「票面（12 场）」＝v1/17:29 首发值
  0910 批 ← 备份链 data.js._bak_fix0910_135359（13:52 初稿）
"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"D:\Cola\足球分析学习"
DRAFTS = os.path.join(ROOT, "_backup", "drafts")
os.makedirs(DRAFTS, exist_ok=True)

# ---- 0911：HANDOFF 票面表 ----
h = io.open(r"D:\Cola\_tmp_football\fri0911\HANDOFF_260911.md", encoding="utf-8").read()
sec = h[h.index("## 一、票面"):h.index("> 预警卡")]
ms = []
for line in sec.splitlines():
    m = re.match(r"\|\s*(\d{3})\s*\|\s*([\d:]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
    if m:
        tm = re.match(r"(.+?)\s*vs\s*(.+?)（(.+?)）", m.group(3))
        ms.append(dict(no=m.group(1), time=m.group(2),
                       home=(tm.group(1).strip() if tm else m.group(3).strip()),
                       away=(tm.group(2).strip() if tm else ""),
                       league=(tm.group(3).strip() if tm else ""),
                       dir=m.group(4).strip().replace(" B", "").replace("·单选", ""), 
                       scores=m.group(5).strip(), ht=m.group(6).strip(),
                       ou=m.group(7).strip().replace("**", "")))
d911 = dict(key="2026-09-11", title="周五批 12 场（V11.46·首战）", taken="2026-09-11 17:29（v1 首发·回填）",
            matches=ms, warn={}, backfill="HANDOFF_260911.md §一票面表（v1/17:29 首发值）")
io.open(os.path.join(DRAFTS, "2026-09-11.draft.json"), "w", encoding="utf-8").write(
    json.dumps(d911, ensure_ascii=False, indent=1))
print("✅ 0911 回填快照：%d 场" % len(ms))

# ---- 0910：备份链初稿 ----
src = io.open(r"D:\Cola\足球分析学习\_backup\发布目录归档_20260912\data.js._bak_fix0910_135359",
              encoding="utf-8", errors="replace").read()
i = src.index('"2026-09-10": {')
m2 = re.search(r'\n  "\d{4}-\d{2}-\d{2}": \{', src[i + 10:])
blk = src[i:i + 10 + m2.start()] if m2 else src[i:i + 200000]
ms2 = []
for m in re.finditer(r'no: "(\d{3})"', blk):
    no = m.group(1)
    if any(x["no"] == no for x in ms2):
        continue
    b = blk[m.start():m.start() + 1600]
    f = {}
    for k in ("home", "away", "league", "lg", "time", "dir", "scores", "ht", "ou"):
        mm = re.search(r'%s: "([^"]*)"' % k, b)
        if mm:
            f[k] = mm.group(1)
    if "dir" in f and "scores" in f and "ht" in f and "ou" in f:
        ms2.append(dict(no=no, **f))
d910 = dict(key="2026-09-10", title="周四批 7 场（V11.44·首战）", taken="2026-09-10 13:52（初稿·回填）",
            matches=ms2, warn={}, backfill="备份链 data.js._bak_fix0910_135359")
io.open(os.path.join(DRAFTS, "2026-09-10.draft.json"), "w", encoding="utf-8").write(
    json.dumps(d910, ensure_ascii=False, indent=1))
print("✅ 0910 回填快照：%d 场" % len(ms2))
