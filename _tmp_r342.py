# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# R342 调整：B 级第 3 位 = max(第3主方向, 最高反向)；落选反向存入 rev 字段
# 格式: (no, 新scores, 新ht, rev字段, 说明)
repl = [
    # 003 浦和：第3主方向 0-2(9.9%) > 反向 1-0(6.1%) → 0-2 入 TOP3，1-0 转 rev
    ('{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-0*", ht: "负负/平负/平胜*", ou: "总进球 2·3", risk: 5,',
     '{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 0-1", ht: "负负/平负/平负", ou: "总进球 2·3", risk: 5, rev: "1-0",'),
    # 004 神户：第3主方向 2-1(8.9%) > 反向 0-1(7.9%) → 2-1 入 TOP3，0-1 转 rev
    ('{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 1-2*", ht: "胜胜/平平/平负*", ou: "总进球 2·3", risk: 5,',
     '{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 1-0", ht: "胜胜/平平/平胜", ou: "总进球 2·3", risk: 5, rev: "1-2",'),
    # 005 首尔：第3主方向 1-0(8.8%) > 反向 1-2(7.4%) → 1-0 入 TOP3，1-2 转 rev
    ('{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,',
     '{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/胜胜/平胜", ou: "总进球 2·3", risk: 4, rev: "1-2",'),
    # 008 博尔顿：第3主方向 1-0(8.2%) > 反向 1-2(7.5%) → 1-0 入 TOP3，1-2 转 rev
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/胜胜/平胜", ou: "总进球 2·3", risk: 4, rev: "1-2",'),
    # 009 米亚尔比：第3主方向 1-2(8.6%) > 反向 1-0(8.2%) → 1-2 入 TOP3，1-0 转 rev
    ('{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 2·3", risk: 5,',
     '{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/平负", ou: "总进球 2·3", risk: 5, rev: "1-0",'),
    # 011 奥斯陆：第3主方向 0-1(8.4%) > 反向 2-1(7.6%) → 0-1 入 TOP3，2-1 转 rev
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 2·3", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/平负", ou: "总进球 2·3", risk: 4, rev: "2-1",'),
    # 019 阿拉维斯：第3主方向 2-0(9.5%) > 反向 0-1(8.6%) → 2-0 入 TOP3，0-1 转 rev
    ('{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-0 / 1-1 / 0-1*", ht: "胜胜/平平/平负*", ou: "总进球 1·2", risk: 4,',
     '{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-0 / 1-1 / 2-0", ht: "胜胜/平平/胜胜", ou: "总进球 1·2", risk: 4, rev: "0-1",'),
    # 024 塞维利亚：第3主方向 2-1(9.0%) > 反向 0-1(8.5%) → 2-1 入 TOP3，0-1 转 rev
    ('{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 0-1*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,',
     '{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-0", ht: "平平/胜胜/胜胜", ou: "总进球 2·3", risk: 4, rev: "0-1",'),
    # 026 弗鲁米嫩塞：0-0(9.1%) 与反向 1-0(9.1%) 并列 → 主方向优先 0-0 入 TOP3，1-0 转 rev
    ('{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 4,',
     '{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-0", ht: "平平/平负/平平", ou: "总进球 1·2", risk: 4, rev: "1-0",'),
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
