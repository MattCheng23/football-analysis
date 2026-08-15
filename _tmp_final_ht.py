# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def ht_options(h, a):
    opts = []
    for hh in range(0, h+1):
        for ha in range(0, a+1):
            if hh + ha > 3: continue
            hd = '胜' if hh > ha else ('平' if hh == ha else '负')
            fd = '胜' if h > a else ('平' if h == a else '负')
            opts.append(hd + fd)
    return list(dict.fromkeys(opts))

# 最终版设计（每个比分配一个 ht，3 个不同，物理可能，方向匹配）
final = {
    # 008 博尔顿 胜/平B：1-1(平平)/2-1(胜胜或平胜)/2-2(胜平：半场2-0)
    '008': {'dir': '胜/平', 'scores': ['1-1','2-1','2-2'], 'ht': ['平平','胜胜','胜平']},
    # 009 米亚尔比 平/负B：1-2(平负)/1-1(平平)/2-2(负平：半场0-1追平)
    '009': {'dir': '平/负', 'scores': ['1-2','1-1','2-2'], 'ht': ['平负','平平','负平']},
    # 010 诺维奇 胜/平B：2-1(胜胜)/1-1(平平)/2-2(胜平)
    '010': {'dir': '胜/平', 'scores': ['2-1','1-1','2-2'], 'ht': ['胜胜','平平','胜平']},
    # 011 奥斯陆 负/平B：1-2(平负)/1-1(平平)/0-1(负负：半场0-1)
    '011': {'dir': '负/平', 'scores': ['1-2','1-1','0-1'], 'ht': ['平负','平平','负负']},
    # 014 玛丽港 负C：0-2(负负)/1-2(平负)/1-1*(平平*：反向平)
    '014': {'dir': '负', 'scores': ['0-2','1-2','1-1*'], 'ht': ['负负','平负','平平*']},
    # 016 谢菲联 胜B：2-1(胜胜)/3-1(平胜)/2-0(负胜❌不可能→2-0只能胜胜/平胜)
    #   修正：2-1(胜胜)/3-1(平胜)/2-0(平胜重复)→ 2-1(胜胜)/2-0(平胜)/3-1(负胜：半场0-1大逆转)
    '016': {'dir': '胜', 'scores': ['2-1','2-0','3-1'], 'ht': ['胜胜','平胜','负胜']},
    # 019 阿拉维斯 平/负B：1-1(平平)/0-1(平负)/1-2(负负)
    '019': {'dir': '平/负', 'scores': ['1-1','0-1','1-2'], 'ht': ['平平','平负','负负']},
    # 024 塞维利亚 平/负B：1-2(平负)/1-1(平平)/0-1(负负)
    '024': {'dir': '平/负', 'scores': ['1-2','1-1','0-1'], 'ht': ['平负','平平','负负']},
    # 026 弗鲁米嫩塞 平/负B：1-1(平平)/0-1(平负)/1-2(负负)
    '026': {'dir': '平/负', 'scores': ['1-1','0-1','1-2'], 'ht': ['平平','平负','负负']},
}

print('=== 最终版逐场校验 ===')
all_ok = True
for no, g in final.items():
    scs, hts = g['scores'], g['ht']
    dr = g['dir']
    errors = []
    # 1. ht 3 个不同
    if len(set(hts)) != 3: errors.append(f'ht重复 {hts}')
    # 2. ht 物理可能
    for s, ht in zip(scs, hts):
        h, a = map(int, s.replace('*','').split('-'))
        if ht.replace('*','') not in ht_options(h, a): errors.append(f'{s}→{ht} 不可能')
    # 3. 方向匹配
    for s, ht in zip(scs, hts):
        h, a = map(int, s.replace('*','').split('-'))
        fd = '胜' if h > a else ('平' if h == a else '负')
        if ht[1] != fd: errors.append(f'{s}→{ht} 第二字不匹配')
    # 4. 比分TOP1方向
    h, a = map(int, scs[0].replace('*','').split('-'))
    fd = '胜' if h > a else ('平' if h == a else '负')
    if fd not in dr: errors.append(f'TOP1方向 {scs[0]} 不在 {dr}')
    status = '✅' if not errors else '❌'
    if errors: all_ok = False
    print(f'{no} {dr} {status} | {scs} | {hts} | {errors if errors else "OK"}')
print()
print('全部通过:' , all_ok)
