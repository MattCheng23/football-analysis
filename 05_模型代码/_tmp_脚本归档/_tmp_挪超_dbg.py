# -*- coding: utf-8 -*-
"""调试 teams API：打印原始返回片段"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

for tid in [4113, 4114, 4115, 8630]:
    r = subprocess.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    raw = r.stdout.decode("utf-8", errors="replace")
    print(f"== id {tid}: len={len(raw)} ==")
    print(raw[:300])
    print()
