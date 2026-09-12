# 足球分析预测站 · 前端审美与可用性审查报告

- **审查对象**：`D:\Cola\足球分析学习\_发布_public\`（index / avoid / review / report + css/style.css + js/app.js + js/gate.js）
- **线上版本**：v202609120545 · `https://football-analysis-report.pages.dev/`
- **审查方式**：源码逐行对照 Vercel Web Interface Guidelines + 线上实机核验（WebBridge 扩展 · Chrome 1912×863 桌面 + CDP 模拟 375×812 移动端 + 亮/暗双主题实测）
- **审查日期**：2026-09-12
- **约束**：只审不改，未修改任何站点文件（改动量为 0）

---

## ① 执行摘要

| 级别 | 条数 | 性质 |
|---|---|---|
| **P0** | 5 | 可读性 / 可访问性实质缺陷，用户已经在受影响 |
| **P1** | 8 | 明显降低体验或违反规范，建议本迭代修 |
| **P2** | 6 | 打磨项与代码卫生 |

**一句话结论**：信息架构与移动端卡片化做得相当扎实（375px 零横向溢出、表格卡片化生效、双层主题 token 完整、体量裁剪到 221KB 首屏），但**全站次要文字（`--sub`）与暗色主色按钮存在系统性对比度不足**，叠加移动端大量 10.5–12px 小字后，"看得清"这一条最基本的可用性没有守住；另有 3 处结构性缺陷（日历不可键盘操作、搜索框无标签、report 页无入口）需要结构性修。

**实测基线（可信、可复现）**

| 指标 | 值 |
|---|---|
| 桌面首屏 header+nav 高度 | 276 + 70 = **346px / 863px（40%）** |
| 移动端 375px 横向溢出 | **0**（hero-glow 420px 被 `overflow:hidden` 正确裁剪） |
| 移动端首屏 header+nav | 166 + 55 = 221px / 812px |
| avoid 页文字节点 | 1411 个，其中 **798 个 < 12px（57%）** |
| 对比度实测不达标 | 暗色 **41 处** / 亮色 **6 处**（仅纯色背景，可精确计算） |
| 首屏资源 | 8 请求 / 2.29MB，其中 data-history.js 1.66MB（首屏后注入） |
| CSS 体量 | style.css 2751 行 / 132KB |

---

## ② P0 · 逐条

### P0-1 暗色主题"主色按钮"白字对比度 1.54:1 —— 主操作不可读

- **现象**：暗色模式下，所有"主色底 + 白字"的元素（首页的 `全部 / 10 场` 激活筛选胶囊、`上批/下批` hover 态、导航 `.active` 等）白字压在青色 `#00e5ff` 上，实测对比度 **1.54:1**，肉眼接近"亮块上的白雾"。亮色模式同一类元素为 **4.38:1**，同样低于 4.5:1 门槛。
- **证据**：
  - `css/style.css:52` `--primary: #00e5ff;`（暗色 token）
  - `css/style.css:13` `--primary: #4a7bb5;`（亮色 token）
  - `css/style.css:2194` `.lvl-pill.active.lvl-all { background: var(--primary) !important; color: #fff !important; }`
  - `css/style.css:1576` `.batch-nav:not(:disabled):hover { background: var(--primary) !important; color: #fff !important; }`
  - 线上实测（暗色）：`{"fs":12,"cr":1.54,"need":4.5,"bg":"rgb(0, 229, 255)","c":"rgb(255,255,255)","t":"全部"}`
  - 线上实测（亮色）：`{"fs":12,"cr":4.38,"need":4.5,"bg":"rgb(74, 123, 181)","c":"rgb(255,255,255)","t":"全部"}`
- **依据条款**：Hover & Interactive States —"Interactive states increase contrast"；隐含 a11y 对比度基线（WCAG AA 正文 4.5:1）。
- **建议修法**：暗色下把"主色底"上的文字色改为深色 `#04141a`（对 `#00e5ff` 约 12:1），或改用 `--primary-dark: #00b8d4` 作底；亮色下把 `.lvl-pill.active` / `.batch-nav:hover` 底色换成 `--primary-dark: #3a6697`（白字 5.6:1）。**一处 token 级改动可同时修 6+ 个组件。**
- **影响面**：全站 4 页所有主色按钮与激活态；暗色模式下最严重。

### P0-2 全站次要文字 `--sub` 对比度不足（亮 3.12–3.59:1 / 暗 4.07:1）

- **现象**：`--sub` 承担了全站绝大部分辅助信息——表头、`data-l` 标签（移动端卡片的字段名）、`.hint` 说明、`.lbl`、`.mt-line`、`.match-time`、`.cal-count`、页脚。实测：
  - 亮色 `.sub`/`.hint`/`.lbl` 在卡片上 **3.59:1**，在页面底色上 **3.12:1**
  - 暗色 `.sub` 在卡片上 **4.07:1**
  - 移动端字段标签实测 **4.07:1**（`反环 2`，12.5px）
  - 最差组合：`1 正 2 反 · 0 场` → **4.04:1 @ 10px**；`🕐 15:30` → **4.18:1 @ 11px**
- **证据**：
  - `css/style.css:12` `--sub: #76889e;`（亮）
  - `css/style.css:51` `--sub: #5f7699;`（暗）
  - `css/style.css:1357` `.sub, .hint, .card .desc { color: color-mix(in srgb, var(--sub) 92%, transparent); }` ← **在已偏浅的 `--sub` 上又叠一层透明，把 3.59 拉到 3.31**
  - `css/style.css:877` `.table-wrap tbody td::before { ... color: var(--sub); ... }`（移动端字段标签）
  - `css/style.css:952` `.match-time{color:#8a94a6;...}`
  - 线上实测：暗色点名的 41 处里，`--sub` 系占多数
- **依据条款**：Hover & Interactive States（对比度递进）；Typography（小字可读性）。
- **建议修法**：`--sub` 亮色改 `#5a6b80`（对 `#fdfeff` 约 5.3:1）、暗色改 `#8fa3bd`（对 `#0b1120` 约 6.6:1）；**并删掉 `:1357` 的 `color-mix(..., 92%, transparent)`**，直接 `color: var(--sub)`。
- **影响面**：全站；移动端 798 个 <12px 文字节点几乎全部依赖此色。

### P0-3 移动端 57% 文字 < 12px（最小 10px）

- **现象**：avoid 页 1411 个叶子文字节点中 **798 个（56.6%）小于 12px**；375px 下字号直方图集中在 `10.5px×63 / 11px×42 / 11.5px×36 / 10px×4`。中文在 10–11.5px 下笔画糊成一片，对手机端阅读是实质障碍。
- **证据**：
  - `css/style.css:444` `.lg-sm { padding:1px 7px; font-size:10.5px; ... }`
  - `css/style.css:1851` `.lg { font-size: 10.5px !important; padding: 2px 8px !important; }`
  - `css/style.css:845 / 848`（640px 断点）`.cal-cell{font-size:11px}`、`.prob-txt{font-size:11px}`
  - `css/style.css:902`（640px 断点）`.header-top .contact-item { font-size: 10.5px; ... }`
  - `css/style.css:798` `.footer-note { opacity:.7; font-size:11.5px; }`
  - 线上实测（375px）：`{"fontSizeHistogram":{"10":4,"11":42,"12":16,"13":55,"10.5":63,"11.5":36,"12.5":48,...}}`，`{"textNodes":{"total":1411,"under12px":798}}`
- **依据条款**：Typography（正文可读性）；Content Handling。
- **建议修法**：设一条下限——**移动端最小正文 12px、字段标签 ≥ 11.5px**；把 `.lg` 从 10.5 提到 11.5，`.contact-item` 从 10.5 提到 12，`.cal-cell` 从 11 提到 12。预计整页高度增加约 3%。
- **影响面**：移动端全部 3 页；影响最大的正是"快速扫读"这一核心场景。

### P0-4 日历日期单元格用 `<div onclick>`，键盘与屏读器完全不可达

- **现象**：首页/复盘页的批次日历里，可选日期是 12 个 `<div class="cal-cell has-data" onclick="selectDate(...)">`。**没有 `role`、没有 `tabindex`、没有键盘事件**——Tab 键无法聚焦，Enter/Space 无效，屏读器读不出这是可点日期。这是"选批次"这一主功能的唯一入口。
- **证据**：
  - `js/app.js:98` `` html += `<div class="cal-cell ${has ? "has-data" : ""} ..." ${has ? `onclick="selectDate('${key}')" title="${fmtDate(key)}"` : ""}>` ``
  - `js/app.js` 全文扫描：`keydown/keyup/keypress` 命中 **0** 次；`role=` 命中 **0** 次；`tabindex` 命中 **0** 次；`aria-` 命中 **1** 次（`js/app.js:832`，仅 SVG 装饰的 `aria-hidden`）
  - 线上实测：`{"nonSemanticClickables":["div.cal-cell.has-data :: 1", ... ×12],"hasRole":0}`
- **依据条款**：Accessibility —"Interactive elements need keyboard handlers"、"`<button>` for actions, not `<div onClick>`"；Anti-patterns —"`<div>` or `<span>` with click handlers (should be `<button>`)"。
- **建议修法**：`js/app.js:98` 改为输出 `<button class="cal-cell ...">`（CSS 已有 `.cal-cell` 样式，加 `appearance:none;border:0;font:inherit` 即可）；至少补 `role="button" tabindex="0"` + `onkeydown` 处理 Enter/Space，并加 `aria-label="${fmtDate(key)}，查看该批预测"`、当前日期加 `aria-current="date"`。
- **影响面**：键盘用户与辅助技术用户**完全无法切换批次**。

### P0-5 搜索框无标签，清空按钮仅 24×24 且无 aria-label

- **现象**：红黑总榜的搜索框（该页核心功能）没有 `<label>`、没有 `aria-label`、没有 `name`、没有 `autocomplete`；右侧清空按钮 `✕` 只有 `title="清空"`，命中区仅 **24×24px**。
- **证据**：
  - `js/app.js:1038` `<input id="avoidSearchInput" type="text" placeholder="🔍 搜索队伍（如 天狼星 / 本菲卡）…" oninput="renderAvoidSearch(this.value)">`
  - `js/app.js:1039` `<button class="avoid-search-clear" onclick="..." title="清空">✕</button>`
  - `css/style.css:1036` `.avoid-search-clear { position:absolute; right:6px; width:24px; height:24px; ... }`
  - 线上实测：`{"searchInput":{"name":null,"autocomplete":null,"aria":null,"hasLabel":false,"spellcheck":null}}`、`{"searchClear":{"aria":null,"title":"清空","size":"24x24"}}`
- **依据条款**：Accessibility —"Form controls need `<label>` or `aria-label`"、"Icon-only buttons need `aria-label`"；Forms —"Inputs need `autocomplete` and meaningful `name`"。
- **建议修法**：输入框加 `aria-label="搜索队伍"` 与 `name="q"`、`autocomplete="off"`；清空按钮加 `aria-label="清空搜索"`，命中区用 `padding`/`::before` 撑到 ≥44×44（视觉仍可保持 24px 圆点）。
- **影响面**：avoid 页搜索；屏读器用户听到"编辑框"但不知搜什么。

---

## ③ P1 · 逐条

### P1-1 暗色主题不跟随系统，且 `color-scheme` 缺失导致原生控件"串色"
- **证据**：`index.html:17-23`（同款见 `avoid.html:11-17`、`review.html:11-17`）只读 `localStorage`，不查 `prefers-color-scheme`；线上实测本机系统为暗色而站点仍渲染亮色：`{"prefersDark":true,"isDarkClass":false,"bgColor":"rgb(213, 226, 243)"}`。
- `css/style.css` 全文 `color-scheme` 命中 **0**；线上 `getComputedStyle(document.documentElement).colorScheme === "normal"` → 暗色下滚动条、`<select>` 下拉、输入框仍按亮色渲染。
- **依据条款**：Dark Mode & Theming —"`color-scheme: dark` on `<html>` for dark themes"。
- **修法**：初始化脚本加 `if (!localStorage.getItem('dsh-theme') && matchMedia('(prefers-color-scheme: dark)').matches) add('dark')`；`:root{color-scheme:light}` / `html.dark{color-scheme:dark}`。

### P1-2 `meta theme-color` 与实际页面背景不符，暗色下仍是青色
- **证据**：`index.html:12` `<meta name="theme-color" content="#0f766e">`，而实测亮色页面底色是 `#e9eef6`、暗色是 `#070b14`；线上 dark 态实测 `metaTheme` 仍为 `"#0f766e"`。移动端浏览器 UI 条会与页面脱节。
- **附带**：`avoid.html` / `review.html` 连 `theme-color` 和 `og:*` 都没有（`avoid.html` 第 3-8 行只有 title+stylesheet+preload）。
- **依据条款**：Dark Mode & Theming —"`<meta name="theme-color">` matches page background"。
- **修法**：改为亮色 `#e9eef6`，并用 `media="(prefers-color-scheme: dark)"` 提供第二枚；或在切主题时用 JS 同步 `content`。补全三页 og 标签。

### P1-3 移动端 19 个命中区 < 44px
- **证据**（375px 实测）：`{"smallTargets":{"count":19,"samples":[{"c":"batch-nav","s":"51x32"},{"c":"updlog-btn","s":"83x26"},{"c":"theme-toggle","s":"95x34"},{"c":"active","s":"92x38"}]}}`
- 对应 CSS：`css/style.css:1713` `.batch-nav { padding:6px 12px !important; font-size:12.5px !important; min-height:34px; }`、`css/style.css:1858` `min-height:32px`、`css/style.css:798` 页脚、`js/app.js:1036` 的 24×24 清空键。
- 桌面同样偏小：`{"batchNav":"59x30","themeToggle":"95x34","updlog-btn":"83x26"}`（回顶按钮 `.back-top` 44×44 达标，可作基准）。
- **依据条款**：Touch & Interaction；可点区域惯例 ≥44×44。
- **修法**：给 `.batch-nav`/`.updlog-btn`/`.theme-toggle` 加 `min-height:44px`，移动端用 `padding` 撑高而不放大字号。

### P1-4 `report.html`（34KB 报告页）在主站无任何入口
- **证据**：`report.html` 全文 `href=` 命中 **0**；`js/app.js` 全文 `report` 命中 **0**；三页 `nav` 只有 `index/avoid/review`（`index.html:55-57`）。该页实际不可达。
- **附带**：`report.html:253-256` 的四个 `.tab-btn` 是纯 `<button>` 点击切换，无 `role="tablist"/"tab"/"aria-selected"`，无 ←/→ 方向键（`report.html:493` 只有 click 委托）。
- **修法**：三页导航加一项或在首页加卡片入口；tab 补 `role="tablist"` + `aria-selected` + 方向键漫游。

### P1-5 `report.html` 与主站是两套设计系统，且与其余页互为镜像错误
- **证据**：`report.html` 内联整套 CSS（`report.html:7-247`），字体栈是 `"HarmonyOS Sans SC","MiSans","PingFang SC",...`（`report.html:71`），**不用站点的 Smiley Sans**；暗色类名是 `body.dark`（`report.html:43`），而其余三页是 `html.dark`（`css/style.css:44`）；`report.html` 无 `prefers-reduced-motion`、无 `@font-face`、无 `og:*`。
- **修法**：中期把 report 页并入 `css/style.css` 的 token 体系；短期至少统一字体与暗色类名，避免同一个 `dsh-theme` 偏好出两种行为。

### P1-6 `js/app.js` 对 `<th>` 绑定点击排序，无键盘等价
- **证据**：`js/app.js:797` `th.addEventListener("click", () => { ... })`；`th` 不是可聚焦元素，无 `tabindex`、无 Enter/Space 处理。**依据条款**：Interactive elements need keyboard handlers；Drag/gesture 类交互需键盘替代。

### P1-7 首屏标题区占 40%，第一个预测卡在 813px 处
- **证据**：桌面实测 `{"vh":863,"headerH":276,"navH":70,"firstCardTop":380,"firstRowTop":813}`——第一个比赛行刚好压着 863px 折线；移动端 `{"headerH":166,"navH":55,"firstCardTop":241,"firstRowTop":684}`。用户要"看预测"，先要滚过整屏装饰。
- **建议**：桌面把 header padding 收到 `28px 0 34px`、`header-hero-stats` 折进 `.sub` 行；或给日历卡加 `max-height` 折叠（移动端已有折叠按钮 `.cal-toggle`，桌面没有）。

### P1-8 `--font-num` 依赖 Windows 独占字体 Bahnschrift，跨平台等宽失效
- **证据**：`css/style.css:41` `--font-num: "Bahnschrift", "DIN Alternate", "Arial Narrow", "Segoe UI", sans-serif;`
- 线上实测（Windows 有 Bahnschrift）：`{"numVar":{"ones":108.45,"eights":108.45,"zeros":108.45,"tabularOK":true}}`（等宽成立）；
- 但 `.kpi .num` 之类元素实际落到 body 字体，实测 `{"bodyVar":{"ones":59.2,"eights":95.81,"zeros":100,"tabularOK":false}}`。
- **修法**：`--font-num` 末尾补 `ui-monospace, "SF Mono", "Roboto Mono", monospace`，并在 `@font-face` 的 `unicode-range` 已覆盖 `U+20-7E` 的前提下**给数字容器加 `font-variant-numeric: tabular-nums`**（Smiley Sans 本身非等宽数字，靠该属性无法补救，必须换族）。

---

## ④ P2 · 逐条

### P2-1 `.rev-score` 改判标记暗色下 4.38:1
- `css/style.css:467` `.rev-score { color:#d9480f; ... }`；线上暗色实测 `{"fs":13,"cr":4.38,"need":4.5,"t":"1-0*"}`。这是"改判"的功能性信号色，建议暗色下换 `#ff8a4c`。

### P2-2 `.hint` 存在 CSS 互撞（后写的覆盖先写的）
- `css/style.css:770` 定义 `h2 .hint { margin-left:auto; font-size:12px; ... }`，而 `css/style.css:1002` 又写 `.updlog-head .hint { font-size:11.5px; }`；同时 `:1357` 的 `.sub,.hint,.card .desc` 覆盖其颜色。三者叠加是 P0-2 的成因之一。

### P2-3 `.kpi .kpi-num / .ss-num / .stat-num` 是死规则
- `css/style.css:1337-1349` 为这三个类写了渐变文字标题效果，但线上实测 `{"numEl":null,"kpiNumExists":false}`——当前 DOM 不存在这些类（KPI 走 `.kpi .num` / `.ring-num b`，见 `css/style.css:515`、`:534`）。此段 CSS 无出口。

### P2-4 `fonts/LXGWNeoXiHei-subset.woff2`（157KB）已加载但无人使用
- `fonts/font.css:9-14` 声明了 `LXGW Neo XiHei`，但 `css/style.css` 全文 `font-family` 只引用 `Smiley Sans Oblique`（`:40`、`:42`）。
- 线上实测 `document.fonts` 状态：`["Smiley Sans Oblique/loaded","LXGW Neo XiHei/unloaded"]`；资源计时里 `LXGWNeoXiHei-subset.woff2` 被请求但 0 字节（未真正传输）。**仓库里躺着一个 157KB 的未使用字体。**

### P2-5 首屏就有两次全量 `renderAll()`
- 首页脚本 `index.html:102` 在 history 数据到达后再跑一次 `renderAll()`；`js/app.js:1166` 在 `DOMContentLoaded` 已跑过一次。实测 `layoutShift: 0`、`clsAttr: 0`（因为测的是 load 之后），但用户可见的"先渲染→300ms 后重渲染"闪烁风险仍在，且 `renderAll` 的 `catch` 分支（`js/app.js:1151-1157`）会用错误卡替换内容——二次渲染时如果 history 数据异常，用户会看到"🚫 页面渲染异常"盖掉本来正常的内容。

### P2-6 `review.html:118-119` 重复调用
- `review.html:118` 与 `:119` 是两行完全相同的 `try { if (typeof mergeReviewExtra === "function") mergeReviewExtra(); } catch (e) {}`。无害，但属复制粘贴残留。

---

## ⑤ 设计评审（impeccable / make-interfaces-feel-better 视角）

**做得好、别动的地方**：①浅色"雾蓝 + 玻璃卡片"的方向是对的，低饱和主色不刺眼，符合"舒适优先"的既定目标；②双层 token（`:root` / `html.dark`）覆盖完整，四个语义色（risk-high/mid/ok + primary）体系清楚；③640px 表格卡片化实现得相当细致——`data-l` 标签化、`data-sf` 整行跨列、比分/半全场强制整行防重叠（`css/style.css:862-932`），375px 实测零溢出、零裁切，这块质量明显高于同类数据站；④`.lg` 联赛色 20+ 种有注释、有别名合并（`:416-445`），运营友好。

### 5.1 信息层级
- **问题**：每个卡片标题都是 `font-weight:800` + 同色大字号（`css/style.css:1352`），首页 5 个 H2 视觉权重完全相同，"完整预测清单"这个真正的主内容没有比"更新日志"更突出。**建议**：一级卡标题 18px/800 + 主色，二级分区标题降到 15px/700 + `--ink`，用字号而非仅用颜色区分层级。
- **问题**：`h2` 里塞了按钮和 hint（线上取到 `"💡\n 🔽 展开全部\n"`），标题语义被污染。**建议**：标题行拆成 `h2` + 右侧 `.card-actions` 容器。

### 5.2 间距节奏
- **问题**：间距值散乱——`padding: 7px 11px`(`:957`)、`9px 11px`(`:869`)、`11px 12px`、`14px 16px`(`:392`)、`12px 13px`(`:850`) 等十余种组合，缺少 4/8 基准刻度。**建议**：收敛到 `4/8/12/16/24` 五档，用 `--sp-1..5` 变量；行内 padding 统一 `12px`。
- **问题**：`.card` 内边距在 ≤480px 变成 `12px 10px`（`:934`），而表格卡片自身还有 `9px 11px`（`:869`），两级内边距几乎相等 → 手机端"卡片套卡片"的层级感变弱。**建议**：外层 `.card` 保持 ≥16px，内层行卡 10–12px，让嵌套关系读得出来。

### 5.3 排版
- **行高**：`body line-height:1.8`（`:94`）对 15.5px 中文偏松（约 27.9px 实测），长段落读起来散。**建议**：正文 1.7，密集表格区 1.5，标题 1.3——分场景给，而不是全局 1.8。
- **数字等宽**：比分/总进球/半全场列已经做对了（`:1213-1217` + 实测 `tabular-nums`）；但**表格首列场次号、KPI 数字、联赛统计数走的是 body 字体**（实测 `ones 59.2` vs `eights 95.81`，非等宽）。**建议**：给 `.td` 数字列与所有统计数字容器统一挂 `--font-num`。
- **中文标点与省略号**：placeholder 已正确使用 `…`（`js/app.js:1038`），这点合规。
- **标题折行**：`h1` 未使用 `text-wrap: balance`（实测 `h1Wrap: "wrap"`），长标题易出孤字。**建议**：`.card h2, header.site h1 { text-wrap: balance; }`。

### 5.4 动效
- **已有的好**：`css/style.css:1275-1277` 用 `*,*::before,*::after { transition:none!important; animation:none!important }` 一刀切降级，覆盖彻底；`:2052` 有第二处。
- **问题**：`transition: all` 出现 **12 次**（`:207, 216, 243, 322, 352, 660, 682, 705, 715, 766, 795, 812`），全部应列出具体属性；`report.html:122` 也有一处。
- **问题**：`:1276` 的全局 `transition:none !important` 过于粗暴——它同时干掉了颜色过渡，主题切换会"瞬间跳变"而不是淡入。**建议**：改成只禁 `animation` 与 `transform/opacity` 过渡，保留 `background-color/color` 的 0.2s。
- **问题**：`html { scroll-behavior: smooth; }`（`:82`）未在 reduced-motion 下关闭，回顶按钮还硬编码 `behavior:'smooth'`（`index.html:72`）。**建议**：`@media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto} }`。

### 5.5 emoji 当图标
- **风险（已实测）**：emoji 宽度实测 `{"🟢":55,"🟡":55,"🔴":55,"⭐":55,"⚽":40,"🌙":55,"🏆":55}`——**`⚽` 只有 40px，比同组 emoji 窄 27%**，因为它落在文本呈现（text presentation）分支上。同一行里混排就会出现基线/宽度跳动。
- **可访问性**：emoji 目前是裸露的裸文本（`index.html:42` 的 `⚽`、`avoid.html:36` 的 `🏆`、`js/app.js:415` 的 `🔽 展开全部`），屏读器会念出"足球 足球分析预测站"，且 emoji 语义随平台变化（🟡 在不同系统偏橙/偏绿，而本站用它表达"偏黑"这一精确语义）。
- **建议**：①**状态语义不要只靠 emoji** —— 🟢🟡🔴 旁已有文字（"红榜/偏黑"），保持这个做法，别退化成纯 emoji；②装饰性 emoji（标题前缀 ⚽🏆🔍📋）包 `<span aria-hidden="true">`；③给 `⚽` 这类文本呈现 emoji 补 `&#xFE0F;`（VS16）或删掉换 SVG；④数字/状态列改用 CSS 圆点（`background:var(--risk-ok)`）更可控。

### 5.6 暗色主题一致性
- 主线一致（`html.dark` + token 全面覆盖，`:44-78` 后各组件均有 dark 覆写）。**不一致点**：`report.html:43` 用 `body.dark`，其余页 `html.dark`；`report.html` 无 `color-scheme`、无主题初始化内联脚本 → 刷新会先闪一下亮色。
- `--sub` 与 `--footer-ink` 在暗色下都偏低（4.07 / 3.42），是 P0-2 的一部分。

### 5.7 移动端 640px 断点
- **结论：这一块是本站最强项**。375px 实测：`overflowX: 0`、`wideEls` 只有被 `overflow:hidden` 正确裁剪的装饰层；`thead display:none`、`tr display:grid`（2 列 / rv-row 4 列）、`td::before` 注入 `data-l` 标签全部生效；无任何文字被裁切（`clipped: []`）。
- **仍可改进**：移动端 `header.site { padding:14px 16px 12px }`（`:893`）已很紧，但 `.cal-card` 仍占 67px 且默认折叠态只显示"批次日历 12 个批次"——建议把当前批次直接写进折叠条（如"批次日历 · 9/12 周六批 10 场"），再省一次点击。

### 5.8 表格窄屏可读性
- 已做卡片化，很好。但**桌面表格 sticky 表头 + `backdrop-filter: blur(8px)`**（`:1310-1314`）在长表格滚动时，若某列背景不透明会出现"半透明叠字"；建议 sticky 表头同时给 `background: var(--thead-bg)` 实色兜底。
- 窄屏（641–900px 之间）表格仍是真表格 + `overflow-x`，这一段没有专门处理，平板竖屏会有横向滚动。**建议**：把卡片化断点从 640px 提到 720px。

### 5.9 AI 味 / 模板感诊断
- **低**。没有常见的紫蓝渐变、没有无意义大圆角卡片堆叠、没有"赋能/闭环"式空话。文案是具体的（"数据双源核验""样本库 4000+ 场"）。
- 轻微模板味：①`header.site::after` 放了个 120px 的 `⚽` 水印（`:135`），属于常见的"加个大 emoji 当装饰"套路，且它是 `content` 伪元素，屏读器处理不一致——建议换成 SVG 或去掉；②`hero-glow / hero-deco / hero-ring / hero-sheen` 四层装饰（`index.html:29-32`）在视觉上几乎看不出差别，建议砍到 1–2 层，省渲染也省代码。

---

## ⑥ Quick Wins（按性价比排序，≤10 条）

| # | 动作 | 位置 | 收益 | 改动量 |
|---|---|---|---|---|
| 1 | `--sub` 亮色改 `#5a6b80`、暗色改 `#8fa3bd`，并删掉 `:1357` 的 92% 透明叠加 | `css/style.css:12,51,1357` | 修掉全站最大一类对比度失败（P0-2） | **S** |
| 2 | 暗色主色底按钮文字改深色 `#04141a`；亮色 `.lvl-pill.active`/`.batch-nav:hover` 底改 `--primary-dark` | `css/style.css:2194,1576` + 暗色 token | 修掉 1.54:1 的"不可读主操作"（P0-1） | **S** |
| 3 | 页脚 `.footer-note`/`.footer-disclaimer` 去掉 `opacity` 并升到 12px | `css/style.css:798-802` | 免责声明这类必须可读的文字立刻可读（现值 3.48:1 @10.5px） | **S** |
| 4 | 给 `.batch-nav`/`.updlog-btn`/`.theme-toggle` 加 `min-height:44px`，清空键撑到 44×44 | `css/style.css:1713,1858`；`js/app.js:1036` | 移动端 19 处小命中区收敛（P1-3） | **S** |
| 5 | 搜索框补 `aria-label`/`name`/`autocomplete`，清空键补 `aria-label` | `js/app.js:1038-1039` | P0-5 | **S** |
| 6 | `.lg` 10.5→11.5px、`.contact-item` 10.5→12px、`.cal-cell` 11→12px | `css/style.css:444,1851,902,845` | 缓解"57% 文字 <12px"（P0-3） | **S** |
| 7 | 日历格子 `<div>` → `<button>`，补 `aria-label`/`aria-current` | `js/app.js:98` + `css/style.css:705` | 键盘用户恢复"选批次"能力（P0-4） | **M** |
| 8 | `html.dark{color-scheme:dark}` + 主题初始化读 `prefers-color-scheme` + `theme-color` 跟随 | `css/style.css:44`、`index/avoid/review.html:12-23` | 原生控件串色 + 系统暗色不生效（P1-1/P1-2） | **M** |
| 9 | 12 处 `transition: all` 展开为具体属性 | `css/style.css:207,216,243,322,352,660,682,705,715,766,795,812` | 消除性能与动效不可控点（P2） | **M** |
| 10 | 三页导航补 `report.html` 入口 | `index.html:55-57` 等 | 激活一个 34KB 的哑页面（P1-4） | **S** |

> 若只能做两件：**#1 + #2**。它们都是 1–2 行 token/选择器改动，却分别修掉"次要文字看不清"和"主按钮读不出"这两个最伤用户的点。

---

## ⑦ 审查范围与限制

**已查（有实测证据）**
- 源码逐行对照：`index.html`(115) / `avoid.html`(102) / `review.html`(133) / `report.html`(509) / `css/style.css`(2751) / `js/app.js`(1204) / `js/gate.js`(34) / `fonts/font.css`(15)
- 线上 3 页（`/`、`/avoid.html`、`/review.html`）桌面 1912×863 实机截图 + 度量
- 线上 375×812 移动端（CDP `Emulation.setDeviceMetricsOverride`）截图 + 度量
- 亮色 / 暗色双主题实测（含 `getComputedStyle` token 取值与对比度计算）
- 资源体积、请求数、字体加载状态、`document.fonts` 状态

**未查 / 查不到（如实说明）**
1. **键盘 focus 环未能实机验证**：WebBridge 浏览器窗口 `document.hasFocus() === false`，脚本 `focus()` 不触发 `:focus-visible`，实测返回 `matchesFocusVisible:false`。此条**只做了源码判定**：`css/style.css:81` 有全局 `:focus-visible { outline:2px solid color-mix(in srgb, var(--primary) 60%, transparent); outline-offset:2px }`，`css/style.css:1032` 的 `outline:none` 仅作用于 `.avoid-search input`（且 `:1034` 有 `:focus` 替代环）。**结论：全站 focus 环应存在，但蓝色 60% 透明的环在深蓝 header 上对比偏弱——建议实机 Tab 走一遍确认。**
2. **未做真实触屏/真机测试**：移动端为 CDP 视口模拟，非真机；字体回退、emoji 彩色渲染在不同系统上的差异未验。第三点里 `⚽` 宽度 40 vs 55 只在 Windows Chrome 上实测。
3. **未做屏读器实测**：无 NVDA/VoiceOver，a11y 结论基于 DOM/属性静态检查 + 规则比对。
4. **未评估键盘 Tab 顺序的合理性**（仅取到 `focusableCount: 26` 与前 12 个序列）。
5. **report.html 未做线上核验**：该页不在导航中，也未在线上单独跑度量；其结论（无入口、`body.dark` 类名不一致、无 reduced-motion、独立字体栈）**全部来自源码静态检查**。
6. **未审查 `js/data*.js`（2.9MB 数据文件）内容**：按要求只看结构，未检查数据正确性。
7. **未做性能剖析**（无 Lighthouse / Performance 面板 trace）：体量数据来自 `performance.getEntriesByType('resource')`。首屏 2.29MB 中 data-history.js 占 1.66MB，**是否值得进一步拆分未做评估**——它已在 `load` 后 300ms 注入，属于既有的提速设计。
8. **未评估 `gate.js` 的密码门**：该脚本当前在三个页面均被注释掉（`index.html:112-114` 等），仅审了源码层面的 `outline:none`（`js/gate.js:13`）与无 `aria-live` 的错误提示（`js/gate.js:17`）。

**审查方式说明**：本次为**只审不改**，未修改任何站点文件（`_发布_public` 下改动量为 0）。所有证据为 `file:line` 或线上实测值/截图路径，无印象式结论。

**截图证据**（`D:\Cola\足球分析学习\03_报告复盘\截图_260912_网页审美审查\`）

| 文件 | 内容 |
|---|---|
| `desktop_index_light.png` | 首页 1912×863 亮色 |
| `desktop_avoid_light.png` | 红黑总榜 1912×863 亮色 |
| `desktop_review_light.png` | 赛后复盘 1912×863 亮色 |
| `mobile375_index_light.png` | 首页 375×812 亮色（含卡片化表格） |
| `mobile375_index_dark.png` | 首页 375×812 暗色（暴露 P0-2 小字对比度） |

---

## 附：Handoff / 后续操作指引

- **直接开工**：从上表 Quick Wins **#1、#2** 起手（各 1–2 行），改完部署后建议用同一套度量脚本复测对比度（本报告使用的探针脚本在 `D:\Cola\_tmp_webaudit\`，核心为 `probe.js` / `probe7.js` / `40_contrast.js`）。
- **结构性改动**（P0-4 日历按钮化、P1-4 report 入口、P1-5 设计系统合并）建议单独开一批，改完必须做三页 × 双主题 × 双断点的回归（本次基线值已列在①）。
- **相关技能**：`impeccable`（`polish` / `audit` 子流程）、`make-interfaces-feel-better`（数字等宽、命中区、同心圆角）、`redesign-existing-projects`（若决定做设计系统合并）、`web-design-guidelines`（本报告规则来源）。
- **注意**：`css/style.css` 是 2751 行单文件且存在 `:770`/`:1002`/`:1357` 这类互撞规则，改动前建议先在该文件内搜同类选择器，避免"改了没生效"。
