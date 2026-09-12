# -*- coding: utf-8 -*-
"""fix_006_ht.py — 纠正 006 半全场判定（机械复核：半场 0-1→全场平＝负平，票面未含 → ht=no）
同时修正 results/evidence/双日志（把「4/4 全中」改为「3/4」，并补 G-HT 第 3 例证据）
"""
import io, re, shutil, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习")
JS = R / "_发布_public" / "js"
BAK = R / "_backup" / "auto_bak"
TS = time.strftime("%Y%m%d_%H%M%S")


def sub1(t, old, new, tag):
    n = t.count(old)
    assert n == 1, "[%s] 期望 1 次，实际 %d 次：%s" % (tag, n, old[:80])
    return t.replace(old, new, 1)


dr = (JS / "data-review.js").read_text(encoding="utf-8")
shutil.copy2(JS / "data-review.js", BAK / ("data-review.js_%s_pre006ht.bak" % TS))
# ① results：h ok→no + 摘要改写
dr = sub1(dr, 'score: "1-1（0-1）", d: "ok", s: "ok", h: "ok", ou: "总进球 2·3+3·4"',
          'score: "1-1（0-1）", d: "ok", s: "ok", h: "no", ou: "总进球 2·3+3·4"', "006 results h")
dr = sub1(dr, 'signal: "🟢4/4 全中（方向✅客胜/平含平 + 比分✅1-1=TOP2 + ht✅平负=TOP2 + ou✅2球∈2·3+3·4）；',
          'signal: "🟡3/4（方向✅客胜/平含平 + 比分✅1-1=TOP2 + ou✅2球∈2·3+3·4；'
          '**ht❌半场 0-1→全场平＝「负平」，票面 负负/平负/平平 未含**）；', "006 results signal")
# ② evidence：signal/txt 修正 + 补 G-HT 第 3 例
dr = sub1(dr, 'signal: "🟢4/4 全中·双档 ou 救回 1 分·红牌场 10 人守平·SA-1「热那亚攻残」判定复核",',
          'signal: "🟡3/4（ht 失手：负平未列）·双档 ou 救回 1 分·红牌场 10 人守平·SA-1「热那亚攻残」判定复核",',
          "006 evidence signal")
dr = sub1(dr, "总进球✅（2 球∈2·3+3·4）＝**4/4 🟢（本批第 3 场满贯，前两场 001/002）**。",
          "总进球✅（2 球∈2·3+3·4）＝**3/4 🟡**（**ht 失手**：半场 0-1→全场 1-1＝「负平」，"
          "票面 ht 为 负负/平负/平平，**未含「领先被追平」分支**）。", "006 evidence verdict")
dr = sub1(dr, "⑥**归属：L-OU（双档条款正证）/ G-CR（预警≠改方向正证）/ L-SA（攻残判定样本门）/ M-红牌记录**",
          "⑥**G-HT 半场分支不全（第 3 例·本次机械复核抓出）**：半场客队领先的两个终局分支＝"
          "「负负（保持）+ 负平（被追平）」，票面只列 负负、未列 负平 → 实际 50′ 被追平即落在漏列支；"
          "与 0911-003（半场 1-1 只列平平）、0912-005（半场 1-1 漏平胜）、0911-012（科里蒂巴 3-3 负平）同族"
          "＝**G-HT「半场形态必须覆盖该半场结果的两条终局分支」证据升至 4 例**；"
          "⑦**归属：L-OU（双档条款正证）/ G-CR（预警≠改方向正证）/ L-SA（攻残判定样本门）/ "
          "G-HT（半场两向分支漏源）/ M-红牌记录**", "006 evidence 归属")
(JS / "data-review.js").write_text(dr, encoding="utf-8", newline="\n")

# ③ 双日志修正
for f, pairs in ((R / "01_当前模型" / "联赛蒸馏日志_20260906.md",
                  [("方向✅/比分✅/ht✅/ou✅＝🟢**4/4**", "方向✅/比分✅/**ht❌（负平未列）**/ou✅＝🟡**3/4**"),
                   ("**HT-3=遵守**（ht 含平平·半场平 1 席）",
                    "**G-HT 半场两向分支=违规**（半场 0-1 的两条终局分支应含 负负+负平，实际只列 负负）")]),
                 (R / "01_当前模型" / "整体蒸馏日志_20260907.md",
                  [("🟢4/4 全中 | 整体层＝**双档 ou 条款（V11.46-1）", "🟡3/4（ht 失手）| 整体层＝**双档 ou 条款（V11.46-1）"),
                   ("| L-OU（双档正证）+G-CR（预警正证）+L-SA（攻残样本门）+M（红牌记录） |",
                    "| L-OU（双档正证）+G-CR（预警正证）+L-SA（攻残样本门）+**G-HT（半场两向分支漏源·第 4 例）**+M（红牌记录） |")])):
    t = f.read_text(encoding="utf-8")
    shutil.copy2(f, BAK / (f.name + "_%s_pre006ht.bak" % TS))
    for old, new in pairs:
        t = sub1(t, old, new, f.name)
    f.write_text(t, encoding="utf-8", newline="\n")
print("✅ 006 已纠正：3/4（ht=no）+ 双日志同步 + G-HT 第 4 例证据")
