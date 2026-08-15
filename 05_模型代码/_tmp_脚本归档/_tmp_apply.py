# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 001 鹿岛 A：主胜61%，期望2.8，卫冕主场大胜 → 2-0/2-1/3-0（ou 2·3）
    ('{ no: "001", home: "鹿岛鹿角", away: "名古屋鲸八", league: "日职联", lg: "lg-j1",\n          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 2,',
     '{ no: "001", home: "鹿岛鹿角", away: "名古屋鲸八", league: "日职联", lg: "lg-j1",\n          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 2-1 / 3-0", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 2,'),
    # 003 浦和 B：客胜56%，广岛火热大胜 → 0-2/1-2/1-0*（ou 2·3）
    ('{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-1 / 1-1 / 1-0*", ht: "平负/平平/平胜*", ou: "总进球 1·2", risk: 5,',
     '{ no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-0*", ht: "负负/平负/平胜*", ou: "总进球 2·3", risk: 5,'),
    # 004 神户 B：胜/平42%，对攻大球 → 2-1/1-1/1-2*（ou 2·3）
    ('{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 1-0 / 0-1*", ht: "平平/胜胜/平负*", ou: "总进球 1·2", risk: 5,',
     '{ no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 1-2*", ht: "胜胜/平平/平负*", ou: "总进球 2·3", risk: 5,'),
    # 010 诺维奇 B：胜/平49%，大球倾向(3.4) → 2-1/2-2/1-2*（ou 3·4）
    ('{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,',
     '{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 2-2 / 1-2*", ht: "胜胜/平平/平负*", ou: "总进球 3·4", risk: 4,'),
    # 011 奥斯陆 B：负/平43%，挪超2.94上调 → 1-1/1-2/1-0*（ou 2·3）
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 2·3", risk: 4,'),
    # 016 谢菲联 B：胜56%，期望3.1 → 2-1/2-0/1-1*（ou 2·3）
    ('{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 1-0 / 1-1*", ht: "胜胜/平胜/平平*", ou: "总进球 2·3", risk: 3,',
     '{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 1-1*", ht: "胜胜/平胜/平平*", ou: "总进球 2·3", risk: 3,'),
    # 024 塞维利亚 B：胜/平44%，期望2.6 → 1-1/2-1/0-1*（ou 2·3）
    ('{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 1-0 / 0-1*", ht: "平平/胜胜/平负*", ou: "总进球 1·2", risk: 4,',
     '{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 0-1*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,'),
]
cnt = 0
for old, new in repl:
    n = s.count(old)
    if n != 1:
        print('WARN count=%d -> %s' % (n, old[:60]))
        continue
    s = s.replace(old, new)
    cnt += 1
with io.open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('replaced: %d / %d' % (cnt, len(repl)))
