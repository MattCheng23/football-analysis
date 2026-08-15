# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 从 data.js 读取并全量校验（含 ht 物理匹配）
src = io.open(r'D:\Cola\足球分析学习\_发布_public\js\data.js', encoding='utf-8').read()
import re
m15 = src[src.index('"2026-08-15"'):]

def ht_options(h, a):
    opts = []
    for hh in range(0, h+1):
        for ha in range(0, a+1):
            if hh + ha > 3: continue
            hd = '胜' if hh > ha else ('平' if hh == ha else '负')
            fd = '胜' if h > a else ('平' if h == a else '负')
            opts.append(hd + fd)
    return list(dict.fromkeys(opts))

err = 0
for m in re.finditer(r'no: "(\d+)", home: "([^"]+)", away: "([^"]+)", league: "([^"]+)", lg: "([^"]+)",\s*dir: "([^"]+)", dc: "([^"]+)", scores: "([^"]+)", ht: "([^"]+)", ou: "([^"]+)", risk: (\d+),', m15):
    no, home, away, league, lg, dr, dc, scores, ht, ou, risk = m.groups()
    scs = [x.strip() for x in scores.split('/')]
    hts = [x.strip() for x in ht.split('/')]
    # 1. ht 3 个不同
    if len(set(hts)) != 3: err += 1; print(f'{no} ht重复 {hts}')
    # 2. ht 物理可能 + 方向匹配
    for s, h in zip(scs, hts):
        hh, aa = map(int, s.replace('*','').split('-'))
        if h.replace('*','') not in ht_options(hh, aa): err += 1; print(f'{no} {s}→{h} 物理不可能')
        fd = '胜' if hh > aa else ('平' if hh == aa else '负')
        if h[1] != fd: err += 1; print(f'{no} {s}→{h} 方向不匹配')
    # 3. 反向结构
    rev = sum(1 for s in scs if '*' in s)
    expect = 1 if 'C' in dr else 0
    if rev != expect: err += 1; print(f'{no} ABC反 {dr} rev={rev}')
print('总错误:', err)
