# -*- coding: utf-8 -*-
"""fix_calendar.py — 修复拆分引入的日历回归（2026-09-12）
① 日历数据源改 BATCH_META（核心文件自带，首屏即正确）② 默认月份=最新批所在月（原硬编码 2026-08）
③ renderAll 纳入 renderCalendar（历史批次异步加载后自动刷新）
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\Cola\足球分析学习\_发布_public\js\app.js"
s = io.open(P, encoding="utf-8").read()
R = []

# ① 默认月份跟随最新批
R.append((
 "let calYear = 2026, calMonth = 7; // 2026-08",
 "/* 默认月份＝最新批所在月（原硬编码 2026-08 → 2026-09-12 修复：拆分后首屏只含最新批，\n"
 "   固定 8 月会显示「0 个批次」；改用 BATCH_META（核心文件自带）后首屏即正确） */\n"
 "const _metaSrc = (typeof BATCH_META !== \"undefined\") ? BATCH_META : BATCHES;\n"
 "const _newestKey = Object.keys(_metaSrc).sort().pop() || \"2026-08\";\n"
 "let calYear = parseInt(_newestKey.slice(0, 4), 10);\n"
 "let calMonth = parseInt(_newestKey.slice(5, 7), 10) - 1;"))

# ② 日历键集合与 has/reviewed 改走 BATCH_META
R.append((
 "function renderCalendar() {\n  const keys = Object.keys(BATCHES).sort();",
 "function renderCalendar() {\n"
 "  const metaSrc = (typeof BATCH_META !== \"undefined\") ? BATCH_META : BATCHES;\n"
 "  const keys = Object.keys(metaSrc).sort();"))
R.append((
 "    const batch = BATCHES[key];\n    const has = !!batch;\n    const reviewed = batch && batch.reviewed;",
 "    const batch = metaSrc[key];\n    const has = !!batch;\n    const reviewed = !!(batch && batch.reviewed);"))

# ③ renderAll 纳入日历刷新
R.append((
 "  const b = BATCHES[currentKey];\n  renderBatchHeader();",
 "  const b = BATCHES[currentKey];\n  renderCalendar();   // 历史批次异步到达后随之刷新（2026-09-12）\n  renderBatchHeader();"))

ok = 0
for a, b in R:
    n = s.count(a)
    if n != 1:
        print("❌ MISS(%d): %s" % (n, a[:60])); sys.exit(1)
    s = s.replace(a, b); ok += 1
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("app.js 日历修复 %d 处 ✓" % ok)
