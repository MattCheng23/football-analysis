# -*- coding: utf-8 -*-
import io, math, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(8):
        for a in range(8): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d

# R299 校准后的最终 λ（60% 吸收）
lam_final = {
    '001': (2.26, 1.26), '003': (1.36, 2.16), '004': (1.86, 1.66), '005': (1.75, 1.45),
    '006': (1.05, 1.05), '008': (2.01, 1.71), '009': (1.32, 1.42), '010': (2.31, 1.81),
    '011': (1.35, 1.60), '014': (1.19, 1.69), '016': (2.31, 1.51), '019': (1.81, 1.31),
    '024': (1.81, 1.51), '026': (1.15, 1.55),
}
dirs = {'001':'胜','003':'负/平','004':'胜/平','005':'胜/平','006':'平/负','008':'胜/平','009':'平/负','010':'胜/平','011':'负/平','014':'负','016':'胜','019':'胜/平','024':'胜/平','026':'平/负'}
grades = {'001':'A','003':'B','004':'B','005':'B','006':'B','008':'B','009':'B','010':'B','011':'B','014':'C','016':'B','019':'B','024':'B','026':'B'}

# ht 映射：比分 → 半全场（3 个不同，主方向，第3位高价值剧本）
ht_map = {
    '001': ['胜胜', '平胜', '负胜'],
    '003': ['平负', '平平', '负负'],
    '004': ['平平', '胜胜', '胜平'],
    '005': ['平平', '胜胜', '胜平'],
    '006': ['平平', '平负', '负负'],
    '008': ['平平', '胜胜', '胜平'],
    '009': ['平平', '平负', '负负'],
    '010': ['胜胜', '平平', '胜平'],
    '011': ['平平', '平负', '负平'],
    '014': ['平负', '负负', '平平'],  # C: 2主(0-1,1-2)+1反(1-1*)
    '016': ['胜胜', '平胜', '负胜'],
    '019': ['胜胜', '平平', '平胜'],
    '024': ['平平', '胜胜', '平胜'],
    '026': ['平负', '平平', '负负'],
}

print('=== R299 校准最终版 ===')
for no in ['001','003','004','005','006','008','009','010','011','014','016','019','024','026']:
    lh, la = lam_final[no]
    p = probs(lh, la)
    srt = sorted(p.items(), key=lambda x: -x[1])
    main = [k for k, v in srt if (('胜' in dirs[no] and k[0]>k[1]) or ('平' in dirs[no] and k[0]==k[1]) or ('负' in dirs[no] and k[0]<k[1]))]
    if grades[no] == 'C':
        # C级: 2主 + 1反
        rev = [k for k, v in srt if not (('胜' in dirs[no] and k[0]>k[1]) or ('平' in dirs[no] and k[0]==k[1]) or ('负' in dirs[no] and k[0]<k[1]))]
        scores = main[:2] + [rev[0]]
    else:
        scores = main[:3]
    sc_str = ' / '.join(f'{h}-{a}' + ('*' if (grades[no]=='C' and i==2) else '') for i,(h,a) in enumerate(scores))
    hts = ht_map[no]
    ht_str = ' / '.join(hts[i] + ('*' if (grades[no]=='C' and i==2) else '') for i in range(3))
    # ou
    tg = {}
    for k in scores:
        t = k[0]+k[1]
        tg[t] = tg.get(t,0)+p[k]
    srt_tg = sorted(tg.items(), key=lambda x:-x[1])
    ou = '%d·%d' % (min(srt_tg[0][0],srt_tg[1][0]), max(srt_tg[0][0],srt_tg[1][0]))
    print(f'{no} {dirs[no]}{grades[no]} | {sc_str} | {ht_str} | ou {ou}')
