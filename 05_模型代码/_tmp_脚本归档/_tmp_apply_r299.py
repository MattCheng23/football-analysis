# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# R299 校准最终版（A=3主 / B=3主 / C=2主1反；λ 按 8/14 分联赛偏差 60% 吸收）
repl = [
    # 001 鹿岛 胜A：期望3.5 → 2-1/2-0/3-1
    ('{ no: "001", home: "鹿岛鹿角", away: "名古屋鲸八", league: "日职联", lg: "lg-j1",\n          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 2-1 / 3-0", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 2,',
     '{ no: "001", home: "鹿岛鹿角", away: "名古屋鲸八", league: "日职联", lg: "lg-j1",\n          dir: "胜（A级）", dc: "dir-win", scores: "2-1 / 2-0 / 3-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 2,'),
    # 003 浦和 负/平B：期望3.5 → 1-2/1-1/0-2
    ('{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-1 / 1-1 / 1-2", ht: "平负/平平/负负", ou: "总进球 1·2", risk: 5,',
     '{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-2", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 5,'),
    # 004 神户 胜/平B：1-1/2-1/2-2
    ('{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "胜胜/平平/胜平", ou: "总进球 2·3", risk: 5,',
     '{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/胜胜/胜平", ou: "总进球 2·3", risk: 5,'),
    # 005 首尔 胜/平B：1-1/2-1/1-0
    ('{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "胜胜/平平/胜平", ou: "总进球 2·3", risk: 4,',
     '{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/胜胜/胜平", ou: "总进球 2·3", risk: 4,'),
    # 006 光州 平/负B：1-1/0-1/0-0
    ('{ no: "006", home: "光州FC", away: "浦项制铁", league: "韩职", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-0 / 0-1 / 1-1", ht: "平平/平负/平平", ou: "总进球 0·1", risk: 5,',
     '{ no: "006", home: "光州FC", away: "浦项制铁", league: "韩职", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 0-0", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 5,'),
    # 008 博尔顿 胜/平B：2-1/1-1/2-2
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "胜胜/平平/胜平", ou: "总进球 2·3", risk: 4,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "平平/胜胜/胜平", ou: "总进球 2·3", risk: 4,'),
    # 009 米亚尔比 平/负B：1-1/0-1/1-2
    ('{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/负负/平负", ou: "总进球 1·2", risk: 5,',
     '{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 5,'),
    # 010 诺维奇 胜/平B：2-1/2-2/1-1（大球3·4）
    ('{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 2-2 / 3-1", ht: "胜胜/平平/胜胜", ou: "总进球 3·4", risk: 4,',
     '{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 2-2 / 1-1", ht: "胜胜/平平/胜平", ou: "总进球 3·4", risk: 4,'),
    # 011 奥斯陆 负/平B：1-1/1-2/0-1
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 2-2", ht: "平平/负负/负平", ou: "总进球 2·3", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/负平", ou: "总进球 2·3", risk: 4,'),
    # 014 玛丽港 负C：1-2/0-1/1-1*（2主1反）
    ('{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-1 / 1-2 / 1-1*", ht: "平负/负负/平平*", ou: "总进球 1·2", risk: 8,',
     '{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "1-2 / 0-1 / 1-1*", ht: "平负/负负/平平*", ou: "总进球 2·3", risk: 8,'),
    # 016 谢菲联 胜B：2-1/3-1/2-0（大球3·4）
    ('{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 3-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 3,',
     '{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 3-1 / 2-0", ht: "胜胜/平胜/负胜", ou: "总进球 3·4", risk: 3,'),
    # 019 阿拉维斯 胜/平B：1-1/2-1/1-0
    ('{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-0 / 1-1 / 2-1", ht: "胜胜/平平/平胜", ou: "总进球 1·2", risk: 4,',
     '{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "胜胜/平平/平胜", ou: "总进球 2·3", risk: 4,'),
    # 024 塞维利亚 胜/平B：1-1/2-1/2-2
    ('{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/胜胜/平胜", ou: "总进球 1·2", risk: 4,',
     '{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/胜胜/平胜", ou: "总进球 2·3", risk: 4,'),
    # 026 弗鲁米嫩塞 平/负B：1-1/0-1/1-2
    ('{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-1 / 1-1 / 1-2", ht: "平负/平平/负负", ou: "总进球 1·2", risk: 4,',
     '{ no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平负/平平/负负", ou: "总进球 1·2", risk: 4,'),
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
