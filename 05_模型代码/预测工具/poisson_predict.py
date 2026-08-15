# -*- coding: utf-8 -*-
"""V10.36 泊松预测工具：λ 公式化 + 比分概率 + 查表对照 + G 清单
用法：python poisson_predict.py <联赛> <主队> <客队> <主队近5主场进> <主队近5主场失> <客队近5客场进> <客队近5客场失> [主队伤停修正] [客队伤停修正]
例：python poisson_predict.py 巴甲 弗鲁米嫩塞 帕尔梅拉斯 1.6 1.2 1.8 1.0 0 0.3
"""
import sys, io, os, json, math, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = json.load(open(r"D:\Cola\足球分析学习\01_当前模型\联赛攻防基准_20260816.json", encoding="utf-8"))

# V10.35 联赛参数（λ/平局率/大小球/主场系数）——无基准文件的联赛用参数近似
PARAMS = {
    "韩职": {"avg": 2.33, "draw": 0.32, "ou": 2.5, "home": 0.65},
    "巴甲": {"avg": 2.61, "draw": 0.30, "ou": 2.5, "home": 0.95},
    "瑞超": {"avg": 3.07, "draw": 0.25, "ou": 3.0, "home": 0.75},
    "挪超": {"avg": 2.98, "draw": 0.18, "ou": 3.0, "home": 0.85},
    "芬超": {"avg": 2.65, "draw": 0.28, "ou": 2.5, "home": 0.95},
    "美职联": {"avg": 3.24, "draw": 0.25, "ou": 3.0, "home": 0.95},
    "日职": {"avg": 2.90, "draw": 0.25, "ou": 3.0, "home": 0.85},
    "英冠": {"avg": 2.61, "draw": 0.26, "ou": 2.5, "home": 0.80},
    "英超": {"avg": 2.80, "draw": 0.27, "ou": 2.75, "home": 0.85},
    "西甲": {"avg": 2.70, "draw": 0.24, "ou": 2.5, "home": 0.95},
    "德甲": {"avg": 3.20, "draw": 0.25, "ou": 3.25, "home": 0.85},
    "意甲": {"avg": 2.45, "draw": 0.26, "ou": 2.5, "home": 0.85},
    "法甲": {"avg": 2.80, "draw": 0.25, "ou": 2.75, "home": 0.90},
    "荷甲": {"avg": 3.18, "draw": 0.26, "ou": 3.25, "home": 0.85},
    "葡超": {"avg": 2.68, "draw": 0.27, "ou": 2.75, "home": 0.85},
    "欧冠资格赛": {"avg": 2.80, "draw": 0.25, "ou": 2.5, "home": 0.85},
    "欧罗巴资格赛": {"avg": 2.30, "draw": 0.25, "ou": 2.5, "home": 0.70},
    "欧冠": {"avg": 3.00, "draw": 0.28, "ou": 3.0, "home": 0.85},
}

# V10.36 比分查表（联赛特例；缺省=通用）
TABLE = {
    "英超": {"主胜": ["2-0", "2-1", "3-0"]},
    "瑞超": {"主胜": ["2-0", "2-1", "3-0"]},
    "德甲": {"主胜": ["1-0", "2-1", "3-1"], "客胜": ["0-1", "1-2", "1-3"]},
    "巴甲": {"客胜": ["0-1", "1-2", "1-3"]},
    "芬超": {"客胜": ["0-1", "0-2", "1-3"]},
    "葡超": {"主胜": ["1-0", "2-1", "3-0"]},
    "美职联": {"客胜": ["0-1", "1-2", "2-3"]},
}
DEFAULT = {"主胜": ["1-0", "2-0", "2-1"], "平": ["0-0", "1-1", "2-2"], "客胜": ["0-1", "0-2", "1-2"]}

def poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)

def fetch_team_form(tid, mode, n=5):
    """teams API 拉近 N 场（home/away/all）进失球均值"""
    import subprocess as sp
    HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]
    r = sp.run(HEAD + [f"https://www.fotmob.com/api/data/teams?id={tid}"], capture_output=True)
    d = json.loads(r.stdout.decode("utf-8", errors="replace"))
    team = (d.get("team", {}) or {}).get("name", f"#{tid}")
    fx = (d.get("fixtures", {}) or {}).get("allFixtures", {}) or {}
    matches = []
    for f in fx.get("fixtures", []) or []:
        st = f.get("status") or {}
        if not st.get("finished") or not st.get("scoreStr"):
            continue
        sc = st["scoreStr"].replace(" ", "")
        if not re.match(r"^\d+-\d+$", sc):
            continue
        is_home = str((f.get("home") or {}).get("id")) == str(tid)
        if mode == "home" and not is_home:
            continue
        if mode == "away" and is_home:
            continue
        a, b = sc.split("-")
        gf, ga = (int(a), int(b)) if is_home else (int(b), int(a))
        matches.append((gf, ga))
    recent = matches[-n:]
    if not recent:
        return team, None, None
    return team, sum(m[0] for m in recent) / len(recent), sum(m[1] for m in recent) / len(recent)

def main():
    args = sys.argv[1:]
    if len(args) < 7:
        print("参数不足：联赛 主队 客队 主进 主失 客进 客失 [主修] [客修]")
        print("或 --auto 模式：联赛 主队 客队 --home-id X --away-id Y [主修] [客修]（自动拉近5场状态）")
        return
    league, home, away = args[0], args[1], args[2]
    auto = "--home-id" in args or "--away-id" in args
    if auto:
        hid = args[args.index("--home-id") + 1] if "--home-id" in args else None
        aid = args[args.index("--away-id") + 1] if "--away-id" in args else None
        h_atk = h_def = a_atk = a_def = None
        if hid:
            th, h_atk, h_def = fetch_team_form(hid, "home")
            print(f"# 主队自动拉取：{th} 近5主场 进 {h_atk:.2f}/失 {h_def:.2f}" if h_atk else f"# 主队 {th} 无主场数据")
        if aid:
            ta, a_atk, a_def = fetch_team_form(aid, "away")
            print(f"# 客队自动拉取：{ta} 近5客场 进 {a_atk:.2f}/失 {a_def:.2f}" if a_atk else f"# 客队 {ta} 无客场数据")
        rest = [x for x in args[3:] if not x.startswith("--") and not x.isdigit()]
        h_adj = float(rest[0]) if rest and rest[0].replace(".", "", 1).isdigit() else 0.0
        a_adj = float(rest[1]) if len(rest) > 1 and rest[1].replace(".", "", 1).isdigit() else 0.0
    else:
        h_atk, h_def, a_atk, a_def = map(float, args[3:7])
        h_adj = float(args[7]) if len(args) > 7 else 0.0
        a_adj = float(args[8]) if len(args) > 8 else 0.0

    b = BASE.get(league)
    if not b:
        p = PARAMS.get(league)
        if not p:
            print(f"无 {league} 参数")
            return
        b = {"hg": p["avg"] / 2, "ha": p["avg"] / 2, "ag": p["avg"] / 2, "aa": p["avg"] / 2}
    p = PARAMS.get(league, {})
    home_coef = p.get("home", 0.85)

    # λ 公式：联赛基准 × 状态指数（近5场 vs 联赛均值，R342 60% 吸收阻尼）× 主场系数
    def damp(x):
        v = 1 + 0.6 * (x - 1)          # 60% 吸收，防近期爆表
        return max(0.5, min(1.8, v))   # 限幅，防极端状态

    idx_h_atk = h_atk / b["hg"] if b["hg"] else 1.0
    idx_a_def = a_def / b["hg"] if b["hg"] else 1.0   # 客队客场失球 vs 联赛主队均进
    idx_a_atk = a_atk / b["ag"] if b["ag"] else 1.0
    idx_h_def = h_def / b["ag"] if b["ag"] else 1.0   # 主队主场失球 vs 联赛客队均进

    lam_h = b["hg"] * home_coef * damp(idx_h_atk) * damp(idx_a_def) + h_adj
    lam_a = b["ag"] * damp(idx_a_atk) * damp(idx_h_def) + a_adj
    lam_h = max(0.3, min(4.5, lam_h)); lam_a = max(0.3, min(4.5, lam_a))

    # 泊松矩阵
    probs = {}
    for x in range(9):
        for y in range(9):
            probs[(x, y)] = poisson_pmf(x, lam_h) * poisson_pmf(y, lam_a)
    total = sum(probs.values())
    probs = {k: v / total for k, v in probs.items()}

    p_home = sum(v for (x, y), v in probs.items() if x > y)
    p_draw = sum(v for (x, y), v in probs.items() if x == y)
    p_away = sum(v for (x, y), v in probs.items() if x < y)

    # 方向+等级（V10.36 规范）
    top_dir = max([("主胜", p_home), ("平", p_draw), ("客胜", p_away)], key=lambda t: t[1])
    dname, dp = top_dir
    second = sorted([("主胜", p_home), ("平", p_draw), ("客胜", p_away)], key=lambda t: -t[1])[1]
    if dp >= 0.60:
        lv = "A"
    elif dp >= 0.50:
        lv = "A-"
    elif dp >= 0.45:
        lv = "B+"
    elif dp >= 0.40:
        lv = "B"
    elif dp >= 0.35:
        lv = "B-"
    else:
        lv = "C"
    # G2/G3 场次级约束（V10.36 修订：联赛统计仅参考，不做联赛强制）
    # G2：A 级 = 首选 ≥60% + 人工核验（避雷/剧本/冷平史）
    if dp < 0.60 and lv in ("A", "A-"):
        lv = "B+" if lv == "A" else "B"
    # G3：双选触发 = 平局概率 ≥30% 或 首选 <50%（韩/巴/美平局统计高→更易触发，参考）
    must_double = p_draw >= 0.30 or dp < 0.50
    double = f"（G3 双选触发：{dname}/{second[0]}）" if must_double else ""

    # 比分 TOP 排序
    top_scores = sorted(probs.items(), key=lambda kv: -kv[1])[:10]
    top3 = [f"{x}-{y}" for (x, y), _ in top_scores[:3]]

    # 查表对照
    tbl = TABLE.get(league, {}).get(dname, DEFAULT[dname])
    tbl_dir = " / ".join(tbl)

    # 半全场（半场 λ=λ/2 独立近似）
    hh = {}
    for hx in range(5):
        for hy in range(5):
            for fx in range(5):
                for fy in range(5):
                    if fx < hx or fy < hy:
                        continue
                    ph = poisson_pmf(hx, lam_h/2) * poisson_pmf(hy, lam_a/2) * poisson_pmf(fx-hx, lam_h/2) * poisson_pmf(fy-hy, lam_a/2)
                    mk = lambda a, b: "胜" if a > b else ("负" if a < b else "平")
                    key = mk(hx, hy) + mk(fx, fy)
                    hh[key] = hh.get(key, 0.0) + ph
    hh_top = sorted(hh.items(), key=lambda kv: -kv[1])[:3]

    # 总进球（R338：TOP3 比分总球数众数）
    from collections import Counter
    gcnt = Counter((x + y) for (x, y), _ in top_scores[:3])
    g1, g2 = [g for g, _ in gcnt.most_common(2)]

    print(f"== {home} vs {away}（{league}）V10.36 泊松预测 ==")
    print(f"λ: 主 {lam_h:.2f} / 客 {lam_a:.2f}")
    print(f"方向: 主胜 {p_home*100:.0f}%｜平 {p_draw*100:.0f}%｜客胜 {p_away*100:.0f}% → 首选 {dname} {dp*100:.0f}%{double}")
    print(f"等级建议: {lv}（G2 检查：避雷/剧本/冷平历史？有则再降级）")
    print(f"比分 TOP3(泊松): {' / '.join(top3)}")
    print(f"查表组合({dname}): {tbl_dir} ← 按此替换泊松项（叠加队伍规则/预警后定稿）")
    print(f"半全场 TOP3: {' / '.join(f'{k}({v*100:.0f}%)' for k, v in hh_top)}")
    print(f"总进球: {g1}·{g2}（R338 由比分推导）")
    # G1 检查（场次级：λ 和 ≥3.0 或剧本场触发；高进球联赛参考）
    g1_trigger = (lam_h + lam_a) >= 3.0
    g1_txt = "触发（λ和≥3.0）：比分需含 ≥4 球项" if g1_trigger else "未触发（λ和<3.0）：按查表组合即可"
    print(f"G1 检查: {g1_txt}｜G5 检查: {'主胜≥45% 方向必须含主胜' if p_home >= 0.45 else '主胜<45% 无强制'}")

if __name__ == "__main__":
    main()
