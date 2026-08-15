# -*- coding: utf-8 -*-
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pois(k, lam): return math.exp(-lam) * lam**k / math.factorial(k)
def probs(lh, la):
    d = {}
    for h in range(9):
        for a in range(9): d[(h, a)] = pois(h, lh) * pois(a, la)
    return d

# R299 校准 λ（60% 吸收后的晚场值）
lam = {
    '008': (1.65, 1.35), '009': (1.35, 1.45), '010': (1.95, 1.45),
    '011': (1.35, 1.60), '014': (0.80, 1.30), '016': (1.95, 1.15),
    '019': (1.10, 1.30), '024': (1.30, 1.50), '026': (1.00, 1.40),
}
cur = {
    '008': ['1-1','2-1','2-2'], '009': ['1-2','1-1','2-2'], '010': ['2-1','1-1','2-2'],
    '011': ['1-2','1-1','0-1'], '014': ['0-2','1-2','1-1*'], '016': ['2-1','2-0','3-1'],
    '019': ['1-1','0-1','1-2'], '024': ['1-2','1-1','0-1'], '026': ['1-1','0-1','1-2'],
}
dirs = {'008':'胜/平','009':'平/负','010':'胜/平','011':'负/平','014':'负','016':'胜','019':'平/负','024':'平/负','026':'平/负'}

print('=== 逐场：当前比分 vs 校准λ下主方向概率最高的 3 个（含大球）===')
for no in ['008','009','010','011','014','016','019','024','026']:
    lh, la = lam[no]
    p = probs(lh, la)
    srt = sorted(p.items(), key=lambda x: -x[1])
    dr = dirs[no]
    # 主方向比分（含平/负双方向）
    main = [(k, v) for k, v in srt if (('胜' in dr and k[0]>k[1]) or ('平' in dr and k[0]==k[1]) or ('负' in dr and k[0]<k[1]))]
    top3 = main[:3]
    cur_ranks = []
    for s in cur[no]:
        h, a = map(int, s.replace('*','').split('-'))
        r = next((i+1 for i,(k,v) in enumerate(main) if k==(h,a)), '>15')
        cur_ranks.append(f'{s}#{r}')
    print(f'--- {no} {dr} (λ{lh}/{la} 期望{lh+la:.1f}) ---')
    print(f'  当前: {" ".join(cur_ranks)}')
    print(f'  主方向TOP3: {" ".join(f"{h}-{a}({v*100:.1f}%)" for (h,a),v in top3)}')
    # 大球补充候选（主方向内 ≥3球 且概率前8）
    big = [(k,v) for k,v in main if k[0]+k[1]>=3][:3]
    print(f'  主方向大球候选: {" ".join(f"{h}-{a}({v*100:.1f}%)" for (h,a),v in big)}')
    print()
