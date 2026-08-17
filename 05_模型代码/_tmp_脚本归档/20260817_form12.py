# -*- coding: utf-8 -*-
"""12 队近 5 场完整比分（FotMob teamForm 实测，含主客/日期/对手/结果）"""
import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MATCHES = {
    "001": "mon_5147626.json",
    "002": "mon_5107567.json",
    "003": "mon_5836765.json",
    "004": "mon_5868014.json",
    "005": "mon_5887595.json",
    "006": "mon_5103590.json",
}

for no, fn in MATCHES.items():
    d = json.load(open(rf"D:\Cola\_tmp_football\{fn}", encoding='utf-8'))
    tf = d.get('content', {}).get('matchFacts', {}).get('teamForm') or []
    print(f"########## {no} ##########")
    for i, t in enumerate(tf):
        if not isinstance(t, list) or not t:
            continue
        # 队名（isOurTeam）
        t0 = t[0]
        team_name = "?"
        for side in ("home", "away"):
            tm = t0.get(side) or {}
            if tm.get("isOurTeam"):
                team_name = tm.get("name", "?")
                break
        print(f"  【{team_name}】近5场:")
        for m in t[:5]:
            date = (m.get("date") or {}).get("utcTime", "")[:10]
            h = m.get("home") or {}
            a = m.get("away") or {}
            hn, an = h.get("name", "?"), a.get("name", "?")
            sc = m.get("score", "")
            rs = m.get("resultString", "")
            ishome = h.get("isOurTeam")
            print(f"    {date} {'主场' if ishome else '客场'} {hn} {sc} {an} → {rs}")
    print()
