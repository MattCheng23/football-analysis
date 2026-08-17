# -*- coding: utf-8 -*-
"""8月17批 6 场首发核验：方案 F（比赛页 SSR lineup）"""
import json, subprocess, sys, io, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
CACHE = r"D:\Cola\_tmp_football"

MATCHES = {
    "001 赫尔火花vs坦山猫": ("/matches/if-gnistan-vs-ilves/67s812r#5147626", "5147626"),
    "002 赫根vs哈尔姆斯": ("/matches/halmstads-bk-vs-hacken/2bermn#5107567", "5107567"),
    "003 加的夫vs雷克斯": ("/matches/cardiff-city-vs-wrexham/2qgd9a#5836765", "5836765"),
    "004 拉科vs埃尔切": ("/matches/deportivo-coruna-vs-elche/3bp0b9#5868014", "5868014"),
    "005 卡萨皮亚vs本菲卡": ("/matches/benfica-vs-casa-pia-ac/bdprkod#5887595", "5887595"),
    "006 巴西国际vs里莫": ("/matches/remo-vs-internacional/vrfbe#5103590", "5103590"),
}

def fetch(url):
    r = subprocess.run(
        ["curl.exe", "-s", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34",
         "-H", "User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
         f"https://www.fotmob.com{url}"],
        capture_output=True, timeout=60)
    return r.stdout.decode('utf-8', errors='replace')

def extract(html):
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        return None, "no NEXT_DATA"
    d = json.loads(m.group(1))
    lu = d.get("props", {}).get("pageProps", {}).get("content", {}).get("lineup")
    return lu, None

if __name__ == '__main__':
    for label, (page, mid) in MATCHES.items():
        print(f"===== {label} =====")
        html = fetch(page)
        lu, err = extract(html)
        if err or not lu:
            print(f"  {err or 'no lineup'}")
            continue
        lt = lu.get("lineupType", "?")
        print(f"  lineupType: {lt}")
        for side in ("homeTeam", "awayTeam"):
            t = lu.get(side) or {}
            print(f"  {side}: {t.get('name')} {t.get('formation')} 首发{len(t.get('starters') or [])}人")
            for p in (t.get("starters") or []):
                print(f"    {p.get('shirtNumber','?')} {p.get('name')}")
        with open(os.path.join(CACHE, f"mon_lu_{mid}.json"), "w", encoding="utf-8") as f:
            json.dump(lu, f, ensure_ascii=False)
