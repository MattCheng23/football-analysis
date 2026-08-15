# -*- coding: utf-8 -*-
import io, re, json

# 读取 data.js 并解析
src = io.open(r'D:\Cola\足球分析学习\_发布_public\js\data.js', encoding='utf-8').read()

# 提取 8/15 批次 matches（用正则解析每个对象）
m15 = src[src.index('"2026-08-15"'):]
rows = []
for m in re.finditer(r'\{ no: "(\d+)", home: "([^"]+)", away: "([^"]+)", league: "([^"]+)", lg: "([^"]+)",\s*dir: "([^"]+)", dc: "([^"]+)", scores: "([^"]+)", ht: "([^"]+)", ou: "([^"]+)", risk: (\d+),', m15):
    no, home, away, league, lg, dir, dc, scores, ht, ou, risk = m.groups()
    rows.append((no, home, away, dir, scores, ht, ou, int(risk)))

# 生成表格（反向比分用 **加粗** 标记）
def bold_rev(s):
    return re.sub(r'(\d+-\d+)\*', r'**\1\\***', s)

risk_icon = lambda r: '🔴 %d' % r if r >= 7 else ('🟠 %d' % r if r >= 5 else '🟢 %d' % r)

lines = []
lines.append('## 一、完整预测总表（含假赛评分）')
lines.append('')
lines.append('| 编号 | 对阵 | 方向 | 比分 TOP3 | 反向比分* | 半全场 | 大小球 | 假赛分 |')
lines.append('|------|------|------|-----------|----------|--------|--------|--------|')
for no, home, away, dir, scores, ht, ou, risk in rows:
    scs = [s.strip() for s in scores.split('/')]
    revs = [s.replace('*', '') for s in scs if s.endswith('*')]
    sc_bold = ' / '.join(bold_rev(s) for s in scs)
    rev_str = '、'.join(revs) if revs else '—'
    lines.append('| %s | %s vs %s | %s | %s | %s | %s | %s | %s |' % (
        no, home, away, dir.replace('（', '').replace('）', ''), sc_bold, rev_str, ht, ou, risk_icon(risk)))
lines.append('')
lines.append('> **R337 等级说明**：A级=高置信（比分TOP3全主方向）；B级=中置信（2主+1反向）；C级=低置信（1主+2反向）。**加粗标 \\\\* 为反向比分**（该冷门方向下最可能的比分，防爆冷覆盖）；**半全场 TOP3 与比分结构同步**（逐位对应：2-1→胜胜、1-1→平平、1-2→平负）。')
lines.append('> **P8 比分第一性铁律**：比分 TOP3 为泊松 λ 下最合理比分（独立最优），总进球 X·Y 由比分推导（R338：取比分总球数众数前二），**严禁用总进球反向裁剪比分**。')
lines.append('> **R341 赛季阶段假赛曲线**：西甲揭幕战（019/024）认真打，假赛分仅 4；芬超野鸡垫底（014）risk 8。')
lines.append('')
new_block = '\n'.join(lines)

p = r'D:\Cola\足球分析学习\03_报告复盘\详细赛前分析_8-15周六_14场_20260815.md'
s = io.open(p, encoding='utf-8').read()
start = s.index('## 一、')
end = s.index('## 二、')
s = s[:start] + new_block + '\n\n---\n\n' + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('done, block lines:', len(lines))
