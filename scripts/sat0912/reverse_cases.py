# -*- coding: utf-8 -*-
"""reverse_cases2.py — 反向槽决策树数据：逐例算「`*` 项 vs 被挤项 vs 冷门方向 TOP3 形态」
并输出 _tmp_football/sat0912/reverse_cases.md（赛前基线；赛果到手重跑自动补命中列）
"""
import io, json, math, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
R = r"D:\Cola\足球分析学习\_发布_public\js\data-review.js"
OUT = r"D:\Cola\_tmp_football\sat0912\reverse_cases.md"
LAM = {"001": (1.45, 1.25), "002": (1.20, 1.50), "003": (2.00, 0.95), "004": (1.45, 1.75),
       "005": (1.30, 1.45), "006": (0.85, 1.95), "007": (2.35, 1.20), "008": (2.00, 1.50),
       "009": (1.75, 1.00), "010": (2.20, 1.65), "011": (1.50, 1.80), "012": (2.40, 0.80),
       "013": (1.30, 1.70), "014": (1.10, 1.00), "015": (1.90, 1.40), "016": (1.70, 1.20),
       "017": (1.20, 1.10), "018": (1.40, 2.10), "019": (0.85, 1.75), "020": (1.10, 1.15),
       "021": (2.20, 1.00), "022": (1.62, 1.13), "023": (1.80, 1.70), "024": (1.80, 0.80),
       "025": (0.45, 2.50), "026": (1.35, 2.20), "027": (1.30, 0.80), "028": (1.35, 1.30),
       "029": (0.80, 1.70), "030": (2.40, 0.60)}
BASE = {"1-1": 11.88, "2-1": 8.15, "0-1": 7.30, "1-0": 7.13, "2-0": 6.11, "1-2": 5.94,
        "0-0": 5.77, "3-0": 5.26, "2-2": 5.09, "0-2": 4.07, "3-2": 4.58, "3-1": 3.74}
Pf = lambda l, n: math.exp(-l) * l ** n / math.factorial(n)
t = io.open(P, encoding='utf-8').read()
si = t.index('"2026-09-12": {'); se = t.index("/* 红黑总榜", si); seg = t[si:se]
PAT = re.compile(r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)",[\s\S]*?time: "([^"]+)", dir: "([^"]+)",[\s\S]*?scores: "([^"]+)"')
M = {m.group(1): {"h": m.group(2), "a": m.group(3), "tm": m.group(4), "dir": m.group(5), "sc": m.group(6)}
     for m in re.finditer(PAT, seg)}
rv = io.open(R, encoding='utf-8').read()
i = rv.index('"2026-09-12": {')
RES = {}
for m in re.finditer(r'\{ no: "(\d+)", teams: "([^"]+)",[\s\S]{0,80}?score: "(\d+)-(\d+)', rv[i:i + 60000]):
    RES[m.group(1)] = (int(m.group(3)), int(m.group(4)))
L = ["# 0912 批「反向比分槽（`*`）」逐例体检（机器回源）", "",
     "> 口径：冷门侧 `*` 义务槽＝**冷门方向内概率最高项**（V11.45-1）；历史回测（`backtest_reverse2.py`·12 例）`*` 项 **0 命中**。",
     "> 工具：`scripts/sat0912/reverse_cases.py`（赛果入库后重跑自动补命中列）", "",
     "| 场次 | 对阵 | 方向 | 冷门侧(方向) | `*` 项（概率/底座） | 被挤项（概率/底座） | 席位成本 | 冷门方向 TOP3 形态 | 实际 | 判定 |",
     "|---|---|---|---|---|---|---|---|---|---|"]
tot_cost = 0.0
cases = []
for no in sorted(M):
    m = M[no]
    toks = [x.strip() for x in m["sc"].split("/")]
    star = [x for x in toks if x.endswith("*")]
    if not star:
        continue
    lh, la = LAM[no]
    g = {(a, b): Pf(lh, a) * Pf(la, b) for a in range(10) for b in range(10)}
    T = sum(g.values())
    pct = lambda s: round(g[tuple(int(y) for y in s.rstrip("*").split("-"))] / T * 100, 2)
    d = m["dir"].split("（")[0]
    ok = lambda a, b: ("主胜" in d and a > b) or ("客胜" in d and b > a) or ("平" in d and a == b)
    rank = sorted([(k, v) for k, v in g.items() if ok(*k)], key=lambda z: -z[1])
    sel = [tuple(int(y) for y in x.rstrip("*").split("-")) for x in toks]
    disp = next((("%d-%d" % k, round(v / T * 100, 2)) for k, v in rank if k not in sel), ("—", 0.0))
    st = star[0]
    gap = round(disp[1] - pct(st), 2)
    tot_cost += max(0.0, gap)
    coldk = sorted([(k, v) for k, v in g.items() if not ok(*k)], key=lambda z: -z[1])[:3]
    colds = " ".join("%d-%d %.2f%%" % (k[0], k[1], v / T * 100) for k, v in coldk)
    res = RES.get(no)
    resx = "%d-%d" % res if res else "待赛"
    verdict = ""
    if res:
        s_hit = tuple(res) == tuple(int(y) for y in st.rstrip("*").split("-"))
        p_hit = any(tuple(res) == tuple(int(y) for y in x.rstrip("*").split("-")) for x in toks if not x.endswith("*"))
        c_hit = not (("主胜" in d and res[0] > res[1]) or ("客胜" in d and res[1] > res[0]) or ("平" in d and res[0] == res[1]))
        verdict = ("`*`%s｜正路%s｜冷门方向%s" % ("✅" if s_hit else "✗", "✅" if p_hit else "✗", "✅兑现" if c_hit else "✗未兑现"))
    L.append("| %s | %s vs %s | %s | %s | %s %.2f%%（%s） | %s %.2f%%（%s） | **%+.2fpp** | %s | %s | %s |" % (
        no, m["h"], m["a"], d, "非方向集", st, pct(st), BASE.get(st.rstrip("*"), "—"),
        disp[0], disp[1], BASE.get(disp[0], "—"), gap, colds, resx, verdict))
    cases.append({"no": no, "gap": gap, "star": st, "disp": disp[0]})
L += ["", "**席位成本合计（仅计正成本）＝ %+.2fpp**（005-030 内 5 例）；负值＝`*` 项概率**高于**被挤项（即该槽同时是最高剩余项，零成本）。" % tot_cost, "",
      "## 决策树（预登记·赛果到手后按此裁决，禁事后改）", "",
      "| 情形 | 判据 | 优化动作 |",
      "|---|---|---|",
      "| **R1 `*` 项命中** | `*` 命中 ≥2/6 | 义务有效 → 保留 V11.45-1，并把「成本闸门」从 2.0pp 放宽到 **3.0pp**（义务优先级提升） |",
      "| **R2 合理但形态偏差** | 冷门方向兑现，但 `*` 项未命中 **且** 冷门方向 TOP1 形态 ≠ 我选形态 | 形态选择优化：改为「冷门方向 TOP1 形态」，并对「主队攻端哑火 vs 客队零封」做二选一（见下 §形态选择规则） |",
      "| **R3 合理但无法命中** | 冷门方向兑现，`*` 项未命中 **且** 冷门方向 TOP1 形态 = 我选形态 | 属固有概率损失 → 保留义务，但把「被挤项」改为**同方向内次高**（减少正路损失） |",
      "| **R4 不合理** | 冷门方向未兑现 且 被挤项命中 ≥2 例 | 义务降级：`*` 槽改为「**条件触发**」＝coldRisk ≥较高 或 冷链 ≥4/5 环；否则只写 logic 记录不占席位（每批 `*` 上限 3 例） |",
      "| **R5 全批中性** | 冷门兑现 ≤1 且 被挤项命中 ≤1 | 维持现口径，样本并入历史（12→18），累积 30 例再裁 |", "",
      "**形态选择规则（R2 用·预登记）**：冷门方向内择优顺序＝① 该方向泊松 TOP1；② 若 TOP1 与 TOP2 差 <0.5pp → 取「与主方向最可能形态共用进球数」者（保持票面总进球结构一致，利于 ou 联动）；③ 客队零封能力 ≥3 场零封 → 优先零封型（0-1/0-2）；主队攻端近 3 场 0 球 → 优先 1-0/0-1 单球型。"]

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("已写：", OUT)
for c in cases:
    print("  %s `*`=%s 被挤=%s 成本 %+.2fpp" % (c["no"], c["star"], c["disp"], c["gap"]))
print("正成本合计 %+.2fpp" % tot_cost)
json.dump(cases, io.open(r"D:\Cola\_tmp_football\sat0912\reverse_cases.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
