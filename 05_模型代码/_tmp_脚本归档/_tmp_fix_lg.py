# -*- coding: utf-8 -*-
import re
p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
s = open(p, encoding='utf-8').read()
marker = '"2026-08-15": {'
idx = s.index(marker)
head, tail = s[:idx], s[idx:]
# 按完整行（含队名）唯一匹配，避免误伤 8/14 批次
repls = [
    ('005', '首尔FC', 'lg-j1', 'lg-k1'),
    ('006', '光州FC', 'lg-j1', 'lg-k1'),
    ('019', '阿拉维斯', 'lg-j1', 'lg-laliga'),
    ('024', '塞维利亚', 'lg-j1', 'lg-laliga'),
    ('026', '弗鲁米嫩塞', 'lg-j1', 'lg-bras'),
]
for no, home, old_lg, new_lg in repls:
    pat = re.compile(r'(no: "' + no + r'", home: "' + home + r'", away: "[^"]*", league: "[^"]*", lg: ")' + old_lg + r'(")')
    tail, n = pat.subn(r'\1' + new_lg + r'\2', tail, count=1)
    print(no, home, 'ok' if n else 'MISS')
open(p, 'w', encoding='utf-8').write(head + tail)
print('done')
