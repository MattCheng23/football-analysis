/* ============================================================
   足球分析预测站 · 批次数据库
   每新增一个比赛日，在此追加一个批次对象即可（日历自动识别）
   ============================================================ */

const BATCHES = {
  "2026-08-14": {
    title: "8/14 周五批次",
    model: "V10.28 → V10.29-Fix-R5",
    predictDate: "2026-08-14",
    reviewDate: "2026-08-15",
    reviewed: true,
    stats: { dir: "12/17", dirPct: "70.6%", score: "2/17", scorePct: "11.8%", ht: "11/17", htPct: "64.7%" },
    predict: {
      matches: [
        { no: "001", home: "东京绿茵", away: "柏太阳神", league: "日职联", lg: "lg-j1",
          dir: "负/平（B级）", dc: "dir-drawloss", scores: "0-1 / 1-2 / 1-1", ht: "平负/负负/平平", ou: "总进球 1·2",
          logic: "东京绿茵中后场被掏空（队长森田晃树锁骨骨折+主力中卫转会+防线4伤停+近4场失12球+场均不足1球）+国立竞技场主场优势被稀释 vs 柏太阳神首轮开门红+进攻效率碾压（7.4次/球 vs 12.7次）+整体框架完整，看好客队不败（0-1或1-2）" },
        { no: "002", home: "VPS瓦萨", away: "TPS图尔库", league: "芬超", lg: "lg-fin",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 2-1 / 1-0", ht: "胜胜/平胜/平平", ou: "总进球 1·2",
          logic: "瓦萨0伤停+主场9场仅丢7球+主场不败率89% vs TPS3人停赛+客场8场0胜，看好主胜" },
        { no: "003", home: "荷尔斯泰因", away: "圣保利", league: "德乙", lg: "lg-bundes2",
          dir: "平/胜（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 1·2",
          logic: "圣保利近6次交手5胜1平心理碾压但锋线几乎被掏空；荷尔斯泰因后防残缺，平局概率最高" },
        { no: "004", home: "布伦瑞克", away: "波鸿", league: "德乙", lg: "lg-bundes2",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 2-0", ht: "平胜/平平/胜胜", ou: "总进球 2·3",
          logic: "布伦瑞克首轮6-1士气高涨+主场优势 vs 波鸿降班马急需止颓+近5次交手4胜血脉压制，看好主队不败" },
        { no: "005", home: "新未来城体育", away: "费哈", league: "沙特联", lg: "lg-spl",
          dir: "胜（B+级）", dc: "dir-win", scores: "1-0 / 2-0 / 2-1", ht: "胜胜/平胜/平平", ou: "总进球 1·2",
          logic: "新未来城0伤停+近6主场不败+近2次交锋不败 vs 费哈近6场0胜+客场崩盘，看好主胜" },
        { no: "006", home: "埃尔夫斯堡", away: "瓦斯特拉斯", league: "瑞典超", lg: "lg-swe",
          dir: "胜（A级）", dc: "dir-win", scores: "1-0 / 2-1 / 2-0", ht: "胜胜/平胜/平平", ou: "总进球 1·2",
          logic: "埃尔夫斯堡历史交锋5场不败 vs 瓦斯特拉斯头号射手离队+多人缺阵，看好主胜" },
        { no: "007", home: "罗森博格", away: "维京", league: "挪超", lg: "lg-nor",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 1·2",
          logic: "罗森博格近5轮4胜1负+近4次主场对维京不败 vs 维京防线缺人+4天后欧冠生死战轮换，看好主队不败" },
        { no: "008", home: "达曼协作", away: "利雅得体育", league: "沙特联", lg: "lg-spl",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-0 / 1-1 / 2-1", ht: "平胜/平平/胜胜", ou: "总进球 1·2",
          logic: "达曼协作身价碾压但新援磨合不足+伤病影响 vs 利雅得体育阵容完整+93分钟绝杀心理优势，看好主队不败" },
        { no: "009", home: "利雅得新月", away: "费萨里", league: "沙特联", lg: "lg-spl",
          dir: "胜（A级）", dc: "dir-win", scores: "3-0 / 4-0 / 3-1", ht: "胜胜/平胜/胜胜", ou: "总进球 3·4",
          logic: "利雅得新月0伤停+近35次交手27胜8平0负血脉压制+主场场均2.4球 vs 费萨里升班马历史全败，看好主胜" },
        { no: "010", home: "特尔斯达", away: "鹿特丹斯巴达", league: "荷甲", lg: "lg-ered",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 1·2",
          logic: "特尔斯达首轮爆冷士气高涨+近5次主场对鹿特丹不败 vs 客队首轮0进球+客场7场不胜，看好主队不败" },
        { no: "011", home: "瓦尔韦克", away: "多德勒支", league: "荷乙", lg: "lg-eers",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 3-1", ht: "平平/平胜/胜胜", ou: "总进球 2·3",
          logic: "瓦尔韦克降班马+近3次交锋不败+乌内肯领衔 vs 多德勒支首轮逆转开门红，看好主队不败" },
        { no: "012", home: "赫拉克勒斯", away: "邓伯什", league: "荷乙", lg: "lg-eers",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 3-0 / 3-1", ht: "胜胜/平胜/胜胜", ou: "总进球 2·3",
          logic: "赫拉克勒斯降班马+近6次交锋4胜1平1负碾压+近4次全胜，看好主胜" },
        { no: "013", home: "昂纳西", away: "罗德兹", league: "法乙", lg: "lg-l2",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2",
          logic: "罗德兹跨赛季23场不败+近8次交手5胜1平2负 vs 昂纳西中场5人缺阵+近5次主场不胜，看好客队不败" },
        { no: "014", home: "兰斯", away: "敦刻尔克", league: "法乙", lg: "lg-l2",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 1-2 / 0-1", ht: "平平/平负/负负", ou: "总进球 1·2",
          logic: "敦刻尔克首轮4-1大胜+主帅14次对兰斯不败 vs 兰斯7人缺阵+近5次交手不胜，看好客队不败" },
        { no: "015", home: "圣埃蒂安", away: "克莱蒙", league: "法乙", lg: "lg-l2",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 1-0 / 3-0", ht: "胜胜/平胜/胜胜", ou: "总进球 1·2",
          logic: "圣埃蒂安首轮6分钟3球+近10次交手7胜+德比战主场 vs 克莱蒙防线残阵+进攻乏力，看好主胜" },
        { no: "016", home: "狼队", away: "布莱克本", league: "英冠", lg: "lg-champ",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 2-1 / 1-0", ht: "胜胜/平胜/平平", ou: "总进球 1·2",
          logic: "狼队身价碾压+近10次交手5胜4平1负+希门尼斯回归 vs 布莱克本四线减员+防线重组，看好主胜" },
        { no: "017", home: "葡萄牙体育", away: "吉马良斯", league: "葡超", lg: "lg-prime",
          dir: "胜（A级）", dc: "dir-win", scores: "2-0 / 3-1 / 2-1", ht: "胜胜/平胜/胜胜", ou: "总进球 2·3",
          logic: "葡萄牙体育主场对吉马良斯7连胜+上赛季5-1/4-1双杀+身价差10倍 vs 客队24射0进球，看好主胜" }
      ],
      coldRisk: [
        { rank: "🥇", no: "014", teams: "兰斯 vs 敦刻尔克", dir: "客胜", lv: "tag-red", lvTxt: "最高", logic: "兰斯7人缺阵+主帅14次对敦刻尔克不胜+敦刻尔克首轮4-1大胜" },
        { rank: "🥈", no: "013", teams: "昂纳西 vs 罗德兹", dir: "客胜", lv: "tag-orange", lvTxt: "较高", logic: "昂纳西队长+主力后腰双停赛+近10次交手1胜4平5负" },
        { rank: "🥉", no: "004", teams: "布伦瑞克 vs 波鸿", dir: "客胜", lv: "tag-orange", lvTxt: "较高", logic: "波鸿近5次交手4胜血脉碾压+降班马急需止颓" },
        { rank: "4", no: "008", teams: "达曼协作 vs 利雅得体育", dir: "客胜", lv: "tag-yellow", lvTxt: "中等", logic: "达曼协作新援磨合不足+上赛季末同场地93分钟被绝杀" },
        { rank: "5", no: "007", teams: "罗森博格 vs 维京", dir: "客胜", lv: "tag-yellow", lvTxt: "中等", logic: "维京实力占优（第2名），若全力出战仍可客场取胜" },
        { rank: "6", no: "006", teams: "埃尔夫斯堡 vs 瓦斯特拉斯", dir: "平局", lv: "tag-yellow", lvTxt: "中等", logic: "主队主力中锋+门将缺阵+近4个主场不胜" },
        { rank: "7", no: "016", teams: "狼队 vs 布莱克本", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "8", no: "003", teams: "荷尔斯泰因 vs 圣保利", dir: "客胜", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "9", no: "010", teams: "特尔斯达 vs 鹿特丹斯巴达", dir: "客胜", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "10", no: "011", teams: "瓦尔韦克 vs 多德勒支", dir: "客胜", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "11", no: "002", teams: "VPS瓦萨 vs TPS图尔库", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "12", no: "005", teams: "新未来城体育 vs 费哈", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "13", no: "009", teams: "利雅得新月 vs 费萨里", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "14", no: "012", teams: "赫拉克勒斯 vs 邓伯什", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "15", no: "015", teams: "圣埃蒂安 vs 克莱蒙", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" },
        { rank: "16", no: "017", teams: "葡萄牙体育 vs 吉马良斯", dir: "平局", lv: "tag-gray", lvTxt: "低", logic: "" }
      ],
      alerts: [
        { script: "胜负", no: "007", teams: "罗森博格 vs 维京", lv: "tag-orange", lvTxt: "中等偏高", logic: "罗森博格抢开局+维京实力占优反击高效" },
        { script: "胜平", no: "006", teams: "埃尔夫斯堡 vs 瓦斯特拉斯", lv: "tag-orange", lvTxt: "中等偏高", logic: "主队近4个主场不胜+主力缺阵，半场领先守不住" },
        { script: "负平", no: "007", teams: "罗森博格 vs 维京", lv: "tag-yellow", lvTxt: "中等", logic: "维京客场先进球+罗森博格主场韧性" },
        { script: "胜平", no: "016", teams: "狼队 vs 布莱克本", lv: "tag-yellow", lvTxt: "中等", logic: "狼队3名攻击手缺阵，若久攻不下可能被逼平" },
        { script: "胜负", no: "004", teams: "布伦瑞克 vs 波鸿", lv: "tag-gray", lvTxt: "中等偏低", logic: "布伦瑞克半场领先+波鸿降班马急需止颓可能反扑" },
        { script: "胜平", no: "003", teams: "荷尔斯泰因 vs 圣保利", lv: "tag-gray", lvTxt: "中等偏低", logic: "圣保利近6次交手5胜1平心理碾压" },
        { script: "胜负", no: "008", teams: "达曼协作 vs 利雅得体育", lv: "tag-gray", lvTxt: "中等偏低", logic: "达曼协作若半场领先，利雅得体育上赛季末93分钟绝杀有翻盘能力" },
        { script: "负胜", no: "008", teams: "达曼协作 vs 利雅得体育", lv: "tag-gray", lvTxt: "中等偏低", logic: "利雅得体育若客场先进球，达曼协作新援磨合后可能反扑" },
        { script: "胜平", no: "008", teams: "达曼协作 vs 利雅得体育", lv: "tag-gray", lvTxt: "中等偏低", logic: "达曼协作若半场领先，利雅得体育防守纪律性强可能扳平" },
        { script: "胜平", no: "010", teams: "特尔斯达 vs 鹿特丹斯巴达", lv: "tag-gray", lvTxt: "中等偏低", logic: "特尔斯达若半场领先但防守不稳，鹿特丹斯巴达可能扳平" },
        { script: "胜平", no: "011", teams: "瓦尔韦克 vs 多德勒支", lv: "tag-gray", lvTxt: "中等偏低", logic: "瓦尔韦克若半场领先，多德勒支年轻阵容体能更好可能扳平" },
        { script: "胜平", no: "013", teams: "昂纳西 vs 罗德兹", lv: "tag-gray", lvTxt: "中等偏低", logic: "昂纳西若主场先进球，罗德兹23场不败底蕴有扳平能力" },
        { script: "负平", no: "013", teams: "昂纳西 vs 罗德兹", lv: "tag-gray", lvTxt: "中等偏低", logic: "罗德兹若客场先进球，昂纳西主场有韧性可能追平" },
        { script: "胜平", no: "014", teams: "兰斯 vs 敦刻尔克", lv: "tag-gray", lvTxt: "中等偏低", logic: "兰斯若主场先进球，敦刻尔克首轮4-1状态火热有扳平能力" },
        { script: "负平", no: "014", teams: "兰斯 vs 敦刻尔克", lv: "tag-gray", lvTxt: "中等偏低", logic: "敦刻尔克若客场先进球，兰斯主场有韧性可能追平" }
      ],
      dirStats: [
        { label: "胜（A级）", count: 8, nos: "002·005·006·009·012·015·016·017", cls: "g", h: 100 },
        { label: "胜/平（B级）", count: 6, nos: "003·004·007·008·010·011", cls: "y", h: 75 },
        { label: "平/负（B级）", count: 3, nos: "001·013·014", cls: "r", h: 37 }
      ],
      zeroZero: [
        { no: "013", teams: "昂纳西 vs 罗德兹", p: 15, lv: "tag-orange", lvTxt: "中等偏高" },
        { no: "014", teams: "兰斯 vs 敦刻尔克", p: 15, lv: "tag-orange", lvTxt: "中等偏高" },
        { no: "002", teams: "VPS瓦萨 vs TPS图尔库", p: 8, lv: "tag-gray", lvTxt: "低" },
        { no: "003", teams: "荷尔斯泰因 vs 圣保利", p: 10, lv: "tag-gray", lvTxt: "低" },
        { no: "005", teams: "新未来城体育 vs 费哈", p: 10, lv: "tag-gray", lvTxt: "低" },
        { no: "006", teams: "埃尔夫斯堡 vs 瓦斯特拉斯", p: 8, lv: "tag-gray", lvTxt: "低" },
        { no: "008", teams: "达曼协作 vs 利雅得体育", p: 10, lv: "tag-gray", lvTxt: "低" },
        { no: "010", teams: "特尔斯达 vs 鹿特丹斯巴达", p: 10, lv: "tag-gray", lvTxt: "低" }
      ]
    },
    review: {
      results: [
        { no: "001", teams: "东京绿茵 vs 柏太阳神", league: "日职联", lg: "lg-j1", score: "1-3（0-2）", d: "ok", s: "no", h: "ok", signal: "正常", sc: "ok" },
        { no: "002", teams: "VPS瓦萨 vs TPS图尔库", league: "芬超", lg: "lg-fin", score: "1-3（0-2）", d: "no", s: "no", h: "no", signal: "🔴 演戏嫌疑（VPS瓦萨）", sc: "danger" },
        { no: "003", teams: "荷尔斯泰因 vs 圣保利", league: "德乙", lg: "lg-bundes2", score: "2-2（0-2）", d: "ok", s: "no", h: "no", signal: "🟡 观察", sc: "watch" },
        { no: "004", teams: "布伦瑞克 vs 波鸿", league: "德乙", lg: "lg-bundes2", score: "0-1（0-1）", d: "no", s: "no", h: "no", signal: "🟡 首轮6-1后断崖", sc: "watch" },
        { no: "005", teams: "新未来城体育 vs 费哈", league: "沙特联", lg: "lg-spl", score: "2-1（2-0）", d: "ok", s: "ok", h: "ok", signal: "正常", sc: "ok" },
        { no: "006", teams: "埃尔夫斯堡 vs 瓦斯特拉斯", league: "瑞典超", lg: "lg-swe", score: "3-0（1-0）", d: "ok", s: "no", h: "ok", signal: "正常", sc: "ok" },
        { no: "007", teams: "罗森博格 vs 维京", league: "挪超", lg: "lg-nor", score: "2-1（1-0）", d: "ok", s: "ok", h: "ok", signal: "正常", sc: "ok" },
        { no: "008", teams: "达曼协作 vs 利雅得体育", league: "沙特联", lg: "lg-spl", score: "4-2（1-1）", d: "ok", s: "no", h: "ok", signal: "正常", sc: "ok" },
        { no: "009", teams: "利雅得新月 vs 费萨里", league: "沙特联", lg: "lg-spl", score: "4-2（3-0）", d: "ok", s: "no", h: "ok", signal: "🔴 半场领先收缩", sc: "danger" },
        { no: "010", teams: "特尔斯达 vs 鹿特丹斯巴达", league: "荷甲", lg: "lg-ered", score: "1-3（0-1）", d: "no", s: "no", h: "no", signal: "非演戏（预测误判）", sc: "ok" },
        { no: "011", teams: "瓦尔韦克 vs 多德勒支", league: "荷乙", lg: "lg-eers", score: "2-2（0-1）", d: "ok", s: "no", h: "no", signal: "🟡 观察", sc: "watch" },
        { no: "012", teams: "赫拉克勒斯 vs 邓伯什", league: "荷乙", lg: "lg-eers", score: "3-2（1-0）", d: "ok", s: "no", h: "ok", signal: "🔴 放水实锤", sc: "danger" },
        { no: "013", teams: "昂纳西 vs 罗德兹", league: "法乙", lg: "lg-l2", score: "2-0（1-0）", d: "no", s: "no", h: "no", signal: "🟡 冷门场主胜（R333）", sc: "watch" },
        { no: "014", teams: "兰斯 vs 敦刻尔克", league: "法乙", lg: "lg-l2", score: "3-3（1-1）", d: "ok", s: "no", h: "ok", signal: "🟡 客队压制仍平", sc: "watch" },
        { no: "015", teams: "圣埃蒂安 vs 克莱蒙", league: "法乙", lg: "lg-l2", score: "3-1（1-0）", d: "ok", s: "no", h: "ok", signal: "正常（射正5:0碾压）", sc: "ok" },
        { no: "016", teams: "狼队 vs 布莱克本", league: "英冠", lg: "lg-champ", score: "2-2（1-1）", d: "no", s: "no", h: "ok", signal: "🟡 身价碾压却平（R332）", sc: "watch" },
        { no: "017", teams: "葡萄牙体育 vs 吉马良斯", league: "葡超", lg: "lg-prime", score: "3-2（3-0）", d: "ok", s: "no", h: "ok", signal: "🟡 半场3-0收缩（R328）", sc: "watch" }
      ],
      evidence: [
        { no: "001", teams: "鹿岛鹿角 2-1 名古屋鲸八", league: "日职联", stats: "xG 1.33:0.90、射门 16:13、控球 49%:51%", signal: "⭐ 三指标全中", txt: "22'莱奥、54'原辉绮（扳平）、90+8'关川绝杀——A级正路主场小胜剧本，2-1=比分TOP1+半全场胜胜=TOP1，补时绝杀说明进程比预期胶着（名古屋新帅米哈针对性布置）", sc: "ok" },
        { no: "012", teams: "赫拉克勒斯 3-2", league: "荷乙", stats: "射门 29:8、射正 17:6、进攻 113:52、角球 11:6", signal: "🔴 放水实锤", txt: "3-0 领先（74'）后 87'、88' 连丢 2 球收窄——射门 29 次只进 3 球", sc: "danger" },
        { no: "002", teams: "VPS瓦萨 1-3", league: "芬超", stats: "射门 8:9、射正 4:4、控球 54.4%、角球 7:4、红牌 1:0", signal: "🔴 演戏嫌疑", txt: "第4主场控球角球占优却 1-3 惨败（第8）+ 红牌松散踢法", sc: "danger" },
        { no: "009", teams: "利雅得新月 4-2", league: "沙特联", stats: "射门 14:7、射正 5:5（持平）、控球 58.6%", signal: "🔴 领先收缩", txt: "半场 3-0 后下半场丢 2 球，射正持平——控制力骤降", sc: "danger" },
        { no: "017", teams: "葡萄牙体育 3-2", league: "葡超", stats: "半场 3-0，全场 3-2（下半场丢 2 球）", signal: "🟡 领先收缩", txt: "半场 3-0 后被追到 3-2——R328 同 009 模式，葡体入观察", sc: "watch" },
        { no: "010", teams: "特尔斯达 1-3", league: "荷甲", stats: "射门 5:13、射正 1:9", signal: "非演戏", txt: "客队射正 9 次碾压——模型误判客队状态（R329 教训）", sc: "ok" },
        { no: "016", teams: "狼队 2-2", league: "英冠", stats: "射门 11:6、射正 2:4（落后）、控球 48.8%", signal: "🟡 身价-状态背离", txt: "身价碾压却射正落后——R332 以状态为准", sc: "watch" }
      ],
      avoidHigh: [
        { team: "VPS瓦萨", league: "芬超", reason: "002：第4主场控球54.4%占优却1-3惨败+红牌" },
        { team: "TPS土尔库", league: "芬超", reason: "002：历史克VPS，客场3-1大胜排名高4位对手" },
        { team: "赫拉克勒斯", league: "荷乙", reason: "012：射门29:8碾压，3-0领先87'/88'连丢2球" },
        { team: "利雅得新月", league: "沙特联", reason: "009：半场3-0后射正持平、丢2球收窄" }
      ],
      avoidWatch: [
        { team: "瓦尔韦克", league: "荷乙", reason: "011：降班马主场射正持平只打平" },
        { team: "荷尔斯泰因", league: "德乙", reason: "003：半场0-2后追平，主场韧性存疑" },
        { team: "圣保利", league: "德乙", reason: "003：心理碾压却只拿平局" },
        { team: "布伦瑞克", league: "德乙", reason: "004：首轮6-1后主场0-1（R331）" },
        { team: "狼队", league: "英冠", reason: "016：身价碾压却射正2:4落后（R332）" },
        { team: "昂纳西", league: "法乙", reason: "013：冷门风险场却主胜完场（R333）" },
        { team: "葡萄牙体育", league: "葡超", reason: "017：半场3-0后丢2球被追到3-2（R328）" }
      ]
    }
  },
  "2026-08-15": {
    title: "8/15 周六批次",
    model: "V10.29-Fix-R5",
    predictDate: "2026-08-15",
    reviewDate: "",
    reviewed: false,
    stats: { dir: "-", dirPct: "-", score: "-", scorePct: "-", ht: "-", htPct: "-" },
    predict: {
      matches: [
        { no: "001", home: "鹿岛鹿角", away: "名古屋鲸八", league: "日职联", lg: "lg-j1",
          dir: "胜（A级）", dc: "dir-win", scores: "2-1 / 2-0 / 3-1", ht: "胜胜/平胜/负胜", ou: "总进球 2·3", risk: 2,
          logic: "卫冕冠军主场气势如虹 vs 名古屋防线告急保级队，看好主胜大球" },
        { no: "003", home: "浦和红钻", away: "广岛三箭", league: "日职联", lg: "lg-j1",
          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-2", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 5,
          logic: "浦和5人停赛+后防大换血 vs 广岛状态火热，客队不败且可能大胜" },
        { no: "004", home: "神户胜利船", away: "东京FC", league: "日职联", lg: "lg-j1",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/负平", ou: "总进球 2·3", risk: 5,
          logic: "残阵对残阵：神户锋线3缺 vs 东京后防4缺，双方防线都残，对攻大球倾向" },
        { no: "005", home: "首尔FC", away: "大田市民", league: "韩职", lg: "lg-j1",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 1-0", ht: "平平/平胜/胜胜", ou: "总进球 2·3", risk: 4,
          logic: "榜首4场不胜急需止颓+主场对攻，大田反弹中，胜负平皆可能且进球偏多" },
        { no: "006", home: "光州FC", away: "浦项制铁", league: "韩职", lg: "lg-j1",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 5,
          logic: "垫底vs五连败，双弱对话，光州进攻乏力恐难挡铁人" },
        { no: "008", home: "博尔顿", away: "普雷斯顿", league: "英冠", lg: "lg-champ",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "1-1 / 2-1 / 2-2", ht: "平平/平胜/胜平", ou: "总进球 2·3", risk: 4,
          logic: "首发确认：普雷斯顿中卫吉布森停赛由Lindsay顶替+锋线双主力Osmajic/Lang坐替补（Erabi/Burgzorg首发）+友谊赛4连败；博尔顿升班马主场首秀Simons停赛Watson顶替，但历史交锋近10次2胜3平5负" },
        { no: "009", home: "米亚尔比", away: "天狼星", league: "瑞超", lg: "lg-swe",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 1-3", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 5,
          logic: "首发确认：天狼星主力齐整（Bjerkebo 12球8助领衔）vs 米亚尔比 Bergström 首发；天狼星16轮不败+客场5连胜+场均2.9球 vs 米亚尔比8轮不胜+主场4连不胜，瑞超3.07高进球" },
        { no: "010", home: "诺维奇", away: "西布罗姆维奇", league: "英冠", lg: "lg-champ",
          dir: "胜/平（B级）", dc: "dir-windraw", scores: "2-1 / 1-1 / 3-1", ht: "胜胜/平平/平胜", ou: "总进球 2·3", risk: 4,
          logic: "首发确认：诺维奇 Toure领衔（Kvistgaarden/Ahmed/Topic伤缺）vs 西布朗 Morgan+Heggebo双前锋（多名新援英冠首秀磨合不足）；2026年两次交手诺维奇5-0和3-1完胜，但西布朗近7次对诺维奇6次≥14射门" },
        { no: "011", home: "奥斯陆KFUM", away: "利勒斯特罗姆", league: "挪超", lg: "lg-nor",
          dir: "负/平（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 1-3", ht: "平负/平平/负负", ou: "总进球 2·3", risk: 4,
          logic: "首发已核实：KFUM 3-4-3 埃克雷姆领衔主力齐整（阿莱萨米/塞门斯伤缺）vs 利勒斯特罗姆 4-5-1 沿用上轮奥尔森单前锋（4球射手卡尔巴克已卖土耳其）；利勒斯特罗姆第4（16场25分）但近6场2胜4负（刚主场0-2负罗森博格）+失20球；首回合2-1胜+交锋3连胜；KFUM第12但联赛2连胜+进球联赛第2少（12球）" },
        { no: "014", home: "玛丽港", away: "塞伊奈约基", league: "芬超", lg: "lg-fin",
          dir: "负（C级）", dc: "dir-drawloss", scores: "0-2 / 1-2 / 1-1*", ht: "负负/平负/平平*", ou: "总进球 2·3", risk: 8,
          logic: "首发已核实：玛丽港 4-3-3 卢恩领衔 vs SJK 4-4-2 姆姆/斯特伦领衔；玛丽港19场5分垫底+近5场0胜+近2场0进球+连续14场未零封+场均0.5球联赛最差；SJK第10近5场6球+对玛丽港4连胜（交锋30次15胜），野鸡剧本矩阵" },
        { no: "016", home: "谢菲尔德联", away: "伯明翰", league: "英冠", lg: "lg-champ",
          dir: "胜（B级）", dc: "dir-win", scores: "2-1 / 3-1 / 2-0", ht: "胜胜/负胜/平胜", ou: "总进球 2·3", risk: 3,
          logic: "首发已核实：谢菲联4-4-2 库珀/班福德/坎农（核心哈默卖考文垂+菲利普斯/奥尼扬戈伤缺+Chong伤疑）vs 伯明翰4-2-3-1 斯坦斯菲尔德+普里斯克（莱昂纳德伤缺+边卫布坎南/莱尔德伤愈恢复期）；伯明翰斯坦斯菲尔德近3季41球火力强但防线重组" },
        { no: "019", home: "阿拉维斯", away: "赫塔费", league: "西甲", lg: "lg-j1",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,
          logic: "首发名单已出：阿拉维斯核心射手博耶未进名单确认缺阵+主力中卫停赛+后卫被赫塔费挖走；赫塔费新援Mangala首发+上季第7防守近皇马水平+近6次交锋4胜1平1负" },
        { no: "024", home: "塞维利亚", away: "巴列卡诺", league: "西甲", lg: "lg-j1",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-2 / 1-1 / 0-1", ht: "平负/平平/负负", ou: "总进球 1·2", risk: 4,
          logic: "新帅Luis García Plaza对巴列卡诺16次仅4胜2平10负（克星）+中卫Marcao/边锋Alfonso González伤缺；夏窗11人离队磨合不足；巴列卡诺射正率46%占优（Luiz Felipe伤缺）" },
        { no: "026", home: "弗鲁米嫩塞", away: "帕尔梅拉斯", league: "巴甲", lg: "lg-j1",
          dir: "平/负（B级）", dc: "dir-drawloss", scores: "1-1 / 0-1 / 1-2", ht: "平平/平负/负负", ou: "总进球 1·2", risk: 4,
          logic: "帕尔梅拉斯第1（48分）但周中解放者杯1-1消耗+Paulinho/Khellven/Jefté伤缺；弗鲁米嫩塞第4刚换帅（Zubeldía下课Marcão临时）+主力射手John Kennedy伤缺+主场连续4平韧性足" }
      ],
      coldRisk: [
        { rank: "🥇", no: "014", teams: "玛丽港 vs 塞伊奈约基", dir: "主胜", lv: "tag-red", lvTxt: "最高", logic: "野鸡垫底队，爆冷主场赢球/平局剧本" },
        { rank: "🥈", no: "024", teams: "塞维利亚 vs 巴列卡诺", dir: "客胜", lv: "tag-orange", lvTxt: "较高", logic: "夏窗11人离队新帅磨合+中卫Marcao伤缺，客胜30%>平局26%" },
        { rank: "🥉", no: "009", teams: "米亚尔比 vs 天狼星", dir: "主胜", lv: "tag-orange", lvTxt: "较高", logic: "领头羊9年未客胜克星，爆冷主胜剧本" },
        { rank: "4", no: "003", teams: "浦和红钻 vs 广岛三箭", dir: "主胜", lv: "tag-yellow", lvTxt: "中等", logic: "浦和5人停赛+后防换血，爆冷主胜剧本" },
        { rank: "5", no: "006", teams: "光州FC vs 浦项制铁", dir: "主胜", lv: "tag-yellow", lvTxt: "中等", logic: "双弱对话，光州主场爆冷赢球剧本" },
        { rank: "6", no: "019", teams: "阿拉维斯 vs 赫塔费", dir: "客胜", lv: "tag-gray", lvTxt: "低", logic: "主场占优，爆冷概率低" }
      ],
      alerts: [
        { script: "胜平", no: "001", teams: "鹿岛鹿角 vs 名古屋鲸八", lv: "tag-orange", lvTxt: "中等偏高", logic: "卫冕主场领先后可能松懈" },
        { script: "胜负", no: "024", teams: "塞维利亚 vs 巴列卡诺", lv: "tag-orange", lvTxt: "中等偏高", logic: "娃娃兵防线不稳，主队可能爆冷" },
        { script: "胜平", no: "004", teams: "神户胜利船 vs 东京FC", lv: "tag-yellow", lvTxt: "中等", logic: "残阵对攻防线都漏，领先可能被追平" },
        { script: "负胜", no: "026", teams: "弗鲁米嫩塞 vs 帕尔梅拉斯", lv: "tag-yellow", lvTxt: "中等", logic: "主队主场可能先进球，帕尔梅拉斯反扑" }
      ],
      zeroZero: [
        { no: "006", teams: "光州FC vs 浦项制铁", p: 15, lv: "tag-orange", lvTxt: "中等偏高" },
        { no: "014", teams: "玛丽港 vs 塞伊奈约基", p: 12, lv: "tag-gray", lvTxt: "低" },
        { no: "019", teams: "阿拉维斯 vs 赫塔费", p: 9, lv: "tag-gray", lvTxt: "低" },
        { no: "024", teams: "塞维利亚 vs 巴列卡诺", p: 7, lv: "tag-gray", lvTxt: "低" },
        { no: "009", teams: "米亚尔比 vs 天狼星", p: 6, lv: "tag-gray", lvTxt: "低" }
      ]
    },
    review: {
      results: [
        { no: "001", teams: "鹿岛鹿角 vs 名古屋鲸八", league: "日职联", lg: "lg-j1", score: "2-1（1-0）", d: "ok", s: "ok", h: "ok", signal: "正常（90+8绝杀）", sc: "ok" }
      ],
      evidence: [], avoidHigh: [], avoidWatch: []
    }
  }
};

/* 全局累计命中率（跨批次） */
const GLOBAL_STATS = {
  dir: "53/74", dirPct: "71.6%",
  score: "35/74", scorePct: "47.3%",
  ht: "50/74", htPct: "67.6%",
  updated: "2026-08-15"
};
