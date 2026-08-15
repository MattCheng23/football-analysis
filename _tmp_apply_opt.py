# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 008 博尔顿：2-2 → 1-0（1-0 概率 8.2% > 2-2 6.2%，主队零封）
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/胜平", ou: "总进球 2·3", risk: 4,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 2·3", risk: 4,'),
    # 014 玛丽港：0-2 → 0-1 首位（0-1 15.9% 远超），0-2 保留
    ('{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-1*", ht: "负负/平负/平平*", ou: "总进球 2·3", risk: 8,',
     '{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-1 / 0-2 / 1-1*", ht: "平负/负负/平平*", ou: "总进球 1·2", risk: 8,'),
    # 016 谢菲联：3-1 → 1-0（1-0 8.8% > 3-1 6.4%），ht 用负胜保持去重
    ('{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 3-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 3,',
     '{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 1-0", ht: "胜胜/平胜/负胜", ou: "总进球 1·3", risk: 3,'),
    # 026 弗鲁米嫩塞：1-2 → 0-2（0-2 8.9% ≥ 1-2，且避免双平 ht 重复）
    ('{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,',
     '{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 0-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,'),
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
