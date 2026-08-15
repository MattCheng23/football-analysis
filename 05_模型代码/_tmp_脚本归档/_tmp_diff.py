# -*- coding: utf-8 -*-
import io, math, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(9):
        for a in range(9): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d
def ht_options(h, a):
    opts = []
    for hh in range(0, h+1):
        for ha in range(0, a+1):
            if hh + ha > 3: continue
            hd = '胜' if hh > ha else ('平' if hh == ha else '负')
            fd = '胜' if h > a else ('平' if h == a else '负')
            opts.append(hd + fd)
    return list(dict.fromkeys(opts))

# 差异化方案：每场大球覆盖用不同比分
# 008 对攻场 → 2-2（博尔顿主场近10场7场>3球）
# 009 客队火力 → 1-3（天狼星客场场均2.9，客胜3球覆盖）
# 010 主队强攻 → 3-1（诺维奇主场+交锋优势，3-1 杯赛赢过西布朗）
# 011 客队零封 → 0-2（利勒斯特罗姆第4攻防俱佳，0-2 客胜）
new = {
    '008': (1.65, 1.35, ['1-1','2-1','2-2'], ['平平','胜胜','胜平']),
    '009': (1.35, 1.45, ['1-2','1-1','1-3'], ['平负','平平','负负']),
    '010': (1.95, 1.45, ['2-1','1-1','3-1'], ['胜胜','平平','平胜']),
    '011': (1.35, 1.60, ['1-2','1-1','0-2'], ['平负','平平','负负']),
}
print('=== 差异化方案校验（概率 + ht 物理 + ou 推导）===')
for no in ['008','009','010','011']:
    lh, la, scs, hts = new[no]
    p = probs(lh, la)
    print(f'--- {no} (λ{lh}/{la}) ---')
    # ht 校验
    ok = True
    for s, ht in zip(scs, hts):
        h, a = map(int, s.replace('*','').split('-'))
        prob = p[(h,a)]*100
        phys = ht in ht_options(h,a)
        if not phys: ok = False; print(f'  ❌ {s}→{ht} 不可能')
        print(f'  {s} ({prob:.1f}%) → {ht} {"✅" if phys else "❌"}')
    # ou 推导
    tg = {}
    for s in scs:
        h, a = map(int, s.replace('*','').split('-'))
        t = h+a
        tg[t] = tg.get(t,0) + p[(h,a)]
    srt = sorted(tg.items(), key=lambda x: -x[1])
    ou = '%d·%d' % (min(srt[0][0],srt[1][0]), max(srt[0][0],srt[1][0]))
    dup = '⚠️ht重复' if len(set(hts)) != 3 else 'OK'
    print(f'  总球分布: {[(k, round(v*100,1)) for k,v in srt]} → ou {ou} | ht去重 {dup}')
    print()
