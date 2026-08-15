# -*- coding: utf-8 -*-
import math

def pois(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def analyze(name, mode, lh, la, base_note):
    probs = {}
    tg = {}
    for h in range(0, 8):
        for a in range(0, 8):
            p = pois(h, lh) * pois(a, la)
            probs[(h, a)] = p
            t = h + a
            tg[t] = tg.get(t, 0) + p
    top = sorted(probs.items(), key=lambda x: -x[1])[:10]
    tgt = sorted(tg.items(), key=lambda x: -x[1])[:3]
    win = sum(p for (h, a), p in probs.items() if h > a)
    draw = sum(p for (h, a), p in probs.items() if h == a)
    loss = sum(p for (h, a), p in probs.items() if h < a)
    print('%s | %s lambda %.2f/%.2f 期望%.2f | %s' % (name, mode, lh, la, lh + la, base_note))
    print('  方向: 主胜%.0f%% 平%.0f%% 客胜%.0f%%' % (win * 100, draw * 100, loss * 100))
    print('  比分TOP10: %s' % ', '.join('%s(%.1f)' % (f'{h}-{a}', p * 100) for (h, a), p in top))
    print('  总进球分布TOP3: %s' % ', '.join('%d球(%.1f%%)' % (t, p * 100) for t, p in tgt))
    print()

# ============ 019 阿拉维斯 vs 赫塔费 ============
# 西甲场均2.55，R334赛季初+0.3球/场 → 基准 λ 每队 2.85/2 ≈ 1.425
# 阿拉维斯主场：主场系数 1.0（西甲中下游主场稳）→ 1.45
# 赫塔费客场：铁血防守著称，客场进攻乏力 → 0.95（低于基准，赫塔费防守好但进攻差）
analyze('019 阿拉维斯vs赫塔费', '西甲揭幕+R334', 1.45, 0.95,
        '阿拉维斯主场稳(西甲中游主场优势) + 赫塔费铁血防守但客场进攻乏力')

# ============ 024 塞维利亚 vs 巴列卡诺 ============
# 西甲场均2.55 + R334 → 基准 1.425
# 塞维利亚主场：即使卖15人娃娃兵，主场气势+新帅首秀 → 1.45（原1.3过低，主场因素没算）
# 巴列卡诺客场：专挑硬骨头但客场进攻一般 → 1.15
analyze('024 塞维利亚vs巴列卡诺', '西甲揭幕+R334+R335', 1.45, 1.15,
        '塞维利亚主场(卖15人但主场+新帅首秀) + 巴列卡诺客场中规中矩')
