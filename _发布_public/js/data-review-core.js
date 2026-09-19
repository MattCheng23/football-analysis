/* 复盘数据（2026-08-20 拆分自 data.js，由复盘页加载；首页不加载以提速） */
const REVIEW_EXTRA = {
    "2026-09-19": {
    results: [
        { no: "001", teams: "长崎航海 1-1 大阪樱花", league: "日职", lg: "lg-j1", score: "1-1（1-0）", d: "ok", s: "ok", h: "no", ou: "总进球 2·3", signal: "🟡3/4（方向✅ 比分✅ ht❌ ou✅）；四维实际：方向 平／比分 1-1／ht 胜平／总进球 2；归属 **G-ht路径（ht 集 平胜 / 胜胜 / 负胜 未含实际 胜平）**；兑现 **稳胜兑现**；过程分 4/4；xG 合计 3.47（无 λ 可对照）", sc: "watch" }
      ],
    evidence: [
        { no: "001", teams: "长崎航海 1-1 大阪樱花", league: "日职", lg: "lg-j1", stats: "**主源 FotMob matchDetails id=5803596**（终场 payload·机械提取）：控球 44:56、射门 14:17、射正 1:6、**xG 1.55:1.92**、绝佳机会 2:2、角球 7:4、红牌 0:0；半场 **1-0**；阵型 主 3-4-2-1／客 3-4-2-1；**第二源：待补**（官方 getUniformMatchResultV1 的 lastUpdateTime 未更新时按降级口径先入库）；**逐张牌**：17′ Riku Yamada Yellow(主)；41′ Jackson Irvine Yellow(客)；50′ Shunya Yoneda Yellow(主)；68′ Takumi Nakamura Yellow(客)；84′ Dion Cools Yellow(客)", signal: "🟡3/4（方向✅ 比分✅ ht❌ ou✅） 四维实际：方向 平／比分 1-1／ht 胜平／总进球 2", txt: "全场 **1-1**（半场 **1-0**）：34′ Matheus Jesus（主）；51′ Lucas Fernandes（客）。预测 主胜/平（B级） · 1-1 / 2-1 / 3-1 · ht 平胜 / 胜胜 / 负胜 · 总进球 2·3：四维 **方向✅ 比分✅ ht❌ ou✅ ＝ 🟡3/4**。①**双源核验＝未完成**（主源终场齐备；第二源待补）；②**偏差归属＝G-ht路径（ht 集 平胜 / 胜胜 / 负胜 未含实际 胜平）**；③**演戏排查：R328 半场领先收缩（半场 1-0 领先方最终未胜）**；④**控分排查：时段 34′／51′（进球分布跨全段，共 2 球）；无 85′+ 集中爆发剧本**；⑤**条款核对**：✓ 含 1-1 V11.53-9（票面必含双向档）；✓ V11.53-8（三档上限 4 已≥4）；✓ C21（ht 第二字∈方向集）；⑥**口径对照**：xG 合计 3.47（无 λ 可对照）；⑦**兑现路径**：**稳胜兑现**（Lucas Fernandes 51′ 定型）｜方向路径 稳胜｜86′+ 进球 0 个｜末球 51′；⑧**过程分 4/4（①方向覆盖✓；②V11.53-9双向档✓；③V11.53-8大分覆盖✓；④C21半全场✓）**。（本条由机械复盘引擎生成：事实与规则核对项均为当场可验证值，跨场批末蒸馏与需外部情报的深度归因留待模型补写）⑨**预警命中核验**：coldRisk 中等（赛前预警已登记，冷门兑现率基准 ≥中等 36.1%）；⑩**逐张牌**：17′ Riku Yamada Yellow(主)；41′ Jackson Irvine Yellow(客)；50′ Shunya Yoneda Yellow(主)；68′ Takumi Nakamura Yellow(客)；84′ Dion Cools Yellow(客)。" }
      ],
      avoidHigh: [], avoidWatch: []
  },};
