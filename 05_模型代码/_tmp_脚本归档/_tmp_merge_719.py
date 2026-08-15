# -*- coding: utf-8 -*-
"""合并 7/19 周日批次为 001-014：删除原 2026-07-20 与 2026-07-19 两个批次，重建为完整 2026-07-19 批次"""
import re

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
s = open(p, encoding='utf-8').read()

def mm(no, home, away, league, lg, dstr, dc, scores, ht):
    return f'        {{ no: "{no}", home: "{home}", away: "{away}", league: "{league}", lg: "{lg}",\n          dir: "{dstr}", dc: "{dc}", scores: "{scores}", ht: "{ht}" }},'

def rr(no, teams, league, lg, score, d, s, h, signal, sc):
    return f'        {{ no: "{no}", teams: "{teams}", league: "{league}", lg: "{lg}", score: "{score}", d: "{d}", s: "{s}", h: "{h}", signal: "{signal}", sc: "{sc}" }},'

matches = [
    ("001", "蔚山HD", "安养FC", "韩职", "lg-k1", "胜（B级）", "dir-win", "2-0 / 2-1 / 1-0", "胜胜/平胜/平平"),
    ("002", "济州SK", "仁川联", "韩职", "lg-k1", "胜（B级）", "dir-win", "1-0 / 0-0 / 0-1", "平胜/平平/胜胜"),
    ("003", "大田市民", "光州FC", "韩职", "lg-k1", "胜（B级）", "dir-win", "1-0 / 2-0 / 1-1", "平胜/胜胜/平平"),
    ("004", "布洛马波卡纳", "马尔默", "瑞超", "lg-swe", "负（B级）", "dir-drawloss", "0-2 / 1-2 / 0-3", "负负/平负/平平"),
    ("005", "哥德堡", "代格福什", "瑞超", "lg-swe", "胜（B级）", "dir-win", "2-0 / 2-1 / 1-0", "胜胜/平胜/平平"),
    ("006", "VPS瓦萨", "图尔库国际", "芬超", "lg-fin", "负/平（B级）", "dir-drawloss", "1-2 / 1-1 / 0-1", "平负/平平/负负"),
    ("007", "奥卢", "埃尔维斯", "芬超", "lg-fin", "平/胜（B级）", "dir-windraw", "1-1 / 1-0 / 0-0", "平平/平胜/胜胜"),
    ("008", "索尔纳", "奥尔格里特", "瑞超", "lg-swe", "胜（B级）", "dir-win", "2-0 / 2-1 / 1-0", "胜胜/平胜/平平"),
    ("009", "KFUM奥斯陆", "克里斯蒂安松", "挪超", "lg-nor", "胜/平（B级）", "dir-windraw", "1-0 / 1-1 / 0-0", "平平/胜胜/平胜"),
    ("010", "迈阿密国际", "哥伦布机员", "美职联", "lg-mls", "胜/平（B级）", "dir-windraw", "2-1 / 1-0 / 3-1", "胜胜/平胜/平平"),
    ("011", "温哥华白浪", "洛杉矶FC", "美职联", "lg-mls", "胜/平（B级）", "dir-windraw", "2-1 / 1-1 / 2-2", "胜胜/平平/平胜"),
    ("012", "桑托斯", "雷莫", "巴西杯", "lg-bras", "胜（A级）", "dir-win", "2-0 / 3-0 / 2-1", "胜胜/平胜/平平"),
    ("013", "芝加哥火焰", "夏洛特FC", "美职联", "lg-mls", "胜（B-级）", "dir-win", "2-1 / 1-0 / 1-1", "胜胜/平胜/平平"),
    ("014", "圣路易斯城", "皇家盐湖城", "美职联", "lg-mls", "胜（A级）", "dir-win", "2-0 / 2-1 / 1-0", "胜胜/平胜/平平"),
]
results = [
    ("001", "蔚山HD vs 安养FC", "韩职", "lg-k1", "3-1（0-0）", "ok", "no", "ok", "正常（3-1偏大）", "ok"),
    ("002", "济州SK vs 仁川联", "韩职", "lg-k1", "3-3（2-2）", "no", "no", "ok", "🟡 大球平局（3-3未覆盖）", "watch"),
    ("003", "大田市民 vs 光州FC", "韩职", "lg-k1", "2-0（0-0）", "ok", "ok", "ok", "正常（2-0=TOP2）", "ok"),
    ("004", "布洛马波卡纳 vs 马尔默", "瑞超", "lg-swe", "1-2（0-0）", "ok", "ok", "ok", "正常（1-2=TOP2）", "ok"),
    ("005", "哥德堡 vs 代格福什", "瑞超", "lg-swe", "2-0（1-0）", "ok", "ok", "ok", "正常（2-0=TOP1）", "ok"),
    ("006", "VPS瓦萨 vs 图尔库国际", "芬超", "lg-fin", "0-1（0-1）", "ok", "ok", "ok", "正常（0-1=TOP3）", "ok"),
    ("007", "奥卢 vs 埃尔维斯", "芬超", "lg-fin", "1-0（0-0）", "ok", "ok", "ok", "正常（1-0=TOP2+平胜）", "ok"),
    ("008", "索尔纳 vs 奥尔格里特", "瑞超", "lg-swe", "0-3（0-1）", "no", "no", "no", "🟡 10人伤缺爆冷（R335沾边）", "watch"),
    ("009", "KFUM奥斯陆 vs 克里斯蒂安松", "挪超", "lg-nor", "2-1（2-0）", "ok", "no", "no", "正常（2-1未覆盖）", "ok"),
    ("010", "迈阿密国际 vs 哥伦布机员", "美职联", "lg-mls", "2-2（2-1）", "ok", "no", "no", "🟡 平局（高价值预警胜平命中）", "watch"),
    ("011", "温哥华白浪 vs 洛杉矶FC", "美职联", "lg-mls", "1-1（0-1）", "ok", "ok", "no", "正常（1-1=TOP2）", "ok"),
    ("012", "桑托斯 vs 雷莫", "巴西杯", "lg-bras", "0-0（0-0）", "no", "no", "no", "🟡 冷平（A级未兑现）", "watch"),
    ("013", "芝加哥火焰 vs 夏洛特FC", "美职联", "lg-mls", "2-1（1-1）", "ok", "ok", "no", "正常（2-1=TOP1）", "ok"),
    ("014", "圣路易斯城 vs 皇家盐湖城", "美职联", "lg-mls", "1-1（0-0）", "no", "no", "no", "🟡 冷平（A级未兑现）", "watch"),
]

ms = "\n".join(mm(*x) for x in matches)
rs = "\n".join(rr(*x) for x in results)
new_batch = f'''  "2026-07-19": {{
    title: "7/19 周日批次（历史补录）",
    model: "V9.x",
    predictDate: "2026-07-19",
    reviewed: true,
    stats: {{ dir: "10/14", dirPct: "71.4%", score: "7/14", scorePct: "50%", ht: "7/14", htPct: "50%" }},
    predict: {{
      matches: [
{ms}
      ],
      coldRisk: [], alerts: [], zeroZero: []
    }},
    review: {{
      results: [
{rs}
      ],
      evidence: [], avoidHigh: [], avoidWatch: []
    }}
  }},
'''

# 删除旧的两个批次（2026-07-20 与 2026-07-19 各自的对象块：从 '  "2026-07-20": {' 到 '  },' 结束）
def remove_batch(text, key):
    pat = re.compile(r'  "' + key + r'": \{.*?\n  \},\n', re.DOTALL)
    new, n = pat.subn('', text, count=1)
    return new, n

s, n1 = remove_batch(s, '2026-07-20')
s, n2 = remove_batch(s, '2026-07-19')
print('removed 7/20:', n1, 'removed 7/19:', n2)

anchor = '  "2026-08-09": {'
idx = s.index(anchor)
s = s[:idx] + new_batch + s[idx:]
open(p, 'w', encoding='utf-8').write(s)
print('done')
