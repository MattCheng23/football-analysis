# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 最终版敲定：仅 011 调整（0-1 → 2-2，P9 大球覆盖），其余 8 场保持
repl = [
    # 011 奥斯陆：0-1 → 2-2（客队第4火力，2-2 覆盖 4 球偏差；ht 负负→负平）
    ('{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-1", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 4,',
     '{ no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",\n          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 2-2", ht: "平负/平平/负平", ou: "总进球 2·3", risk: 4,'),
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
