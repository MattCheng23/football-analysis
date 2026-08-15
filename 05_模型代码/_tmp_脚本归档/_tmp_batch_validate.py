# -*- coding: utf-8 -*-
"""data.js 批次校验 + GLOBAL_STATS 重算"""
import re, io, sys, json

path = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
with io.open(path, "r", encoding="utf-8") as f:
    src = f.read()

# 1) 提取批次块（key + 到下一个 key 或文件结尾）
key_pat = re.compile(r'^\s*"(\d{4}-\d{2}-\d{2})":\s*\{', re.M)
keys = [(m.group(1), m.start()) for m in key_pat.finditer(src)]
blocks = []
for i, (k, s) in enumerate(keys):
    e = keys[i+1][1] if i+1 < len(keys) else len(src)
    blocks.append((k, src[s:e]))

print("=== 批次清单 (%d 个) ===" % len(blocks))
tot = {"d": 0, "s": 0, "h": 0, "n": 0}
for k, blk in blocks:
    title_m = re.search(r'title:\s*"([^"]*)"', blk)
    stats_m = re.search(r'stats:\s*\{([^}]*)\}', blk)
    res_n = len(re.findall(r'\{ no: "[^"]+", teams:', blk.split("review:")[-1]))
    d_ok = len(re.findall(r'\bd: "ok"', blk.split("review:")[-1]))
    s_ok = len(re.findall(r'\bs: "ok"', blk.split("review:")[-1]))
    h_ok = len(re.findall(r'\bh: "ok"', blk.split("review:")[-1]))
    tot["d"] += d_ok; tot["s"] += s_ok; tot["h"] += h_ok; tot["n"] += res_n
    print("%s | %s | results=%d d=%d s=%d h=%d | stats=%s" % (
        k, (title_m.group(1) if title_m else "?"), res_n, d_ok, s_ok, h_ok,
        stats_m.group(1).strip() if stats_m else "?"))

print("\n=== GLOBAL 汇总 (已确认赛果场次) ===")
print("总场次: %d" % tot["n"])
print("方向: %d/%d = %.1f%%" % (tot["d"], tot["n"], 100.0*tot["d"]/tot["n"] if tot["n"] else 0))
print("比分: %d/%d = %.1f%%" % (tot["s"], tot["n"], 100.0*tot["s"]/tot["n"] if tot["n"] else 0))
print("半全场: %d/%d = %.1f%%" % (tot["h"], tot["n"], 100.0*tot["h"]/tot["n"] if tot["n"] else 0))

# 2) 括号平衡粗查
print("\n=== 括号平衡 ===")
print("{}: %d vs %d %s" % (src.count("{"), src.count("}"), "OK" if src.count("{")==src.count("}") else "MISMATCH"))
print("[]: %d vs %d %s" % (src.count("["), src.count("]"), "OK" if src.count("[")==src.count("]") else "MISMATCH"))
print("(): %d vs %d %s" % (src.count("("), src.count(")"), "OK" if src.count("(")==src.count(")") else "MISMATCH"))

# 3) 重复对阵检测（跨批次同对阵同比分）
print("\n=== 重复场次检测（同对阵同赛果跨批次） ===")
pair = {}
for k, blk in blocks:
    for m in re.finditer(r'\{ no: "[^"]+", teams: "([^"]+)", league: "[^"]*", lg: "[^"]*", score: "([^"]*)"', blk.split("review:")[-1]):
        key = m.group(1) + " || " + m.group(2)
        pair.setdefault(key, []).append(k)
dup = {kk: vv for kk, vv in pair.items() if len(vv) > 1 and "|| " in kk and kk.split("|| ")[1].strip()}
for kk, vv in sorted(dup.items()):
    print("重复: %s 出现在 %s" % (kk, vv))
if not dup:
    print("无重复")

# 4) 残留检查
print("\n=== 残留检查 ===")
for bad in ['"2026-07-19"', '"2026-08-13"', '"2026-08-10"', '":---"', '"2026-08-05": {', "凯拉特"]:
    print("%s 出现 %d 次" % (bad, src.count(bad)))
