# -*- coding: utf-8 -*-
"""从已知队伍 teams API 扩散挪超全部队伍 ID + 打印队伍赛程"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

def get_team(tid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

d = get_team(9917)
details = d.get("details") or {}
print("team:", details.get("name"), details.get("id"))
fx = (d.get("fixtures") or {}).get("allFixtures") or {}
print("keys:", list(fx.keys()))
# 打印赛程全部（含对手 id）
fixtures = fx.get("fixtures") or []
print(f"fixtures count: {len(fixtures)}")
# 收集所有对手
opps = {}
for f in fixtures:
    h = f.get("home") or {}
    a = f.get("away") or {}
    for side in (h, a):
        if side.get("id") and side.get("name"):
            opps[side["id"]] = side["name"]
for tid, name in sorted(opps.items(), key=lambda kv: kv[1]):
    print(f"{tid}\t{name}")
