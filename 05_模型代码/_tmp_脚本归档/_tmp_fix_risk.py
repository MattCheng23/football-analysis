# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 005 首尔 5->4
    ('{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 5,',
     '{ no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,'),
    # 006 光州 7->5
    ('{ no: "006", home: "光州FC", away: "浦项制铁", league: "韩职", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-0 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 0·1", risk: 7,',
     '{ no: "006", home: "光州FC", away: "浦项制铁", league: "韩职", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-0 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 0·1", risk: 5,'),
    # 008 博尔顿 5->4
    ('{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 5,',
     '{ no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",\n          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-2*", ht: "平平/胜胜/平负*", ou: "总进球 2·3", risk: 4,'),
    # 009 米亚尔比 7->5
    ('{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 7,',
     '{ no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 5,'),
    # 011 奥斯陆 5->4
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 5,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 1·2", risk: 4,'),
    # 019 阿拉维斯 7->4（西甲揭幕战认真打）
    ('{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-0 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 0·1", risk: 7,',
     '{ no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",\n          dir: "平/负（B级）", dc: "dir-drawloss", scores: "0-0 / 0-1 / 1-0*", ht: "平平/平负/平胜*", ou: "总进球 0·1", risk: 4,'),
    # 024 塞维利亚 8->4（西甲揭幕战认真打；阵容剧变=实力问题非假赛）
    ('{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "平/负（C级）", dc: "dir-drawloss", scores: "1-2 / 1-0* / 2-1*", ht: "平负/胜胜*/平胜*", ou: "总进球 1·3", risk: 8,',
     '{ no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",\n          dir: "平/负（C级）", dc: "dir-drawloss", scores: "1-2 / 1-0* / 2-1*", ht: "平负/胜胜*/平胜*", ou: "总进球 1·3", risk: 4,'),
    # 024 冷门榜逻辑修正（去"揭幕战"表述，强调阵容剧变）
    ('{ rank: "🥇", no: "024", teams: "塞维利亚 vs 巴列卡诺", dir: "客胜", lv: "tag-red", lvTxt: "最高", logic: "阵容剧变+揭幕战，主胜不可信" },',
     '{ rank: "🥇", no: "024", teams: "塞维利亚 vs 巴列卡诺", dir: "客胜", lv: "tag-orange", lvTxt: "较高", logic: "夏窗卖15人娃娃兵防线，主胜不可信" },'),
    # 024 预警逻辑修正
    ('{ script: "胜负", no: "024", teams: "塞维利亚 vs 巴列卡诺", lv: "tag-orange", lvTxt: "中等偏高", logic: "揭幕战娃娃兵，主队可能爆冷" },',
     '{ script: "胜负", no: "024", teams: "塞维利亚 vs 巴列卡诺", lv: "tag-orange", lvTxt: "中等偏高", logic: "娃娃兵防线不稳，主队可能爆冷" },'),
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
