# -*- coding: utf-8 -*-
"""score_versions.py — 各版本票面 × 真实赛果 机械评分（拿事实说话·禁事后解释）
数据源：versions.json（git 各版本票面，机器提取）+ data-review.js REVIEW_EXTRA['2026-09-12'].results（复盘真源）
输出：_tmp_football/sat0912/version_scores.md（逐版本四维命中 + 关键对照组 + 让位兑现统计）
"""
import io, json, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
V = json.load(io.open(r"D:\Cola\_tmp_football\sat0912\versions.json", encoding="utf-8"))
CUR = {"label": "2145 回滚 001/002（当前上线）",
       "matches": {}}
# 当前工作区 = 最新版
t = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data.js", encoding="utf-8").read()
si = t.index('"2026-09-12": {'); se = t.index("/* 红黑总榜", si)
PAT = (r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)", league: "([^"]+)", lg: "[^"]+", '
       r'time: "([^"]+)", dir: "([^"]+)", dc: "[^"]+", scores: "([^"]+)", ht: "([^"]+)", '
       r'ou: "([^"]+)", risk: (\d+),')
for m in re.finditer(PAT, t[si:se]):
    CUR["matches"][m.group(1)] = {"home": m.group(2), "away": m.group(3), "time": m.group(5),
                                  "dir": m.group(6), "scores": m.group(7), "ht": m.group(8), "ou": m.group(9)}
V["CUR"] = CUR

# ---- 赛果（复盘真源）----
rv = io.open(r"D:\Cola\足球分析学习\_发布_public\js\data-review.js", encoding="utf-8").read()
i = rv.index('"2026-09-12": {')
seg = rv[i:i + 60000]
RES = {}
for m in re.finditer(r'\{ no: "(\d+)", teams: "([^"]+)", league: "([^"]+)", lg: "[^"]+", score: "([^"]+)"', seg):
    no, teams, lg, score = m.group(1), m.group(2), m.group(3), m.group(4)
    mm = re.match(r"(\d+)-(\d+)", score)
    hh = re.search(r"（(\d+)-(\d+)）", score)
    RES[no] = {"teams": teams, "league": lg, "gf": int(mm.group(1)), "ga": int(mm.group(2)),
               "hgf": int(hh.group(1)) if hh else None, "hga": int(hh.group(2)) if hh else None}
print("已知赛果：%d 场 %s" % (len(RES), ",".join(sorted(RES))))

HOME_FIX = {(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)}
AWAY_FIX = {(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4), (2, 4), (0, 5), (1, 5), (2, 5)}
DRAW_FIX = {(0, 0), (1, 1), (2, 2), (3, 3)}
CLS = {1: lambda i, j: i + j >= 4, 2: lambda i, j: i + j >= 5,
       3: lambda i, j: abs(i - j) >= 3, 4: lambda i, j: min(i, j) == 0 and abs(i - j) >= 2}
RESULT_OF = lambda i, j: "胜" if i > j else ("负" if j > i else "平")


def token_hit(tok, i, j):
    tok = tok.strip()
    if not re.match(r"^\d+-\d+", tok):
        cls = {"胜其它": "胜", "负其它": "负", "平其它": "平"}.get(tok)
        if not cls:
            return False
        if RESULT_OF(i, j) != cls:
            return False
        panel = HOME_FIX if cls == "胜" else (AWAY_FIX if cls == "负" else DRAW_FIX)
        return (i, j) not in panel
    a, b = (int(x) for x in tok.rstrip("*").split("-"))
    return (a, b) == (i, j)


def score(ver):
    rows, hit = [], {"score": 0, "top1": 0, "dir": 0, "ht": 0, "ou": 0, "n": 0,
                     "score11": 0, "n11": 0, "dir11": 0, "ht11": 0, "ou11": 0}
    for no in sorted(RES):
        if no not in ver["matches"]:
            continue
        mt = ver["matches"][no]
        r = RES[no]
        i, j = r["gf"], r["ga"]
        toks = [x.strip() for x in mt["scores"].split("/")]
        s_hit = any(token_hit(x, i, j) for x in toks)
        t1_hit = token_hit(toks[0], i, j)
        dset = mt["dir"].split("（")[0]
        dir_hit = any(k in dset for k in (["主胜"] if i > j else (["客胜"] if j > i else ["平"])))
        ht_hit = None
        if r["hgf"] is not None:
            pair = RESULT_OF(r["hgf"], r["hga"]) + RESULT_OF(i, j)
            ht_hit = any(x.strip().rstrip("*") == pair for x in mt["ht"].split("/"))
        tot = i + j
        nums = set(int(x) for x in re.findall(r"\d", mt["ou"]))
        ou_hit = tot in nums
        hit["n"] += 1
        hit["score"] += s_hit; hit["top1"] += t1_hit; hit["dir"] += dir_hit
        hit["ht"] += bool(ht_hit); hit["ou"] += ou_hit
        if "011" <= no <= "030":
            hit["n11"] += 1
            hit["score11"] += s_hit; hit["dir11"] += dir_hit
            hit["ht11"] += bool(ht_hit); hit["ou11"] += ou_hit
        rows.append((no, mt["scores"], "%d-%d" % (i, j), "✓" if s_hit else "✗",
                     "✓" if t1_hit else "·", "✓" if dir_hit else "✗",
                     "·" if ht_hit is None else ("✓" if ht_hit else "✗"), "✓" if ou_hit else "✗"))
    return hit, rows


print("\n版本评分（已出赛果 %d 场）：" % len(RES))
print("%-34s %-8s %-8s %-8s %-8s %-8s" % ("版本", "比分(全/11-30)", "TOP1", "方向", "ht", "ou"))
summary = {}
for rev, ver in V.items():
    h, rows = score(ver)
    summary[rev] = {"label": ver["label"], "hit": h, "rows": rows}
    print("%-34s %-8s %-8s %-8s %-8s %-8s" % (
        ver["label"][:32],
        "%d/%d (%d/%d)" % (h["score"], h["n"], h["score11"], h["n11"]),
        "%d/%d" % (h["top1"], h["n"]), "%d/%d" % (h["dir"], h["n"]),
        "%d/%d" % (h["ht"], h["n"]), "%d/%d" % (h["ou"], h["n"])))

# 逐场对照（所有版本票面 + 赛果）
print("\n逐场对照：")
hdr = ["场次", "赛果"] + [k for k in V]
print(" | ".join(hdr))
for no in sorted(RES):
    cells = [no, "%d-%d" % (RES[no]["gf"], RES[no]["ga"])] + \
            [V[k]["matches"][no]["scores"].replace(" ", "") for k in V]
    print(" | ".join(cells))

# 让位兑现统计（当前版）
print("\n让位兑现（当前版·实际结果为该类的场次 → 票内是否含同类项）：")
cur = V["CUR"]["matches"]
for c, fn in CLS.items():
    act = [no for no in sorted(RES) if fn(RES[no]["gf"], RES[no]["ga"])]
    cov = [no for no in act if any(fn(*[int(y) for y in x.strip().rstrip("*").split("-")])
                                   for x in cur[no]["scores"].split("/") if re.match(r"^\d+-\d+", x.strip()))]
    print("  类%d：实际 %d 场 %s → 票内同类覆盖 %d 场 %s" % (c, len(act), ",".join(act), len(cov), ",".join(cov)))

json.dump({k: {"label": v["label"], "hit": v["hit"]} for k, v in summary.items()},
          io.open(r"D:\Cola\_tmp_football\sat0912\version_scores.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n已写 version_scores.json（逐场明细见 stdout / 报告）")
