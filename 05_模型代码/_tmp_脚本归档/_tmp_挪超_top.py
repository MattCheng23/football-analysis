# -*- coding: utf-8 -*-
"""探查 __NEXT_DATA__ 顶层结构"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def fetch(url):
    r = subprocess.run(["curl.exe", "-s", "-L", "-A", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", url], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

html = fetch("https://www.fotmob.com/leagues/91/overview/eliteserien")
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
if not m:
    print("NO NEXT_DATA"); sys.exit(1)
data = json.loads(m.group(1))
print("top keys:", list(data.keys()))
pp = data.get("props", {}).get("pageProps", {})
print("pageProps type:", type(pp), "len:", len(pp))
if isinstance(pp, dict) and pp:
    for k, v in pp.items():
        print(" ", k, type(v).__name__, (len(v) if hasattr(v, '__len__') else ''))
elif isinstance(pp, list):
    print("list len", len(pp))
    if pp:
        print(json.dumps(pp[0], ensure_ascii=False)[:800])
