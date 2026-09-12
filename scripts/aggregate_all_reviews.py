# -*- coding: utf-8 -*-
"""aggregate_all_reviews.py — 全量复盘命中聚合（用于核对/更新 GLOBAL_STATS）

口径（与网站「累计全量」一致）：
  遍历 data-review.js REVIEW_EXTRA 所有日期块的 results 数组，
  方向/比分/半全场取字段 d/s/h == "ok"，总进球取 signal 内 ou✅/❌。
用法：
  python aggregate_all_reviews.py                # 打印全量聚合 + 与 data.js GLOBAL_STATS 对比
  python aggregate_all_reviews.py --json         # 仅输出 JSON（供脚本消费）
"""
import io, json, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
JS = Path(r"D:\Cola\足球分析学习\_发布_public\js")
ENTRY = re.compile(r'\{ no: "(\d{3})".*?sc: "\w+" \s*\}', re.S)
KV = re.compile(r'([A-Za-z_]\w*)\s*:\s*"((?:[^"\\]|\\.)*)"')
DATE = re.compile(r'\n\s{0,4}"(\d{4}-\d{2}-\d{2})": \{')


def blocks(text):
    """返回 [(date, results_text)] —— 结构感知：只取 results 数组（到 evidence/下一日期/文件尾）"""
    out = []
    hits = list(DATE.finditer(text))
    for i, m in enumerate(hits):
        date = m.group(1)
        start = m.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        seg = text[start:end]
        rk = seg.find('results: [')
        if rk < 0:
            continue
        ev = seg.find('evidence: [', rk)
        out.append((date, seg[rk:ev if ev > 0 else len(seg)]))
    return out


def verdict(sig, *labels):
    for lab in labels:
        mm = re.search(re.escape(lab) + r'\s*([✅❌])', sig)
        if mm:
            return mm.group(1) == '✅'
    return None


def main():
    text = (JS / "data-review.js").read_text(encoding='utf-8')
    per_date, tot = {}, dict(n=0, d=0, s=0, h=0, o=0, o_n=0)
    for date, blk in blocks(text):
        n = d = s = h = o = o_n = 0
        rows = []
        for m in ENTRY.finditer(blk):
            f = dict(KV.findall(m.group(0)))
            sig = f.get('signal', '')
            n += 1
            dh = f.get('d') == 'ok'; sh = f.get('s') == 'ok'; hh = f.get('h') == 'ok'
            oh = verdict(sig, 'ou', '总进球')
            d += dh; s += sh; h += hh
            if oh is not None:
                o_n += 1
                o += oh
            rows.append((f.get('no'), f.get('teams', ''), dh, sh, hh, oh))
        per_date[date] = dict(n=n, d=d, s=s, h=h, o=o, o_n=o_n, rows=rows)
        tot['n'] += n; tot['d'] += d; tot['s'] += s; tot['h'] += h
        tot['o'] += o; tot['o_n'] += o_n
    if '--json' in sys.argv:
        print(json.dumps(dict(total=tot, per_date={k: {kk: vv for kk, vv in v.items() if kk != 'rows'}
                                                   for k, v in per_date.items()}), ensure_ascii=False, indent=1))
        return
    print("=" * 92)
    print(f"REVIEW_EXTRA 全量聚合：{len(per_date)} 个批次，{tot['n']} 场")
    print(f"  方向 {tot['d']}/{tot['n']} = {tot['d']/tot['n']*100:.1f}%")
    print(f"  比分 {tot['s']}/{tot['n']} = {tot['s']/tot['n']*100:.1f}%")
    print(f"  半全场 {tot['h']}/{tot['n']} = {tot['h']/tot['n']*100:.1f}%")
    print(f"  总进球 {tot['o']}/{tot['o_n']} = {tot['o']/tot['o_n']*100:.1f}%  （可判定 {tot['o_n']} 场）")
    print("=" * 92)
    # 与 data.js GLOBAL_STATS 对比
    dj = (JS / "data.js").read_text(encoding='utf-8')
    m = re.search(r'GLOBAL_STATS\s*=\s*\{(.*?)\};', dj, re.S)
    if m:
        gs = dict(KV.findall(m.group(1)))
        print("data.js GLOBAL_STATS：")
        for k in ('dir', 'dirPct', 'score', 'scorePct', 'ht', 'htPct', 'ou', 'ouPct', 'updated'):
            if k in gs:
                print(f"  {k:<10} {gs[k]}")
        print("\n对照：")
        print(f"  dir   GLOBAL={gs.get('dir')}   聚合={tot['d']}/{tot['n']}")
        print(f"  score GLOBAL={gs.get('score')}   聚合={tot['s']}/{tot['n']}")
        print(f"  ht    GLOBAL={gs.get('ht')}   聚合={tot['h']}/{tot['n']}")
        print(f"  ou    GLOBAL={gs.get('ou')}   聚合={tot['o']}/{tot['o_n']}")
    print("\n最近 6 个批次明细：")
    for date in sorted(per_date)[-6:]:
        v = per_date[date]
        print(f"  {date}: n={v['n']:<3} 方向 {v['d']}/{v['n']}  比分 {v['s']}/{v['n']}  "
              f"ht {v['h']}/{v['n']}  ou {v['o']}/{v['o_n']}")


main()
