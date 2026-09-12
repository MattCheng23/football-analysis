# -*- coding: utf-8 -*-
"""auto_review_pipeline.py — 0912 批无人值守复盘流水线（机械部分全自动·幂等·可续跑）

做四件事（每场）：
  ① FotMob 主源刷新（curl + x-mas）→ 解析 FT/半场/进球链/牌/统计/射门图/阵容/POM/近5/H2H
  ② 官方第二源核验（读 official snapshot；比分不一致 → 标「待核」跳过入库）
  ③ 机械判定四维（方向/比分/ht/ou）+ 生成 results/evidence 条目（含事实数字，归属留给模型）
  ④ 幂等入库：data-review.js + reviewedCount + 双日志行
最后：门禁（node --check / hole_guard / review_gate_check / check_batch_full）→ 可选部署

用法：
  python auto_review_pipeline.py --dry-run          # 只算不写（校验判定逻辑）
  python auto_review_pipeline.py                    # 全量入库（幂等）
  python auto_review_pipeline.py --matches 007,008  # 指定场次
"""
import io, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = Path(r"D:\Cola\足球分析学习")
JS = REPO / "_发布_public" / "js"
BAK = REPO / "_backup" / "auto_bak"
O = Path(r"D:\Cola\_tmp_football\sat0912")
LOG_L = REPO / "01_当前模型" / "联赛蒸馏日志_20260906.md"
LOG_G = REPO / "01_当前模型" / "整体蒸馏日志_20260907.md"
HDR = "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"
DRY = "--dry-run" in sys.argv
ONLY = None
if "--matches" in sys.argv:
    ONLY = set(sys.argv[sys.argv.index("--matches") + 1].split(","))
IDS = json.load(io.open(O / "fm_ids.json", encoding="utf-8"))
LAM = {"001": (1.45, 1.25), "002": (1.20, 1.50), "003": (2.00, 0.95), "004": (1.45, 1.75),
       "005": (1.30, 1.45), "006": (0.85, 1.95), "007": (2.35, 1.20), "008": (2.00, 1.50),
       "009": (1.75, 1.00), "010": (2.20, 1.65), "011": (1.50, 1.80), "012": (2.40, 0.80),
       "013": (1.30, 1.70), "014": (1.10, 1.00), "015": (1.90, 1.40), "016": (1.70, 1.20),
       "017": (1.20, 1.10), "018": (1.40, 2.10), "019": (0.85, 1.75), "020": (1.10, 1.15),
       "021": (2.20, 1.00), "022": (1.62, 1.13), "023": (1.80, 1.70), "024": (1.80, 0.80),
       "025": (0.45, 2.50), "026": (1.35, 2.20), "027": (1.30, 0.80), "028": (1.35, 1.30),
       "029": (0.80, 1.70), "030": (2.40, 0.60)}
HOME_FIX = {(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)}
AWAY_FIX = {(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4), (2, 4), (0, 5), (1, 5), (2, 5)}
DRAW_FIX = {(0, 0), (1, 1), (2, 2), (3, 3)}
PANEL = HOME_FIX | AWAY_FIX | DRAW_FIX


def sh(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, shell=isinstance(cmd, str))
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, str(e)


def fetch_fm(no):
    mid = IDS[no]
    url = "https://www.fotmob.com/api/data/matchDetails?matchId=%s" % mid
    rc, body = sh(["curl.exe", "-s", "-m", "45", "-H", HDR, url])
    if not (body or "").strip().startswith("{"):
        return None
    (O / ("res_fm_%s.json" % no)).write_text(body, encoding="utf-8")
    return json.loads(body)


def gl(d, *ks, default=None):
    for k in ks:
        if isinstance(d, dict) and k in d:
            d = d[k]
        elif isinstance(d, list) and isinstance(k, int) and 0 <= k < len(d):
            d = d[k]
        else:
            return default
    return d


def parse(no, j):
    gp, hd, c = j.get("general") or {}, j.get("header") or {}, j.get("content") or {}
    mf = c.get("matchFacts") or {}
    ib = mf.get("infoBox") or {}
    teams = hd.get("teams") or []
    hs, as_ = gl(teams, 0, "score"), gl(teams, 1, "score")
    evs = (mf.get("events") or {}).get("events") or []
    hg = ag = 0
    goals, cards = [], []
    for e in evs:
        t = e.get("timeStr") or str(e.get("time"))
        who = e.get("player")
        who = who.get("name") if isinstance(who, dict) else (who or "")
        if e.get("type") == "Goal":
            s = "主" if e.get("isHome") else "客"
            tag = "点球" if e.get("isPenalty") else ("乌龙" if e.get("ownGoal") else "")
            goals.append("%s′ %s（%s%s）" % (t, who, s, tag))
            if (e.get("time") or 0) <= 45:
                hg, ag = (hg + 1, ag) if s == "主" else (hg, ag + 1)
        elif e.get("type") == "Card":
            cards.append("%s′ %s（%s·%s）" % (t, who, "主" if e.get("isHome") else "客", e.get("card") or ""))
    grp = ((gl(c, "stats", "Periods", "All") or {}).get("stats")) or []
    stats = []
    for gi in grp:
        for it in (gi.get("stats") or []):
            v = it.get("stats")
            if isinstance(v, list) and len(v) == 2 and v[0] is not None:
                stats.append((it.get("title") or it.get("key"), v[0], v[1]))
    st = {k: (a, b) for k, a, b in stats}
    shots = (c.get("shotmap") or {}).get("shots") or []
    tid_h = gl(teams, 0, "id")
    agg = {"主": {"n": 0, "xG": 0.0, "on": 0, "goal": 0}, "客": {"n": 0, "xG": 0.0, "on": 0, "goal": 0}}
    for s in shots:
        k = "主" if s.get("teamId") == tid_h else "客"
        agg[k]["n"] += 1
        agg[k]["xG"] += float(s.get("expectedGoals") or 0)
        agg[k]["on"] += 1 if s.get("isOnTarget") else 0
        agg[k]["goal"] += 1 if s.get("eventType") == "Goal" else 0
    lu = c.get("lineup") or {}
    return {"no": no, "hs": hs, "as": as_, "ft_finished": bool(gp.get("finished")),
            "ht": (hg, ag), "goals": goals, "cards": cards,
            "red_h": gl(hd, "status", "numberOfHomeRedCards"), "red_a": gl(hd, "status", "numberOfAwayRedCards"),
            "stats": st, "shot_agg": agg,
            "home": gl(teams, 0, "name"), "away": gl(teams, 1, "name"),
            "league": gl(ib, "Tournament", "leagueName"), "stadium": gl(ib, "Stadium", "name"),
            "referee": (gl(ib, "Referee", "text") or "") or "",
            "coach_h": gl(lu, "homeTeam", "coach", "name"), "coach_a": gl(lu, "awayTeam", "coach", "name"),
            "form_h": gl(lu, "homeTeam", "formation"), "form_a": gl(lu, "awayTeam", "formation"),
            "rating_h": gl(lu, "homeTeam", "rating"), "rating_a": gl(lu, "awayTeam", "rating"),
            "pom": mf.get("playerOfTheMatch") or {},
            "h2h": (c.get("h2h") or {}).get("summary")}


def fm_date_status(date="20260912"):
    """FotMob 按日期接口（一次拿全批·快路径）：返回 {no: {'finished':bool,'score':(h,a),'started':bool}}"""
    out = {}
    cache = O / ("fm_date_%s.json" % date)
    rc, body = sh(["curl.exe", "-s", "-m", "40", "-H", HDR,
                   "https://www.fotmob.com/api/data/matches?date=%s" % date])
    if (body or "").strip().startswith("{"):
        cache.write_text(body, encoding="utf-8")
    elif cache.exists():
        body = cache.read_text(encoding="utf-8")
    else:
        return out
    try:
        j = json.loads(body)
    except Exception:
        return out
    want = {int(v): k for k, v in IDS.items()}
    for lg in j.get("leagues", []):
        for m in lg.get("matches", []):
            mid = m.get("id")
            if mid in want:
                st = m.get("status") or {}
                h, a = (m.get("home") or {}), (m.get("away") or {})
                out[want[mid]] = {"finished": bool(st.get("finished")), "started": bool(st.get("started")),
                                  "score": (h.get("score"), a.get("score"))}
    return out


def official_scores():
    """官方快照解析（fetch_official_snap.py 生成 official_snap_2.txt）
    格式：周六NNN ｜ 联赛 ｜ 09-12HH:MM ｜ 主队 ｜ 主FT ｜ : ｜ 客FT ｜ 客队 ｜ 主HT ｜ : ｜ 客HT ｜ 加时 ｜ 状态
    """
    p = O / "official_snap_2.txt"
    if not p.exists():
        return {}
    t = p.read_text(encoding="utf-8")
    out = {}
    pat = re.compile(r"周六(\d{3})\|([^|]+)\|([\d\-]+[\d:]*)\|([^|]+)\|(\d+)\|:\|(\d+)\|([^|]+)\|(\d*)\|:\|(\d*)\|([^|]*)\|([^|]+)")
    for m in pat.finditer(t):
        no, lg, tm, h, hf, af, a, hh, ah, extra, st = (x.strip() for x in m.groups())
        out[no] = {"home": h, "away": a, "ft": (int(hf), int(af)),
                   "ht": (int(hh), int(ah)) if hh.isdigit() and ah.isdigit() else None,
                   "status": st, "done": ("直播结束" in st or "完" in st)}
    return out


def verdicts(no, mt, act):
    """四维机械判定（mt=票面, act=实际）"""
    i, j = act["hs"], act["as"]
    toks = [x.strip() for x in mt["sc"].split("/")]
    def tok_hit(t):
        if not re.match(r"^\d+-\d+", t):
            cls = {"胜其它": "胜", "负其它": "负", "平其它": "平"}.get(t)
            if not cls:
                return False
            real = "胜" if i > j else ("负" if j > i else "平")
            if real != cls:
                return False
            return (i, j) not in PANEL
        a, b = (int(x) for x in t.rstrip("*").split("-"))
        return (a, b) == (i, j)
    s_hit = any(tok_hit(t) for t in toks)
    t1_hit = tok_hit(toks[0])
    d = mt["dir"].split("（")[0]
    real = "主胜" if i > j else ("客胜" if j > i else "平")
    d_hit = real in d
    hi, hj = act["ht"]
    pair = ("胜" if hi > hj else ("负" if hj > hi else "平")) + ("胜" if i > j else ("负" if j > i else "平"))
    h_hit = any(x.strip().rstrip("*") == pair for x in mt["ht"].split("/"))
    tot = i + j
    nums = set(int(x) for x in re.findall(r"\d", mt["ou"]))
    o_hit = tot in nums
    return {"d": "ok" if d_hit else "no", "s": "ok" if s_hit else "no", "h": "ok" if h_hit else "no",
            "ou": "ok" if o_hit else "no", "score": "%d-%d" % (i, j), "ht_pair": pair,
            "top1": t1_hit, "n_hit": sum([d_hit, s_hit, h_hit, o_hit])}


def main():
    dj = (JS / "data.js").read_text(encoding="utf-8")
    dr = (JS / "data-review.js").read_text(encoding="utf-8")
    si = dj.index('"2026-09-12": {')
    tickets = {}
    for m in re.finditer(r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)",[\s\S]*?dir: "([^"]+)",[\s\S]*?scores: "([^"]+)", ht: "([^"]+)", ou: "([^"]+)"', dj[si:]):
        tickets[m.group(1)] = {"home": m.group(2), "away": m.group(3), "dir": m.group(4),
                               "sc": m.group(5), "ht": m.group(6), "ou": m.group(7)}
    # 已入库场次（0912 块内 results 的 no 列表·容忍字段间隔）
    blk_start = dr.index('"2026-09-12": {')
    nxt = re.search(r'\n  "2026-\d\d-\d\d": \{', dr[blk_start + 10:])
    blk_end = blk_start + 10 + nxt.start() if nxt else len(dr)
    seg = dr[blk_start:blk_end]
    done = set(re.findall(r'no: "(\d+)", teams: "[^"]*",[\s\S]{0,200}?score: "\d+-\d+', seg))
    todo = [n for n in sorted(tickets) if n not in done and (ONLY is None or n in ONLY)]
    print("待复盘 %d 场：%s（已入库 %d 场）" % (len(todo), ",".join(todo), len(done)))
    off = official_scores()
    fmd = fm_date_status()
    print("官方快照场次：%s｜FotMob 日期接口命中：%d 场（finished=%d）" % (
        ",".join(sorted(off)) if off else "缺",
        len(fmd), sum(1 for v in fmd.values() if v["finished"])))
    rows, mism = [], []
    for no in todo:
        o = off.get(no) or {}
        fd = fmd.get(no) or {}
        # ① 先过状态门（快路径·零成本）：未终场直接跳过，不抓详情
        if not (fd.get("finished") or o.get("done")):
            print("  … %s 未终场（FotMob 日期接口/官方均未终场）跳过" % no)
            continue
        # ② 终场 → 抓 FotMob 详情
        j = fetch_fm(no)
        if not j:
            print("  ⚠ %s FotMob 取数失败" % no); continue
        a = parse(no, j)
        v = verdicts(no, tickets[no], a)
        ok2 = True
        if o.get("ft"):
            if (o["ft"][0], o["ft"][1]) != (a["hs"], a["as"]):
                ok2 = False
                mism.append("%s(FM %d-%d vs 官方 %d-%d)" % (no, a["hs"], a["as"], o["ft"][0], o["ft"][1]))
        if o.get("ht") and (o["ht"][0], o["ht"][1]) != a["ht"]:
            mism.append("%s半场(FM %d-%d vs 官方 %d-%d)" % (no, a["ht"][0], a["ht"][1], o["ht"][0], o["ht"][1]))
        flag = "✅" if ok2 else "❌双源不一致"
        print("  %s %s %s-%s（半场 %d-%d）%d/4 d=%s s=%s h=%s ou=%s %s%s" % (
            no, tickets[no]["home"], a["hs"], a["as"], a["ht"][0], a["ht"][1],
            v["n_hit"], v["d"], v["s"], v["h"], v["ou"], flag,
            "［官方/日期源终场门］" if (fd.get("finished") or o.get("done")) and not a["ft_finished"] else ""))
        rows.append({"no": no, "act": a, "v": v, "mt": tickets[no], "dual_ok": ok2})
    (O / "auto_review_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n判定完成 %d 场（写入 auto_review_rows.json）%s" % (
        len(rows), "；⚠ 双源不一致：%s（需人工核验，勿入库）" % ",".join(mism) if mism else ""))
    print("DRY-RUN：未写库" if DRY else "下一步由入库器消费 auto_review_rows.json（见 auto_ingest_reviews.py）")


if __name__ == "__main__":
    main()
