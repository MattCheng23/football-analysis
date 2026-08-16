# -*- coding: utf-8 -*-
"""提取 5 场目标未赛比赛的 matchId + 两队 H2H（matchDetails API）"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

PAIRS = [
    (8404, 8007, "奥勒松 vs 瓦勒伦加"),
    (9917, 8608, "莫尔德 vs 特罗姆瑟"),
    (8468, 8448, "布兰 vs 汉坎"),
    (8509, 8609, "萨普斯堡 vs 桑纳菲"),
    (8417, 8605, "腓特烈 vs 克里斯蒂"),
]

def get_team(tid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

# 找每场 matchId：从主队赛程找未赛 vs 客队
for hid, aid, label in PAIRS:
    d = get_team(hid)
    fx = (d.get("fixtures") or {}).get("allFixtures") or {}
    fixtures = fx.get("fixtures") or []
    target = None
    for f in fixtures:
        st = f.get("status") or {}
        h = f.get("home") or {}
        a = f.get("away") or {}
        if str(h.get("id")) == str(hid) and str(a.get("id")) == str(aid) and not st.get("finished"):
            target = f
            break
    if not target:
        print(f"{label}: 未找到未赛比赛")
        continue
    pg = target.get("pageUrl") or ""
    mid = pg.rsplit("#", 1)[-1] if "#" in pg else "?"
    utc = (target.get("status") or {}).get("utcTime") or ""
    print(f"{label}: matchId={mid} utc={utc}")
    # 拉 H2H
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/matchDetails?matchId={mid}"], capture_output=True)
    md = json.loads(r.stdout.decode("utf-8", errors="replace"))
    h2h = md.get("h2h") or {}
    prev = h2h.get("previousMeetings") or h2h.get("previousMeetingsList") or []
    print(f"   H2H 结构 keys: {list(h2h.keys())}")
    for m in (prev if isinstance(prev, list) else []):
        st = m.get("status") or {}
        h = m.get("home") or {}
        a = m.get("away") or {}
        print(f"   {st.get('utcTime','')[:10]} {h.get('name')} {st.get('scoreStr','?')} {a.get('name')}")
