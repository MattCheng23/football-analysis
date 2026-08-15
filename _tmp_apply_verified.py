# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 008 博尔顿：1-1/2-1/2-2 平平/平胜/胜平（保持方向，ht 微调）
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "平胜/平平/负平", ou: "总进球 2·3", risk: 4,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/胜平", ou: "总进球 2·3", risk: 4,'),
    # 009 米亚尔比：平/负B，大球 1-2/1-1/2-2（天狼星16轮不败+瑞超高进球）
    ('{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 5,',
     '{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 2-2", ht: "平负/平平/负平", ou: "总进球 2·3", risk: 5,'),
    # 010 诺维奇：2-1/1-1/2-2（保持方向，西布朗防守稳补平局）
    ('{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 2-2 / 1-1", ht: "胜胜/平平/负平", ou: "总进球 3·4", risk: 4,',
     '{ no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-2", ht: "胜胜/平平/胜平", ou: "总进球 2·3", risk: 4,'),
    # 011 奥斯陆：负/平B，1-2/1-1/0-1（客队第4占优）
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/负负", ou: "总进球 2·3", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-1", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 4,'),
    # 014 玛丽港：负C，0-2/1-2/1-1*（垫底+野鸡，大球覆盖）
    ('{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "1-2 / 0-1 / 1-1*", ht: "平负/负负/平平*", ou: "总进球 2·3", risk: 8,',
     '{ no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",\n          dir: "负（C级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-1*", ht: "负负/平负/平平*", ou: "总进球 2·3", risk: 8,'),
    # 016 谢菲联：胜B，2-1/2-0/3-1（伯明翰边后卫双伤缺）
    ('{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 3-1 / 2-0", ht: "胜胜/平胜/负胜", ou: "总进球 3·4", risk: 3,',
     '{ no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",\n          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 2-0 / 3-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 3,'),
    # 019 阿拉维斯：平/负B（修正！核心伤缺+被挖后卫 vs 赫塔费第7）
    ('{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 2·3", risk: 4,',
     '{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,'),
    # 024 塞维利亚：平/负B（修正！新帅对巴列卡诺克星战绩）
    ('{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/负平", ou: "总进球 2·3", risk: 4,',
     '{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-1", ht: "平负/平平/负负", ou: "总进球 1·2", risk: 4,'),
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
