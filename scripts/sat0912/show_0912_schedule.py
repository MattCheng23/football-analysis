# -*- coding: utf-8 -*-
"""show_0912_schedule.py — 列出 0912 批 10 场的编号/时间/对阵/我方判定（用于复盘进度与 handoff）。"""
import io, json, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习\_发布_public\js")
dj = (R / "data.js").read_text(encoding='utf-8')
k = dj.index('"2026-09-12": {')
nxt = re.search(r'\n  "20\d{2}-\d{2}-\d{2}": \{', dj[k + 10:])
blk = dj[k: k + 10 + (nxt.start() if nxt else 60000)]
mi = blk.find('matches: [')
op = blk.index('[', mi)
depth = 0
for j in range(op, len(blk)):
    if blk[j] == '[':
        depth += 1
    elif blk[j] == ']':
        depth -= 1
        if depth == 0:
            break
arr = blk[op + 1:j]
hits = [m.start() for m in re.finditer(r'\{\s*no:\s*"\d{3}"', arr)]
dr = (R / "data-review.js").read_text(encoding='utf-8')
have = set()
if '"2026-09-12": {' in dr:
    seg = dr[dr.index('"2026-09-12": {'):]
    have = set(re.findall(r'\{ no: "(\d{3})"', seg[:seg.find('evidence: [')]))
print(f"{'#':<5}{'时间':<8}{'对阵':<34}{'联赛':<8}{'我方判定':<40}{'状态'}")
for i, st in enumerate(hits):
    e = arr[st: hits[i + 1] if i + 1 < len(hits) else len(arr)]
    g = lambda n: (re.search(n + r':\s*"((?:[^"\\]|\\.)*)"', e) or [None, ''])[1]
    no = re.search(r'no:\s*"(\d{3})"', e).group(1)
    tag = "✅已复盘" if no in have else "待复盘"
    print(f"{no:<5}{g('time'):<8}{(g('home') + ' vs ' + g('away')):<34}{g('league'):<8}"
          f"{(g('dir') + ' ' + g('scores'))[:38]:<40}{tag}")
