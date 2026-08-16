# -*- coding: utf-8 -*-
"""解析挪超联赛页积分榜（Googlebot UA）+ 本轮赛程"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def fetch(url):
    r = subprocess.run(["curl.exe", "-s", "-L", "-A", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", url], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

html = fetch("https://www.fotmob.com/leagues/91/overview/eliteserien")
print("html len:", len(html))
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
if not m:
    print("NO NEXT_DATA")
    sys.exit(1)
data = json.loads(m.group(1))
pp = data.get("props", {}).get("pageProps", {})
print("pageProps keys:", list(pp.keys()))
# 常见结构：pageProps.league.table / table
def walk(d, path=""):
    if isinstance(d, dict):
        for k in list(d.keys())[:200]:
            walk(d[k], f"{path}.{k}")
    elif isinstance(d, list):
        pass

# 直接找 table
tbl = None
for key in ("table", "leagueTable", "standings"):
    if key in pp:
        tbl = pp[key]
        print("FOUND", key)
        break
if tbl is None:
    # 深搜
    def find_table(obj):
        if isinstance(obj, dict):
            if "table" in obj and isinstance(obj["table"], list) and obj["table"] and "idx" in obj["table"][0]:
                return obj["table"]
            for v in obj.values():
                r = find_table(v)
                if r: return r
        elif isinstance(obj, list):
            for v in obj:
                r = find_table(v)
                if r: return r
        return None
    tbl = find_table(pp)
    if tbl is None:
        print(json.dumps(pp, ensure_ascii=False)[:3000])
        sys.exit(0)
print(json.dumps(tbl[0], ensure_ascii=False))
for row in tbl:
    name = row.get("name") or row.get("teamName") or ""
    print(f"{row.get('idx')}\t{name}\tP{row.get('played')} W{row.get('wins')} D{row.get('draws')} L{row.get('losses')} 分{row.get('pts')} 进{row.get('scores')} 失{row.get('conceded')}")
