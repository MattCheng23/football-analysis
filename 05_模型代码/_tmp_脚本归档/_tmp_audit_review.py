# -*- coding: utf-8 -*-
"""盘点 7/21 至今各批次复盘缺口"""
import re, io

src = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data.js", encoding="utf-8").read()
keys = [(m.group(1), m.start()) for m in re.finditer(r'^\s*"(\d{4}-\d{2}-\d{2})":\s*\{', src, re.M)]
print("批次 | reviewed | results | evidence | 缺证据/待复盘")
for i, (k, s) in enumerate(keys):
    e = keys[i+1][1] if i+1 < len(keys) else len(src)
    blk = src[s:e]
    rev = "Y" if re.search(r"reviewed:\s*true", blk) else "N"
    rev_part = blk.split("review:")[-1]
    res = len(re.findall(r'\{ no: "[^"]+", teams:', rev_part))
    ev = 0
    if "evidence:" in rev_part:
        ev_part = rev_part.split("evidence:")[1].split("avoidHigh")[0]
        ev = len(re.findall(r"\{ no:", ev_part))
    flag = "OK" if res == ev else ("缺EVIDENCE" if ev == 0 else "部分缺")
    print("%s | %s | %d | %d | %s" % (k, rev, res, ev, flag))
