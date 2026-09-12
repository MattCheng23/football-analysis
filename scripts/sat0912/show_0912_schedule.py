# -*- coding: utf-8 -*-
"""show_0912_schedule.py — 0912 批进度视图（编号/时间/对阵/联赛/dir/比分/ht/ou/复盘状态）
用法：python show_0912_schedule.py            # 表格
      python show_0912_schedule.py --verify-handoff  # 校验 HANDOFF_260912.md 表格与 data.js 是否一致
"""
import io, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习\_发布_public\js")
HANDOFF = Path(r"D:\Cola\_tmp_football\sat0912\HANDOFF_260912.md")


def load_matches():
    dj = (R / "data.js").read_text(encoding='utf-8')
    k = dj.index('"2026-09-12": {')
    nxt = re.search(r'\n  "20\d{2}-\d{2}-\d{2}": \{', dj[k + 10:])
    blk = dj[k: k + 10 + (nxt.start() if nxt else len(dj) - k)]   # 0912 为末批，兜底须到文件尾（60000 会截断尾部场次）
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
    arr = blk[op + 1:j]
    hits = [m.start() for m in re.finditer(r'\{\s*no:\s*"\d{3}"', arr)]
    out = []
    for i, st in enumerate(hits):
        e = arr[st: hits[i + 1] if i + 1 < len(hits) else len(arr)]
        g = lambda n: (re.search(n + r':\s*"((?:[^"\\]|\\.)*)"', e) or [None, ''])[1]
        out.append(dict(no=g('no'), time=g('time'), home=g('home'), away=g('away'), league=g('league'),
                        dir=re.sub(r'（[^）]*）', '', g('dir')), scores=g('scores'), ht=g('ht'),
                        ou=re.sub(r'^总进球\s*', '', g('ou'))))
    return out


def done_nos():
    dr = (R / "data-review.js").read_text(encoding='utf-8')
    if '"2026-09-12": {' not in dr:
        return set()
    seg = dr[dr.index('"2026-09-12": {'):]
    return set(re.findall(r'\{ no: "(\d{3})"', seg[:seg.find('evidence: [')]))


def norm(s):
    return re.sub(r'\s+', '', s or '').replace('／', '/')


def main():
    ms = load_matches()
    done = done_nos()
    if '--verify-handoff' in sys.argv:
        hd = HANDOFF.read_text(encoding='utf-8')
        bad = []
        for m in ms:
            row = [ln for ln in hd.splitlines() if re.match(r'\|\s*%s\s*\|' % m['no'], ln)]
            if not row:
                bad.append(f"{m['no']} 行缺失"); continue
            cells = [c.strip() for c in row[0].strip('|').split('|')]
            if len(cells) < 8:
                bad.append(f"{m['no']} 列数不足({len(cells)})"); continue
            _, _, opp, lg, dr_, sc, ht_, ou_ = cells[:8]
            exp_opp = f"{m['home']} vs {m['away']}"
            checks = [("对阵", norm(opp), norm(exp_opp)), ("联赛", norm(lg), norm(m['league'])),
                      ("dir", norm(dr_), norm(m['dir'])), ("比分", norm(sc), norm(m['scores'])),
                      ("ht", norm(ht_), norm(m['ht'])), ("ou", norm(ou_), norm(m['ou']))]
            for name, got, exp in checks:
                if got != exp:
                    bad.append(f"{m['no']} {name}: HANDOFF={got!r} vs 源={exp!r}")
        print(f"HANDOFF 校验：{len(ms)} 场，" + ("✅ 全部与 data.js 一致" if not bad else f"❌ {len(bad)} 处不符"))
        for b in bad:
            print("  -", b)
        sys.exit(1 if bad else 0)
    print(f"{'#':<5}{'时间':<8}{'对阵':<34}{'联赛':<7}{'dir':<10}{'比分':<24}{'ht':<18}{'ou':<10}{'状态'}")
    for m in ms:
        st = "✅已复盘" if m['no'] in done else "待复盘"
        print(f"{m['no']:<5}{m['time']:<8}{(m['home'] + ' vs ' + m['away']):<34}{m['league']:<7}"
              f"{m['dir']:<10}{m['scores']:<24}{m['ht']:<18}{m['ou']:<10}{st}")
    print(f"\n复盘进度：{len(done)}/{len(ms)}")


main()
