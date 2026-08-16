# -*- coding: utf-8 -*-
"""探查 league results 页 __NEXT_DATA__ 结构"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

URL = "https://www.fotmob.com/leagues/91/results/eliteserien?season=2026"
HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"]
r = subprocess.run(HEAD + [URL], capture_output=True)
html = r.stdout.decode("utf-8", errors="replace")
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
if not m:
    print("NO NEXT_DATA"); sys.exit(1)
data = json.loads(m.group(1))
pp = data.get("props", {}).get("pageProps", {})
print("pageProps keys:", list(pp.keys()))
for k, v in pp.items():
    if isinstance(v, dict):
        print(f"  {k}: dict keys={list(v.keys())[:15]}")
    elif isinstance(v, list):
        print(f"  {k}: list len={len(v)}")
    else:
        print(f"  {k}: {type(v).__name__} = {str(v)[:80]}")
