# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 009 米亚尔比：2-2 → 1-3（天狼星客场火力场均2.9，客胜3球偏差覆盖）
    ('{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 2-2", ht: "平负/平平/负平", ou: "总进球 2·3", risk: 5,',
     '{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 1-3", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 5,'),
    # 010 诺维奇：2-2 → 3-1（诺维奇主场强攻+交锋优势，杯赛3-1赢过西布朗）
    ('{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "胜胜/平平/胜平", ou: "总进球 2·3", risk: 4,',
     '{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 3-1", ht: "胜胜/平平/平胜", ou: "总进球 2·3", risk: 4,'),
    # 011 奥斯陆：2-2 → 0-2（利勒斯特罗姆第4攻防俱佳，客胜2球零封）
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 2-2", ht: "平负/平平/负平", ou: "总进球 2·3", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-2", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 4,'),
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
