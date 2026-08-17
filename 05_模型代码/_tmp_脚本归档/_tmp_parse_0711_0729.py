# -*- coding: utf-8 -*-
"""解析竞彩预测场次全记录_0711-0729.md → 生成 data.js 历史批次（跳过 07-19，与已建批次冲突）"""
import re

SRC = r'D:\Cola\足球分析学习\02_模型记忆\历史批次提取\竞彩预测场次全记录_0711-0729.md'
DST = r'D:\Cola\足球分析学习\_发布_public\js\data.js'

lines = open(SRC, encoding='utf-8').read().splitlines()
rows = []
for ln in lines:
    if not ln.strip().startswith('|'):
        continue
    cells = [c.strip() for c in ln.strip().strip('|').split('|')]
    if len(cells) != 11 or cells[0] == '编号' or cells[0].startswith(':'):
        continue
    rows.append(cells)

LG = {
    '韩职': 'lg-k1', '瑞超': 'lg-swe', '挪超': 'lg-nor', '芬超': 'lg-fin',
    '巴甲': 'lg-bras', '美职联': 'lg-mls', '欧冠': 'lg-ucl', '欧冠资格赛': 'lg-ucl',
    '欧罗巴': 'lg-uel', '欧联资格赛': 'lg-uel', '东南亚锦标赛': 'lg-asean',
}

def lg_of(league):
    return LG.get(league, 'lg-j1')

def dir_of(d):
    d = d.replace('（首选）', '').replace('(首选)', '').replace('（次选）', '').replace('(次选)', '')
    d = d.replace('首选', '').replace('次选', '')
    if '客胜' in d or '负（' in d or d.startswith('负') or '客队不败' in d or ('负' in d and '胜' not in d and '平' not in d):
        base = '负'
    elif '主胜' in d or d.startswith('胜') or ('胜' in d and '负' not in d and '平' not in d):
        base = '胜'
    elif '平局' in d or d.startswith('平') or ('平' in d and '胜' not in d and '负' not in d):
        base = '平'
    else:
        # 复合：含胜/平/负多个 → 取主选
        base = '胜' if d.startswith('胜') else ('负' if d.startswith('负') else ('平' if d.startswith('平') else '平'))
    lv = ''
    m = re.search(r'[A-C][+-]?', d)
    if m:
        lv = '（' + m.group(0) + '级）'
    elif 'A级' in d or 'A-' in d:
        lv = '（A级）'
    elif 'B级' in d or 'B+' in d or 'B-' in d:
        lv = '（B级）'
    return base + lv

def dc_of(base):
    return {'胜': 'dir-win', '平': 'dir-draw', '负': 'dir-drawloss'}.get(base, 'dir-draw')

def clean_scores(s):
    s = s.replace('（半场', '')
    if s in ('?', '—', ''):
        return '-'
    return s.replace('/', ' / ')

# 按日期分组（仅保留 7/21 世界杯决赛后至今的联赛分析；7/21 之前为世界杯分析，参考价值低不建批次）
from collections import OrderedDict
by_date = OrderedDict()
for r in rows:
    d = r[1]
    if d < '07-21':
        continue
    by_date.setdefault(d, []).append(r)

def build_batch(date, rows):
    ms, rs = [], []
    for i, r in enumerate(rows, 1):
        no = f'{i:03d}'
        league = r[2]
        teams = r[3]
        parts = teams.split(' vs ')
        home = parts[0] if len(parts) > 1 else teams
        away = parts[1] if len(parts) > 1 else '?'
        dstr = dir_of(r[4])
        base = dstr[0]
        scores = clean_scores(r[5])
        ht = clean_scores(r[6])
        lg = lg_of(league)
        ms.append(f'        {{ no: "{no}", home: "{home}", away: "{away}", league: "{league}", lg: "{lg}",\n          dir: "{dstr}", dc: "{dc_of(base)}", scores: "{scores}", ht: "{ht}" }},')
        # results：赛果格式 "0-3（半场0-1）" → "0-3（0-1）"；判定 ✅→ok ❌→no ?→跳过
        res = r[7]
        if res in ('?', ''):
            continue
        score = re.sub(r'半场', '', res)
        d_ok = 'ok' if r[8] in ('✅', '⚠️') or '次选' in r[8] else ('no' if r[8] == '❌' else 'no')
        s_ok = 'ok' if r[9] == '✅' else 'no'
        h_ok = 'ok' if r[10] == '✅' else 'no'
        sig = '正常' if (d_ok == s_ok == h_ok == 'ok') else ('🟡 部分命中' if (d_ok == 'ok' or s_ok == 'ok' or h_ok == 'ok') else '全错')
        sc = 'ok' if sig == '正常' else ('watch' if sig == '🟡 部分命中' else 'ok')
        rs.append(f'        {{ no: "{no}", teams: "{teams}", league: "{league}", lg: "{lg}", score: "{score}", d: "{d_ok}", s: "{s_ok}", h: "{h_ok}", signal: "{sig}（A/B档案提取，待交叉核验）", sc: "{sc}" }},')
    # stats
    n = len(rs)
    dc = sum(1 for x in rs if '"ok"' in x.split('d: "')[1][:3]) if n else 0
    dcount = sum(1 for x in rs if re.search(r'd: "(ok)"', x))
    scount = sum(1 for x in rs if re.search(r's: "(ok)"', x))
    hcount = sum(1 for x in rs if re.search(r'h: "(ok)"', x))
    return f'''  "2026-{date}": {{
    title: "{date} 批次（历史补录·A/B档案）",
    model: "V8-V9",
    predictDate: "2026-{date}",
    reviewed: true,
    stats: {{ dir: "{dcount}/{n}", dirPct: "{round(dcount*100/n) if n else 0}%", score: "{scount}/{n}", scorePct: "{round(scount*100/n) if n else 0}%", ht: "{hcount}/{n}", htPct: "{round(hcount*100/n) if n else 0}%" }},
    predict: {{
      matches: [
{chr(10).join(ms)}
      ],
      coldRisk: [], alerts: [], zeroZero: []
    }},
    review: {{
      results: [
{chr(10).join(rs)}
      ],
      evidence: [], avoidHigh: [], avoidWatch: []
    }}
  }},
'''

blocks = ""
for d, rws in by_date.items():
    blocks += build_batch(d, rws)

s = open(DST, encoding='utf-8').read()
# 清理上次插入的批次（2026-07-11 至 2026-07-29 之间，含非法 ':---' 批次）
pat_clean = re.compile(r'  "2026-07-\d\d": \{.*?\n  \},\n', re.DOTALL)
s, n_clean = pat_clean.subn('', s)
print('cleaned old batches:', n_clean)
anchor = '  "2026-08-06": {'
idx = s.index(anchor)
s = s[:idx] + blocks + s[idx:]
open(DST, 'w', encoding='utf-8').write(s)
print('batches:', len(by_date), '| dates:', list(by_date.keys()))
