# -*- coding: utf-8 -*-
import math

def pois(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def full_model(name, league_avg, mode, lh, la, note):
    """完整模型：联赛参数 → λ → 泊松 → 期望贴合选比"""
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
    exp = lh + la
    print('%s | 联赛场均%.2f | %s λ%.2f/%.2f 期望%.2f' % (name, league_avg, mode, lh, la, exp))
    print('  方向: 主胜%.0f%% 平%.0f%% 客胜%.0f%% | 总进球TOP3: %s' % (
        win * 100, draw * 100, loss * 100,
        ', '.join('%d球(%.1f%%)' % (t, p * 100) for t, p in tgt)))
    print('  比分TOP12: %s' % ', '.join('%s(%.1f)' % (f'{h}-{a}', p * 100) for (h, a), p in top))
    print('  [%s]' % note)
    print()

# ========== 全面 λ 审计：以联赛参数为基准 ==========
# 日职 2.60 | 韩职 2.37 | 瑞超 3.07 | 挪超 2.94 | 芬超 2.69 | 巴甲 2.66 | 英冠 ~2.7 | 西甲 2.55
# R334: 新赛季联赛（英冠/西甲）每队 +0.15

full_model('001 鹿岛vs名古屋', 2.60, '日职中段', 1.9, 0.9, '鹿岛卫冕主场 vs 保级队，期望2.80>基准2.60合理')
full_model('003 浦和vs广岛', 2.60, '日职中段', 1.0, 1.8, '浦和5停赛 vs 广岛火热，期望2.80合理')
full_model('004 神户vs东京', 2.60, '日职中段', 1.5, 1.3, '残阵对残阵，期望2.80合理')
full_model('005 首尔vs大田', 2.37, '韩职中段', 1.6, 1.3, '榜首主场对攻，期望2.90>2.37合理')
full_model('006 光州vs浦项', 2.37, '韩职双弱', 0.9, 0.9, '双弱对话，期望1.80<2.37合理(进球乏力)')
full_model('008 博尔顿vs普雷斯顿', 2.70, '英冠新季R334', 1.65, 1.35, '基准1.35+0.15=1.5/1.2+主场修正，期望3.00')
full_model('009 米亚尔比vs天狼星', 3.07, '瑞超中段', 1.35, 1.45, '★瑞超场均3.07被低估!原1.1/1.2(2.3)<<3.07，上调至1.35/1.45(2.8)')
full_model('010 诺维奇vs西布朗', 2.70, '英冠新季R334', 1.95, 1.45, '诺维奇大球，期望3.40')
full_model('011 奥斯陆vs利勒', 2.94, '挪超中段', 1.35, 1.6, '★挪超2.94略被低估，原1.2/1.5(2.7)，上调至1.35/1.6(2.95)')
full_model('014 玛丽港vs塞伊奈约基', 2.69, '芬超野鸡', 0.8, 1.3, '垫底队(0胜4平12负)进攻极弱，期望2.10<2.69合理')
full_model('016 谢菲联vs伯明翰', 2.70, '英冠新季R334', 1.95, 1.15, '升级热门主场，期望3.10')
full_model('019 阿拉维斯vs赫塔费', 2.55, '西甲揭幕R334', 1.45, 0.95, '主场49%+赫塔费铁血，期望2.40')
full_model('024 塞维利亚vs巴列卡诺', 2.55, '西甲揭幕R334', 1.45, 1.15, '主场44%+卖15人，期望2.60')
full_model('026 弗鲁米嫩塞vs帕尔梅拉斯', 2.66, '巴甲中段', 1.0, 1.4, '主弱客强但客轮换，期望2.40')
