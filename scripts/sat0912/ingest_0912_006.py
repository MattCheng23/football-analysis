# -*- coding: utf-8 -*-
"""ingest_0912_006.py — 006 复盘入库（FotMob 全量主源 + 官方第二源）
双源核验：FotMob id=5749672（finished=True 1-1）+ 竞彩官方比分直播（1:1·半场 0:1·直播结束）
"""
import io, re, shutil, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = Path(r"D:\Cola\足球分析学习")
JS = R / "_发布_public" / "js"
BAK = R / "_backup" / "auto_bak"
TS = time.strftime("%Y%m%d_%H%M%S")
LOG_L = R / "01_当前模型" / "联赛蒸馏日志_20260906.md"
LOG_G = R / "01_当前模型" / "整体蒸馏日志_20260907.md"


def sub1(t, old, new, tag):
    n = t.count(old)
    assert n == 1, "[%s] 期望 1 次命中，实际 %d 次：%s" % (tag, n, old[:90])
    return t.replace(old, new, 1)


RES = ('        { no: "006", teams: "热那亚 1-1 弗洛西诺内", league: "意甲", lg: "lg-sa", '
       'score: "1-1（0-1）", d: "ok", s: "ok", h: "ok", ou: "总进球 2·3+3·4", '
       'signal: "🟢4/4 全中（方向✅客胜/平含平 + 比分✅1-1=TOP2 + ht✅平负=TOP2 + ou✅2球∈2·3+3·4）；'
       '14′ Kvernadze（客·POM 8.6）0-1 → 50′ Vásquez（主）1-1；**双档 ou 价值实证**（实际 2 球，'
       '若按单档 3·4 即失手）；86′ 主队 Vásquez 第二黄→红牌（10 人守平）；'
       'coldRisk 主胜·参考级未兑现且方向守住＝**「预警≠改方向」正证第 3 例**", sc: "ok" }')

EVI = ('        { no: "006", teams: "热那亚 1-1 弗洛西诺内", league: "意甲", lg: "lg-sa", '
       'stats: "**主源 FotMob matchDetails id=5749672**：控球 44%:56%、射门 17:26、射正 5:6'
       '（射门图 on-target 11:19）、**xG 1.86:1.95**、xGOT 0.88:1.76、绝佳机会 2:1（主队错失 2）、'
       '角球 8:9、禁区触球 25:38、解围 28:44、扑救 5:4、黄牌 主1:客2、'
       '**红牌 主1:客0（86′ Johan Vásquez 第二黄·YellowRed）**、传球 276:354、传球成功率 64%:78%、'
       '阵容均分 6.8:7.0（3-5-2 De Rossi / 4-3-3 Alvini）、POM Giorgi Kvernadze（弗洛西诺内·8.58）、'
       '天气 28℃/湿度 48%/风 3/降水 0、球场 Stadio Comunale Luigi Ferraris、裁判 Antonio Rapuano；'
       '**副源 竞彩官方比分直播**：09-12 21:00 热那亚 1:1 弗洛西诺内·半场 0:1·直播结束（比分双源一致）", '
       'signal: "🟢4/4 全中·双档 ou 救回 1 分·红牌场 10 人守平·SA-1「热那亚攻残」判定复核", '
       'txt: "全场 1-1（半场 0-1）：14′ Giorgi Kvernadze（客）0-1 → 50′ Johan Vásquez（主）1-1；'
       '86′ Vásquez 第二黄被罚下（主队 10 人作战至终场）；牌：客 16′ Cittadini/61′ Bracaglia，主 48′ Messias。'
       '预测 客胜/平（B级）0-1 / 1-1 / 1-3、ht 负负/平负/平平、ou 总进球 2·3+3·4：'
       '方向✅（平∈客胜/平）+比分✅（1-1=TOP2）+半全场✅（半场 0-1→全场平＝平负=TOP2）+'
       '总进球✅（2 球∈2·3+3·4）＝**4/4 🟢（本批第 3 场满贯，前两场 001/002）**。'
       '要点：①**双档 ou 价值实证（V11.46-1）**：实际 2 球——单档 3·4 会失手、单档 2·3 会命中，'
       '而本场双档（2·3+3·4）同时覆盖 2/3/4 球＝**双档配额条款的直接正证**（本批双档 3 场：006/009/014）；'
       '②**coldRisk 006 主胜·参考级（24.4%·链 3/5 环）未兑现且方向守住**＝「预警≠改方向」正证第 3 例'
       '（前两例 0911-012、0912-002）；③**红牌核验**：主队 86′ 第二黄被罚下（YellowRed），'
       'FotMob status numberOfHomeRedCards=1 与事件流一致 → 末段 10 人守平，未改变比分；'
       '④**SA-1「攻残」判定复核（关键）**：赛前以「热那亚 xG 0.63/场＝真攻残」为反环证据之一，'
       '实际热那亚主场 **xG 1.86·射门 17 次·绝佳机会 2**（虽 0-1 落后仍扳平）→ '
       '**「攻残」样本（3 场）被本场打脸**，与 9/2 小样本主客场战力陷阱同型 → 归属 L-SA（攻残判定加样本门）；'
       '⑤过程对比：客队控球 56%、射门 26:17、射正质量更高（xGOT 1.76:0.88），主队绝佳机会 2:1 但错失 2 次'
       '＝**均势对攻下的平局**（与本批 003 的单向碾压形成对照）；'
       '⑥**归属：L-OU（双档条款正证）/ G-CR（预警≠改方向正证）/ L-SA（攻残判定样本门）/ M-红牌记录**" }')

dr = (JS / "data-review.js").read_text(encoding="utf-8")
shutil.copy2(JS / "data-review.js", BAK / ("data-review.js_%s_pre006.bak" % TS))
assert '"006", teams: "热那亚 1-1 弗洛西诺内"' not in dr, "006 已入库"
dr = sub1(dr, '（6-1 不在固定面板 1-0…5-2 内）→ **若按 A2 保留「其它」档，本场比分票可中**（+1 席位命中）；',
          '（6-1 不在固定面板 1-0…5-2 内）→ **若按 A2 保留「其它」档，本场比分票可中**（+1 席位命中）；', "占位")
# 插入 results（追加到 005 结果条目之后·005 为末条故无尾逗号）
dr = sub1(dr, '席位成本未转化为实际损失", sc: "miss" }',
          '席位成本未转化为实际损失", sc: "miss" },\n' + RES, "results 006")
# 插入 evidence（追加到 005 evidence（当前末条）之后·保持 001→006 顺序）
dr = sub1(dr, '观众 21,342、裁判 Alberola Rojas" }',
          '观众 21,342、裁判 Alberola Rojas" },\n' + EVI, "evidence 006")
(JS / "data-review.js").write_text(dr, encoding="utf-8", newline="\n")

dj = (JS / "data.js").read_text(encoding="utf-8")
shutil.copy2(JS / "data.js", BAK / ("data.js_%s_pre006.bak" % TS))
dj = sub1(dj, "reviewedCount: 5,", "reviewedCount: 6,", "reviewedCount")
(JS / "data.js").write_text(dj, encoding="utf-8", newline="\n")

lg = LOG_L.read_text(encoding="utf-8")
shutil.copy2(LOG_L, BAK / ("联赛日志_%s_pre006.bak" % TS))
ROW_L = ("| 9/12 | 006 热那亚 1-1 弗洛西诺内 | 意甲 | 1-1（0-1） | 14′ Kvernadze（客·POM 8.6）0-1 → "
         "50′ Vásquez（主）1-1；86′ Vásquez 第二黄→**红牌（主 10 人守平）**；控球 44%:56%·射门 17:26·"
         "**xG 1.86:1.95**·xGOT 0.88:1.76·绝佳机会 2:1（主错失 2）；方向✅/比分✅/ht✅/ou✅＝🟢**4/4** | "
         "【条款核对】**V11.46-1 双档配额=正证**（实际 2 球：单档 3·4 失手、双档 2·3+3·4 命中）；"
         "**V11.45-1 覆盖义务=不触发且方向守住**（coldRisk 主胜·参考级未兑现＝「预警≠改方向」第 3 例）；"
         "**SA-1 攻残判定=需加样本门**（赛前判「热那亚 xG 0.63/场＝真攻残」，实际主场 xG 1.86·射门 17·"
         "绝佳机会 2 → 3 场小样本被打破，与 9/2 小样本陷阱同型）；**HT-3=遵守**（ht 含平平·半场平 1 席）；"
         "**R414 红牌=记录**（86′ 第二黄·未改比分） |\n")
LOG_L.write_text(lg.rstrip("\n") + "\n" + ROW_L, encoding="utf-8", newline="\n")

gl = LOG_G.read_text(encoding="utf-8")
shutil.copy2(LOG_G, BAK / ("整体日志_%s_pre006.bak" % TS))
ROW_G = ("| 9/12 | 006 热那亚 1-1 弗洛西诺内（0912 批） | 🟢4/4 全中 | 整体层＝**双档 ou 条款（V11.46-1）"
         "首个正证**（实际 2 球：单档 3·4 失手／双档 2·3+3·4 命中）＋**「预警≠改方向」正证第 3 例**"
         "（coldRisk 主胜·参考级未兑现、方向守住客胜/平）＋**攻残判定样本门**（3 场样本判死不成立："
         "热那亚主场 xG 1.86） | L-OU（双档正证）+G-CR（预警正证）+L-SA（攻残样本门）+M（红牌记录） |\n")
LOG_G.write_text(gl.rstrip("\n") + "\n" + ROW_G, encoding="utf-8", newline="\n")
print("✅ 006 入库完成：results+evidence｜reviewedCount=6｜双日志各 1 行")
