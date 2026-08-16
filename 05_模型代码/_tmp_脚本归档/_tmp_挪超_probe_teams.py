# -*- coding: utf-8 -*-
"""探测 FotMob teams API：ID 范围扫描，找挪超队伍并打印关键字段"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

def probe(tid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    try:
        d = json.loads(r.stdout.decode("utf-8", errors="replace"))
    except Exception:
        return None
    if not d:
        return None
    t = d.get("team") or {}
    return t

# 先看一个已知队伍字段结构（博德闪耀 4113 猜测）
for tid in [4113, 4114, 4115]:
    t = probe(tid)
    if t:
        print(f"== {tid} ==")
        print(json.dumps(t, ensure_ascii=False)[:400])
        break
