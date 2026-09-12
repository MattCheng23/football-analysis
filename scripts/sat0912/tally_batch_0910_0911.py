# -*- coding: utf-8 -*-
"""统一口径重算 0910 / 0911 两批四维命中台账（v3·结构感知 + 键值对解析 + 严格交叉校验）。

v2 的两个 bug（已修）：
 1) 字段正则 `s: "..."` 会命中 `teams: "..."` 的尾部 → 比分被全部误判为 ❌；
 2) 校验逻辑对"取到非 ok/no 的坏值"静默跳过 → 掩盖了 1)。
v3 改为把每条 entry 解析成 dict（键值对），并对每个维度强制要求字段值 ∈ {ok,no}，否则报 ERROR。
"""
import re, io, sys, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = Path(r"D:\Cola\足球分析学习\_发布_public\js\data-review.js")
text = P.read_text(encoding='utf-8')

KV = re.compile(r'([A-Za-z_]\w*)\s*:\s*"((?:[^"\\]|\\.)*)"')
ENTRY = re.compile(r'\{ no: "(\d{3})".*?sc: "\w+" \s*\}', re.S)
DIMS = (('d', '方向'), ('s', '比分'), ('h', '半全场'))


def slice_results(date):
    key = f'"{date}": {{'
    k = text.find(key)
    if k < 0:
        return None
    seg = text[k:]
    rk = seg.find('results: [')
    if rk < 0:
        return None
    start = k + rk
    end = text.find('evidence: [', start)
    nxt = re.search(r'\n  "\d{4}-\d{2}-\d{2}": \{', text[start:])
    if end < 0 or (nxt and start + nxt.start() < end):
        end = start + (nxt.start() if nxt else len(text) - start)
    return text[start:end]


def verdict(sig, *labels):
    for lab in labels:
        m = re.search(re.escape(lab) + r'\s*([✅❌])', sig)
        if m:
            return m.group(1) == '✅'
    return None


def parse(date):
    blk = slice_results(date)
    if blk is None:
        return []
    rows = []
    for m in ENTRY.finditer(blk):
        e = m.group(0)
        f = dict(KV.findall(e))
        f.setdefault('no', m.group(1))
        errs = []
        for key, lab in DIMS:
            if f.get(key) not in ('ok', 'no'):
                errs.append(f"字段 {key} 取值异常：{f.get(key)!r}")
        ou_hit = verdict(f.get('signal', ''), 'ou', '总进球')
        if ou_hit is None:
            errs.append("OU 无判定标记")
        warn = []
        for key, lab in DIMS:
            sv = verdict(f.get('signal', ''), lab)
            if sv is not None and f.get(key) in ('ok', 'no'):
                if (f[key] == 'ok') != sv:
                    warn.append(f"{lab}:字段{f[key]}/signal{'✅' if sv else '❌'}")
        rows.append(dict(no=f['no'], d=f.get('d'), s=f.get('s'), h=f.get('h'),
                         ou_hit=ou_hit, ou=f.get('ou', ''), sc=f.get('sc', ''),
                         warn=warn, errs=errs))
    return rows


summary, all_rows = {}, {}
print("=" * 104)
for date in ["2026-09-09", "2026-09-10", "2026-09-11"]:
    rows = parse(date)
    all_rows[date] = rows
    n = len(rows)
    dims = {'dir': 0, 'score': 0, 'ht': 0, 'ou': 0}
    print(f"\n### {date}  results 共 {n} 场")
    print(f"{'场':<5}{'方向':<5}{'比分':<5}{'半全场':<6}{'总进球':<6}{'档位':<16}{'sc':<8}校验")
    for r in rows:
        dh, sh, hs, oh = r['d'] == 'ok', r['s'] == 'ok', r['h'] == 'ok', r['ou_hit'] is True
        dims['dir'] += dh; dims['score'] += sh; dims['ht'] += hs; dims['ou'] += oh
        note = ';'.join(r['warn'] + ['❗' + x for x in r['errs']])
        print(f"{r['no']:<5}{'✅' if dh else '❌':<5}{'✅' if sh else '❌':<5}{'✅' if hs else '❌':<6}"
              f"{'✅' if oh else '❌':<6}{(r['ou'] or '-'):<16}{r['sc']:<8}{note}")
    tot = sum(dims.values())
    summary[date] = (n, dims, tot)
    print(f"→ 方向 {dims['dir']}/{n} ({dims['dir']/n*100:.1f}%) | 比分 {dims['score']}/{n} "
          f"({dims['score']/n*100:.1f}%) | 半全场 {dims['ht']}/{n} ({dims['ht']/n*100:.1f}%) | "
          f"总进球 {dims['ou']}/{n} ({dims['ou']/n*100:.1f}%)  ==> 四维 {tot}/{n*4} "
          f"({tot/(n*4)*100:.1f}%)")

print("\n" + "=" * 104)
print("【两批对照·修正后】")
for date, (n, dims, tot) in summary.items():
    print(f"  {date}: 四维 {tot}/{n*4} = {tot/(n*4)*100:.1f}%  |  方向 {dims['dir']}/{n}  "
          f"比分 {dims['score']}/{n}  半全场 {dims['ht']}/{n}  总进球 {dims['ou']}/{n}")
bad = sum(len(r['errs']) + len(r['warn']) for rows in all_rows.values() for r in rows)
print(f"\n异常计数（字段取值错/交叉校验不符）：{bad}  →  {'✅ 全部一致' if bad == 0 else '⚠ 需人工复核'}")

Path(r"D:\Cola\足球分析学习\scripts\sat0912\_tally_0910_0911.json").write_text(
    json.dumps({d: [(r['no'], r['d'], r['s'], r['h'], r['ou_hit'], r['ou'], r['sc']) for r in v]
                for d, v in all_rows.items()}, ensure_ascii=False, indent=1), encoding='utf-8')
print("明细已存 scripts\\sat0912\\_tally_0910_0911.json")

