# -*- coding: utf-8 -*-
import io, math, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(8):
        for a in range(8): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d
def dk(k):
    h, a = k; return '胜' if h > a else ('平' if h == a else '负')

lam = {'001':[1.9,0.9],'003':[1.0,1.8],'004':[1.5,1.3],'005':[1.6,1.3],'006':[0.9,0.9],'008':[1.65,1.35],'009':[1.35,1.45],'010':[1.95,1.45],'011':[1.35,1.6],'014':[0.8,1.3],'016':[1.95,1.15],'019':[1.45,0.95],'024':[1.45,1.15],'026':[1.0,1.4]}
dirs = {'001':'胜','003':'负/平','004':'胜/平','005':'胜/平','006':'平/负','008':'胜/平','009':'平/负','010':'胜/平','011':'负/平','014':'负','016':'胜','019':'胜/平','024':'胜/平','026':'平/负'}

print('=== R342 最终选比（前2主 + 第3位max(主3,反) + rev）===')
for no in ['003','004','005','008','009','011','019','024','026']:
    p = probs(*lam[no])
    srt = sorted(p.items(), key=lambda x: -x[1])
    main = [k for k, v in srt if dk(k) in dirs[no]]
    rev = [k for k, v in srt if dk(k) not in dirs[no]]
    top2 = main[:2]
    third = main[2] if p[main[2]] >= p[rev[0]] else rev[0]
    in_rev = third in rev
    scores = top2 + [third]
    rev_score = (rev[0] if in_rev else rev[0])  # 反向参考：始终输出最高反向
    # ou 推导：比分总球数概率加权前二
    tg = {}
    for k in scores:
        t = k[0] + k[1]
        tg[t] = tg.get(t, 0) + p[k]
    srt_tg = sorted(tg.items(), key=lambda x: -x[1])
    ou = sorted([srt_tg[0][0], srt_tg[1][0]])[0] if len(srt_tg) < 2 else sorted([srt_tg[0][0], srt_tg[1][0]]).__str__()
    ou2 = '%d·%d' % (min(srt_tg[0][0], srt_tg[1][0]), max(srt_tg[0][0], srt_tg[1][0]))
    sc_str = ' / '.join(f'{h}-{a}' + ('*' if (i == 2 and in_rev) else '') for i, (h, a) in enumerate(scores))
    print(f'{no} {dirs[no]}B | 比分: {sc_str} | rev参考: {rev_score[0]}-{rev_score[1]} | 总进球: {ou2} | 反向在TOP3: {in_rev}')
