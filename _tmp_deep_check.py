# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 晚场 9 场：当前比分/半全场 + P9 大球覆盖检查 + ht 合理性
cur = {
    '008': ('胜/平', ['1-1','2-1','2-2'], ['平平','平胜','胜平']),
    '009': ('平/负', ['1-2','1-1','2-2'], ['平负','平平','负平']),
    '010': ('胜/平', ['2-1','1-1','2-2'], ['胜胜','平平','胜平']),
    '011': ('负/平', ['1-2','1-1','0-1'], ['平负','平平','负负']),
    '014': ('负',   ['0-2','1-2','1-1*'], ['负负','平负','平平*']),
    '016': ('胜',   ['2-1','3-1','2-0'], ['胜胜','平胜','负胜']),
    '019': ('平/负', ['1-1','0-1','1-2'], ['平平','平负','负负']),
    '024': ('平/负', ['1-2','1-1','0-1'], ['平负','平平','负负']),
    '026': ('平/负', ['1-1','0-1','1-2'], ['平平','平负','负负']),
}

print('=== 逐场检查：进球覆盖 + 半全场合理性 ===')
for no in ['008','009','010','011','014','016','019','024','026']:
    dr, scs, hts = cur[no]
    print(f'--- {no} {dr} ---')
    # 1) 进球区间覆盖（P9：应含 ≥3 球偏差覆盖；2-2/3-1/2-3 类）
    for i, s in enumerate(scs):
        h, a = map(int, s.replace('*','').split('-'))
        total = h + a
        ht = hts[i]
        # 2) ht 合理性：该比分能否打出该半全场？
        # 半场方向 vs 全场方向推导
        # 枚举半场 (hh,ha)，hh<=h, ha<=a，且 hh+ha <= 3
        possible = set()
        for hh in range(0, h+1):
            for ha in range(0, a+1):
                if hh + ha > 3: continue
                hd = '胜' if hh > ha else ('平' if hh == ha else '负')
                fd = '胜' if h > a else ('平' if h == a else '负')
                possible.add(hd + fd)
        ok = ht.replace('*','') in possible
        mark = '✅' if ok else '❌ 不可能'
        print(f'  {s} ({total}球) → ht {ht} {mark}')
    # 3) 是否有 ≥3 球偏差覆盖
    totals = [sum(map(int, s.replace("*","").split("-"))) for s in scs]
    big = any(t >= 3 for t in totals)
    print(f'  进球区间: {sorted(set(totals))} | ≥3球覆盖: {"✅" if big else "⚠️ 无（偏保守）"}')
    print()
