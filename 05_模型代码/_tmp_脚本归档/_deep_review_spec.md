# 历史批次深度复盘规格（子代理共享 v1）

## 任务
为 data.js（D:\Cola\足球分析学习\_发布_public\js\data.js）指定批次的 review.evidence 数组补全逐场深度复盘条目。results 已存在（对阵/赛果/三指标判定），**不需要改 results**，只补 evidence。

## 每场 evidence 条目格式（JS 一行）
{ no: "XX", teams: "主队 比分 客队", league: "联赛", lg: "lg-xxx", stats: "…", signal: "…", txt: "…", sc: "ok|watch|danger" }

- no/teams/league/lg：与 results 一致（teams 用 results 的 teams 字段，比分写进 txt 或 teams 后均可）
- stats：FotMob 实数据，至少 3 项（射门/射正/角球/控球/xG/禁区内触球/最佳球员评分），格式 "xG a:b、射门 a:b、控球 a%:b%、角球 a:b"
- signal：短标签（如 "正常" / "🟡 XX信号" / "🔴 高嫌疑"），与 sc 对应
- txt：①进球时间线（谁、几分进球，比分变化）②"演戏排查："结论（R321-R328 层面，正常写"无异常"）③"控分排查："结论（跨线球/波胆卡位/时段分布/领先方节奏——**必须带"控分排查："前缀**，网页渲染会截断该段，数据本地保留）
- sc：与 results 的 sc 一致（ok/watch/danger）

## 判定口径
- 演戏排查六项（R321-R328）：碾压收窄(R326)/占优惨败(R327)/转化率倒挂(R324)/半场领先收缩(R328)/补时剧本/闪击收工(R322)
- 控分排查四查：时段进球分布（<25'/75-90'/补时90+）、总进球卡位（跨 2.5/3.5/4.5/5.5 整数线=跨线球）、领先方节奏（停手/补刀）、关键事件时机（乌龙/绝杀/点球）
- 跨线球：尾声进球使总进球恰好跨整数大球线（如 1-1→2-1 两球→三球跨2.5线）
- 结论强度：无异常→"演戏排查：无异常"；有信号→"演戏排查：🟡 XX（R32X）"；强证据→"演戏排查：🔴 XX（R32X）"
- **禁止编造**：所有 stats/进球时间线必须来自 FotMob（read_page fotmob.com/matches/{slug}/{id}）或双源核验；搜不到就写"（数据待补）"，严禁虚构
- 网页合规：控分内容只出现在"控分排查："前缀后；演戏排查正常写

## 输出
按批次给出可直接粘贴进 data.js 的 evidence 数组行（保持 JS 语法），并报告：每场 signal/sc、异常场清单（🔴/🟡）、是否全部完成。

## 数据源
FotMob 优先：read_page https://www.fotmob.com/matches/{slug}/{id}（需要 id 时先用 web_search "fotmob 队名 vs 队名 日期" 找比赛页链接）。双源核验赛果；搜索摘要仅辅助。

## HTTP 调用铁律（防弹窗，用户明确要求）
- **彻底禁止 Invoke-WebRequest / Invoke-RestMethod**（任何形式，包括带 -UseBasicParsing——会弹用户屏幕确认窗）
- 一切 HTTP 数据获取：①read_page 工具读 FotMob 网页；或②curl.exe -s（Windows 自带，无弹窗）
- FotMob API 直连（实测可用）：`curl.exe -s -H "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34" "https://www.fotmob.com/api/data/matchDetails?matchId={id}"`
