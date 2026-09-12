# -*- coding: utf-8 -*-
"""fm_full_extract.py — FotMob matchDetails 全量证据提取（复盘主源·v1）
输出：fm_ext_<no>.json（结构化）+ 屏幕可读摘要
覆盖：比分/半场/裁判/球场/观众/天气｜进球链+牌+换人｜全量统计（含 xG/xGOT/绝佳机会/防守项）｜
      射门图聚合（每队射门/xG/xGOT/情景）｜阵容与球员评分（首发均分/替补登场/教练/身价）｜
      两队近况逐场（teamForm·日期/对手/比分/W-D-L）｜H2H 逐场交锋史｜进攻区域｜动量
用法：python fm_full_extract.py 003 004 005
"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
O = r"D:\Cola\_tmp_football\sat0912"


def g(d, *ks, default=None):
    for k in ks:
        if isinstance(d, dict) and k in d:
            d = d[k]
        elif isinstance(d, list) and isinstance(k, int) and 0 <= k < len(d):
            d = d[k]
        else:
            return default
    return d


def pname(v):
    """球员字段可能是 str 或 {'name': ...} 字典"""
    if isinstance(v, dict):
        return v.get("name") or g(v, "name", "fullName") or ""
    return v or ""


def side_of(e):
    return "主" if e.get("isHome") else "客"


for no in sys.argv[1:]:
    p = os.path.join(O, "res_fm_%s.json" % no)
    j = json.load(io.open(p, encoding="utf-8"))
    gp, hd, c = j.get("general") or {}, j.get("header") or {}, j.get("content") or {}
    mf = c.get("matchFacts") or {}
    ib = mf.get("infoBox") or {}
    teams = hd.get("teams") or []
    H = {"no": no, "fotmob_id": gp.get("matchId"), "finished": gp.get("finished"),
         "home": g(teams, 0, "name") or "", "away": g(teams, 1, "name") or "",
         "hs": g(teams, 0, "score"), "as": g(teams, 1, "score"),
         "league": g(ib, "Tournament", "leagueName"), "round": g(ib, "Tournament", "roundName"),
         "stadium": g(ib, "Stadium", "name"), "city": g(ib, "Stadium", "city"),
         "attendance": ib.get("Attendance"), "referee": g(ib, "Referee", "text") or ib.get("Referee"),
         "weather": c.get("weather"), "status_raw": hd.get("status")}
    # 半场比分（FotMob: header.status.scoreStr 常为全场；用前 45 分钟进球推算）
    evs = (mf.get("events") or {}).get("events") or []
    hg = ag = 0
    goals, cards, subs = [], [], []
    for e in evs:
        t = e.get("timeStr") or str(e.get("time"))
        who = pname(e.get("player") or e.get("name"))
        minute = e.get("time") or 0
        if e.get("type") == "Goal":
            s = side_of(e)
            tag = "点球" if e.get("isPenalty") else ("乌龙" if e.get("ownGoal") else "")
            goals.append("%s′ %s（%s）%s" % (t, who, s, tag))
            if minute <= 45:
                if s == "主":
                    hg += 1
                else:
                    ag += 1
        elif e.get("type") == "Card":
            cards.append("%s′ %s（%s·%s）" % (t, who, side_of(e), e.get("card") or ""))
        elif e.get("type") == "substitution" or e.get("type") == "Substitution":
            subs.append("%s′ %s↔%s（%s）" % (t, who, e.get("swap") or e.get("name2") or "", side_of(e)))
    H["goals"], H["cards"], H["subs"] = goals, cards, subs
    H["ht_est"] = "%d-%d" % (hg, ag)
    H["ht_official_hint"] = g(hd, "status", "scoreStr")
    # 统计
    grp = ((g(c, "stats", "Periods", "All") or {}).get("stats")) or []
    stats = []
    for grpitem in grp:
        for it in (grpitem.get("stats") or []):
            v = it.get("stats")
            if isinstance(v, list) and len(v) == 2 and v[0] is not None:
                stats.append((it.get("title") or it.get("key"), v[0], v[1]))
    H["stats"] = stats
    # 射门图聚合
    shots = (c.get("shotmap") or {}).get("shots") or []
    tid_h, tid_a = g(teams, 0, "id"), g(teams, 1, "id")
    agg = {"主": {"n": 0, "xG": 0.0, "xGOT": 0.0, "on": 0, "goal": 0, "sit": {}},
           "客": {"n": 0, "xG": 0.0, "xGOT": 0.0, "on": 0, "goal": 0, "sit": {}}}
    for s in shots:
        k = "主" if s.get("teamId") == tid_h else "客"
        a = agg[k]
        a["n"] += 1
        a["xG"] += float(s.get("expectedGoals") or 0)
        a["xGOT"] += float(s.get("expectedGoalsOnTarget") or 0)
        a["on"] += 1 if s.get("isOnTarget") else 0
        a["goal"] += 1 if s.get("eventType") == "Goal" else 0
        sit = s.get("situation") or "?"
        a["sit"][sit] = a["sit"].get(sit, 0) + 1
    H["shotmap_agg"] = agg
    # 阵容/评分
    lu = c.get("lineup") or {}
    for k, side in (("homeTeam", "主"), ("awayTeam", "客")):
        t = lu.get(k) or {}
        H["lineup_" + side] = {
            "team": t.get("name"), "formation": t.get("formation"), "rating": t.get("rating"),
            "avg_age": t.get("averageStarterAge"), "market_value": t.get("totalStarterMarketValue"),
            "coach": g(t, "coach", "name"),
            "starters": [(p2.get("name"), g(p2, "performance", "rating"), p2.get("shirtNumber"))
                         for p2 in (t.get("starters") or [])],
            "subs_used": [(p2.get("name"), g(p2, "performance", "rating"),
                           [(ev.get("time"), ev.get("type")) for ev in (g(p2, "performance", "substitutionEvents") or [])])
                          for p2 in (t.get("subs") or []) if g(p2, "performance", "substitutionEvents")]}
    # 球员评分 TOP（全场）
    ps = c.get("playerStats") or {}
    tops = []
    for pid, pv in (ps.items() if isinstance(ps, dict) else []):
        rt = None
        for s in (pv.get("stats") or []):
            stt = s.get("stats") or {}
            if "FotMob rating" in stt:
                rt = g(stt, "FotMob rating", "stat", "value")
        if rt:
            tops.append((pv.get("name"), pv.get("teamName"), rt))
    H["top_ratings"] = sorted(tops, key=lambda z: -(z[2] or 0))[:8]
    H["player_of_match"] = {"name": g(mf, "playerOfTheMatch", "name", "fullName"),
                            "team": g(mf, "playerOfTheMatch", "teamName"),
                            "rating": g(mf, "playerOfTheMatch", "rating", "num")}
    # 近况逐场（teamForm = [主队近场[], 客队近场[]]）
    tf = mf.get("teamForm") or []
    def fmt_form(lst, own_id):
        out = []
        for m in (lst or []):
            tt = m.get("tooltipText") or {}
            d = (m.get("date") or {}).get("utcTime", "")[:10]
            hs, as_ = tt.get("homeScore"), tt.get("awayScore")
            home, away = tt.get("homeTeam"), tt.get("awayTeam")
            ha = "主" if str(tt.get("homeTeamId")) == str(own_id) else "客"
            opp = away if ha == "主" else home
            out.append("%s %s %s vs %s %s-%s %s" % (d, m.get("resultString"), ha, opp, hs, as_, m.get("score")))
        return out
    H["form_home"] = fmt_form(tf[0] if len(tf) > 0 else [], tid_h)
    H["form_away"] = fmt_form(tf[1] if len(tf) > 1 else [], tid_a)
    # H2H 逐场
    h2h = (c.get("h2h") or {})
    H["h2h_summary"] = h2h.get("summary")
    H["h2h_all"] = len(h2h.get("matches") or [])
    H["h2h"] = []
    for m in (h2h.get("matches") or []):
        hs_, as_ = g(m, "home", "score"), g(m, "away", "score")
        if hs_ is None or as_ is None:
            continue
        H["h2h"].append("%s %s %s-%s %s（%s%s）" % ((m.get("time") or {}).get("utcTime", "")[:10],
                                                    g(m, "home", "name"), hs_, as_, g(m, "away", "name"),
                                                    g(m, "league", "name"),
                                                    "" if m.get("finished") else "·未开赛"))
    H["h2h"] = H["h2h"][:10]
    H["attacking_zones"] = c.get("attackingZones")
    json.dump(H, io.open(os.path.join(O, "fm_ext_%s.json" % no), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("=" * 100)
    print("[%s] %s %s-%s %s｜HT(推算) %s｜%s R%s｜%s｜裁判 %s｜观众 %s" % (
        no, H["home"], H["hs"], H["as"], H["away"], H["ht_est"], H["league"], H["round"],
        H["stadium"], H["referee"], H["attendance"]))
    w = H["weather"] or {}
    print("  天气：%s℃/湿度%s%%/风%s/降水%s｜%s" % (w.get("temperature"), w.get("relativeHumidity"),
                                                    w.get("windSpeed"), w.get("precipitation"), w.get("description")))
    print("  进球链：%s" % " → ".join(goals))
    print("  牌：%s｜换人：%s" % ("；".join(cards) or "无", "；".join(subs[:8]) or "无"))
    print("  射门图：主 %s｜客 %s" % (agg["主"], agg["客"]))
    print("  阵容：主 %s %s（均分 %s·均龄 %s）｜客 %s %s（均分 %s·均龄 %s）" % (
        H["lineup_主"]["formation"], H["lineup_主"]["coach"], H["lineup_主"]["rating"], H["lineup_主"]["avg_age"],
        H["lineup_客"]["formation"], H["lineup_客"]["coach"], H["lineup_客"]["rating"], H["lineup_客"]["avg_age"]))
    print("  POM：%s（%s·%s）" % (H["player_of_match"]["name"], H["player_of_match"]["team"], H["player_of_match"]["rating"]))
    print("  评分 TOP5：%s" % "；".join("%s(%s) %s" % t for t in H["top_ratings"][:5]))
    print("  主队近况逐场：%s" % " ｜ ".join(H["form_home"][:6]))
    print("  客队近况逐场：%s" % " ｜ ".join(H["form_away"][:6]))
    print("  H2H 汇总 %s｜逐场：%s" % (H["h2h_summary"], " ｜ ".join(H["h2h"][:6])))
print("\n已写 fm_ext_<no>.json")
