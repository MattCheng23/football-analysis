# -*- coding: utf-8 -*-
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 8/14 批次实际赛果（双源核验台账）=====
# (no, 对阵, 联赛, 实际比分, 半场)
results = [
    ('001', '东京绿茵 vs 柏太阳神', '日职', '1-3', '0-2'),
    ('002', 'VPS瓦萨 vs TPS图尔库', '芬超', '1-3', '0-2'),
    ('003', '荷尔斯泰因 vs 圣保利', '德乙', '2-2', '0-2'),
    ('004', '布伦瑞克 vs 波鸿', '德乙', '0-1', '0-1'),
    ('005', '新未来城 vs 费哈', '沙特', '2-1', '2-0'),
    ('006', '埃尔夫斯堡 vs 瓦斯特拉斯', '瑞超', '3-0', '1-0'),
    ('007', '罗森博格 vs 维京', '挪超', '2-1', '1-0'),
    ('008', '达曼协作 vs 利雅得体育', '沙特', '4-2', '1-1'),
    ('009', '利雅得新月 vs 费萨里', '沙特', '4-2', '3-0'),
    ('010', '特尔斯达 vs 鹿特丹斯巴达', '荷甲', '1-3', '0-1'),
    ('011', '瓦尔韦克 vs 多德勒支', '荷乙', '2-2', '0-1'),
    ('012', '赫拉克勒斯 vs 邓伯什', '荷乙', '3-2', '1-0'),
    ('013', '昂纳西 vs 罗德兹', '法乙', '2-0', '1-0'),
    ('014', '兰斯 vs 敦刻尔克', '法乙', '3-3', '1-1'),
    ('015', '圣埃蒂安 vs 克莱蒙', '法乙', '3-1', '1-0'),
    ('016', '狼队 vs 布莱克本', '英冠', '2-2', '1-1'),
    ('017', '葡萄牙体育 vs 吉马良斯', '葡超', '3-2', '3-0'),
]

# 8/14 预测时使用的 λ（模型当时估计）
pred_lam = {
    '001': (1.3, 1.5), '002': (1.4, 1.3), '003': (1.2, 1.4), '004': (1.3, 1.3),
    '005': (1.5, 1.2), '006': (1.9, 1.2), '007': (1.7, 1.3), '008': (1.5, 1.3),
    '009': (2.6, 1.1), '010': (1.4, 1.6), '011': (1.7, 1.3), '012': (2.2, 1.0),
    '013': (1.3, 1.1), '014': (1.5, 1.0), '015': (1.8, 1.0), '016': (1.7, 1.1),
    '017': (2.1, 0.9),
}

print('=' * 80)
print('R299 赛后偏差回传：8/14 实际 vs 预测 λ 对比')
print('=' * 80)
total_pred = 0
total_act = 0
league_stats = {}
for no, teams, lg, actual, half in results:
    fh, fa = map(int, actual.split('-'))
    act_total = fh + fa
    ph, pa = pred_lam[no]
    pred_total = ph + pa
    total_pred += pred_total
    total_act += act_total
    diff = act_total - pred_total
    if lg not in league_stats:
        league_stats[lg] = {'pred': 0, 'act': 0, 'n': 0}
    league_stats[lg]['pred'] += pred_total
    league_stats[lg]['act'] += act_total
    league_stats[lg]['n'] += 1
    print(f'{no} {teams} | 实际 {actual}(={act_total}球) | 预测λ期望 {pred_total:.1f} | 偏差 {diff:+.1f}')

print()
print(f'全场均值: 预测 {total_pred/17:.2f} vs 实际 {total_act/17:.2f} → 偏差 {(total_act-total_pred)/17:+.2f} 球/场')
print()
print('分联赛偏差（R299 校准依据）:')
for lg, st in league_stats.items():
    pd = st['pred'] / st['n']
    ad = st['act'] / st['n']
    print(f'  {lg}: {st["n"]}场 预测{pd:.2f} vs 实际{ad:.2f} → 偏差{ad-pd:+.2f}')

# 大小球命中分析（模型预测小球 vs 实际大球比例）
print()
print('实际总进球分布:')
from collections import Counter
dist = Counter(fh+fa for _,_,_,a,_ in results)
for t in sorted(dist):
    print(f'  {t}球: {dist[t]}场')
big = sum(1 for _,_,_,a,_ in results if sum(map(int,a.split('-'))) >= 3)
print(f'≥3球: {big}/17 ({big/17*100:.0f}%)  ← R334 依据')
