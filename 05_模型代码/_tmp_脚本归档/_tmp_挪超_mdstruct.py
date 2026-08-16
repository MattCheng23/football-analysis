# -*- coding: utf-8 -*-
"""探查 matchDetails 结构：h2h/lineup/prevMatch 等字段"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

def get_match(mid):
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/matchDetails?matchId={mid}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

md = get_match(5104980)
print("top keys:", list(md.keys()))
for k in ("general", "content", "h2h"):
    if k in md:
        v = md[k]
        print(f"--- {k}: type={type(v).__name__}")
        if isinstance(v, dict):
            print("   keys:", list(v.keys()))
# 找 h2h 深层
def deep_find(obj, name, path="", depth=0):
    if depth > 4: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if name.lower() in k.lower():
                print(f"   FOUND {path}.{k}: {json.dumps(v, ensure_ascii=False)[:300]}")
            deep_find(v, name, f"{path}.{k}", depth+1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            deep_find(v, name, f"{path}[{i}]", depth+1)

deep_find(md, "h2h")
deep_find(md, "previousMeetings")
