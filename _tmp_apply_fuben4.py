# -*- coding: utf-8 -*-
"""副本4落地：修正 8/10 批次003+追加005/006；新建 8/12 批次；追加 8/13 批次006-009"""
import re
p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
s = open(p, encoding='utf-8').read()

def mm(no, home, away, league, lg, dstr, dc, scores, ht):
    return f'        {{ no: "{no}", home: "{home}", away: "{away}", league: "{league}", lg: "{lg}",\n          dir: "{dstr}", dc: "{dc}", scores: "{scores}", ht: "{ht}" }},'

def rr(no, teams, league, lg, score, d, s, h, signal, sc):
    return f'        {{ no: "{no}", teams: "{teams}", league: "{league}", lg: "{lg}", score: "{score}", d: "{d}", s: "{s}", h: "{h}", signal: "{signal}", sc: "{sc}" }},'

# ===== 1) 修正 8/10 批次：003 替换为瓦斯特拉斯 1-0 + 追加 005/006 =====
old_003_m = re.compile(r'(  "2026-08-10": \{.*?matches: \[\n)(.*?)(        \{ no: "003", home: "尤尔加登", away: "瓦斯特拉斯".*?\n          dir: "胜（B级）".*?\n          dir: "负（A级）".*?)(\n)', re.DOTALL)
# 直接定位 003 行替换
pat_m3 = re.compile(r'        \{ no: "003", home: "尤尔加登", away: "瓦斯特拉斯", league: "瑞超", lg: "lg-swe",\n          dir: "胜（B级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "平胜/胜胜/平平" \},\n')
new_m3 = ('        { no: "003", home: "瓦斯特拉斯", away: "尤尔加登", league: "瑞超", lg: "lg-swe",\n'
          '          dir: "负（A级）", dc: "dir-drawloss", scores: "0-1 / 0-2 / 1-2", ht: "负负/平负/平平" },\n')
s, n1 = pat_m3.subn(new_m3, s, count=1)
print('8/10 003 match replaced:', n1)

pat_r3 = re.compile(r'        \{ no: "003", teams: "尤尔加登 vs 瓦斯特拉斯", league: "瑞超", lg: "lg-swe", score: "6-0（3-0）", d: "ok", s: "no", h: "ok", signal: "正常（6-0未覆盖，胜胜TOP2）", sc: "ok" \},\n')
new_r3 = ('        { no: "003", teams: "瓦斯特拉斯 vs 尤尔加登", league: "瑞超", lg: "lg-swe", score: "1-0", d: "no", s: "no", h: "no", signal: "全错（⚠️修正：原误用一周前尤尔加登6-0赛果，实为瓦斯特拉斯1-0爆冷）", sc: "watch" },\n')
s, n2 = pat_r3.subn(new_r3, s, count=1)
print('8/10 003 result replaced:', n2)

# 追加 005 天狼星（在 004 results 后插入 match+result）
pat_m004 = re.compile(r'(        \{ no: "004", home: "巴拉纳竞技", away: "维多利亚", league: "巴西杯", lg: "lg-bras",\n          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "胜胜/平胜/平平" \},\n)')
new_m005 = ('        { no: "004", home: "巴拉纳竞技", away: "维多利亚", league: "巴西杯", lg: "lg-bras",\n'
            '          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "胜胜/平胜/平平" },\n'
            '        { no: "005", home: "天狼星", away: "布洛马波卡纳", league: "瑞超", lg: "lg-swe",\n'
            '          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-0 / 1-1", ht: "胜胜/平胜/平平" },\n'
            '        { no: "006", home: "圣克拉拉", away: "马德拉国民", league: "葡超", lg: "lg-prime",\n'
            '          dir: "平/胜（B级）", dc: "dir-windraw", scores: "1-1 / 0-0 / 1-0", ht: "平平/平胜/胜胜" },\n')
s, n3 = pat_m004.subn(new_m005, s, count=1)
print('8/10 005/006 match added:', n3)

pat_r004 = re.compile(r'        \{ no: "004", teams: "巴拉纳竞技 vs 维多利亚", league: "巴西杯", lg: "lg-bras", score: "2-0（1-0）", d: "ok", s: "ok", h: "ok", signal: "正常（2-0=TOP2）", sc: "ok" \},\n')
new_r005 = ('        { no: "004", teams: "巴拉纳竞技 vs 维多利亚", league: "巴西杯", lg: "lg-bras", score: "2-0（1-0）", d: "ok", s: "ok", h: "ok", signal: "正常（2-0=TOP2）", sc: "ok" },\n'
            '        { no: "005", teams: "天狼星 vs 布洛马波卡纳", league: "瑞超", lg: "lg-swe", score: "2-2（2-2）", d: "no", s: "no", h: "ok", signal: "🟡 2-0领先后3分钟连丢2球（乌雷转会缺阵，平平TOP3）", sc: "watch" },\n')
s, n4 = pat_r004.subn(new_r005, s, count=1)
print('8/10 005 result added:', n4)

# 8/10 stats 更新
s = s.replace('stats: { dir: "3/4", dirPct: "75%", score: "2/4", scorePct: "50%", ht: "3/4", htPct: "75%" },\n    predictDate: "2026-08-10",',
              'stats: { dir: "2/5", dirPct: "40%", score: "2/5", scorePct: "40%", ht: "3/5", htPct: "60%" },\n    predictDate: "2026-08-10",')
print('8/10 stats updated')

# ===== 2) 新建 8/12 批次（9 场）=====
b812_m = [
    ("001", "江原FC", "大阪钢巴", "亚冠", "lg-k1", "胜/平（B级）", "dir-windraw", "- / - / 0-0", "平平/平胜/胜胜"),
    ("002", "凯拉特", "索菲亚列夫斯基", "欧冠资格赛", "lg-ucl", "平/负（B级）", "dir-drawloss", "0-0 / 0-1 / 1-1", "平平/平负/负负"),
    ("003", "博德闪耀", "圣吉罗斯", "欧冠资格赛", "lg-ucl", "胜（A级）", "dir-win", "2-1 / 2-0 / 3-2", "胜胜/平胜/平平"),
    ("004", "萨巴赫", "奥胡斯", "欧冠资格赛", "lg-ucl", "胜/平（B级）", "dir-windraw", "1-0 / 1-1 / 2-1", "平胜/平平/胜胜"),
    ("005", "奈梅亨", "奥林匹亚科斯", "欧冠资格赛", "lg-ucl", "平/负（B级）", "dir-drawloss", "0-1 / 1-1 / 0-2", "平平/平负/负负"),
    ("006", "采列", "阿拉拉特亚美尼亚", "欧冠资格赛", "lg-ucl", "平/负（B级）", "dir-drawloss", "1-1 / 1-2 / 0-1", "平平/平负/负负"),
    ("007", "布拉迪斯拉发", "米亚尔比", "欧冠资格赛", "lg-ucl", "胜（B级）", "dir-win", "2-0 / 2-1 / 1-0", "胜胜/平胜/平平"),
    ("008", "格拉茨风暴", "费内巴切", "欧冠资格赛", "lg-ucl", "负/平（B级）", "dir-drawloss", "0-1 / 1-1 / 0-2", "平负/负负/平平"),
    ("009", "里昂", "布拉格斯巴达", "欧冠资格赛", "lg-ucl", "胜（B级）", "dir-win", "2-0 / 3-1 / 2-1", "胜胜/平胜/平平"),
]
b812_r = [
    ("001", "江原FC vs 大阪钢巴", "亚冠", "lg-k1", "0-0（0-0）", "ok", "ok", "ok", "正常（0-0=TOP3+平平TOP1，加时不计）", "ok"),
    ("002", "凯拉特 vs 索菲亚列夫斯基", "欧冠资格赛", "lg-ucl", "0-1（0-1）", "ok", "ok", "ok", "⭐三指标全中（0-1=TOP2+负负TOP3）", "ok"),
    ("003", "博德闪耀 vs 圣吉罗斯", "欧冠资格赛", "lg-ucl", "2-2（0-0）", "ok", "no", "ok", "正常（加时3-2晋级，平平TOP3）", "ok"),
    ("004", "萨巴赫 vs 奥胡斯", "欧冠资格赛", "lg-ucl", "4-0（0-0）", "ok", "no", "ok", "正常（胜胜TOP3，4-0未覆盖）", "ok"),
    ("005", "奈梅亨 vs 奥林匹亚科斯", "欧冠资格赛", "lg-ucl", "1-1（0-0）", "ok", "ok", "ok", "⭐三指标全中（1-1=TOP2+平平TOP1）", "ok"),
    ("006", "采列 vs 阿拉拉特亚美尼亚", "欧冠资格赛", "lg-ucl", "2-0（0-0）", "no", "no", "no", "全错（首回合1-2落败主场2-0逆转，R211）", "ok"),
    ("007", "布拉迪斯拉发 vs 米亚尔比", "欧冠资格赛", "lg-ucl", "2-0（0-0）", "ok", "ok", "ok", "⭐三指标全中（2-0=TOP1+胜胜TOP1）", "ok"),
    ("008", "格拉茨风暴 vs 费内巴切", "欧冠资格赛", "lg-ucl", "0-1（0-0）", "ok", "ok", "ok", "⭐三指标全中（0-1=TOP1+负负TOP2）", "ok"),
    ("009", "里昂 vs 布拉格斯巴达", "欧冠资格赛", "lg-ucl", "3-0（1-0）", "ok", "no", "ok", "正常（34'客队红牌崩盘，胜胜TOP1）", "ok"),
]
ms812 = "\n".join(mm(*x) for x in b812_m)
rs812 = "\n".join(rr(*x) for x in b812_r)
b812 = f'''  "2026-08-12": {{
    title: "8/12 周二批次（副本4补录）",
    model: "V10.0",
    predictDate: "2026-08-12",
    reviewed: true,
    stats: {{ dir: "8/9", dirPct: "88.9%", score: "5/9", scorePct: "55.6%", ht: "8/9", htPct: "88.9%" }},
    predict: {{
      matches: [
{ms812}
      ],
      coldRisk: [], alerts: [], zeroZero: []
    }},
    review: {{
      results: [
{rs812}
      ],
      evidence: [], avoidHigh: [], avoidWatch: []
    }}
  }},
'''
anchor = '  "2026-08-13": {'
idx = s.index(anchor)
s = s[:idx] + b812 + s[idx:]
print('8/12 batch inserted')

# ===== 3) 8/13 追加 006-009 =====
pat_m813 = re.compile(r'(  "2026-08-13": \{.*?matches: \[\n)(.*?)(\n      \],)', re.DOTALL)
add_m813 = ('\n' +
    '        { no: "006", home: "格拉斯哥流浪者", away: "雅盖隆", league: "欧联资格赛", lg: "lg-uel",\n'
    '          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 2-0 / 1-0", ht: "胜胜/平胜/平平" },\n'
    '        { no: "007", home: "安德莱赫特", away: "塞萨洛尼基", league: "欧联资格赛", lg: "lg-uel",\n'
    '          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜" },\n'
    '        { no: "008", home: "哈茨", away: "本菲卡", league: "欧联资格赛", lg: "lg-uel",\n'
    '          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/负负" },\n'
    '        { no: "009", home: "米拉索", away: "基多大学体育", league: "解放者杯", lg: "lg-bras",\n'
    '          dir: "胜（B+级）", dc: "dir-win", scores: "1-0 / 2-0 / 1-1", ht: "胜胜/平胜/平平" },\n')
s, n5 = pat_m813.subn(lambda m: m.group(1) + m.group(2) + add_m813 + m.group(3), s, count=1)
print('8/13 006-009 matches added:', n5)

pat_r813 = re.compile(r'(  "2026-08-13": \{.*?results: \[\n)(.*?)(\n      \],)', re.DOTALL)
add_r813 = ('\n' +
    '        { no: "006", teams: "格拉斯哥流浪者 vs 雅盖隆", league: "欧联资格赛", lg: "lg-uel", score: "1-1（1-0）", d: "ok", s: "no", h: "no", signal: "🟡 半场领先被扳平（R291残阵防线胜平剧本）", sc: "watch" },\n'
    '        { no: "007", teams: "安德莱赫特 vs 塞萨洛尼基", league: "欧联资格赛", lg: "lg-uel", score: "3-2（1-1）", d: "ok", s: "no", h: "ok", signal: "正常（平胜TOP2，3-2未覆盖）", sc: "ok" },\n'
    '        { no: "008", teams: "哈茨 vs 本菲卡", league: "欧联资格赛", lg: "lg-uel", score: "1-1（0-0）", d: "ok", s: "ok", h: "ok", signal: "⭐三指标全中（控分修正：强队次回合客场保守R319，1-1=TOP1+平平TOP1）", sc: "ok" },\n')
s, n6 = pat_r813.subn(lambda m: m.group(1) + m.group(2) + add_r813 + m.group(3), s, count=1)
print('8/13 006-008 results added:', n6)

# 8/13 stats 更新（原 3/5、1/5、2/5 → 6/8、2/8、4/8）
s = s.replace('stats: { dir: "3/5", dirPct: "60%", score: "1/5", scorePct: "20%", ht: "2/5", htPct: "40%" },\n    predictDate: "2026-08-13",',
              'stats: { dir: "6/8", dirPct: "75%", score: "2/8", scorePct: "25%", ht: "4/8", htPct: "50%" },\n    predictDate: "2026-08-13",')
print('8/13 stats updated')

open(p, 'w', encoding='utf-8').write(s)
print('done')
