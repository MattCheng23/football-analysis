# -*- coding: utf-8 -*-
"""V10.36 赛后自动核查：FT 拉取 → 数据提取 → 演戏排查六项初筛 → 跨线球
用法：python post_match_check.py <matchId> [<matchId> ...]
输出：每场 JSON 报告 + 文本摘要（人工复核异常项）
"""
import sys, io, json, subprocess, re, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = "https://www.fotmob.com/api/data/matchDetails?matchId={}"
HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

def fetch(mid):
    r = subprocess.run(HEAD + [API.format(mid)], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

def check(mid):
    d = fetch(mid)
    if "error" in d:
        return {"matchId": mid, "error": d.get("message")}
    g = d.get("general", {})
    st = (d.get("header", {}) or {}).get("status", {})
    if not st.get("finished"):
        return {"matchId": mid, "status": "未完赛", "score": st.get("scoreStr")}
    home = g.get("homeTeam", {}).get("name")
    away = g.get("awayTeam", {}).get("name")
    score = st.get("scoreStr", "").replace(" ", "")
    m = re.match(r"^(\d+)-(\d+)$", score)
    if not m:
        return {"matchId": mid, "status": "比分异常", "score": score}
    fh, fa = int(m.group(1)), int(m.group(2))

    # 事件：进球/红牌（含时间线）
    ev = (d.get("header", {}) or {}).get("events", {}) or {}
    goals = []   # (minute, team, who)
    reds = []
    def evlist(key):
        v = ev.get(key, {})
        return v if isinstance(v, dict) else {}
    for pname, arr in evlist("homeTeamGoals").items():
        for e in arr:
            goals.append((e.get("time", 0), "home", pname))
    for pname, arr in evlist("awayTeamGoals").items():
        for e in arr:
            goals.append((e.get("time", 0), "away", pname))
    for pname, arr in evlist("homeTeamRedCards").items():
        for e in arr:
            reds.append((e.get("time", 0), "home", pname))
    for pname, arr in evlist("awayTeamRedCards").items():
        for e in arr:
            reds.append((e.get("time", 0), "away", pname))
    goals.sort()
    reds.sort()

    # 半场比分（time<=45 上半场）
    ht_h = sum(1 for t, side, _ in goals if t <= 45 and side == "home")
    ht_a = sum(1 for t, side, _ in goals if t <= 45 and side == "away")

    # shotmap 统计（射门/射正/xG/进球）
    sm = (d.get("content", {}) or {}).get("shotmap", {}) or {}
    shots = sm.get("shots", []) or []
    stat = {}
    for s in shots:
        tid = s.get("teamId")
        t = stat.setdefault(tid, {"shots": 0, "on": 0, "xg": 0.0})
        t["shots"] += 1
        if s.get("isOnTarget"):
            t["on"] += 1
        t["xg"] += s.get("expectedGoals", 0) or 0
    tid_h = g.get("homeTeam", {}).get("id")
    tid_a = g.get("awayTeam", {}).get("id")
    sh = stat.get(tid_h, {}); sa = stat.get(tid_a, {})

    # 最佳球员
    potm = ((d.get("content", {}) or {}).get("matchFacts", {}) or {}).get("playerOfTheMatch", {}) or {}
    potm_team = potm.get("teamId")

    # ---- 演戏排查六项 + 跨线 ----
    signals = []
    total_goals = fh + fa
    lose_tid = tid_a if fh > fa else tid_h
    win_tid = tid_h if fh > fa else tid_a
    if sh.get("shots") and sa.get("shots"):
        ratio = max(sh["shots"], sa["shots"]) / max(1, min(sh["shots"], sa["shots"]))
        # R326：赢球方 85' 后连丢 ≥2 球（放水/收窄）——85' 后进球属于【输球方】才算
        late_loser = [t for t, side, _ in goals if t >= 85 and ((side == "home" and lose_tid == tid_h) or (side == "away" and lose_tid == tid_a))]
        if ratio >= 2.5 and len(late_loser) >= 2:
            signals.append(f"R326 碾压收窄候选：射门比 {ratio:.1f} + 赢球方85'后连丢{len(late_loser)}球")
        # 转化率（胜方 vs 负方）
        if fh != fa:
            wg = fh if win_tid == tid_h else fa
            lg_ = fa if win_tid == tid_h else fh
            wconv = wg / max(1, stat.get(win_tid, {}).get("on", 0))
            lconv = lg_ / max(1, stat.get(lose_tid, {}).get("on", 0))
            if wconv > 0.3 and lconv < 0.15 and wconv > lconv * 2:
                signals.append(f"R324 转化率倒挂候选：胜方 {wconv:.0%} vs 负方 {lconv:.0%}")
    # R327 占优惨败：输球方射门/xG 全面占优
    if fh != fa:
        lstat = stat.get(lose_tid, {})
        wstat = stat.get(win_tid, {})
        if lstat.get("shots", 0) > wstat.get("shots", 0) * 1.3 and lstat.get("xg", 0) > wstat.get("xg", 0) * 1.3:
            signals.append(f"R327 占优惨败候选：输球方射门 {lstat.get('shots')} vs {wstat.get('shots')}、xG {lstat.get('xg',0):.2f} vs {wstat.get('xg',0):.2f}")
    # R328 半场领先收缩
    if ht_h - ht_a >= 2 and fh <= fa:
        signals.append(f"R328 半场领先收缩候选：半场 {ht_h}-{ht_a} 终场 {fh}-{fa}")
    elif ht_a - ht_h >= 2 and fa <= fh:
        signals.append(f"R328 半场领先收缩候选：半场 {ht_a}-{ht_h}(客) 终场 {fa}-{fh}")
    # R322 闪击收工
    if goals and goals[0][0] <= 5 and total_goals <= 2:
        signals.append(f"R322 闪击收工候选：{goals[0][0]}' 进球全场仅 {total_goals} 球")
    # 补时/尾声剧本 + 跨线球
    cur = 0
    crossing = []
    for t, side, _ in sorted(goals):
        cur += 1
        if t >= 85:
            for line in (2.5, 3.5, 4.5, 5.5):
                if cur - 1 < line < cur:
                    crossing.append(f"{t}' 第{cur}球跨{line}线")
    if crossing:
        signals.append("尾声跨线：" + "、".join(crossing))
    # 最佳球员在输球方
    if potm_team and fh != fa:
        if (fh < fa and potm_team == tid_h) or (fa < fh and potm_team == tid_a):
            signals.append("最佳球员在输球方（黑天鹅/异常信号）")
    # 红牌（事实信息，不计入演戏信号权重）
    red_note = f"；红牌 {len(reds)} 张（{'、'.join(f'{t}\' {p}' for t, _, p in reds)}）" if reds else ""

    report = {
        "matchId": mid, "teams": f"{home} {score} {away}",
        "ft": [fh, fa], "ht": [ht_h, ht_a], "total_goals": total_goals,
        "shots": f"{sh.get('shots', '?')}:{sa.get('shots', '?')}",
        "onTarget": f"{sh.get('on', '?')}:{sa.get('on', '?')}",
        "xG": f"{sh.get('xg', 0):.2f}:{sa.get('xg', 0):.2f}",
        "reds": [f"{t}' {p}" for t, _, p in reds],
        "goal_timeline": [f"{t}'{p}" for t, _, p in goals],
        "signals": signals,
        "verdict": "🔴 嫌疑" if len(signals) >= 2 else ("🟡 观察" if signals else "无异常"),
    }
    if red_note:
        report["note"] = red_note.lstrip("；")
    return report

for mid in sys.argv[1:]:
    try:
        r = check(mid)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        print()
    except Exception as e:
        print(f"{mid}: ERR {e}")
