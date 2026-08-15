# -*- coding: utf-8 -*-
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def full_probs(lh, la):
    probs = {}
    for h in range(0, 8):
        for a in range(0, 8):
            probs[(h, a)] = pois(h, lh) * pois(a, la)
    return probs

# 8/14 批次：每场 λ（联赛参数+状态，R6 视角）、实际赛果
# (no, 对阵, 联赛, λ主, λ客, 实际比分, 实际半场比分, R6方向, R6等级)
games = [
    ('001', '东京绿茵 vs 柏太阳神', '日职2.60', 1.3, 1.5, '1-3', '0-2', '负/平', 'B'),
    ('002', 'VPS瓦萨 vs TPS图尔库', '芬超2.69', 1.4, 1.3, '1-3', '0-2', '平/负', 'C'),
    ('003', '荷尔斯泰因 vs 圣保利', '德乙~2.6', 1.2, 1.4, '2-2', '0-2', '负/平', 'B'),
    ('004', '布伦瑞克 vs 波鸿', '德乙~2.6', 1.3, 1.3, '0-1', '0-1', '负/平', 'B'),
    ('005', '新未来城 vs 费哈', '沙特~2.7', 1.5, 1.2, '2-1', '2-0', '胜/平', 'B'),
    ('006', '埃尔夫斯堡 vs 瓦斯特拉斯', '瑞超3.07', 1.9, 1.2, '3-0', '1-0', '胜', 'A'),
    ('007', '罗森博格 vs 维京', '挪超2.94', 1.7, 1.3, '2-1', '1-0', '胜/平', 'B'),
    ('008', '达曼协作 vs 利雅得体育', '沙特~2.7', 1.5, 1.3, '4-2', '1-1', '胜/平', 'B'),
    ('009', '利雅得新月 vs 费萨里', '沙特~2.7', 2.6, 1.1, '4-2', '3-0', '胜', 'B'),
    ('010', '特尔斯达 vs 鹿特丹斯巴达', '荷甲3.15', 1.4, 1.6, '1-3', '0-1', '负/平', 'B'),
    ('011', '瓦尔韦克 vs 多德勒支', '荷乙~2.9', 1.7, 1.3, '2-2', '0-1', '胜/平', 'B'),
    ('012', '赫拉克勒斯 vs 邓伯什', '荷乙~2.9', 2.2, 1.0, '3-2', '1-0', '胜', 'B'),
    ('013', '昂纳西 vs 罗德兹', '法乙~2.3', 1.3, 1.1, '2-0', '1-0', '胜/平', 'B'),
    ('014', '兰斯 vs 敦刻尔克', '法乙~2.3', 1.5, 1.0, '3-3', '1-1', '胜/平', 'B'),
    ('015', '圣埃蒂安 vs 克莱蒙', '法乙~2.3', 1.8, 1.0, '3-1', '1-0', '胜', 'A'),
    ('016', '狼队 vs 布莱克本', '英冠~2.7', 1.7, 1.1, '2-2', '1-1', '胜/平', 'B'),
    ('017', '葡萄牙体育 vs 吉马良斯', '葡超2.60', 2.1, 0.9, '3-2', '3-0', '胜', 'B'),
]

def pick_scores(probs, direction, grade, n=8):
    """R6 选比：按方向分组，取泊松概率最高，按 ABC 结构"""
    win = [(k, p) for k, p in probs.items() if k[0] > k[1]]
    draw = [(k, p) for k, p in probs.items() if k[0] == k[1]]
    loss = [(k, p) for k, p in probs.items() if k[0] < k[1]]
    win.sort(key=lambda x: -x[1]); draw.sort(key=lambda x: -x[1]); loss.sort(key=lambda x: -x[1])
    main_dirs = []  # 主方向
    if '胜' in direction: main_dirs.append(win)
    if '平' in direction: main_dirs.append(draw)
    if '负' in direction: main_dirs.append(loss)
    # 反向 = 不在主方向里的
    rev_dirs = []
    for d in (win, draw, loss):
        if d not in main_dirs: rev_dirs.append(d)
    if grade == 'A':
        # 3 个主方向比分（去重比分）
        picks = []
        for d in main_dirs:
            for k, p in d:
                if k not in picks: picks.append(k)
                if len(picks) >= 3: break
            if len(picks) >= 3: break
    elif grade == 'B':
        picks = []
        for d in main_dirs:
            for k, p in d:
                if k not in picks: picks.append(k)
                if len(picks) >= 2: break
            if len(picks) >= 2: break
        for d in rev_dirs:
            for k, p in d:
                if k not in picks:
                    picks.append(k)
                    break
            if len(picks) >= 3: break
    else:  # C: 1主+2反
        picks = []
        for d in main_dirs:
            for k, p in d:
                picks.append(k); break
            break
        for d in rev_dirs:
            for k, p in d:
                if k not in picks:
                    picks.append(k)
                    if len(picks) >= 3: break
            if len(picks) >= 3: break
    return picks[:3]

def ht_for(score):
    """比分 → 半全场（R6 逐位对应：取该比分下概率最高的半全场形态）"""
    h, a = score
    if h > a:
        # 主胜：胜胜（半场领先）最常见，其次平胜
        return '胜胜' if h >= 2 and a <= 1 else '平胜'
    elif h == a:
        return '平平'
    else:
        return '负负' if a >= 2 and h <= 1 else '平负'

def ht_mark(i, grade):
    """反向位置标 *（B 第3位、C 第2/3位）"""
    if grade == 'B' and i == 2: return '*'
    if grade == 'C' and i >= 1: return '*'
    return ''

print('=' * 110)
print('R6 回测：8/14 批次 001-017 — 比分 TOP3 + 半全场 TOP3 完整推导')
print('=' * 110)
for no, teams, lg, lh, la, actual, half, direction, grade in games:
    probs = full_probs(lh, la)
    picks = pick_scores(probs, direction, grade)
    sc_str = ' / '.join(f'{h}-{a}' for h, a in picks)
    hts = [ht_for(s) for s in picks]
    ht_str = ' / '.join(hts[i] + ht_mark(i, grade) for i in range(3))
    # 判定
    act_score = tuple(map(int, actual.split('-')))
    s_hit = act_score in picks
    # 半全场：实际半场比分 → 实际半全场
    hh, ha = map(int, half.split('-'))
    fh, fa = map(int, actual.split('-'))
    act_ht = ('胜' if hh > ha else '平' if hh == ha else '负') + ('胜' if fh > fa else '平' if fh == fa else '负')
    h_hit = act_ht in [h.replace('*', '') for h in hts]
    # 方向
    dir_map = ('胜' if fh > fa else '平' if fh == fa else '负')
    d_hit = dir_map in direction
    # 概率标注
    p_str = ', '.join(f'{h}-{a}({p*100:.1f}%)' for (h, a), p in sorted(probs.items(), key=lambda x: -x[1])[:5])
    mark = lambda b: '✅' if b else '❌'
    print(f'{no} {teams} | {lg} λ{lh}/{la}')
    print(f'   R6预测: {direction}{grade} | 比分: {sc_str} | 半全场: {ht_str}')
    print(f'   实际: {actual}({half}) | 半全场={act_ht} | 方向{mark(d_hit)} 比分{mark(s_hit)} 半全场{mark(h_hit)}')
    print(f'   泊松TOP5: {p_str}')
    if not s_hit:
        near = [f'{h}-{a}' for (h, a) in sorted(probs.items(), key=lambda x: -x[1])[:10] if (h, a) == act_score]
        print(f'   ⚠️ 比分未命中: 实际{actual}在泊松TOP10排名={[i+1 for i,(k,p) in enumerate(sorted(probs.items(),key=lambda x:-x[1])[:12]) if k==act_score] or "12名以外"}')
    print()
