# -*- coding: utf-8 -*-
"""提取挪超 2026 赛季全部已赛赛果 + 队伍 ID 映射（方案 A：league results Googlebot UA）"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

URL = "https://www.fotmob.com/leagues/91/results/eliteserien?season=2026"
HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"]

r = subprocess.run(HEAD + [URL], capture_output=True)
html = r.stdout.decode("utf-8", errors="replace")
print(f"html len: {len(html)}")
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
if not m:
    print("NO NEXT_DATA"); sys.exit(1)
data = json.loads(m.group(1))
allm = data["props"]["pageProps"]["fixtures"]["allMatches"]
print(f"total matches: {len(allm)}")

# 队伍 ID 映射
teams = {}
for f in allm:
    h = f.get("home") or {}
    a = f.get("away") or {}
    teams[h["id"]] = h["name"]
    teams[a["id"]] = a["name"]

targets = ["奥勒松", "瓦勒伦加", "莫尔德", "特罗姆瑟", "布兰", "汉坎", "萨普斯堡", "桑纳菲", "腓特烈", "克里斯蒂"]
aliases = {
    "奥勒松": ["Aalesund", "AaFK"], "瓦勒伦加": ["Valerenga", "Valerenga"], "莫尔德": ["Molde"],
    "特罗姆瑟": ["Tromso"], "布兰": ["Brann"], "汉坎": ["HamKam", "Ham-Kam"], "萨普斯堡": ["Sarpsborg"],
    "桑纳菲": ["Sandefjord"], "腓特烈": ["Fredrikstad"], "克里斯蒂": ["Kristiansund"],
}
print("\n== 队伍 ID ==")
for tid, name in sorted(teams.items(), key=lambda kv: kv[1]):
    mark = ""
    for cn, als in aliases.items():
        if any(al.lower() in name.lower() for al in als):
            mark = f"  <- {cn}"
    print(f"{tid}\t{name}{mark}")

# 打印全部已赛场次（倒序，含比分与 matchId）
print("\n== 已赛场次（最近 30 场）==")
done = [f for f in allm if (f.get("status") or {}).get("finished")]
done.sort(key=lambda f: (f.get("status") or {}).get("utcTime") or "")
for f in done[-30:]:
    st = f["status"]
    pg = f.get("pageUrl") or ""
    mid = pg.rsplit("#", 1)[-1] if "#" in pg else "?"
    print(f"{st.get('utcTime','')[:16]}  {f['home']['name']} {st.get('scoreStr','?')} {f['away']['name']}  matchId={mid}")

# 找目标 5 场的下一轮对阵（未赛）
print("\n== 未赛场次（近期 15 场）==")
todo = [f for f in allm if not (f.get("status") or {}).get("finished")]
todo.sort(key=lambda f: (f.get("status") or {}).get("utcTime") or "")
for f in todo[:15]:
    st = f["status"]
    pg = f.get("pageUrl") or ""
    mid = pg.rsplit("#", 1)[-1] if "#" in pg else "?"
    print(f"{st.get('utcTime','')[:16]}  {f['home']['name']} vs {f['away']['name']}  matchId={mid}")
