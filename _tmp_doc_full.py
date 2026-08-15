# -*- coding: utf-8 -*-
import io, re

# 读取 data.js
src = io.open(r'D:\Cola\足球分析学习\_发布_public\js\data.js', encoding='utf-8').read()
m15 = src[src.index('"2026-08-15"'):]

rows = []
for m in re.finditer(r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)", league: "([^"]+)", lg: "([^"]+)",\s*dir: "([^"]+)", dc: "([^"]+)", scores: "([^"]+)", ht: "([^"]+)", ou: "([^"]+)", risk: (\d+),', m15):
    no, home, away, league, lg, dir, dc, scores, ht, ou, risk = m.groups()
    rows.append(dict(no=no, home=home, away=away, dir=dir, scores=scores, ht=ht, ou=ou, risk=int(risk), logic=''))

# logic 提取
for m in re.finditer(r'no: "(\d+)"[^}]*?logic: "([^"]+)"', m15):
    rows = [dict(r, logic=m.group(2)) if r['no'] == m.group(1) else r for r in rows]

def bold_rev(s):
    return re.sub(r'(\d+-\d+)\*', r'**\1\\***', s)

risk_icon = lambda r: '🔴 %d' % r if r >= 7 else ('🟠 %d' % r if r >= 5 else '🟢 %d' % r)

L = []
L.append('# 8/15 周六批次 · 14 场完整赛前分析（终版 · R337-R341 全规则）')
L.append('')
L.append('> 分析日期：2026-08-15（第三版 · 泊松 λ 全量校验）')
L.append('> 模型：V10.29-Fix-R6 + 五大联赛模型 v1.0')
L.append('> 规则：R337 ABC 三级制 + R338 总进球推导 + R339 分层选比 + R340 联赛分层 + R341 赛季阶段假赛曲线')
L.append('> 🛡️ **真实性铁律**：伤停/排名/战绩为联网核实事实；λ/比分/评分为模型推断，非事实陈述')
L.append('')
L.append('## 一、完整预测总表（含假赛评分）')
L.append('')
L.append('| 编号 | 对阵 | 方向 | 比分 TOP3 | 反向比分* | 半全场 | 总进球 | 假赛分 |')
L.append('|------|------|------|-----------|----------|--------|--------|--------|')
for r in rows:
    scs = [s.strip() for s in r['scores'].split('/')]
    revs = [s.replace('*', '') for s in scs if s.endswith('*')]
    rev_str = '、'.join(revs) if revs else '—'
    L.append('| %s | %s vs %s | %s | %s | %s | %s | %s | %s |' % (
        r['no'], r['home'], r['away'], r['dir'].replace('（', '').replace('）', ''),
        ' / '.join(bold_rev(s) for s in scs), rev_str, r['ht'], r['ou'], risk_icon(r['risk'])))
L.append('')
L.append('> **R337**：A级=3主方向；B级=2主+1反向*；C级=1主+2反向*。**加粗标 \\\\* 为反向比分**，半全场与比分逐位对应。')
L.append('> **R338**：总进球由比分推导（取比分总球数概率最高两个）。**R341**：西甲揭幕战认真打 risk 4；芬超野鸡垫底 014 risk 8。')
L.append('')
L.append('---')
L.append('')
L.append('## 二、逐场伤停核实（联网核实事实）')
L.append('')
L.append('| 场次 | 主队伤停 | 客队伤停 | 影响 |')
L.append('|------|---------|---------|------|')
L.append('| 001 | 鹿岛 3 伤 | 名古屋 3 伤 | 双方均衡，鹿岛深度优 |')
L.append('| 003 | 🔴 浦和 5 停赛+后防换血 | 广岛 3 伤 | 浦和重创，广岛利好 |')
L.append('| 004 | 🔴 神户锋线 3 缺 | 🔴 东京后防 4 缺 | 残阵对残阵 |')
L.append('| 005 | 首尔基本齐整 | 大田基本齐整 | 均衡 |')
L.append('| 006 | 光州有伤停 | 浦项有伤停 | 双弱双伤 |')
L.append('| 008 | 博尔顿 0 伤（齐整！）| 普雷斯顿 1 伤 | 升班马阵容利好 |')
L.append('| 009 | 🔴 米亚尔比残阵 | 天狼星齐整 | 米亚尔比重创 |')
L.append('| 010 | 诺维奇 7 伤 | 西布朗 2 伤 | 诺维奇伤重但主场 |')
L.append('| 011 | 奥斯陆有伤停 | 利勒斯特罗姆齐整 | 客队利好 |')
L.append('| 014 | 玛丽港实力弱 | 塞伊奈约基齐整 | 客队明显优 |')
L.append('| 016 | 谢菲联 4 缺 | 伯明翰伤愈利好 | 谢菲联有伤但主场强 |')
L.append('| 019 | 西甲揭幕信息少 | 赫塔费稳定 | R336 揭幕谨慎 |')
L.append('| 024 | 塞维利亚娃娃兵+新帅 | 巴列卡诺稳定 | 🔴 主队剧变 |')
L.append('| 026 | 弗鲁米嫩塞新帅首秀 | 帕尔梅拉斯轮换+伤兵 | 双方调整 |')
L.append('')
L.append('---')
L.append('')
L.append('## 三、假赛评分卡明细（R341 赛季阶段曲线）')
L.append('')
# 分组
hi = [r for r in rows if r['risk'] >= 7]
mid = [r for r in rows if 5 <= r['risk'] <= 6]
lo = [r for r in rows if r['risk'] <= 4]
L.append('### 🔴 高风险（≥7，回避/降级）')
L.append('')
L.append('| 场次 | 分数 | 评分依据 |')
L.append('|------|------|---------|')
for r in hi:
    L.append('| **%s %s vs %s** | **%d** | %s |' % (r['no'], r['home'], r['away'], r['risk'], r['logic']))
if not hi:
    L.append('| （无）| — | 本轮无 ≥7 高风险场 |')
L.append('')
L.append('### 🟠 中风险（5-6，警惕）')
L.append('')
L.append('| 场次 | 分数 | 评分依据 |')
L.append('|------|------|---------|')
for r in mid:
    L.append('| %s %s vs %s | %d | %s |' % (r['no'], r['home'], r['away'], r['risk'], r['logic']))
L.append('')
L.append('### 🟢 低风险（≤4，正常）')
L.append('')
L.append('| 场次 | 分数 | 评分依据 |')
L.append('|------|------|---------|')
for r in lo:
    L.append('| %s %s vs %s | %d | %s |' % (r['no'], r['home'], r['away'], r['risk'], r['logic']))
L.append('')
L.append('---')
L.append('')
L.append('## 四、方向统计（ABC 三级制）')
L.append('')
# 统计方向
from collections import defaultdict
stats = defaultdict(list)
for r in rows:
    stats[r['dir'].replace('（', '').replace('）', '')].append(r['no'])
L.append('| 方向 | 场次 | 数量 |')
L.append('|------|------|------|')
for k, v in sorted(stats.items()):
    L.append('| %s | %s | %d |' % (k, '、'.join(v), len(v)))
L.append('')
L.append('---')
L.append('')
L.append('## 五、大小球分布（R338 总进球推导）')
L.append('')
L.append('- **大球（总进球 ≥2·3）**：%s' % '、'.join(r['no'] for r in rows if '2·3' in r['ou'] or '3·4' in r['ou']))
L.append('- **小球（总进球 ≤1·2）**：%s' % '、'.join(r['no'] for r in rows if r['ou'] in ('总进球 0·1', '总进球 1·2')))
L.append('')
L.append('---')
L.append('')
L.append('## 六、冷门风险 Top6（爆冷方向）')
L.append('')
L.append('| 排名 | 场次 | 冷门方向 | 风险 | 核心逻辑 |')
L.append('|------|------|----------|------|----------|')
for m in re.finditer(r'rank: "([^"]+)", no: "(\d+)", teams: "([^"]+)", dir: "([^"]+)", lv: "([^"]+)", lvTxt: "([^"]+)", logic: "([^"]+)"', m15):
    rank, no, teams, d, lv, lvtxt, logic = m.groups()
    icon = '🔴' if 'red' in lv else ('🟠' if 'orange' in lv else ('🟡' if 'yellow' in lv else '⚪'))
    L.append('| %s | %s %s | %s | %s %s | %s |' % (rank, no, teams, d, icon, lvtxt, logic))
L.append('')
L.append('---')
L.append('')
L.append('## 七、高价值预警')
L.append('')
for m in re.finditer(r'script: "([^"]+)", no: "(\d+)", teams: "([^"]+)", lv: "([^"]+)", lvTxt: "([^"]+)", logic: "([^"]+)"', m15):
    script, no, teams, lv, lvtxt, logic = m.groups()
    icon = '🟠' if 'orange' in lv else '🟡'
    L.append('- **%s**：%s %s（%s %s）— %s' % (script, no, teams, icon, lvtxt, logic))
L.append('')
L.append('---')
L.append('')
L.append('## 八、0-0 预警（泊松概率）')
L.append('')
for m in re.finditer(r'no: "(\d+)", teams: "([^"]+)", p: (\d+), lv: "([^"]+)", lvTxt: "([^"]+)"', m15):
    no, teams, p, lv, lvtxt = m.groups()
    icon = '🟠' if 'orange' in lv else ('🟡' if 'yellow' in lv else '⚪')
    L.append('- %s %s：**%s%%**（%s %s）' % (no, teams, p, icon, lvtxt))
L.append('')
L.append('---')
L.append('')
L.append('## 九、一句话结论')
L.append('')
L.append('> **终版：A 级仅 001 鹿岛 1 场；B 级 12 场（含 019/024 西甲揭幕主场优势胜/平）；C 级 1 场（014 玛丽港野鸡）。假赛风险按 R341 赛季曲线：西甲揭幕认真打（risk 4），芬超野鸡垫底最高（risk 8）。比分按 R338 期望贴合：瑞超/挪超高进球联赛 λ 上调，大球场 7 场（2·3 及以上）。冷门方向 014/009/003/006 均为爆冷主胜剧本。** 🎯')
L.append('')
out = '\n'.join(L)
with io.open(r'D:\Cola\足球分析学习\03_报告复盘\详细赛前分析_8-15周六_14场_20260815.md', 'w', encoding='utf-8') as f:
    f.write(out)
print('written, lines:', len(L))
