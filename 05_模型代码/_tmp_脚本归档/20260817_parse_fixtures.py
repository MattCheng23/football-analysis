# -*- coding: utf-8 -*-
"""解析 8/17 批 6 场 matchId/pageUrl（UTC 2026-08-17 比赛）"""
import json, io

out = io.StringIO()
files = {
    "001_芬超": ("finsu", ["Ilves", "Ilves/2"]),
    "002_瑞超": ("ruichao", ["Halmstad", "Häcken", "BK Häcken", "Halmstads"]),
    "003_英冠": ("yingguan", ["Cardiff", "Wrexham"]),
    "004_西甲": ("xijia", ["Deportivo", "Elche", "La Coruña", "Coruña"]),
    "005_葡超": ("puchao", ["Casa Pia", "Benfica"]),
    "006_巴甲": ("bajia", ["Internacional", "Remo", "RS"]),
}
base = r"D:\Cola\_tmp_football\fixtures_20260817"
for label, (name, keys) in files.items():
    with open(f"{base}\\{name}.json", encoding="utf-8") as f:
        j = json.load(f)
    matches = j.get("fixtures", {}).get("allMatches", []) or []
    seen = {}
    for m in matches:
        seen[m.get("id")] = m
    out.write(f"\n===== {label}（UTC 8/17 共 {len(seen)} 场全赛季，筛出当日）=====\n")
    day = []
    for m in seen.values():
        st = m.get("status", {})
        utc = st.get("utcTime", "")
        if utc.startswith("2026-08-17"):
            day.append(m)
    for m in sorted(day, key=lambda x: x.get("status", {}).get("utcTime", "")):
        home = m.get("home", {}).get("name", "?")
        away = m.get("away", {}).get("name", "?")
        utc = m.get("status", {}).get("utcTime", "?")
        fin = m.get("status", {}).get("finished", False)
        mark = " <== 候选" if any(k.lower() in (home + away).lower() for k in keys) else ""
        out.write(f"  {utc} {home} vs {away} id={m.get('id')} fin={fin} {m.get('pageUrl')}{mark}\n")
    if not day:
        out.write("  （当日无比赛）\n")

with open(r"D:\Cola\_tmp_football\fixtures_parse.txt", "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print(out.getvalue())
