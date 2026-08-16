# -*- coding: utf-8 -*-
"""提取 5 场 H2H 完整列表 + 排名表"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

PAIRS = [
    (5104980, "奥勒松 vs 瓦勒伦加"),
    (5104978, "莫尔德 vs 特罗姆瑟"),
    (5104981, "布兰 vs 汉坎"),
    (5104983, "萨普斯堡 vs 桑纳菲"),
    (5104984, "腓特烈 vs 克里斯蒂"),
]

def get_match(mid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/matchDetails?matchId={mid}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

for mid, label in PAIRS:
    md = get_match(mid)
    content = md.get("content") or {}
    h2h = content.get("h2h") or {}
    print(f"\n===== {label} =====")
    print("summary:", h2h.get("summary"))
    matches = h2h.get("matches") or []
    for m in matches:
        t = (m.get("time") or {}).get("utcTime", "")[:10]
        h = (m.get("home") or {}).get("name", "?")
        a = (m.get("away") or {}).get("name", "?")
        sc = ((m.get("status") or {}).get("scoreStr")) or ""
        lg = ((m.get("league") or {}).get("name")) or ""
        print(f"  {t} {h} {sc} {a} [{lg}]")
