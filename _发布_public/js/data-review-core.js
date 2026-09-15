/* 复盘数据（2026-08-20 拆分自 data.js，由复盘页加载；首页不加载以提速） */
const REVIEW_EXTRA = {
    "2026-09-15": {
    results: [
        { no: "001", teams: "叻武里 4-6 上海海港", league: "亚冠精英", lg: "lg-ucl", score: "4-6（0-3）", d: "ok", s: "no", h: "ok", ou: "总进球 3·4", signal: "🟡2/4（方向✅ 比分❌ ht✅ ou❌）；四维实际：方向 客胜／比分 4-6／ht 负负／总进球 10；归属 **L-λ/形态（票面 1-2 / 1-1 / 1-3 未含实际 4-6） ＋ L-ou档（档 总进球 3·4 vs 实际 10 球）**；兑现 **未兑现**；过程分 4/4；", sc: "watch" }
      ],
    evidence: [
        { no: "001", teams: "叻武里 4-6 上海海港", league: "亚冠精英", lg: "lg-ucl", stats: "**主源 FotMob matchDetails id=6049979**（终场 payload·机械提取）：控球 53:47、射门 21:13、射正 9:6、**xG -:-**、绝佳机会 5:5、角球 9:2、红牌 0:0；半场 **0-3**；阵型 主 4-2-3-1／客 3-5-2；**第二源：待补**（官方 getUniformMatchResultV1 的 lastUpdateTime 未更新时按降级口径先入库）；**逐张牌**：39′ Miguel Yellow(客)；74′ Roque Mesa Yellow(主)；77′ Tossawat Limwanasthien Yellow(主)", signal: "🟡2/4（方向✅ 比分❌ ht✅ ou❌） 四维实际：方向 客胜／比分 4-6／ht 负负／总进球 10", txt: "全场 **4-6**（半场 **0-3**）：31′ Prince Ampem（客）；36′ Prince Ampem（客）；45′ Prince Ampem（客）；51′ Lei Wu（客）；71′ Njiva Rakotoharimalala（主）；84′ Njiva Rakotoharimalala（主）；86′ Jaume Grau（客）；90′ Njiva Rakotoharimalala（主）；90′ Ekanit Panya（主）；90′ Leonardo（客）。预测 客胜/平（B级） · 1-2 / 1-1 / 1-3 · ht 平平/负平/负负 · 总进球 3·4：四维 **方向✅ 比分❌ ht✅ ou❌ ＝ 🟡2/4**。①**双源核验＝未完成**（主源终场齐备；第二源待补）；②**偏差归属＝L-λ/形态（票面 1-2 / 1-1 / 1-3 未含实际 4-6） ＋ L-ou档（档 总进球 3·4 vs 实际 10 球）**；③**演戏排查：补时剧本（90′+ 进球 3 个）**；④**控分排查：时段 31′／36′／45′／51′／71′／84′／86′／90′／90′／90′；**85′+ 有 3 球**（须人工确认是否追分压上所致）**；⑤**条款核对**：✓ 含 1-2 V11.53-9（票面必含双向档）；✓ V11.53-8（三档上限 4 已≥4）；✓ C21（ht 第二字∈方向集）；⑥**口径对照**：；⑦**兑现路径**：**未兑现**（Leonardo 90′ 定型）｜方向路径 稳胜｜86′+ 进球 4 个｜末球 90′；⑧**过程分 4/4（①方向覆盖✓；②V11.53-9双向档✓；③V11.53-8大分覆盖✓；④C21半全场✓）**。（本条由机械复盘引擎生成：事实与规则核对项均为当场可验证值，跨场批末蒸馏与需外部情报的深度归因留待模型补写）⑨**预警命中核验**：coldRisk 中等（赛前预警已登记，冷门兑现率基准 ≥中等 36.1%）；⑩**逐张牌**：39′ Miguel Yellow(客)；74′ Roque Mesa Yellow(主)；77′ Tossawat Limwanasthien Yellow(主)。" }
      ],
      avoidHigh: [], avoidWatch: []
  },};
