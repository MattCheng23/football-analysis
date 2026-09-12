# -*- coding: utf-8 -*-
"""logic_audit.py — 核心逻辑「篇幅 + 近5场完整性 + H2H 完整性」体检（机器回源）
判定：
  近5完整 = 近况段内比分 token ≥10（双方各 ≥5 条逐场比分）
  H2H完整 = H2H 段内比分 token ≥4 且写明近10 总战绩（胜平负）
  篇幅   = logic 字符数（>1600 判冗长）；条款引用密度 = (V11./R\d+/§) 出现次数
"""
import io, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
t = io.open(P, encoding='utf-8').read()
si = t.index('"2026-09-12": {')
se = t.index("/* 红黑总榜", si)
PAT = re.compile(r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)",[\s\S]*?logic: "([\s\S]*?)"\s*\}')
TOK = re.compile(r"\d+[-:]\d+")
rows = []
for m in re.finditer(PAT, t[si:se]):
    no, h, a, lg = m.group(1), m.group(2), m.group(3), m.group(4)
    n = len(lg)
    # 近况段
    j = lg.find("近况")
    j2 = lg.find("H2H", j) if j >= 0 else -1
    near = lg[j:j2] if j >= 0 and j2 > j else (lg[j:j + 700] if j >= 0 else "")
    near_tok = len(TOK.findall(near))
    # H2H 段
    k = lg.find("H2H")
    k2 = lg.find("伤停", k) if k >= 0 else -1
    h2h = lg[k:k2] if k >= 0 and k2 > k else (lg[k:k + 500] if k >= 0 else "")
    h2h_tok = len(TOK.findall(h2h))
    h2h_sum = bool(re.search(r"近\s?10[^。；]{0,30}\d+\s?胜\s?\d+\s?平\s?\d+\s?负|近\s?10[^。；]{0,20}\d+胜\d+平\d+负", h2h))
    rules = len(re.findall(r"V11\.\d+|R\d{3}|§\d", lg))
    rows.append((no, h, a, n, near_tok, h2h_tok, h2h_sum, rules))
print("%-4s %-14s %5s %6s %6s %6s %5s" % ("场次", "对阵", "字数", "近5token", "H2Htoken", "近10字样", "条款引"))
bad_near, bad_h2h, long_ = [], [], []
for no, h, a, n, nt, ht, hs, ru in rows:
    flag = ""
    if nt < 10:
        flag += "近5缺 "; bad_near.append(no)
    if ht < 4 or not hs:
        flag += "H2H缺 "; bad_h2h.append(no)
    if n > 1600:
        flag += "冗长 "; long_.append(no)
    print("%-4s %-14s %5d %6d %6d %6s %5d  %s" % (no, ("%s vs %s" % (h, a))[:14], n, nt, ht, "✓" if hs else "✗", ru, flag))
print("\n汇总：%d 场｜近5 不全 %d 场 %s｜H2H 不全 %d 场 %s｜>1600 字 %d 场 %s" %
      (len(rows), len(bad_near), ",".join(bad_near), len(bad_h2h), ",".join(bad_h2h), len(long_), ",".join(long_)))
print("字数：中位 %d｜最大 %d｜均值 %d" % (sorted(r[3] for r in rows)[len(rows) // 2], max(r[3] for r in rows),
                                       sum(r[3] for r in rows) // len(rows)))
