# -*- coding: utf-8 -*-
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(8):
        for a in range(8): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d

# R299 分联赛偏差系数（8/14 实测）
league_adj = {
    '日职': +1.20, '芬超': +1.30, '德乙': -0.10, '沙特': +1.93, '瑞超': -0.10,
    '挪超': +0.00, '荷甲': +1.00, '荷乙': +1.40, '法乙': +1.43, '英冠': +1.20, '葡超': +2.00,
    '韩职': +0.5,  # 韩职无 8/14 样本，用全场均值的一半（保守）
    '西甲': +1.2,  # 西甲揭幕，参考英冠/五大联赛级 +1.2
    '巴甲': +0.5,  # 巴甲无样本，保守取半
}
# 但 R299 偏差回传不能全量一次性吸收（防止过拟合），按 60% 吸收 + 方向符号
def adj_lam(lh, la, lg, absorb=0.6):
    d = league_adj[lg]
    delta = d * absorb / 2  # 每队分一半
    return max(0.5, lh + delta), max(0.5, la + delta)

# 8/15 当前 λ（模型基准）与联赛
base = {
    '001': (1.9, 0.9, '日职'), '003': (1.0, 1.8, '日职'), '004': (1.5, 1.3, '日职'),
    '005': (1.6, 1.3, '韩职'), '006': (0.9, 0.9, '韩职'),
    '008': (1.65, 1.35, '英冠'), '009': (1.35, 1.45, '瑞超'), '010': (1.95, 1.45, '英冠'),
    '011': (1.35, 1.6, '挪超'), '014': (0.8, 1.3, '芬超'), '016': (1.95, 1.15, '英冠'),
    '019': (1.45, 0.95, '西甲'), '024': (1.45, 1.15, '西甲'), '026': (1.0, 1.4, '巴甲'),
}
dirs = {'001':'胜','003':'负/平','004':'胜/平','005':'胜/平','006':'平/负','008':'胜/平','009':'平/负','010':'胜/平','011':'负/平','014':'负','016':'胜','019':'胜/平','024':'胜/平','026':'平/负'}

print('=== R299 校准后 8/15 λ 与泊松 TOP5 ===')
for no in ['001','003','004','005','006','008','009','010','011','014','016','019','024','026']:
    lh, la, lg = base[no]
    nlh, nla = adj_lam(lh, la, lg)
    p = probs(nlh, nla)
    srt = sorted(p.items(), key=lambda x: -x[1])
    # 方向概率
    win = sum(v for (h,a),v in p.items() if h>a)
    draw = sum(v for (h,a),v in p.items() if h==a)
    loss = sum(v for (h,a),v in p.items() if h<a)
    # 主方向 TOP3
    main = [k for k,v in srt if (('胜' in dirs[no] and k[0]>k[1]) or ('平' in dirs[no] and k[0]==k[1]) or ('负' in dirs[no] and k[0]<k[1]))][:3]
    sc_str = ' / '.join(f'{h}-{a}' for h,a in main)
    tops = ' '.join(f'{h}-{a}({v*100:.1f}%)' for (h,a),v in srt[:5])
    print(f'{no} {dirs[no]} | λ {lh}/{la} → 校准 {nlh:.2f}/{nla:.2f} (期望{nlh+nla:.1f}) | 主胜{win*100:.0f}% 平{draw*100:.0f}% 客胜{loss*100:.0f}%')
    print(f'    主方向TOP3: {sc_str}')
    print(f'    泊松TOP5: {tops}')
    print()
