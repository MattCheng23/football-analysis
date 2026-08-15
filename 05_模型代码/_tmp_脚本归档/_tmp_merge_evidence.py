# -*- coding: utf-8 -*-
"""合并 evidence_2026-07-2X.md 到 data.js 对应批次 evidence 数组"""
import re, io, glob

data_path = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
src = io.open(data_path, encoding="utf-8").read()
for f in sorted(glob.glob(r"D:\Cola\足球分析学习\05_模型代码\_tmp_脚本归档\evidence_2026-*.md")):
    key = re.search(r"evidence_(\d{4}-\d{2}-\d{2})\.md", f).group(1)
    md = io.open(f, encoding="utf-8").read()
    # 提取 { no: ... } 数组行（每行一个条目，以 "}, " 或 "}" 结尾）
    lines = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("{ no:") and (s.endswith("}") or s.endswith("},")):
            lines.append(s.rstrip(","))
    if not lines:
        print("!! %s 无数组行" % key)
        continue
    # 定位批次块
    m = re.search(r'^\s*"%s": \{' % key, src, re.M)
    if not m:
        print("!! %s 批次不存在" % key)
        continue
    blk_start = m.start()
    nxt = re.search(r'^\s*"\d{4}-\d{2}-\d{2}": \{', src[m.start()+10:], re.M)
    blk_end = m.start() + 10 + (nxt.start() if nxt else len(src) - m.start() - 10)
    blk = src[blk_start:blk_end]
    # 替换 evidence: [] （后面可能跟 , avoidHigh...）
    ev_pat = re.compile(r'evidence:\s*\[\s*\]')
    if not ev_pat.search(blk):
        print("!! %s 未找到空 evidence" % key)
        continue
    new_ev = "evidence: [\n        " + ",\n        ".join(lines) + "\n      ]"
    new_blk, n = ev_pat.subn(lambda _: new_ev, blk, count=1)
    src = src[:blk_start] + new_blk + src[blk_end:]
    print("OK %s: %d 条 evidence 合并" % (key, len(lines)))

io.open(data_path, "w", encoding="utf-8").write(src)
print("data.js 已更新")
