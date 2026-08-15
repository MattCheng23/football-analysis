# -*- coding: utf-8 -*-
import re
p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
s = open(p, encoding='utf-8').read()
times = {
    '001': '17:00', '003': '18:00', '004': '19:00', '005': '18:30', '006': '18:30',
    '008': '19:30', '009': '21:00', '010': '22:00', '011': '22:00',
    '014': '次日 00:00', '016': '次日 00:30', '019': '次日 01:30',
    '024': '次日 03:30', '026': '次日 03:30'
}
marker = '"2026-08-15": {'
idx = s.index(marker)
head, tail = s[:idx], s[idx:]
for no, t in times.items():
    pat = re.compile(r'(\{ no: "' + no + r'", home: "[^"]*", away: "[^"]*", league: "[^"]*", lg: "[^"]*",)')
    tail, n = pat.subn(r'\1 time: "' + t + '",', tail, count=1)
    print(no, 'ok' if n else 'MISS')
open(p, 'w', encoding='utf-8').write(head + tail)
print('done')
