# -*- coding: utf-8 -*-
import io, math

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(9):
        for a in range(9): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d

lam = {'008':(1.65,1.35),'014':(0.8,1.3),'016':(1.95,1.15),'026':(1.0,1.4)}
new_scores = {
    '008': ['1-1','2-1','1-0'],
    '014': ['0-1','0-2','1-1*'],
    '016': ['2-1','2-0','1-0'],
    '026': ['1-1','0-1','0-2'],
}
print('=== ou 重算（R338 概率加权）===')
for no in ['008','014','016','026']:
    lh, la = lam[no]
    p = probs(lh, la)
    tg = {}
    for s in new_scores[no]:
        h, a = map(int, s.replace('*','').split('-'))
        t = h + a
        tg[t] = tg.get(t, 0) + p[(h,a)]
    srt = sorted(tg.items(), key=lambda x: -x[1])
    ou = '%d·%d' % (min(srt[0][0],srt[1][0]), max(srt[0][0],srt[1][0]))
    print(f'{no}: 总球数分布 {[(k, round(v*100,1)) for k,v in srt]} → ou {ou}')
