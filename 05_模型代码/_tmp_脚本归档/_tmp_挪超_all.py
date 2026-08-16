# -*- coding: utf-8 -*-
"""批量拉取挪超 10 队 teams API：近期赛程（主客/比分/对手）+ 联赛排名"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

TEAMS = {
    8404: "奥勒松Aalesund", 8007: "瓦勒伦加Vålerenga", 9917: "莫尔德Molde", 8608: "特罗姆瑟Tromsø",
    8468: "布兰Brann", 8448: "汉坎HamKam", 8509: "萨普斯堡Sarpsborg", 8609: "桑纳菲Sandefjord",
    8417: "腓特烈Fredrikstad", 8605: "克里斯蒂Kristiansund",
}

def get_team(tid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

all_rows = []
for tid, label in TEAMS.items():
    d = get_team(tid)
    fx = (d.get("fixtures") or {}).get("allFixtures") or {}
    fixtures = fx.get("fixtures") or []
    rows = []
    for f in fixtures:
        st = f.get("status") or {}
        if not st.get("finished") or not st.get("scoreStr"):
            continue
        sc = st["scoreStr"].replace(" ", "")
        if not re.match(r"^\d+-\d+$", sc):
            continue
        h = f.get("home") or {}
        a = f.get("away") or {}
        is_home = str(h.get("id")) == str(tid)
        gf, ga = sc.split("-")
        gf, ga = int(gf), int(ga)
        gf, ga = (gf, ga) if is_home else (ga, gf)
        rows.append({
            "date": (st.get("utcTime") or "")[:10],
            "at": "H" if is_home else "A",
            "opp": a.get("name") if is_home else h.get("name"),
            "gf": gf, "ga": ga,
        })
    rows.sort(key=lambda r: r["date"])
    print(f"\n===== {label} (id={tid}) 近8场 =====")
    for r in rows[-8:]:
        print(f"  {r['date']} {r['at']} vs {r['opp']}: {r['gf']}-{r['ga']}")
    all_rows.append((tid, label, rows))

# 汇总近5场主/客场进失球
print("\n\n===== 近5场主/客场进失球均值（供泊松输入）=====")
for tid, label, rows in all_rows:
    last5 = rows[-5:]
    if not last5:
        print(f"{label}: 无数据")
        continue
    avg_gf = sum(r["gf"] for r in last5) / len(last5)
    avg_ga = sum(r["ga"] for r in last5) / len(last5)
    homes = [r for r in rows if r["at"] == "H"][-5:]
    aways = [r for r in rows if r["at"] == "A"][-5:]
    hs = f"近5主 进{sum(r['gf'] for r in homes)/len(homes):.2f}/失{sum(r['ga'] for r in homes)/len(homes):.2f}" if homes else "无主场"
    aw = f"近5客 进{sum(r['gf'] for r in aways)/len(aways):.2f}/失{sum(r['ga'] for r in aways)/len(aways):.2f}" if aways else "无客场"
    print(f"{label}: 近5总 进{avg_gf:.2f}/失{avg_ga:.2f} | {hs} | {aw}")
