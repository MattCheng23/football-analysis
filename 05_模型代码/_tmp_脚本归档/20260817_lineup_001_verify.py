# -*- coding: utf-8 -*-
"""001 Gnistan vs Ilves 正式首发交叉验证：SSR lineup + matchDetails lineup"""
import subprocess, re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
MAS = '9a9a7e262fce7ff04f0de2242aaf5c34'

def curl(url, extra=None):
    args = ['curl.exe', '-s', '-H', 'x-mas: ' + MAS, '-H', 'User-Agent: ' + UA]
    if extra:
        args += extra
    args.append(url)
    r = subprocess.run(args, capture_output=True, timeout=60)
    return r.stdout.decode('utf-8', errors='replace')

# 1) 比赛页 SSR lineup
html = curl('https://www.fotmob.com/matches/if-gnistan-vs-ilves/67s812r#5147626')
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
if m:
    d = json.loads(m.group(1))
    lu = d.get('props', {}).get('pageProps', {}).get('content', {}).get('lineup')
    print('SSR lineupType:', lu.get('lineupType') if lu else None)
    if lu:
        for side in ('homeTeam', 'awayTeam'):
            t = lu.get(side) or {}
            print(f'  {side}: {t.get("name")} {t.get("formation")}')
            for p in (t.get('starters') or []):
                print(f'    {p.get("shirtNumber")} {p.get("name")} {p.get("position") or ""}')
else:
    print('SSR: no NEXT_DATA')

# 2) matchDetails API lineup
api = curl('https://www.fotmob.com/api/data/matchDetails?matchId=5147626')
try:
    j = json.loads(api)
    lu = j.get('content', {}).get('lineup')
    print('API lineupType:', lu.get('lineupType') if lu else None)
    if lu:
        for side in ('homeTeam', 'awayTeam'):
            t = lu.get(side) or {}
            print(f'  {side}: {t.get("name")} {t.get("formation")}')
            for p in (t.get('starters') or []):
                print(f'    {p.get("shirtNumber")} {p.get("name")} {p.get("position") or ""}')
    else:
        print('API: no lineup (coverage lower)')
except Exception as e:
    print('API err:', e, api[:200])
