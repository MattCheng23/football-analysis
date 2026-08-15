# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 回滚"泊松保守化"优化，恢复大球/偏差覆盖（R342：λ 已按 8/14 偏差上调，比分应体现上调后的进球量）
repl = [
    # 008 博尔顿：1-0 → 2-2（对攻场，博尔顿主场近10场7场>3球，大球覆盖）
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 2·3", risk: 4,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/胜平", ou: "总进球 2·3", risk: 4,'),
    # 014 玛丽港：0-1 首位 → 0-2 首位（野鸡场按剧本矩阵，客胜大球覆盖；0-2/1-2 覆盖 2-3 球）
    ('{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-1 / 0-2 / 1-1*", ht: "平负/负负/平平*", ou: "总进球 1·2", risk: 8,',
     '{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-1*", ht: "负负/平负/平平*", ou: "总进球 2·3", risk: 8,'),
    # 016 谢菲联：1-0 → 3-1（伯明翰防线残阵，谢菲联火力可能大胜，3-1 覆盖偏差比分）
    ('{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 1-0", ht: "胜胜/平胜/负胜", ou: "总进球 1·3", risk: 3,',
     '{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 3-1 / 2-0", ht: "胜胜/平胜/负胜", ou: "总进球 3·4", risk: 3,'),
    # 026 弗鲁米嫩塞：0-2 → 1-2（1-2 覆盖 3 球大球，0-2 偏保守）
    ('{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 0-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,',
     '{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,'),
]
cnt = 0
for old, new in repl:
    n = s.count(old)
    if n != 1:
        print('WARN count=%d -> %s' % (n, old[:55]))
        continue
    s = s.replace(old, new)
    cnt += 1
with io.open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('replaced: %d / %d' % (cnt, len(repl)))
