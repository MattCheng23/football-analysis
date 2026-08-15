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

# ht 设计（前2位对应比分TOP1/2，第3位独立高价值剧本，全部主方向）
ht_map = {
    '001': ['胜胜','平胜','负胜'],
    '003': ['平负','平平','负负'],
    '004': ['平平','胜胜','平胜'],
    '005': ['平平','胜胜','平胜'],
    '006': ['平平','平负','负负'],
    '008': ['平平','胜胜','平胜'],
    '009': ['平平','平负','负负'],
    '010': ['平平','胜胜','胜平'],
    '011': ['平平','平负','负负'],
    '014': ['负负','平平','平胜'],  # C级：1主+2反（后两位加*）
    '016': ['胜胜','平胜','负胜'],
    '019': ['胜胜','平平','平胜'],
    '024': ['平平','胜胜','平胜'],
    '026': ['平负','平平','负负'],
}

print('=== R337修订: AB=正路(3主), C=1主+2反 ===')
for no in ['001','003','004','005','006','008','009','010','011','014','016','019','024','026']:
    p = probs(*lam[no])
    srt = sorted(p.items(), key=lambda x: -x[1])
    is_c = no == '014'
    if is_c:
        # C级: 1主+2反
        main = [k for k, v in srt if dk(k) in dirs[no]][:1]
        rev = [k for k, v in srt if dk(k) not in dirs[no]][:2]
        scores = main + rev
        marks = [''] + ['*'] * 2
    else:
        # A/B级: 3主方向
        scores = [k for k, v in srt if dk(k) in dirs[no]][:3]
        marks = ['', '', '']
    sc_str = ' / '.join(f'{h}-{a}{marks[i]}' for i, (h, a) in enumerate(scores))
    hts = ht_map[no]
    ht_str = ' / '.join(hts[i] + marks[i] for i in range(3))
    # ou：比分总球数概率加权前二
    tg = {}
    for k in scores:
        t = k[0] + k[1]
        tg[t] = tg.get(t, 0) + p[k]
    srt_tg = sorted(tg.items(), key=lambda x: -x[1])
    ou = '%d·%d' % (min(srt_tg[0][0], srt_tg[1][0]), max(srt_tg[0][0], srt_tg[1][0]))
    print(f'{no} {dirs[no]}{"C" if is_c else "B"} | 比分: {sc_str} | ht: {ht_str} | 总进球 {ou}')
