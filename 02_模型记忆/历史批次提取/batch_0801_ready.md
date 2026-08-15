# 8/1 批次（竞彩校正）插入数据块 — 备用

来源：历史提取_0717周五批次.md（3场）+ 历史提取_0718周六批次.md（周六轮001-007共7场）
竞彩编号：周五轮 001-003（8/1）+ 周六轮 001-007（8/1）
命中率：方向 7/10、比分 5/10、半全场 8/10

```js
  "2026-08-01": {
    title: "8/1 批次（竞彩校正：周五轮001-003+周六轮001-007）",
    model: "V9.x",
    predictDate: "2026-08-01",
    reviewed: true,
    stats: { dir: "7/10", dirPct: "70%", score: "5/10", scorePct: "50%", ht: "8/10", htPct: "80%" },
    predict: {
      matches: [
        { no: "001", home: "瓦勒伦加", away: "汉坎", league: "挪超", lg: "lg-nor",
          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 3-1 / 1-0", ht: "胜胜 / 平胜 / 平平" },
        { no: "002", home: "博德闪耀", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 1-0 / 2-1", ht: "胜胜 / 平胜 / 平平" },
        { no: "003", home: "纽约城", away: "多伦多FC", league: "美职联", lg: "lg-mls",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 3-0 / 2-1", ht: "胜胜 / 平胜 / 平平" },
        { no: "004", home: "江原FC", away: "富川FC", league: "韩职", lg: "lg-k1",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 1-0 / 2-1", ht: "胜胜 / 平胜 / 平平" },
        { no: "005", home: "全北现代", away: "首尔FC", league: "韩职", lg: "lg-k1",
          dir: "平/让平（B级）", dc: "dir-draw", scores: "1-1 / 1-0 / 0-1", ht: "平平 / 平胜 / 平负" },
        { no: "006", home: "浦项制铁", away: "金泉尚武", league: "韩职", lg: "lg-k1",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 0-0", ht: "平平 / 平负 / 负负" },
        { no: "007", home: "TPS图尔库", away: "玛丽港", league: "芬超", lg: "lg-fin",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 3-0 / 2-1", ht: "胜胜 / 平胜 / 平平" },
        { no: "008", home: "赫根", away: "卡尔马", league: "瑞超", lg: "lg-swe",
          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "胜胜 / 平胜 / 平平" },
        { no: "009", home: "腓特烈斯塔", away: "桑纳菲", league: "挪超", lg: "lg-nor",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-0 / 1-1 / 0-1", ht: "平胜 / 胜胜 / 平平" },
        { no: "010", home: "拉赫蒂", away: "雅罗", league: "芬超", lg: "lg-fin",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 2-1 / 1-0", ht: "胜胜 / 平胜 / 平平" },
      ],
      coldRisk: [], alerts: [], zeroZero: []
    },
    review: {
      results: [
        { no: "001", teams: "瓦勒伦加 vs 汉坎", league: "挪超", lg: "lg-nor", score: "0-3（0-1）", d: "no", s: "no", h: "no", signal: "全错（16'红牌黑天鹅，竞彩权威）", sc: "ok" },
        { no: "002", teams: "博德闪耀 vs 利勒斯特罗姆", league: "挪超", lg: "lg-nor", score: "4-0（2-0）", d: "ok", s: "no", h: "ok", signal: "🟡 部分命中（胜胜TOP1，竞彩权威）", sc: "watch" },
        { no: "003", teams: "纽约城 vs 多伦多FC", league: "美职联", lg: "lg-mls", score: "1-1（1-1）", d: "no", s: "no", h: "ok", signal: "🟡 部分命中（平平TOP3，竞彩权威）", sc: "watch" },
        { no: "004", teams: "江原FC vs 富川FC", league: "韩职", lg: "lg-k1", score: "0-3（0-1）", d: "no", s: "no", h: "no", signal: "全错（保级队客场爆冷R108，竞彩权威）", sc: "ok" },
        { no: "005", teams: "全北现代 vs 首尔FC", league: "韩职", lg: "lg-k1", score: "0-0（0-0）", d: "ok", s: "no", h: "ok", signal: "🟡 部分命中（平平TOP1，竞彩权威）", sc: "watch" },
        { no: "006", teams: "浦项制铁 vs 金泉尚武", league: "韩职", lg: "lg-k1", score: "0-1（0-0）", d: "ok", s: "ok", h: "ok", signal: "⭐三指标全中（0-1=TOP2+平负TOP2，竞彩权威）", sc: "ok" },
        { no: "007", teams: "TPS图尔库 vs 玛丽港", league: "芬超", lg: "lg-fin", score: "3-0（2-0）", d: "ok", s: "ok", h: "ok", signal: "⭐三指标全中（3-0=TOP2+胜胜TOP1，竞彩权威）", sc: "ok" },
        { no: "008", teams: "赫根 vs 卡尔马", league: "瑞超", lg: "lg-swe", score: "1-1（1-1）", d: "no", s: "no", h: "ok", signal: "🟡 部分命中（平平TOP3，竞彩权威）", sc: "watch" },
        { no: "009", teams: "腓特烈斯塔 vs 桑纳菲", league: "挪超", lg: "lg-nor", score: "1-0（1-0）", d: "ok", s: "ok", h: "ok", signal: "⭐三指标全中（1-0=TOP1+胜胜TOP2，竞彩权威）", sc: "ok" },
        { no: "010", teams: "拉赫蒂 vs 雅罗", league: "芬超", lg: "lg-fin", score: "2-0（0-0）", d: "ok", s: "ok", h: "ok", signal: "⭐三指标全中（2-0=TOP1+平胜TOP2，竞彩权威）", sc: "ok" },
      ],
      evidence: [], avoidHigh: [], avoidWatch: []
    }
  },
```
