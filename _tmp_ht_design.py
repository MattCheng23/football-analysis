# -*- coding: utf-8 -*-
import io, math, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(8):
        for a in range(8): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d

# R299 校准 λ
lam = {'001':(2.26,1.26),'003':(1.36,2.16),'004':(1.86,1.66),'005':(1.75,1.45),'006':(1.05,1.05),'008':(2.01,1.71),'009':(1.32,1.42),'010':(2.31,1.81),'011':(1.35,1.60),'014':(1.19,1.69),'016':(2.31,1.51),'019':(1.81,1.31),'024':(1.81,1.51),'026':(1.15,1.55)}
dirs = {'001':'胜','003':'负/平','004':'胜/平','005':'胜/平','006':'平/负','008':'胜/平','009':'平/负','010':'胜/平','011':'负/平','014':'负','016':'胜','019':'胜/平','024':'胜/平','026':'平/负'}

def ht_candidates(score):
    """比分 → 可能的半全场（半场形态合理）"""
    h, a = score
    res = []
    # 半场比分枚举：0..min(h,a) 大致合理
    for hh in range(0, h + 1):
        for ha in range(0, a + 1):
            if hh + ha > 3: continue  # 半场一般 ≤3 球
            # 半场方向
            hd = '胜' if hh > ha else ('平' if hh == ha else '负')
            # 全场方向
            fd = '胜' if h > a else ('平' if h == a else '负')
            res.append(hd + fd)
    return list(dict.fromkeys(res))

print('=== 逐位 ht 设计（硬约束：3位不重复 + 第二字匹配比分方向）===')
for no in ['001','003','004','005','006','008','009','010','011','014','016','019','024','026']:
    lh, la = lam[no]
    p = probs(lh, la)
    srt = sorted(p.items(), key=lambda x: -x[1])
    is_c = no == '014'
    # 主方向比分
    main = [k for k, v in srt if (('胜' in dirs[no] and k[0]>k[1]) or ('平' in dirs[no] and k[0]==k[1]) or ('负' in dirs[no] and k[0]<k[1]))]
    if is_c:
        rev = [k for k, v in srt if not (('胜' in dirs[no] and k[0]>k[1]) or ('平' in dirs[no] and k[0]==k[1]) or ('负' in dirs[no] and k[0]<k[1]))]
        scores = main[:2] + [rev[0]]
    else:
        scores = main[:3]
    # 逐位找 ht（从候选里选，尽量避开前面已用的）
    hts = []
    used = set()
    for i, sc in enumerate(scores):
        cands = ht_candidates(sc)
        # 优先选未用过的
        pick = None
        for c in cands:
            if c not in used:
                pick = c
                break
        if pick is None:
            pick = cands[0]  # 都用了就复用（去重失败标记）
        used.add(pick)
        hts.append(pick)
    sc_str = ' / '.join(f'{h}-{a}' + ('*' if (is_c and i == 2) else '') for i, (h, a) in enumerate(scores))
    ht_str = ' / '.join(hts[i] + ('*' if (is_c and i == 2) else '') for i in range(3))
    dup = '⚠️重复' if len(set(hts)) < 3 else 'OK'
    print(f'{no} {dirs[no]}{"C" if is_c else "B"} | {sc_str} | {ht_str} | {dup}')
