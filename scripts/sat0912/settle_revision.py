# -*- coding: utf-8 -*-
"""改判结算器：初稿快照 × 终稿 data.js × 赛果 data-review.js 三方对齐，逐场算四维判定。

用法：python settle_revision.py 2026-09-11 [2026-09-10]
判定口径（与复盘台账一致）：
  方向 = 实际 FT 结果 ∈ dir 选项集（剥掉括号级别与 A/B 标记）
  比分 = 实际比分 ∈ scores 三档（忽略 * 反向标记）
  半全场 = (半场领先方+全场结果) 二字组合 ∈ ht 三档（忽略 *）
  总进球 = 实际总球 ∈ ou 档位集（"总进球 2·3" → {2,3}；"1·2+2·3" → {1,2,3}）
"""
import re, io, sys, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:\Cola\足球分析学习")


def tokens_dir(s):
    s = re.sub(r'（[^）]*）|\([^)]*\)', '', s or '')
    return set(re.findall(r'主胜|客胜|平', s))


def band_set(s):
    s = s or ''
    out = set()
    for a, b in re.findall(r'(\d)\s*·\s*(\d)', s):
        lo, hi = int(a), int(b)
        out.update(range(min(lo, hi), max(lo, hi) + 1))
    return out


def scores_set(s):
    return set(re.findall(r'\d+-\d+', (s or '').replace('*', '')))


def ht_set(s):
    return {t.strip() for t in re.split(r'[/／]', (s or '').replace('*', '')) if t.strip()}


def actuals(score_field):
    """'2-3（2-0）' → (combo, ft_result, total, ft_score, ht_score)"""
    m = re.match(r'\s*(\d+)-(\d+)\s*（\s*(\d+)-(\d+)\s*）', score_field)
    if not m:
        m2 = re.match(r'\s*(\d+)-(\d+)\s*$', score_field)
        if not m2:
            return None
        fh, fa = int(m2.group(1)), int(m2.group(2))
        hh = ha = None
    else:
        fh, fa, hh, ha = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    res = '主胜' if fh > fa else ('客胜' if fh < fa else '平')
    ch = '胜' if fh > fa else ('负' if fh < fa else '平')
    if hh is None:
        return res, ch, fh + fa, f"{fh}-{fa}", None, None
    hres = '胜' if hh > ha else ('负' if hh < ha else '平')
    return res, ch, fh + fa, f"{fh}-{fa}", f"{hh}-{ha}", hres + ch


def load_draft(date):
    p = ROOT / "_backup" / "drafts" / f"{date}.draft.json"
    d = json.loads(p.read_text(encoding='utf-8'))
    return {m['no']: m for m in d['matches']}, d.get('taken', '')


def load_final(date):
    t = (ROOT / "_发布_public" / "js" / "data.js").read_text(encoding='utf-8')
    k = t.find(f'"{date}": {{')
    nxt = re.search(r'\n  "20\d{2}-\d{2}-\d{2}": \{', t[k + 10:])
    blk = t[k: k + 10 + (nxt.start() if nxt else 40000)]
    mi = blk.find('matches: [')
    op = blk.index('[', mi)
    depth = 0
    for j in range(op, len(blk)):
        if blk[j] == '[':
            depth += 1
        elif blk[j] == ']':
            depth -= 1
            if depth == 0:
                break
    arr = blk[op + 1:j]                      # matches 数组内部，不含外层方括号
    # 顶层条目 = 深度 1 的 {...}（深度法，避免被 logic 里的 { no: 干扰）
    hits = [m.start() for m in re.finditer(r'\{\s*no:\s*"\d{3}"', arr)]
    out = {}
    for i, st in enumerate(hits):
        e = arr[st: hits[i + 1] if i + 1 < len(hits) else len(arr)]
        g = lambda n: (re.search(n + r':\s*"((?:[^"\\]|\\.)*)"', e) or [None, ''])[1]
        no = re.search(r'no:\s*"(\d{3})"', e).group(1)
        out[no] = dict(no=no, dir=g('dir'), scores=g('scores'), ht=g('ht'), ou=g('ou'))
        if not (out[no]['scores'] and out[no]['ht'] and out[no]['ou']):
            print(f"  [warn] 终稿 {no} 字段缺失：{out[no]}")
    return out


def load_actual(date):
    t = (ROOT / "_发布_public" / "js" / "data-review.js").read_text(encoding='utf-8')
    k = t.find(f'"{date}": {{')
    rk = t.find('results: [', k)
    end = t.find('evidence: [', rk)
    nxt = re.search(r'\n  "20\d{2}-\d{2}-\d{2}": \{', t[rk:])
    if end < 0 or (nxt and rk + nxt.start() < end):
        end = rk + (nxt.start() if nxt else len(t) - rk)
    blk = t[rk:end]
    out = {}
    for m in re.finditer(r'\{ no: "(\d{3})".*?sc: "\w+" \s*\}', blk, re.S):
        e = m.group(0)
        f = lambda n: (re.search(n + r': "((?:[^"\\]|\\.)*)"', e) or [None, ''])[1]
        out[m.group(1)] = f('score')
    return out


for date in sys.argv[1:]:
    draft, taken = load_draft(date)
    final = load_final(date)
    act = load_actual(date)
    print("=" * 104)
    print(f"### {date}  初稿 {taken}（{len(draft)} 场） vs 终稿（{len(final)} 场） vs 赛果（{len(act)} 场）")
    print(f"{'场':<5}{'实际(HT)':<12}{'初稿方向/比分/ht/ou':<22}{'终稿方向/比分/ht/ou':<22}{'初':<4}{'终':<4}Δ 说明")
    tot_d = tot_f = 0
    for no in sorted(act):
        a = actuals(act[no])
        if not a or no not in draft or no not in final:
            print(f"{no:<5}!! 数据缺：draft={no in draft} final={no in final} actual={bool(a)}")
            continue
        res, ch, total, fts, hts, combo = a
        row = {}
        for tag, src in (('d', draft[no]), ('f', final[no])):
            v = []
            v.append(res in tokens_dir(src.get('dir')))
            v.append(fts in scores_set(src.get('scores')))
            v.append(combo in ht_set(src.get('ht')))
            v.append(total in band_set(src.get('ou')))
            row[tag] = v
        sd, sf = sum(row['d']), sum(row['f'])
        tot_d += sd; tot_f += sf
        mark = lambda v: ''.join('✅' if x else '❌' for x in v)
        delta = []
        for i, lab in enumerate(['方向', '比分', 'ht', 'ou']):
            if row['d'][i] != row['f'][i]:
                delta.append(f"{lab}:{'✅→❌' if row['d'][i] else '❌→✅'}")
        print(f"{no:<5}{(fts + '(' + hts + ')') if hts else fts:<12}"
              f"{mark(row['d']):<22}{mark(row['f']):<22}{sd}/4{'':<1}{sf}/4{'':<1}"
              f"{'  ' + '；'.join(delta) if delta else ''}")
    n = len(act)
    print(f"→ 初稿 {tot_d}/{n*4} ({tot_d/(n*4)*100:.1f}%)  |  终稿 {tot_f}/{n*4} "
          f"({tot_f/(n*4)*100:.1f}%)  |  改判净 {tot_f - tot_d:+d} 维 "
          f"({(tot_f-tot_d)/(n*4)*100:+.1f}pp)")
