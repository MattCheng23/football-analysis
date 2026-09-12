# -*- coding: utf-8 -*-
"""提取 data.js 中指定批次的 coldRisk / alerts 数组内容（用于核对 012 冷门档位与批级预警）。"""
import re, io, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = Path(r"D:\Cola\足球分析学习\_发布_public\js\data.js").read_text(encoding='utf-8')

for date in sys.argv[1:] or ["2026-09-11"]:
    k = t.find(f'"{date}": {{')
    if k < 0:
        print(f"!! 未找到批次 {date}"); continue
    nxt = re.search(r'\n  "20\d{2}-\d{2}-\d{2}": \{', t[k + 10:])
    blk = t[k: k + 10 + (nxt.start() if nxt else len(t) - k)]
    print("=" * 90)
    print(f"批次 {date}  块长 {len(blk)}")
    for arr in ("coldRisk", "alerts", "zeroZero", "bigSeven"):
        m = re.search(arr + r':\s*\[', blk)
        if not m:
            print(f"  {arr}: （无此字段）"); continue
        # 配对括号
        i = m.end() - 1
        depth = 0
        for j in range(i, len(blk)):
            if blk[j] == '[':
                depth += 1
            elif blk[j] == ']':
                depth -= 1
                if depth == 0:
                    break
        inner = blk[i + 1:j].strip()
        items = re.findall(r'\{[^{}]*\}', inner, re.S)
        print(f"  {arr}: {len(items)} 项")
        for it in items:
            s = re.sub(r'\s+', ' ', it)
            print("     - " + (s[:230] + ("…" if len(s) > 230 else "")))
