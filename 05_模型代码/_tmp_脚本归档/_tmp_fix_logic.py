# -*- coding: utf-8 -*-
import io

p = r'D:\Cola\足球分析学习\_发布_public\js\data.js'
with io.open(p, 'r', encoding='utf-8') as f:
    s = f.read()

repl = [
    # 011 奥斯陆：补充关键事实
    ('          logic: "挪超场均2.94偏高+客队冲欧战，客队进球多" },',
     '          logic: "利勒斯特罗姆第4（16场25分）+2连胜攻防俱佳（进19失11）vs 奥斯陆第12+进球联赛第2少（12球）；客队基托拉诺腿骨折缺阵" },'),
    # 014 玛丽港：更新为最新数据
    ('          logic: "芬超垫底队（0胜4平12负）vs 中游，野鸡风险高" },',
     '          logic: "玛丽港19场5分垫底+场均0.5球联赛最差+失41球防守最差 vs 塞伊奈约基第10；交锋近6次1胜0平5负，野鸡剧本矩阵" },'),
    # 010 诺维奇：补伤停细节
    ('          logic: "诺维奇主场+交锋优势（近5次3胜1平1负），西布朗防守组织好但客战" },',
     '          logic: "诺维奇主场+交锋优势（近5次3胜1平1负，杯赛主场3-1），但托皮奇等3人伤缺；西布朗防守组织好近5场2胜2平1负" },'),
]
cnt = 0
for old, new in repl:
    n = s.count(old)
    if n != 1:
        print('WARN count=%d -> %s' % (n, old[:50]))
        continue
    s = s.replace(old, new)
    cnt += 1
with io.open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('replaced: %d / %d' % (cnt, len(repl)))
