# -*- coding: utf-8 -*-
import math

def pois(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def analyze(name, mode, lh, la):
    probs = {}
    tg = {}
    for h in range(0, 8):
        for a in range(0, 8):
            p = pois(h, lh) * pois(a, la)
            probs[(h, a)] = p
            t = h + a
            tg[t] = tg.get(t, 0) + p
    top = sorted(probs.items(), key=lambda x: -x[1])[:12]
    tgt = sorted(tg.items(), key=lambda x: -x[1])[:3]
    win = sum(p for (h, a), p in probs.items() if h > a)
    draw = sum(p for (h, a), p in probs.items() if h == a)
    loss = sum(p for (h, a), p in probs.items() if h < a)
    print('%s | %s lambda %.1f/%.1f 期望%.2f' % (name, mode, lh, la, lh + la))
    print('  方向: 主胜%.0f%% 平%.0f%% 客胜%.0f%%' % (win * 100, draw * 100, loss * 100))
    print('  比分TOP8: %s' % ', '.join('%s(%.1f)' % (f'{h}-{a}', p * 100) for (h, a), p in top[:8]))
    print('  总进球分布TOP3: %s' % ', '.join('%d球(%.1f%%)' % (t, p * 100) for t, p in tgt))
    print()

analyze('001 鹿岛vs名古屋', '日职中段', 1.9, 0.9)
analyze('003 浦和vs广岛', '日职中段', 1.0, 1.8)
analyze('004 神户vs东京', '日职中段', 1.5, 1.3)
analyze('005 首尔vs大田', '韩职中段', 1.6, 1.3)
analyze('006 光州vs浦项', '韩职中段', 0.9, 0.9)
analyze('008 博尔顿vs普雷斯顿', '英冠新季R334', 1.65, 1.35)
analyze('009 米亚尔比vs天狼星', '瑞超中段', 1.1, 1.2)
analyze('010 诺维奇vs西布朗', '英冠新季R334', 1.95, 1.45)
analyze('011 奥斯陆vs利勒', '挪超中段', 1.2, 1.5)
analyze('014 玛丽港vs塞伊奈约基', '芬超野鸡', 0.8, 1.3)
analyze('016 谢菲联vs伯明翰', '英冠新季R334', 1.95, 1.15)
analyze('019 阿拉维斯vs赫塔费', '西甲揭幕R336', 1.0, 0.9)
analyze('024 塞维利亚vs巴列卡诺', '西甲揭幕R335', 1.3, 1.5)
analyze('026 弗鲁米嫩塞vs帕尔梅拉斯', '巴甲中段', 1.0, 1.4)
