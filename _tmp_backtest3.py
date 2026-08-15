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

def dir_of(k):
    h, a = k
    return '胜' if h > a else ('平' if h == a else '负')

def pick_scores(probs, direction, grade):
    """R6 选比：主方向 = 全局概率最高的主方向比分；反向 = 概率最高的反向比分"""
    all_sorted = sorted(probs.items(), key=lambda x: -x[1])
    main_dirs = [d for d in '胜平负' if d in direction]
    picks = []
    for k, p in all_sorted:
        if dir_of(k) in main_dirs and k not in picks:
            picks.append(k)
            if grade == 'A' and len(picks) >= 3: break
            if grade == 'B' and len(picks) >= 2: break
            if grade == 'C' and len(picks) >= 1: break
    for k, p in all_sorted:
        if dir_of(k) not in main_dirs and k not in picks:
            picks.append(k)
            if len(picks) >= 3: break
    return picks[:3]

def ht_for(score):
    """比分 → 半全场（该比分下最常见的半场形态）"""
    h, a = score
    if h > a:
        return '胜胜' if (h >= 2 and a <= 1) or (h == 2 and a == 1) else '平胜'
    elif h == a:
        return '平平'
    else:
        return '负负' if (a >= 2 and h <= 1) or (a == 2 and h == 1) else '平负'

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

print('=' * 108)
print('R6 回测：8/14 批次 — 比分 TOP3 + 半全场 TOP3 完整推导（修正版）')
print('=' * 108)
tot = {'d': 0, 's': 0, 'h': 0}
for no, teams, lg, lh, la, actual, half, direction, grade in games:
    probs = full_probs(lh, la)
    picks = pick_scores(probs, direction, grade)
    sc_str = ' / '.join(f'{h}-{a}' for h, a in picks)
    hts = [ht_for(s) for s in picks]
    ht_marks = ['*' if (grade == 'B' and i == 2) or (grade == 'C' and i >= 1) else '' for i in range(3)]
    ht_str = ' / '.join(hts[i] + ht_marks[i] for i in range(3))
    # 实际判定
    act_score = tuple(map(int, actual.split('-')))
    hh, ha = map(int, half.split('-')); fh, fa = map(int, actual.split('-'))
    act_dir = '胜' if fh > fa else ('平' if fh == fa else '负')
    act_ht = ('胜' if hh > ha else '平' if hh == ha else '负') + act_dir
    d_hit = act_dir in direction
    s_hit = act_score in picks
    h_hit = act_ht in [h.replace('*', '') for h in hts]
    tot['d'] += d_hit; tot['s'] += s_hit; tot['h'] += h_hit
    m = lambda b: '✅' if b else '❌'
    rank = [i + 1 for i, (k, p) in enumerate(sorted(probs.items(), key=lambda x: -x[1])[:15]) if k == act_score]
    rstr = f'泊松第{rank[0]}名' if rank else '15名以外'
    print(f'{no} {teams}')
    print(f'   R6: {direction}{grade} | 比分 {sc_str} | 半全场 {ht_str}')
    print(f'   实际 {actual}({half})={act_ht} | 方向{m(d_hit)} 比分{m(s_hit)}({rstr}) 半全场{m(h_hit)}')
    if not s_hit and rank:
        rk = rank[0]
        if rk <= 5:
            print(f'   💡 实际比分在泊松TOP5但未入选TOP3（被反向/结构挤掉）')
    print()
print('=' * 108)
print(f'合计: 方向 {tot["d"]}/17 | 比分 {tot["s"]}/17 | 半全场 {tot["h"]}/17')
