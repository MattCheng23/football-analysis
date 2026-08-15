# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 半全场与比分物理匹配 + 3 个不同 + 最可能半场形态
def ht_options(h, a):
    """该比分下所有物理可能的半全场（半场≤3球）"""
    opts = []
    for hh in range(0, h+1):
        for ha in range(0, a+1):
            if hh + ha > 3: continue
            hd = '胜' if hh > ha else ('平' if hh == ha else '负')
            fd = '胜' if h > a else ('平' if h == a else '负')
            opts.append(hd + fd)
    return list(dict.fromkeys(opts))

# 各场比分与最优 ht（按半场最常见形态：半场0-0/1-0/0-1 优先）
print('=== 每场比分的 ht 候选 ===')
games = {
    '008': ['1-1','2-1','2-2'],
    '009': ['1-2','1-1','2-2'],
    '010': ['2-1','1-1','2-2'],
    '011': ['1-2','1-1','0-1'],
    '014': ['0-2','1-2','1-1*'],
    '016': ['2-1','3-1','2-0'],
    '019': ['1-1','0-1','1-2'],
    '024': ['1-2','1-1','0-1'],
    '026': ['1-1','0-1','1-2'],
}
for no, scs in games.items():
    print(f'--- {no} ---')
    for s in scs:
        h, a = map(int, s.replace('*','').split('-'))
        opts = ht_options(h, a)
        # 按"半场形态合理性"排序：半场0-0/1-0/0-1 最常见
        pref = sorted(opts, key=lambda x: 0 if x[0]=='平' else (1 if x[0]=='胜' else 2))
        print(f'  {s}: {opts} → 推荐 {pref[0]}')
    print()
