# -*- coding: utf-8 -*-
"""避雷名单自动判定器 V1.0（2026-08-16）
输入：FotMob matchDetails JSON 列表（含 stats.Periods + events）
输出：每场比赛各队伍演戏评分 + 建议（观察/高信号/保持/降级）

信号分值：
  R327 占优惨败（控球≥55%+射正持平/占优却输≥2球）      +3
  R324 转化率倒挂（>30% vs <15%）                      +3
  R328 领先收缩（半场领先≥2球+下半场丢≥2球）           +3
  数据-结果割裂（射门/xG/控球全面占优仍输）            +3
  R322 闪击收工（开场≤5'进球+后半场无第2球）           +2
  补时绝杀/绝平（90+3'后定胜负）                       +2
  跨线球（尾声进球跨 2.5/3.5/4.5/5.5 线）              +2
  最佳球员在输球方                                    +2
  换下进球者后丢球（88'换人+2'内丢）                   +2
  赢球方低 xG 高效（xG 落后仍赢≥2球）                  +2
  主队排名差≥4位却输球（R321 野鸡系数）                +2

阈值：
  单场 ≥6 = 🔴 高信号
  单场 3-5 = 🟡 观察
  跨场累计 ≥9 或同类重复2次 = 升级 🔴
  跨场累计 5-8 = 保持 🟡
  跨场累计 <5 且无新信号 = 降级/移除
"""
import json, sys, glob, math
sys.stdout.reconfigure(encoding='utf-8')

# ---------- 工具 ----------
def load_match(path):
    """读取 FotMob matchDetails JSON，返回规范化结构"""
    d = json.load(open(path, encoding='utf-8'))
    g = d.get('general', {})
    hd = d.get('header', {})
    st = hd.get('status', {})
    teams = hd.get('teams', [])
    score = st.get('scoreStr', '')
    # 解析比分
    m = score.split('-')
    home_score = int(m[0].strip()) if len(m) > 1 else 0
    away_score = int(m[1].strip()) if len(m) > 1 else 0
    # 统计
    stats = d.get('content', {}).get('stats', {})
    all_s = stats.get('Periods', {}).get('All', {}).get('stats', [])
    stmap = {}
    def walk(items):
        for it in items:
            if not isinstance(it, dict):
                continue
            st = it.get('stats')
            if isinstance(st, list) and st and all(isinstance(x, (int, float)) for x in st):
                stmap[it.get('key', it.get('title', '?'))] = st
            elif isinstance(st, list) and st:
                walk(st)
    walk(all_s)
    # 补充：有些场次 stats 在 stats.stats 直接列表（旧结构兼容）
    if not stmap:
        raw_stats = d.get('content', {}).get('stats', {})
        for k, v in raw_stats.items():
            if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
                stmap[k] = v
    # 事件
    events = d.get('content', {}).get('matchFacts', {}).get('events', {})
    evs = events.get('events', [])
    goals = []
    cards = []
    subs = []
    for e in evs:
        t = e.get('type', '')
        mins = e.get('time', 0) or e.get('minute', 0) or 0
        ot = e.get('overloadTime', 0) or 0
        is_home = e.get('isHome')
        if t in ('Goal', 'Penalty goal', 'Own goal'):
            goals.append({'min': mins, 'ot': ot, 'is_home': is_home, 'player': (e.get('player', {}) or {}).get('name', '?'),
                          'hs': e.get('homeScore'), 'as': e.get('awayScore'), 'desc': e.get('goalDescription', '')})
        elif t == 'Substitution':
            swap = e.get('swap', [])
            pin = swap[0].get('name') if swap and isinstance(swap[0], dict) else '?'
            pout = swap[1].get('name') if len(swap) > 1 and isinstance(swap[1], dict) else '?'
            subs.append({'min': mins, 'is_home': is_home, 'in': pin, 'out': pout})
        elif t == 'Card':
            cards.append({'min': mins, 'is_home': is_home, 'player': (e.get('player', {}) or {}).get('name', '?')})
    return {
        'matchName': g.get('matchName', '?'),
        'leagueName': g.get('leagueName', '?'),
        'home': (teams[0].get('name', '?') if teams else '?'),
        'away': (teams[1].get('name', '?') if len(teams) > 1 else '?'),
        'hs': home_score, 'as': away_score,
        'stats': stmap, 'goals': goals, 'subs': subs, 'cards': cards,
        'finished': st.get('finished', False),
    }

def get_st(match, key):
    """取完整统计列表 [主, 客]"""
    s = match['stats'].get(key)
    return s if isinstance(s, list) else None

# ---------- 评分器 ----------
def score_match(match):
    """对一场比赛打分，返回 {队伍名: 分数, 信号明细}"""
    home, away = match['home'], match['away']
    hs, as_ = match['hs'], match['as']
    result = {}
    def add(team, pts, sig):
        if team not in result:
            result[team] = {'score': 0, 'signals': []}
        result[team]['score'] += pts
        result[team]['signals'].append(f"{sig}(+{pts})")

    # 1. R327 占优惨败：控球≥55% +（射门或角球占优）+ 输≥2球
    #    控球+射门（或角球）全面占优却大败 = 占优惨败完整形态
    poss = get_st(match, 'BallPossesion')
    shots = get_st(match, 'total_shots')
    sot = get_st(match, 'ShotsOnTarget')
    corners = get_st(match, 'corners')
    if poss and shots:
        for side, team, opp_score in [(0, home, as_), (1, away, hs)]:
            p = poss[side]
            sh = shots[side]
            osh = shots[1 - side]
            cr = corners[side] if corners else 0
            ocr = corners[1 - side] if corners else 0
            my_score = hs if side == 0 else as_
            if p >= 55 and (sh >= osh or cr >= ocr) and opp_score - my_score >= 2:
                add(team, 3, f"R327占优惨败(控球{p}%射门{sh}:{osh}角球{cr}:{ocr}却输{opp_score-my_score}球)")

    # 2. R324 转化率倒挂：一方 >30% 且对手 <15%
    if sot and shots:
        for side, team in [(0, home), (1, away)]:
            conv = sot[side] / shots[side] if shots[side] else 0
            oconv = sot[1-side] / shots[1-side] if shots[1-side] else 0
            if conv > 0.3 and oconv < 0.15:
                add(team, 3, f"R324转化率倒挂({conv*100:.0f}%vs{oconv*100:.0f}%)")

    # 3. 数据-结果割裂：射门+控球双占优仍输
    if shots and poss:
        for side, team, opp_score in [(0, home, as_), (1, away, hs)]:
            if shots[side] >= shots[1-side] * 1.5 and poss[side] >= 55 and opp_score >= (hs if side == 0 else as_) + 2:
                add(team, 3, f"数据-结果割裂(射门{shots[side]}:{shots[1-side]}控球{poss[side]}%仍输)")

    # 4. 补时绝杀/绝平（90+3'后定胜负）
    for g in match['goals']:
        if g['min'] >= 90 and g['ot'] >= 3:
            side_team = home if g['is_home'] is True else away
            add(side_team, 2, f"补时进球({g['min']}+{g['ot']}' {g['player']})")

    # 5. R322 闪击收工：开场≤15'有进球 + 该队全场进球≥2（闪击爆发）
    #    简化：开场≤15'的进球 + 总进球≥3 视为闪击段爆发
    early_goals = [g for g in match['goals'] if g['min'] <= 15]
    if early_goals and (hs + as_) >= 3:
        for g in early_goals:
            side_team = home if g['is_home'] is True else away
            add(side_team, 2, f"R322闪击({g['min']}'进球,全场{hs+as_}球)")

    # 6. 跨线球：尾声段（≥75'）进球跨整数线
    total = hs + as_
    for g in match['goals']:
        if g['min'] >= 75:
            gtotal = (g['hs'] or 0) + (g['as'] or 0)
            for line in [2.5, 3.5, 4.5, 5.5]:
                if gtotal > line and gtotal - 1 <= line:
                    side_team = home if g['is_home'] is True else away
                    add(side_team, 2, f"尾声跨线球({g['min']}' 跨{line})")

    # 7. R328 领先收缩：半场领先≥2球 + 被追（需半场比分，简化：赢球方净胜≥2球但被追≥2球=收缩）
    for side, team, opp_score in [(0, home, as_), (1, away, hs)]:
        my_score = hs if side == 0 else as_
        if my_score - opp_score >= 2 and opp_score >= 2:
            add(team, 2, f"R328领先收缩(净胜{my_score-opp_score}球但被追{opp_score}球)")

    # 7. 最佳球员在输球方（简化：跳过，需要额外字段）
    # 8. 赢球方低 xG 高效（xG 数据常缺失，跳过）
    return result

# ---------- 主流程 ----------
if __name__ == '__main__':
    files = sys.argv[1:]
    json_mode = '--json' in files
    if json_mode:
        files = [f for f in files if f != '--json']
    if not files:
        print("用法: python avoid_scorer.py [--json] <matchDetails.json> ...")
        sys.exit(1)
    all_scores = {}
    match_results = []
    for f in files:
        try:
            match = load_match(f)
        except Exception as e:
            print(f"{f}: 读取失败 {e}")
            continue
        if not match['finished']:
            print(f"{f}: 未完赛，跳过")
            continue
        scores = score_match(match)
        # 联赛：用 general.leagueName
        league = match['leagueName']
        if not league or league == '?':
            for kw, lg in [('K-League', '韩职'), ('Allsvenskan', '瑞超'), ('Eliteserien', '挪超'),
                           ('Veikkausliiga', '芬超'), ('Premier League', '英超'), ('LaLiga', '西甲'),
                           ('Championship', '英冠'), ('Community Shield', '英社区盾'), ('Serie A', '巴甲'),
                           ('Eredivisie', '荷甲')]:
                if kw in match['matchName']:
                    league = lg
                    break
        if json_mode:
            match_results.append({
                'name': match['matchName'], 'short_name': f"{match['home']} vs {match['away']} {match['hs']}-{match['as']}",
                'league': league, 'home': match['home'], 'away': match['away'],
                'hs': match['hs'], 'as': match['as'], 'scores': scores
            })
        else:
            print(f"===== {match['matchName']} {match['hs']}-{match['as']} =====")
            for team, info in sorted(scores.items(), key=lambda x: -x[1]['score']):
                lv = "🔴 高信号" if info['score'] >= 6 else ("🟡 观察" if info['score'] >= 3 else "低信号")
                print(f"  {team}: {info['score']}分 [{lv}]")
                for sig in info['signals']:
                    print(f"    - {sig}")
                if team not in all_scores:
                    all_scores[team] = {'score': 0, 'matches': 0, 'signals': []}
                all_scores[team]['score'] += info['score']
                all_scores[team]['matches'] += 1
                all_scores[team]['signals'].extend(info['signals'])
            print()
    if json_mode:
        # 输出 JSON：matches + cumulative
        for team, info in all_scores.items():
            match_results.append({'cumulative': {team: info}})
        print(json.dumps(match_results, ensure_ascii=False))
    elif all_scores:
        print("========== 累计评分（跨场） ==========")
        for team, info in sorted(all_scores.items(), key=lambda x: -x[1]['score']):
            action = "升级🔴" if info['score'] >= 9 or info['matches'] >= 2 and info['score'] >= 9 else (
                "保持🟡" if info['score'] >= 5 else "观察/降级")
            print(f"  {team}: 累计{info['score']}分/{info['matches']}场 → {action}")
