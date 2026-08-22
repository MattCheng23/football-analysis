/* ============================================================
   足球分析预测站 · 应用逻辑（日历 + 动态渲染）
   ============================================================ */

/* 复盘数据合并（2026-08-20 拆分：data-review.js 由复盘页加载后并入 BATCHES；首页不加载则 review 为空壳） */
(function(){
  if (typeof REVIEW_EXTRA !== "undefined" && typeof BATCHES !== "undefined") {
    Object.keys(REVIEW_EXTRA).forEach(function(k){
      if (BATCHES[k]) BATCHES[k].review = REVIEW_EXTRA[k];
    });
  }
})();

/* ---------- 工具 ---------- */
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
function h(tag, cls, html) { return `<${tag} class="${cls}">${html}</${tag}>`; }
function fmtDate(key) {
  const [y, m, d] = key.split("-");
  return `${y}年${parseInt(m)}月${parseInt(d)}日`;
}
function fmtKey(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/* ---------- 日历状态 ---------- */
let calYear = 2026, calMonth = 7; // 2026-08
let calOpen = false;

/* ---------- 日历渲染 ---------- */
function renderCalendar() {
  const keys = Object.keys(BATCHES).sort();
  const el = document.getElementById("calendar");
  if (!el) return; // 非日历页面（如避雷名单页）跳过
  const first = new Date(calYear, calMonth, 1);
  const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
  const startDow = first.getDay(); // 0=周日
  const weekdays = ["日", "一", "二", "三", "四", "五", "六"];
  // 本月有数据的日期数
  const monthKey = `${calYear}-${String(calMonth + 1).padStart(2, "0")}`;
  const count = keys.filter(k => k.startsWith(monthKey)).length;

  let html = `
    <button class="cal-toggle" onclick="toggleCalendar()">
      <span>📅 批次日历</span>
      <span class="cal-count">${count} 个批次</span>
      <span class="cal-arrow">▼</span>
    </button>
    <div class="cal-body">
      <div class="cal-head">
        <button class="cal-nav" onclick="calShift(-1)" title="上一月">‹</button>
        <div class="cal-title">${calYear} 年 ${calMonth + 1} 月</div>
        <button class="cal-nav" onclick="calShift(1)" title="下一月">›</button>
      </div>
      <div class="cal-grid cal-week">${weekdays.map(w => `<div class="cal-dow">${w}</div>`).join("")}</div>
      <div class="cal-grid cal-days">`;

  for (let i = 0; i < startDow; i++) html += `<div class="cal-cell empty"></div>`;
  const today = new Date();
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  for (let d = 1; d <= daysInMonth; d++) {
    const key = fmtKey(new Date(calYear, calMonth, d));
    const batch = BATCHES[key];
    const has = !!batch;
    const reviewed = batch && batch.reviewed;
    const isCur = key === currentKey;
    const isToday = key === todayKey;
    html += `<div class="cal-cell ${has ? "has-data" : ""} ${isCur ? "current" : ""} ${isToday ? "today" : ""}" ${has ? `onclick="selectDate('${key}')" title="${fmtDate(key)}"` : ""}>
      <span class="cal-num">${d}</span>
      ${has ? `<span class="cal-dot ${reviewed ? "done" : "pending"}" title="${reviewed ? "已复盘" : "预测已发布"}"></span>` : ""}
    </div>`;
  }
  html += `</div>
      <div class="cal-legend">
        <span><span class="cal-dot done"></span> 已复盘</span>
        <span><span class="cal-dot pending"></span> 已预测</span>
      </div>
      <div class="cal-hint">点击日期点切换查看对应批次的预测与复盘</div>
    </div>`;
  el.innerHTML = html;
  // 同步折叠状态
  if (calOpen) el.classList.add("open");
  else el.classList.remove("open");
}

function toggleCalendar() {
  calOpen = !calOpen;
  const el = document.getElementById("calendar");
  if (calOpen) el.classList.add("open");
  else el.classList.remove("open");
}

function calShift(dir) {
  calMonth += dir;
  if (calMonth < 0) { calMonth = 11; calYear--; }
  if (calMonth > 11) { calMonth = 0; calYear++; }
  renderCalendar();
}

/* ---------- 当前选中日期 ---------- */
let currentKey = Object.keys(BATCHES).sort().pop() || "";

function selectDate(key) {
  currentKey = key;
  calOpen = false; // 选完自动收起日历
  renderCalendar();
  renderAll();
}

/* ---------- 渲染：预测 ---------- */
function renderPredict(batch) {
  const el = document.getElementById("predict-view");
  if (!el) return; // 复盘页无预测视图，跳过
  const p = batch.predict;

  // 预测清单（含假赛评分列）；严格按场次号 001-00n 排序（2026-08-18 用户要求，不再按开赛时间）
  const byNo = (a, b) => parseInt(a.no) - parseInt(b.no);
  const sorted = p.matches.slice().sort(byNo);
  const riskTag = r => r >= 7 ? `<span class="tag tag-red">🔴 ${r}</span>`
    : r >= 5 ? `<span class="tag tag-orange">🟠 ${r}</span>`
    : `<span class="tag tag-green">🟢 ${r}</span>`;
  // 预测等级 → 颜色类（R337 v2：A+ A A- 绿系 / B+ 蓝 / B 黄 / B- 紫（1正2反·反向比分标*）/ C 红（1正2反·反向比分标*））
  const lvlClass = d => {
    if (d.includes("A+")) return "lvl-aplus";
    if (d.includes("A-")) return "lvl-aminus";
    if (d.includes("A")) return "lvl-a";
    if (d.includes("B+")) return "lvl-bplus";
    if (d.includes("B-")) return "lvl-bminus";
    if (d.includes("B")) return "lvl-b";
    return "lvl-c";
  };
  // 方向文本精简：保留方向+等级，冷门联动只显示"（冷门第N）"，去掉长描述
  const shortDir = d => {
    const s = (d || "").trim();
    return s.replace(/（冷门第(\d+)）?联动[^）]*）|（冷门第(\d+)联动[^）]*）|（冷门第(\d+)）?联动[^）]*）/, (m, a, b, c) => {
      const n = a || b || c;
      return n ? "（冷门第" + n + "）" : m;
    });
  };
  // 已复盘的赛果回填（供预警命中标注使用；预测表本身不再展示赛果——2026-08-23 用户拍板：赛果只在复盘页）
  const reviewOf = {};
  if (batch.review && Array.isArray(batch.review.results)) {
    batch.review.results.forEach(rv => { reviewOf[rv.no] = rv; });
  }
  const rows = sorted.map(m => {
    const revHtml = m.scores.replace(/(\d+-\d+)\*/g, '<span class="rev-score">$1*</span>');
    const revHt = m.ht.replace(/([胜负平]{2})\*/g, '<span class="rev-score">$1*</span>');
    const lv = (m.dir.match(/([ABC])级/) || [])[1] || "";
    return `<tr data-lvl="${lv.toLowerCase()}">
    <td><span class="no-badge">${m.no}</span></td>
    <td><b class="m-team">${m.home} vs ${m.away}</b><br><span class="mt-line"><span class="lg ${m.lg}">${m.league}</span><span class="match-time">🕐 ${m.time || "-"}</span></span></td>
    <td class="${lvlClass(m.dir)}">${shortDir(m.dir)}</td>
    <td class="score-nums">${revHtml}</td>
    <td>${revHt}</td>
    <td>${m.ou}</td>
    <td>${riskTag(m.risk || 0)}</td>
  </tr>`;
  }).join("");

  // 联赛分布（本批按联赛聚合成徽章条，2026-08-23 丰富）
  const lgMap = {};
  sorted.forEach(m => { lgMap[m.league] = (lgMap[m.league] || 0) + 1; });
  const leagueStat = Object.entries(lgMap)
    .sort((a, b) => b[1] - a[1])
    .map(([lg, n]) => `<span class="bo-item bo-lg"><span class="lg lg-sm ${sorted.find(m => m.league === lg).lg}">${lg}</span> <b>×${n}</b></span>`)
    .join("");

  // 通用截断工具：预览 30 字 + 点击展开全文（必须先于所有使用处定义）
  const cut = (s, n) => { s = (s || "").trim(); return s.length > n ? s.slice(0, n) + "…" : s; };

  // 关键信息提取（8/21 用户要求：大段逻辑→简洁关键信息）：取 logic 中 **加粗段**，方向/伤停/天气 优先，前 3 段各截 36 字，｜ 连接；无加粗段退回 30 字截断
  const logicKey = (l) => {
    if (!l) return "-";
    const segs = [];
    const re = /\*\*(.+?)\*\*/g;
    let m;
    while ((m = re.exec(l))) segs.push(m[1]);
    if (!segs.length) return cut(l, 30);
    const pri = s => s.indexOf("方向") === 0 ? 0 : s.indexOf("伤停") === 0 ? 1 : s.indexOf("天气") === 0 ? 2 : 3;
    const uniq = segs.filter((s, i) => segs.indexOf(s) === i);
    uniq.sort((a, b) => pri(a) - pri(b));
    return uniq.slice(0, 3).map(s => cut(s, 36)).join(" ｜ ");
  };
  // 全文加粗渲染：**X** → <b>X</b>，展开后重点一目了然
  const logicHtml = (l) => (l || "").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");

  // 冷门风险（数据全比赛覆盖；展示仅过滤"低"等级——比赛多时全显示太乱，2026-08-22 用户拍板，与 0-0/7+ 预警一致；按等级从高到低排序，逻辑列预览 30 字 + 点击展开）
  const lvW = { "较高": 4, "中等偏高": 3, "中等": 2, "低": 1 };
  // 已复盘的预警 → 命中标注（2026-08-23 丰富：预测页预警行直接看验证结果）
  const resDir = s => { const m = (s || "").match(/(\d+)-(\d+)/); if (!m) return ""; const h = +m[1], a = +m[2]; return h > a ? "主胜" : h < a ? "客胜" : "平局"; };
  const coldVerifyOf = c => {
    const rv = reviewOf[c.no];
    if (!rv) return "";
    const actual = resDir(rv.score);
    const hit = actual === c.dir;
    return `<span class="rv-flag ${hit ? "rv-hit" : "rv-miss"}" style="margin-left:8px">${hit ? "✅ 命中" : "未触发"}</span>`;
  };
  const coldRows = (p.coldRisk || [])
    .filter(c => c.lvTxt !== "低")
    .slice()
    .sort((a, b) => (lvW[b.lvTxt] || 0) - (lvW[a.lvTxt] || 0))
    .map(c => `<tr>
    <td>${c.rank}</td><td>${c.no} ${c.teams}${coldVerifyOf(c)}</td><td>${shortDir(c.dir)}</td>
    <td><span class="tag ${c.lv}">${c.lvTxt}</span></td>
    <td><details>
      <summary>${cut(c.logic || "-", 30)}</summary>
      <div style="margin-top:6px;font-size:12.5px;color:var(--sub);line-height:1.8">${logicHtml(c.logic)}</div>
    </details></td>
  </tr>`).join("");

  // 高价值预警：只显示中等及以上（2026-08-22 晚用户拍板：低概率不显示——与冷门风险/7+ 一致；评级规则=4 冷门形态：胜平/负平=实力接近场高概率剧本→中等（但按形态成立概率评估：先进球方进球能力弱/追平方追平能力弱→降低），胜负/负胜=冷门低概率→低（德比/避雷/防线残阵等强剧本因素→中等）；逻辑列预览 30 字 + 点击展开
  // 半全场形态命中标注（2026-08-23 丰富）
  const htOfScore = s => {
    const m = (s || "").match(/^(\d+)-(\d+)（(\d+)-(\d+)）?/);
    if (!m) return "";
    const f = m[1] > m[2] ? "胜" : m[1] < m[2] ? "负" : "平";
    const hm = m[3] && m[4] ? (m[3] > m[4] ? "胜" : m[3] < m[4] ? "负" : "平") : "";
    return hm + f;
  };
  const alertVerifyOf = a => {
    const rv = reviewOf[a.no];
    if (!rv) return "";
    const hit = htOfScore(rv.score) === a.script;
    return `<span class="rv-flag ${hit ? "rv-hit" : "rv-miss"}" style="margin-left:8px">${hit ? "✅ 命中" : "未触发"}</span>`;
  };
  const alertRows = (p.alerts || [])
    .filter(a => a.lvTxt !== "低")
    .slice()
    .sort((a, b) => (lvW[b.lvTxt] || 0) - (lvW[a.lvTxt] || 0))
    .map(a => `<tr>
    <td>${a.script}</td><td>${a.no} ${a.teams}${alertVerifyOf(a)}</td>
    <td><span class="tag ${a.lv}">${a.lvTxt}</span></td>
    <td><details>
      <summary>${cut(a.logic, 30) || "-"}</summary>
      <div style="margin-top:6px;font-size:12.5px;color:var(--sub);line-height:1.8">${logicHtml(a.logic)}</div>
    </details></td>
  </tr>`).join("");

  // 0-0 预警已废弃（2026-08-22 用户拍板：33 条 0 命中系统性反向，该大球的场全在预警 0-0——网页卡片移除，数据保留历史）

  // 7+ 球预警：总进球 ≥7 的极端大球，只显示中等偏低及以上等级（全部展示，不截断）
  const bigVerifyOf = z => {
    const rv = reviewOf[z.no];
    if (!rv) return "";
    const sc = rv.score.match(/(\d+)-(\d+)/);
    const hit = sc && (+sc[1] + +sc[2] >= 7);
    return `<span class="rv-flag ${hit ? "rv-hit" : "rv-miss"}" style="margin-left:8px">${hit ? "✅ 命中" : "未触发"}</span>`;
  };
  const bigRows = (p.bigSeven || [])
    .filter(z => z.lvTxt !== "低")
    .slice()
    .sort((a, z) => z.p - a.p)
    .map(z => `<tr>
    <td>${z.no} ${z.teams}${bigVerifyOf(z)}</td>
    <td><div class="prob-bar"><div class="prob-track"><div class="prob-fill" style="width:${z.p}%"></div></div><span class="prob-txt num">${z.p}%</span></div></td>
    <td><span class="tag ${z.lv}">${z.lvTxt}</span></td>
  </tr>`).join("");

  // 核心逻辑速览：自动提取关键信息（方向/伤停/天气）预览 + 点击展开全文（加粗渲染）
  const logicRows = sorted.map(m => `<tr>
    <td><span class="no-badge">${m.no}</span></td>
    <td><b class="m-team">${m.home} vs ${m.away}</b>${m.time ? `<br><span class="mt-line"><span class="lg ${m.lg}">${m.league}</span><span class="match-time">🕐 ${m.time}</span></span>` : ""}</td>
    <td><details>
      <summary>${logicKey(m.logic)}</summary>
      <div style="margin-top:6px;font-size:12.5px;color:var(--sub);line-height:1.8">${logicHtml(m.logic)}</div>
    </details></td>
  </tr>`).join("");

  el.innerHTML = `
    <div class="card">
      <h2><span class="icon">📋</span> 一、完整预测清单（${batch.title}）${batch.updated ? `<span class="mt-line" style="font-size:12px;color:var(--sub);margin-left:10px;">🕐 更新于 ${batch.updated}</span>` : ""}
        <button class="batch-nav" style="margin-left:auto" onclick="copyBatchText('${currentKey}', this)" title="复制本批全部预测为文本">📄 复制清单</button>
      </h2>
      <div class="batch-overview">
        <span class="bo-item">⚽ 本批 <b>${sorted.length} 场</b></span>
        <span class="bo-item">🌡️ 冷门预警 <b>${(p.coldRisk || []).length} 场</b></span>
        ${leagueStat}
      </div>
      <div class="lvl-filter">
        <button class="lvl-pill lvl-all active" data-f="all" onclick="filterLvl(this,'all')"><b>全部</b><i>${sorted.length} 场</i></button>
        <button class="lvl-pill lvl-a" data-f="a" onclick="filterLvl(this,'a')"><b>A 高</b><i>3 正路 · ${sorted.filter(m => /A级/.test(m.dir)).length} 场</i></button>
        <button class="lvl-pill lvl-b" data-f="b" onclick="filterLvl(this,'b')"><b>B 中</b><i>2 正 1 反 · ${sorted.filter(m => /B级/.test(m.dir)).length} 场</i></button>
        <button class="lvl-pill lvl-c" data-f="c" onclick="filterLvl(this,'c')"><b>C 低</b><i>1 正 2 反 · ${sorted.filter(m => /C级/.test(m.dir)).length} 场</i></button>
      </div>
      <div class="table-wrap"><table class="batch-table">
        <thead><tr><th>场次</th><th>对阵（北京时间）</th><th>方向</th><th>比分 TOP3</th><th>半全场 TOP3</th><th>总进球</th><th>假赛分</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <h2><span class="icon">🌡️</span> 冷门风险（${(p.coldRisk || []).length} 场全量）</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>排名</th><th>场次</th><th>冷门方向</th><th>风险等级</th><th>核心逻辑</th></tr></thead>
        <tbody>${coldRows}</tbody>
      </table></div>
      <div class="note">仅显示中等及以上等级（数据覆盖全部比赛），按等级从高到低排序。</div>
    </div>

    <div class="card">
      <h2><span class="icon">🚨</span> 高价值预警</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>剧本</th><th>场次</th><th>概率</th><th>核心逻辑</th></tr></thead>
        <tbody>${alertRows}</tbody>
      </table></div>
      <div class="note">全量展示按概率排序（2026-08-22 用户拍板：平胜/平负=强队半场 0-0 后破门高概率→中等+；胜负/负胜=弱队先进被逆转/爆冷冷门→低，保留展示）。</div>
    </div>

    <div class="card">
      <h2><span class="icon">🎆</span> 7+ 球预警（${(p.bigSeven || []).length} 场全量）</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>7+ 球概率</th><th>等级</th></tr></thead>
        <tbody>${bigRows}</tbody>
      </table></div>
      <div class="note">仅显示中等偏低及以上等级（总进球 ≥7，如 4-3/5-2/6-1，R346），全量展示按概率排序。</div>
    </div>

    <div class="card">
      <h2><span class="icon">💡</span>
        <button class="batch-nav h2-btn" id="logicToggleBtn" onclick="toggleAllLogic(this)" title="展开/折叠全部逻辑">🔽 展开全部</button>
        <span>各场核心逻辑</span> <span class="hint">关键信息预览，点击展开全文</span>
      </h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>对阵</th><th>核心逻辑</th></tr></thead>
        <tbody>${logicRows}</tbody>
      </table></div>
    </div>`;
}

/* ---------- 等级筛选（2026-08-22 新增：批次概览+按 A/B/C 过滤预测表） ---------- */
function filterLvl(btn, lvl) {
  document.querySelectorAll(".lvl-filter button").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  document.querySelectorAll("#predict-view .batch-table tbody tr").forEach(tr => {
    const l = tr.getAttribute("data-lvl") || "";
    tr.style.display = (lvl === "all" || l === lvl) ? "" : "none";
  });
}

/* 核心逻辑全体展开/折叠（2026-08-23：单按钮切换，位置贴标题左侧） */
function toggleAllLogic(btn) {
  const card = btn.closest(".card");
  if (!card) return;
  const all = Array.from(card.querySelectorAll("details"));
  const anyClosed = all.some(d => !d.open);
  all.forEach(d => { d.open = anyClosed; });
  btn.textContent = anyClosed ? "🔼 折叠全部" : "🔽 展开全部";
}

/* ---------- 渲染：复盘 ---------- */
function renderReview(batch) {
  const el = document.getElementById("review-view");
  if (!el) return; // 预测页无复盘视图，跳过
  const r = batch.review;
  if (!r || (!batch.reviewed && (!r.results || r.results.length === 0))) {
    el.innerHTML = `<div class="card"><h2><span class="icon">⏳</span> 复盘未开始</h2>
      <div class="note">该批次预测已发布，比赛结束后复盘数据将在此显示。</div></div>`;
    return;
  }
  const okT = `<span class="tag tag-green">✅</span>`, noT = `<span class="tag tag-red">❌</span>`;
  const dTag = d => d === "ok" ? okT : noT;

  // 工具：赛果串 → 半全场；命中 TOP 几；预警命中判定
  const htFromScore = s => {
    const m = s.match(/^(\d+)-(\d+)（(\d+)-(\d+)）/);
    if (!m) return "";
    const f = m[1] > m[2] ? "胜" : m[1] < m[2] ? "负" : "平";
    const h = m[3] > m[4] ? "胜" : m[3] < m[4] ? "负" : "平";
    return h + f;
  };
  const topOf = (actual, listStr) => {
    // 忽略反向项星号（0-1* 命中实际 0-1 也应计入 TOP N，2026-08-23 修复：011 诺丁汉 0-1* 命中未显示）
    const items = (listStr || "").split("/").map(s => s.trim().replace(/\*$/, ""));
    const i = items.indexOf(actual);
    return i >= 0 ? i + 1 : null;
  };
  const hitTag = top => top ? `<span class="tag tag-green">✅ TOP${top}</span>` : noT;
  const alertOf = m => {
    const actualHt = htFromScore(m.score);
    const scoreMain = m.score.split("（")[0];
    if (batch.alerts) {
      const a = batch.alerts.find(x => x.no === m.no);
      if (a && a.script === actualHt) return `🎯 ${a.script}（${a.lvTxt}）`;
    }
    return "";
  };

  const totalN = batch.predict.matches.length;
  const confirmedN = r.results.length;
  // 控分排查结论仅本地保留（合规），网页只展示演戏排查部分
  const cleanTxt = t => (t || "").split("控分排查：")[0].trim();
  // 本批次总进球（ou）命中：预测总进球区间 vs 实际进球数
  let ouN = 0, ouH = 0;
  r.results.forEach(m => {
    const pm = batch.predict.matches.find(x => x.no === m.no);
    if (!pm || !pm.ou) return;
    const sc = m.score.match(/(\d+)-(\d+)/);
    if (!sc) return;
    const mm = pm.ou.match(/(\d+)[·.x×](\d+)/);
    if (!mm) return;
    ouN++;
    const tg = +sc[1] + +sc[2];
    // 总进球 = 两个离散选项（如 1·2 = 1球或2球），命中 = 实际总进球等于任一选项
    if (tg === +mm[1] || tg === +mm[2]) ouH++;
  });
  const ouPct = ouN ? Math.round(100 * ouH / ouN) + "%" : "—";
  const ouKpi = `<div class="kpi" style="background:rgba(217,119,6,.08);border-color:#d97706"><div class="num">${ouH}/${ouN} <span style="font-size:12px">${ouPct}</span></div><div class="lbl">⚽ 总进球命中</div></div>`;
  // 部分复盘 KPI：统一 x/y + 百分比（2026-08-23 用户要求：与总进球同款）
  const statCell = (hit, total) => total ? `${hit}/${total} <span style="font-size:12px">${Math.round(100 * hit / total)}%</span>` : `0/0 <span style="font-size:12px">—</span>`;
  const statusTag = batch.reviewed
    ? `<span class="tag tag-green">完整复盘</span>`
    : `<span class="tag tag-yellow">部分复盘（已确认 ${confirmedN}/${totalN} 场）</span>`;
  const kpiHtml = batch.reviewed ? `
        <div class="kpi"><div class="num">${batch.stats.dir}</div><div class="lbl">方向命中率 ${batch.stats.dirPct}</div></div>
        <div class="kpi"><div class="num">${batch.stats.score}</div><div class="lbl">比分 TOP3 ${batch.stats.scorePct}</div></div>
        <div class="kpi"><div class="num">${batch.stats.ht}</div><div class="lbl">半全场 TOP3 ${batch.stats.htPct}</div></div>
        ${ouKpi}` : `
        <div class="kpi"><div class="num">${confirmedN}/${totalN}</div><div class="lbl">已确认场次</div></div>
        <div class="kpi"><div class="num">${statCell(r.results.filter(m => m.d === "ok").length, confirmedN)}</div><div class="lbl">方向已命中</div></div>
        <div class="kpi"><div class="num">${statCell(r.results.filter(m => m.s === "ok").length, confirmedN)}</div><div class="lbl">比分已命中</div></div>
        <div class="kpi"><div class="num">${statCell(r.results.filter(m => m.h === "ok").length, confirmedN)}</div><div class="lbl">半全场已命中</div></div>
        ${ouKpi}`;

  const rows = r.results.slice().sort((a, b) => parseInt(a.no) - parseInt(b.no)).map(m => {
    const pm = batch.predict.matches.find(x => x.no === m.no);
    const scoreMain = m.score.split("（")[0];
    const sTop = pm ? topOf(scoreMain, pm.scores) : null;
    const hTop = pm ? topOf(htFromScore(m.score), pm.ht) : null;
    const hCell = hTop ? hitTag(hTop) : (m.h === "ok" ? okT : noT); // 无半场数据时按 h 判定
    const aw = alertOf(m);
    // 总进球命中：预测 ou 区间 vs 实际进球数
    const ouCell = () => {
      const pm = batch.predict.matches.find(x => x.no === m.no);
      if (!pm || !pm.ou) return `<span class="tag tag-gray">—</span>`;
      const sc = m.score.match(/(\d+)-(\d+)/);
      if (!sc) return `<span class="tag tag-gray">—</span>`;
      const mm = pm.ou.match(/(\d+)[·.x×](\d+)/);
      if (!mm) return `<span class="tag tag-gray">—</span>`;
      const tg = +sc[1] + +sc[2];
      // 总进球 = 两个离散选项（如 1·2 = 1球或2球），命中 = 实际总进球等于任一选项
      const hit = tg === +mm[1] || tg === +mm[2];
      const range = pm.ou.replace("总进球 ", "");
      return hit
        ? `<span class="tag tag-green">${range} ✅</span>`
        : `<span class="tag tag-red">${range} ❌ <span style="opacity:.8">实${tg}球</span></span>`;
    };
    // 对阵列：与赛前一致的两行排版
    const nms = (m.teams || "").split(" vs ");
    const homeNm = nms[0] || "", awayNm = nms[1] || "";
    return `<tr class="${m.d === "ok" ? "ok-row" : ""}">
      <td><span class="no-badge">${m.no}</span></td>
      <td><b class="m-team">${homeNm} vs ${awayNm}</b><br><span class="mt-line"><span class="lg ${m.lg}">${m.league}</span>${pm && pm.time ? `<span class="match-time">🕐 ${pm.time}</span>` : ""}</span></td>
      <td><b>${m.score}</b></td>
      <td>${dTag(m.d)}</td>
      <td>${hitTag(sTop)}</td>
      <td>${hCell}</td>
      <td>${ouCell()}</td>
    </tr>`;
  }).join("");

  // 关键场次技术统计：默认只显示信号徽章，点击展开完整统计与解读（游客友好）
  const evRows = r.evidence.map(e => {
    // evidence.teams 形如 "阿拉维斯 3-0 赫塔费" → 拆分对阵（与赛前统一排版）
    const em = (e.teams || "").match(/^(.*?)\s+\d+-\d+\s+(.*)$/);
    const evHome = em ? em[1] : (e.teams || "");
    const evAway = em ? em[2] : "";
    return `<tr>
    <td><b>${e.no}</b> ${evHome} vs ${evAway}<br><span class="mt-line"><span class="lg ${e.lg}">${e.league}</span></span></td>
    <td><details class="ev-detail">
      <summary><span class="tag ${e.sc === "danger" ? "tag-red" : e.sc === "watch" ? "tag-yellow" : "tag-green"}">${e.signal}</span> <span style="font-size:12px;color:var(--sub)">点击展开</span></summary>
      <div style="margin-top:8px;font-size:12.5px;color:var(--sub);line-height:1.8">${e.stats || "—"}<br><br>${cleanTxt(e.txt) || ""}</div>
    </details></td>
  </tr>`;
  }).join("");

  el.innerHTML = `
    <div class="card">
      <h2><span class="icon">📊</span> 批次命中统计（${batch.title}）${statusTag}</h2>
      <div class="kpi-row">
        ${kpiHtml}
      </div>
    </div>

    <div class="card">
      <h2><span class="icon">✅</span> 已核验场次 <span class="hint">点击表头可排序</span></h2>
      <div class="table-wrap"><table data-sort>
        <thead><tr>
          <th data-sortable>场次</th><th>对阵</th><th data-sortable>赛果（半场）</th>
          <th data-sortable>方向</th><th data-sortable>比分</th><th data-sortable>半全场</th><th data-sortable>总进球</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <h2><span class="icon">🔎</span>
        <button class="batch-nav h2-btn" onclick="toggleEvDetails(this)" title="展开/折叠全部技术统计">🔽 展开全部</button>
        <span>关键场次技术统计（演戏信号实证）</span><span class="hint">点击信号标签展开完整数据</span>
      </h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>演戏信号（点击展开）</th></tr></thead>
        <tbody>${evRows}</tbody>
      </table></div>
    </div>`;
}

/* ---------- 站点总览统计条 + 批次趋势图 ---------- */
/* 技术统计全局展开/折叠（2026-08-23 合并为单按钮切换） */
function toggleEvDetails(btn) {
  const card = btn.closest(".card");
  const all = card ? Array.from(card.querySelectorAll(".ev-detail")) : Array.from(document.querySelectorAll(".ev-detail"));
  const anyClosed = all.some(d => !d.open);
  all.forEach(d => { d.open = anyClosed; });
  btn.textContent = anyClosed ? "🔼 折叠全部" : "🔽 展开全部";
}

/* 复制批次预测清单为纯文本（分享/对比用） */
function copyBatchText(key, btn) {
  const b = BATCHES[key];
  if (!b || !b.predict || !b.predict.matches) return;
  const byNo = (a, b) => parseInt(a.no) - parseInt(b.no);
  const sorted = b.predict.matches.slice().sort(byNo);
  const lines = [`${b.title}（${b.model}）`, `更新：${b.updated || "-"}`, ""];
  sorted.forEach(m => {
    lines.push(`[${m.no}] ${m.home} vs ${m.away}（${m.league}${m.time ? " " + m.time : ""}）`);
    lines.push(`  方向：${shortDir(m.dir)}`);
    lines.push(`  比分：${m.scores}`);
    lines.push(`  半全场：${m.ht}`);
    lines.push(`  总进球：${m.ou}`);
    lines.push("");
  });
  const txt = lines.join("\n");
  // 复制反馈（点击按钮/任意反馈元素统一：传入 btn，无 btn 时查 up 链）
  const done = () => {
    const t = btn || document.querySelector(".batch-nav[onclick*='copyBatchText']");
    if (t) { const o = t.textContent; t.textContent = "✅ 已复制"; setTimeout(() => t.textContent = o, 1600); }
  };
  // clipboard API 优先（https 必需），失败降级 execCommand；均无反馈时 alert（仅异常兜底）
  const fallback = () => {
    try {
      const ta = document.createElement("textarea");
      ta.value = txt; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      if (ok) done(); else throw new Error("execCommand failed");
    } catch (e) { alert("复制失败，请手动全选复制"); }
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(txt).then(done).catch(fallback);
  } else {
    fallback();
  }
}
function renderSiteStats() {
  const el = document.getElementById("site-stats");
  if (!el) return;
  const keys = Object.keys(BATCHES).sort();
  const totalBatches = keys.length;
  const reviewed = keys.filter(k => BATCHES[k].reviewed).length;
  let totalMatches = 0, dirHit = 0;
  keys.forEach(k => {
    const b = BATCHES[k];
    // 已复盘判定：review.results 非空（2026-08-23 修复：部分复盘批次 reviewed=false 仍计入）
    if (b.review && b.review.results && b.review.results.length) {
      b.review.results.forEach(m => { totalMatches++; if (m.d === "ok") dirHit++; });
    }
  });
  const dirPct = totalMatches ? Math.round(100 * dirHit / totalMatches) + "%" : "—";
  el.innerHTML = `
    <div class="site-stats">
      <div class="site-stat"><span class="ss-num">${totalBatches}</span><span class="ss-lbl">总批次</span></div>
      <div class="site-stat"><span class="ss-num">${totalMatches}</span><span class="ss-lbl">已复盘场次</span></div>
      <div class="site-stat"><span class="ss-num">${dirPct}</span><span class="ss-lbl">批次方向命中</span></div>
      <div class="site-stat"><span class="ss-num">${GLOBAL_STATS.dirPct}</span><span class="ss-lbl">累计方向命中</span></div>
      <div class="site-stat"><span class="ss-num">${GLOBAL_STATS.ouPct || "-"}</span><span class="ss-lbl">累计总进球命中${GLOBAL_STATS.ouNote ? "（" + GLOBAL_STATS.ouNote + "）" : ""}</span></div>
      <div class="site-stat"><span class="ss-num">${reviewed}/${totalBatches}</span><span class="ss-lbl">已复盘批次</span></div>
      <div class="site-stat"><span class="ss-num">${GLOBAL_STATS.updated.slice(5)}</span><span class="ss-lbl">最后更新</span></div>
    </div>`;
}

/* ---------- 预测级别表现分析 ---------- */
function levelAnalysis(b) {
  // 方向字符串 → 细分档位（V10.31：A+ A A- B+ B C，B- 并入 C）
  const grade = d => {
    if (d.includes("A+")) return "A+";
    if (d.includes("A-")) return "A-";
    if (d.includes("A")) return "A";
    if (d.includes("B+")) return "B+";
    if (d.includes("B-")) return "C"; // B- 并入 C
    if (d.includes("B")) return "B";
    return "C";
  };
  const res = { "A+": { t: 0, h: 0 }, "A": { t: 0, h: 0 }, "A-": { t: 0, h: 0 }, "B+": { t: 0, h: 0 }, "B": { t: 0, h: 0 }, "C": { t: 0, h: 0 } };
  b.review.results.forEach(m => {
    const pm = b.predict.matches.find(x => x.no === m.no);
    if (!pm) return;
    const g = grade(pm.dir);
    res[g].t++;
    if (m.d === "ok") res[g].h++;
  });
  return res;
}

function renderLevelStats() {
  const el = document.getElementById("level-stats");
  if (!el || !BATCHES[currentKey] || !BATCHES[currentKey].reviewed) return;
  const b = BATCHES[currentKey];
  const res = levelAnalysis(b);
  const row = g => {
    const r = res[g];
    const pct = r.t ? Math.round(100 * r.h / r.t) : 0;
    const cls = { "A+": "lvl-aplus", "A": "lvl-a", "A-": "lvl-aminus", "B+": "lvl-bplus", "B": "lvl-b", "C": "lvl-c" }[g];
    return `<tr><td class="num"><span class="${cls}" style="padding:2px 10px">${g}</span></td><td class="num">${r.h}/${r.t}</td><td><div class="prob-bar"><div class="prob-track"><div class="prob-fill" style="width:${pct}%"></div></div><span class="prob-txt num">${pct}%</span></div></td></tr>`;
  };
  el.innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>预测级别</th><th>方向命中</th><th>命中率</th></tr></thead>
      <tbody>${row("A+")}${row("A")}${row("A-")}${row("B+")}${row("B")}${row("C")}</tbody>
    </table></div>
    <div class="note">A 高置信（3正路）｜ B 中置信（2正1反，方向双选）｜ C 低置信（1正2反，方向反向倾斜）——ABC 三档制（2026-08-18 简化，A+/A-/B+/B- 全部并入）。用于检验"高置信更可靠"假设。</div>`;
}

/* ---------- 联赛表现统计（V10.36：方向/比分/半全场三指标） ---------- */
function renderLeagueStats() {
  const el = document.getElementById("league-stats");
  if (!el || !BATCHES[currentKey] || !BATCHES[currentKey].reviewed) return;
  const b = BATCHES[currentKey];
  const map = {};
  b.review.results.forEach(m => {
    const pm = b.predict.matches.find(x => x.no === m.no);
    const lg = (pm && pm.league) || m.league || "其他";
    if (!map[lg]) map[lg] = { t: 0, d: 0, s: 0, h: 0 };
    map[lg].t++;
    if (m.d === "ok") map[lg].d++;
    if (m.s === "ok") map[lg].s++;
    if (m.h === "ok") map[lg].h++;
  });
  const cell = (ok, t) => `${ok}/${t} <span style="font-size:11px;color:var(--sub)">(${Math.round(100 * ok / Math.max(1, t))}%)</span>`;
  const rows = Object.keys(map).sort((a, z) => map[z].t - map[a].t).map(lg => {
    const r = map[lg];
    return `<tr>
      <td>${lg}</td><td class="num">${r.t}</td>
      <td class="num">${cell(r.d, r.t)}</td>
      <td class="num">${cell(r.s, r.t)}</td>
      <td class="num">${cell(r.h, r.t)}</td>
    </tr>`;
  }).join("");
  el.innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>联赛</th><th>场次</th><th>方向</th><th>比分</th><th>半全场</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
}

/* ---------- 冷门预警验证 ---------- */
function resultDir(score) {
  // score 形如 "2-1（0-2）" → 主胜/平/主负
  const m = score.match(/(\d+)-(\d+)/);
  if (!m) return "—";
  const h = +m[1], a = +m[2];
  return h > a ? "主胜" : h < a ? "客胜" : "平局";
}
function renderColdVerify() {
  const el = document.getElementById("cold-verify");
  if (!el || !BATCHES[currentKey] || !BATCHES[currentKey].reviewed) return;
  const b = BATCHES[currentKey];
  const hit = [], miss = [];
  b.predict.coldRisk.forEach(c => {
    const m = b.review.results.find(x => x.no === c.no);
    if (!m) return;
    const actual = resultDir(m.score);
    const ok = actual === c.dir;
    (ok ? hit : miss).push({ rank: c.rank, no: c.no, teams: c.teams, pred: c.dir, actual, lv: c.lv, lvTxt: c.lvTxt, ok });
  });
  const row = c => `<tr>
    <td>${c.rank}</td><td>${c.no} ${c.teams}</td>
    <td>${c.pred}</td><td>${c.actual}</td>
    <td>${c.ok ? `<span class="tag tag-green">✅ 命中</span>` : `<span class="tag tag-gray">未触发</span>`}</td>
  </tr>`;
  el.innerHTML = `
    <div class="lead">冷门预警验证：预测方向与实际赛果一致 = 爆冷命中。${hit.length}/${b.predict.coldRisk.length} 场预警命中。</div>
    <div class="table-wrap"><table>
      <thead><tr><th>排名</th><th>场次</th><th>预警方向</th><th>实际</th><th>验证</th></tr></thead>
      <tbody>${hit.map(row).join("")}${miss.map(row).join("")}</tbody>
    </table></div>`;
}

/* ---------- 表格排序 ---------- */
function initSortable() {
  document.querySelectorAll("table[data-sort]").forEach(tbl => {
    const ths = tbl.querySelectorAll("thead th");
    ths.forEach((th, ci) => {
      if (!th.hasAttribute("data-sortable")) return;
      th.style.cursor = "pointer";
      th.title = "点击排序";
      th.addEventListener("click", () => {
        const tbody = tbl.tBodies[0];
        const rows = Array.from(tbody.rows);
        const dir = tbl._sortDir === "asc" ? "desc" : "asc";
        tbl._sortDir = dir;
        ths.forEach(x => x.classList.remove("sort-on", "sort-asc", "sort-desc"));
        th.classList.add("sort-on", dir === "asc" ? "sort-asc" : "sort-desc");
        rows.sort((a, z) => {
          const av = a.cells[ci].textContent.trim();
          const zv = z.cells[ci].textContent.trim();
          const an = parseFloat(av.replace(/[^\d.-]/g, "")) || 0;
          const zn = parseFloat(zv.replace(/[^\d.-]/g, "")) || 0;
          if (an !== zn) return dir === "asc" ? an - zn : zn - an;
          return dir === "asc" ? av.localeCompare(zv, "zh") : zv.localeCompare(av, "zh");
        });
        rows.forEach(r => tbody.appendChild(r));
      });
    });
  });
}

/* ---------- 全局统计（近7日 + 预警命中率） + 批次头 ---------- */
function renderGlobal(mode) {
  const el = document.getElementById("global-kpi");
  if (!el) return;
  const pct = (h, n) => n ? Math.round(100 * h / n) + "%" : "—";
  const pctN = (h, n) => n ? Math.round(100 * h / n) : 0;
  const keys = Object.keys(BATCHES).sort();
  const weekStart = fmtKey(new Date(Date.now() - 7 * 864e5));
  const isAll = mode === "all"; // 累计全量口径（2026-08-22 新增切换）

  // SVG 环形（专业仪表盘风格）
  const ring = (id, p, size) => {
    const st = 9, r = (size - st) / 2, c = 2 * Math.PI * r;
    const off = c * (1 - Math.min(100, p) / 100);
    return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true">
      <defs><linearGradient id="${id}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="var(--primary)"/><stop offset="100%" stop-color="var(--gold)"/>
      </linearGradient></defs>
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="var(--thead-bg)" stroke-width="${st}"/>
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="url(#${id})" stroke-width="${st}"
        stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${off}" transform="rotate(-90 ${size / 2} ${size / 2})"/>
    </svg>`;
  };
  const kpiRing = (id, p, hit, total, label) => `
    <div class="kpi ring-kpi">
      <div class="ring-wrap">${ring(id, p, 92)}
        <div class="ring-num"><b>${p}%</b><span>${hit}/${total}</span></div>
      </div>
      <div class="lbl">${label}</div>
    </div>`;

  // 近 7 日三指标 + 近 7 日总进球/预警命中（全部统一近 7 日口径）
  const week = { n: 0, d: 0, s: 0, h: 0 };
  const ou = { n: 0, h: 0 }, zz = { n: 0, h: 0 }, bs = { n: 0, h: 0 }, aw = { n: 0, h: 0 };
  keys.forEach(k => {
    const b = BATCHES[k];
    if (!b.review || !b.review.results) return;
    if (!isAll && k < weekStart) return; // 近 7 日口径；累计全量不过滤
    b.review.results.forEach(m => {
      week.n++; if (m.d === "ok") week.d++; if (m.s === "ok") week.s++; if (m.h === "ok") week.h++;
      const pm = b.predict && b.predict.matches.find(x => x.no === m.no);
      const sc = m.score.match(/(\d+)-(\d+)/);
      // 总进球
      if (pm && pm.ou && sc) {
        const mm = pm.ou.match(/(\d+)[·.x×](\d+)/);
        if (mm) { ou.n++; const tg = +sc[1] + +sc[2]; if (tg === +mm[1] || tg === +mm[2]) ou.h++; }
      }
      if (!sc) return;
      // 0-0 预警
      const scoreMain = m.score.split("（")[0];
      const z = (b.zeroZero || []).find(x => x.no === m.no);
      if (z) { zz.n++; if (scoreMain === "0-0") zz.h++; }
      // 7+ 预警
      const b7 = (b.bigSeven || []).find(x => x.no === m.no);
      if (b7) { bs.n++; if (+sc[1] + +sc[2] >= 7) bs.h++; }
      // 高价值预警（半全场剧本）
      if (b.alerts) {
        const a = b.alerts.find(x => x.no === m.no);
        if (a) {
          aw.n++;
          const f = sc[1] > sc[2] ? "胜" : sc[1] < sc[2] ? "负" : "平";
          const hm = m.score.match(/（(\d+)-(\d+)）/);
          const hh = hm ? (hm[1] > hm[2] ? "胜" : hm[1] < hm[2] ? "负" : "平") : "";
          if (a.script === hh + f) aw.h++;
        }
      }
    });
  });

  // KPI 数值：无评估数据时显示「—」（0/0 无信息量，2026-08-23 优化）
  const kpiTag = (h, n) => n ? `${h}/${n} <span style="font-size:12px">${pct(h, n)}</span>` : `<span style="font-size:20px;opacity:.55">—</span>`;
  el.innerHTML = `
    <div class="global-dash">
      <div class="g-tabs">
        <span class="g-tabs-lbl">📊 口径</span>
        <div class="kpi-tabs">
          <button class="${isAll ? "" : "active"}" onclick="renderGlobal('week')">近 7 日</button>
          <button class="${isAll ? "active" : ""}" onclick="renderGlobal('all')">累计全量</button>
        </div>
      </div>
      <div class="g-stats g-4">
        <div class="kpi"><div class="num">${kpiTag(week.d, week.n)}</div><div class="lbl">🧭 方向命中${isAll ? "" : "（近7日）"}</div></div>
        <div class="kpi"><div class="num">${kpiTag(week.s, week.n)}</div><div class="lbl">🎯 比分 TOP3${isAll ? "" : "（近7日）"}</div></div>
        <div class="kpi"><div class="num">${kpiTag(week.h, week.n)}</div><div class="lbl">⏱️ 半全场 TOP3${isAll ? "" : "（近7日）"}</div></div>
        <div class="kpi"><div class="num">${kpiTag(ou.h, ou.n)}</div><div class="lbl">⚽ 总进球命中${isAll ? "" : "（近7日）"}</div></div>
      </div>
    </div>`;
}

function renderBatchHeader() {
  const b = BATCHES[currentKey];
  const el = document.getElementById("batch-header");
  if (el && b) {
    // 上一批/下一批快速导航
    const keys = Object.keys(BATCHES).sort();
    const idx = keys.indexOf(currentKey);
    const prevK = idx > 0 ? keys[idx - 1] : null;
    const nextK = idx < keys.length - 1 ? keys[idx + 1] : null;
    // 更新日志（收纳按钮+浮层）：聚合本批次所有场次 updates，按时间倒序；主清单直接显示最新版
    const ms = (b.predict && b.predict.matches) || [];
    const logItems = ms
      .flatMap(m => (Array.isArray(m.updates) && m.updates.length
        ? m.updates.map(u => ({ no: m.no, teams: `${m.home} vs ${m.away}`, t: u.t, x: u.x })) : []))
      .sort((a, z) => (a.t < z.t ? 1 : a.t > z.t ? -1 : 0));
    const updBtn = `<button class="updlog-btn${logItems.length ? " has-upd" : ""}" onclick="toggleUpdLog()" title="点击展开/收起更新日志">📜 更新日志${logItems.length ? ` <b>${logItems.length}</b>` : ""}</button>`;
    const updDrop = `<div class="updlog-dropdown" id="updlog-dropdown" style="display:none">
      <div class="updlog-head">📜 更新日志 <span class="hint">主清单直接显示最新版，此处记录变更明细（旧值→新值）</span></div>
      ${logItems.length ? `<div class="updlog-list">${logItems.map(it => `<div class="updlog-item">
        <span class="updlog-time">${it.t}</span>
        <span class="updlog-no">${it.no}</span>
        <span class="updlog-teams">${it.teams}</span>
        <span class="updlog-x">${it.x}</span>
      </div>`).join("")}</div>`
      : `<div class="note" style="margin:0">暂无更新——开赛前若有首发/伤停调整，更新版将直接覆盖主清单对应行，变更记录在此。</div>`}
    </div>`;
    el.innerHTML = `
      <div style="position:relative">
        <button class="batch-nav" onclick="selectDate('${prevK}')" ${prevK ? "" : "disabled"} title="${prevK ? fmtDate(prevK) : ""}">‹ 上批</button>
        <span class="badge badge-soft">📅 ${fmtDate(currentKey)}</span>
        <span class="badge badge-solid">${b.title}</span>
        ${b.updated ? `<span class="badge badge-soft">🕐 更新 ${b.updated}</span>` : ""}
        ${updBtn}
        <span class="badge badge-soft" style="margin-left:auto">模型 <b style="color:var(--primary)">${b.model}</b></span>
        ${b.reviewed ? `<span class="badge badge-solid" style="background:linear-gradient(135deg,#15803d,#22a55a)">✅ 已复盘</span>`
                     : `<span class="badge badge-gold">📋 待复盘</span>`}
        <button class="batch-nav" onclick="selectDate('${nextK}')" ${nextK ? "" : "disabled"} title="${nextK ? fmtDate(nextK) : ""}">下批 ›</button>
        ${updDrop}
      </div>`;
  }
}

/* 更新日志浮层展开/收起 */
function toggleUpdLog() {
  const d = document.getElementById("updlog-dropdown");
  if (d) d.style.display = d.style.display === "none" ? "block" : "none";
}

/* ---------- 避雷名单（独立子页面，跨批次聚合+可视化） ---------- */
/* 联赛中文名 → 徽章色类映射（与赛前预测 .lg-* 一致） */
const LG_CLS = {
  "瑞超": "lg-swe", "日职联": "lg-j1", "日乙": "lg-j2", "韩职": "lg-k1",
  "葡超": "lg-prime", "芬超": "lg-fin", "挪超": "lg-nor", "英冠": "lg-champ",
  "巴甲": "lg-bras", "西甲": "lg-laliga", "荷甲": "lg-ered", "荷乙": "lg-eers",
  "英社区盾": "lg-eng", "英超": "lg-eng", "美职联": "lg-mls", "沙特联": "lg-spl",
  "法乙": "lg-l2", "德乙": "lg-bundes2", "欧冠": "lg-ucl", "欧联资格赛": "lg-uel",
  "意甲": "lg-sa", "德甲": "lg-bundes", "德超杯": "lg-bundes", "法甲": "lg-ligue1",
  "英联杯": "lg-champ", "德国杯": "lg-dfb", "巴西杯": "lg-bras", "解放者杯": "lg-copaLib",
  "韩国杯": "lg-k1", "亚冠": "lg-k1", "欧协": "lg-uel", "欧协联": "lg-uel",
  "欧罗巴资格赛": "lg-uel", "欧联": "lg-uel"
};
function lgCls(lg) { return LG_CLS[lg] || "lg-other"; }
function lgBadge(lg, small) {
  return `<span class="lg ${small ? "lg-sm " : ""}${lgCls(lg)}">${lg || ""}</span>`;
}
function renderAvoid() {
  const el = document.getElementById("avoid-view");
  if (!el) return;
  const R = (typeof TEAM_RATING !== "undefined") ? TEAM_RATING : [];
  const by = (g) => R.filter(x => x.g === g);
  const r2 = by("R2"), r1 = by("R1"), n = by("N"), b1 = by("B1"), b2 = by("B2");

  // —— 联赛分布（黑榜+偏黑 = 假球重灾区）——
  const leagueCnt = {};
  b2.concat(b1).forEach(a => {
    (a.lg || "未知").split(",").forEach(lg => { leagueCnt[lg.trim()] = (leagueCnt[lg.trim()] || 0) + 1; });
  });
  const lgEntries = Object.entries(leagueCnt).sort((x, y) => y[1] - x[1]);
  const lgMax = Math.max(1, ...lgEntries.map(([, c]) => c));
  const lgCloud = lgEntries.map(([lg, cnt]) => {
    const hot = cnt >= 3 ? "lgc-hot" : (cnt === 2 ? "lgc-mid" : "");
    return `<span class="avoid-lg-badge ${hot}">${lgBadge(lg, true)}<span class="avoid-lg-cnt">×${cnt}</span></span>`;
  }).join("");
  // 联赛横向条形图（2026-08-23 丰富：直观显示重灾区量级）
  const lgBars = lgEntries.slice(0, 8).map(([lg, cnt]) => `
    <div class="avoid-lbar">
      <span class="lg lg-sm">${lg}</span>
      <div class="avoid-lbar-track"><div class="avoid-lbar-fill" style="width:${Math.round(100 * cnt / lgMax)}%"></div></div>
      <span class="avoid-lbar-num">×${cnt}</span>
    </div>`).join("");

  // —— 单队折叠条目 ——
  const ITEM_DEF = {
    R2: { ic: "⭐", tag: "⭐ 红榜", cls: "tag-green", it: "red" },
    R1: { ic: "🟢", tag: "🟢 偏红", cls: "tag-blue", it: "blue" },
    B1: { ic: "🟡", tag: "🟡 偏黑", cls: "tag-yellow", it: "watch" },
    B2: { ic: "🔴", tag: "🔴 黑榜", cls: "tag-red", it: "high" }
  };
  const item = (a, g) => {
    const d = ITEM_DEF[g];
    const meta = `场次${a.p} · 三指标${a.tp} · 红${a.r}/黑${a.b}`;
    return `
    <details class="avoid-item ${d.it}">
      <summary>
        <span class="avoid-item-ic">${d.ic}</span>
        <span class="avoid-item-name">${a.t}</span>
        <span class="avoid-item-lg">${lgBadge((a.lg || "").split(",")[0])}</span>
        <span style="margin-left:8px;font-size:11px;opacity:.7">${meta}</span>
        <span class="tag ${d.cls}">${d.tag}</span>
        <span class="avoid-item-arrow">▸</span>
      </summary>
      <div class="avoid-item-body">${a.rs || meta}</div>
    </details>`;
  };

  el.innerHTML = `
    <div class="card">
      <h2><span class="icon">🚨</span> 队伍红黑总榜（R358 · 假赛风险评估）</h2>
      <div class="note">赛前分析看双方评级：双红榜=放心正路；任一黑方参与=抓鬼重点。红榜=正路稳定不演戏（三指标全中），黑榜=演戏/剧本嫌疑（避雷/危险信号）。当前 ${R.length} 队（7/21-8/16 全 26 批次聚合），中性 ${n.length} 队未展示。</div>

      <!-- 队伍搜索 -->
      <div class="avoid-search">
        <input id="avoidSearchInput" type="text" placeholder="🔍 搜索队伍（如 天狼星 / 本菲卡）…" oninput="renderAvoidSearch(this.value)">
        <button class="avoid-search-clear" onclick="document.getElementById('avoidSearchInput').value='';renderAvoidSearch('')" title="清空">✕</button>
      </div>

      <!-- 统计仪表盘（含风险指数，2026-08-23 丰富） -->
      <div class="avoid-dash">
        <div class="avoid-stat st-green"><div class="avoid-stat-num">${r2.length}</div><div class="avoid-stat-lbl">⭐ 红榜·稳定</div></div>
        <div class="avoid-stat st-blue"><div class="avoid-stat-num">${r1.length}</div><div class="avoid-stat-lbl">🟢 偏红</div></div>
        <div class="avoid-stat st-batch"><div class="avoid-stat-num">${n.length}</div><div class="avoid-stat-lbl">⚪ 中性</div></div>
        <div class="avoid-stat st-watch"><div class="avoid-stat-num">${b1.length}</div><div class="avoid-stat-lbl">🟡 偏黑</div></div>
        <div class="avoid-stat st-high"><div class="avoid-stat-num">${b2.length}</div><div class="avoid-stat-lbl">🔴 黑榜</div></div>
        <div class="avoid-stat st-index"><div class="avoid-stat-num">${R.length ? Math.round(100 * (b1.length + b2.length) / R.length) : 0}%</div><div class="avoid-stat-lbl">⚠️ 风险指数</div></div>
      </div>

      <!-- 联赛分布可视化（徽章云 + 条形图，2026-08-23 丰富） -->
      <div class="avoid-league">
        <h4>📊 黑榜+偏黑联赛分布 <span class="avoid-league-hint">（假球重灾区，徽章 + 量级条形）</span></h4>
        <div class="avoid-lg-cloud">${lgCloud || '<div class="note">暂无数据</div>'}</div>
        ${lgBars ? `<div class="avoid-lbar-list">${lgBars}</div>` : ""}
      </div>

      <!-- 搜索结果（搜索时显示，替代分组） -->
      <div id="avoidSearchResult" style="display:none">
        <div class="avoid-grid" id="avoidSearchGrid"></div>
        <div class="note" id="avoidSearchEmpty" style="display:none">未找到匹配队伍，换个关键词试试</div>
      </div>

      <!-- 红榜·稳定（默认展开） -->
      <details class="avoid-sec sec-green" open>
        <summary>⭐ 红榜·稳定（${r2.length}）<span class="avoid-sec-hint">三指标全中≥2 且 0 演戏 → 评级 +0.5 档</span></summary>
        <div class="avoid-grid">${r2.map(a => item(a, "R2")).join("") || '<div class="note">暂无</div>'}</div>
      </details>

      <!-- 偏红（默认折叠） -->
      <details class="avoid-sec sec-blue">
        <summary>🟢 偏红（${r1.length}）<span class="avoid-sec-hint">点击展开 ${r1.length} 队</span></summary>
        <div class="avoid-grid">${r1.map(a => item(a, "R1")).join("") || '<div class="note">暂无</div>'}</div>
      </details>

      <!-- 偏黑（默认折叠） -->
      <details class="avoid-sec sec-watch">
        <summary>🟡 偏黑（${b1.length}）<span class="avoid-sec-hint">点击展开 ${b1.length} 队</span></summary>
        <div class="avoid-grid">${b1.map(a => item(a, "B1")).join("") || '<div class="note">暂无</div>'}</div>
      </details>

      <!-- 黑榜（默认展开） -->
      <details class="avoid-sec sec-high" open>
        <summary>🔴 黑榜（${b2.length}）<span class="avoid-sec-hint">避雷/危险信号 → 置信度降一级</span></summary>
        <div class="avoid-grid">${b2.map(a => item(a, "B2")).join("") || '<div class="note">暂无</div>'}</div>
      </details>
    </div>`;
}

/* 红黑榜队伍搜索（按名称/联赛过滤，命中任意档位） */
function renderAvoidSearch(q) {
  const R = (typeof TEAM_RATING !== "undefined") ? TEAM_RATING : [];
  const resBox = document.getElementById("avoidSearchResult");
  const grid = document.getElementById("avoidSearchGrid");
  const empty = document.getElementById("avoidSearchEmpty");
  const sections = document.querySelectorAll(".avoid-sec");
  if (!resBox || !grid) return;
  const kw = (q || "").trim().toLowerCase();
  if (!kw) {
    resBox.style.display = "none";
    sections.forEach(s => s.style.display = "");
    return;
  }
  // 命中匹配（队名/联赛）
  const hits = R.filter(a => (a.t || "").toLowerCase().includes(kw) || (a.lg || "").toLowerCase().includes(kw));
  const ITEM_DEF = { R2: ["⭐ 红榜", "tag-green", "red"], R1: ["🟢 偏红", "tag-blue", "blue"], B1: ["🟡 偏黑", "tag-yellow", "watch"], B2: ["🔴 黑榜", "tag-red", "high"] };
  const itemHtml = (a, g) => {
    const d = ITEM_DEF[g];
    return `<details class="avoid-item ${d[2]}"><summary>
      <span class="avoid-item-ic">${d[0][0]}</span>
      <span class="avoid-item-name">${a.t}</span>
      <span class="avoid-item-lg">${lgBadge((a.lg || "").split(",")[0])}</span>
      <span style="margin-left:8px;font-size:11px;opacity:.7">场次${a.p} · 三指标${a.tp} · 红${a.r}/黑${a.b}</span>
      <span class="tag ${d[1]}">${d[0]}</span>
    </summary><div class="avoid-item-body">${a.rs || ""}</div></details>`;
  };
  const order = { R2: 0, R1: 1, B1: 2, B2: 3 };
  hits.sort((x, y) => order[x.g] - order[y.g]);
  resBox.style.display = "block";
  sections.forEach(s => s.style.display = "none");
  if (hits.length) {
    empty.style.display = "none";
    grid.innerHTML = hits.map(a => itemHtml(a, a.g)).join("");
  } else {
    empty.style.display = "block";
    grid.innerHTML = "";
  }
}

/* ---------- 入口 ---------- */
function renderAll() {
  const b = BATCHES[currentKey];
  renderBatchHeader();
  renderGlobal();
  renderSiteStats();
  renderAvoid();
  if (b) {
    renderPredict(b);
    renderReview(b);
    renderLevelStats();
    renderLeagueStats();
    renderColdVerify();
    initSortable();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // 支持 URL ?date=2026-08-14
  const qs = new URLSearchParams(location.search);
  const d = qs.get("date");
  if (d && BATCHES[d]) currentKey = d;
  renderCalendar();
  renderAll();

  // 主题切换按钮（左上角胶囊，图标 + 文字）
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    const html = document.documentElement;
    const syncIcon = () => { toggle.innerHTML = (html.classList.contains("dark") ? "☀" : "🌙") + "<span> 切换主题</span>"; };
    toggle.addEventListener("click", () => {
      const dark = html.classList.toggle("dark");
      try { localStorage.setItem("dsh-theme", dark ? "dark" : "light"); } catch (e) {}
      syncIcon();
    });
    syncIcon();
  }

  // 打赏支持（顶部 contact-bar 注入按钮 + 微信收款码弹窗）
  const bar = document.querySelector(".contact-bar");
  if (bar) {
    const donateBtn = document.createElement("span");
    donateBtn.className = "contact-item";
    donateBtn.textContent = "❤️ 打赏支持";
    donateBtn.style.cssText = "cursor:pointer;user-select:none;";
    const modal = document.createElement("div");
    modal.style.cssText = "display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;align-items:center;justify-content:center;";
    modal.innerHTML = `
      <div style="background:var(--card,#fff);border-radius:12px;padding:24px 28px;max-width:320px;width:90%;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.25);">
        <h3 style="margin:0 0 6px;font-size:16px;">❤️ 打赏支持</h3>
        <p style="margin:0 0 14px;font-size:12.5px;color:var(--sub,#777);">为爱发电 · 感谢支持！<br>微信扫一扫，随意打赏～</p>
        <img src="images/wechat_qr.png" alt="微信收款码" style="width:200px;height:200px;border-radius:8px;border:1px solid #eee;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='block'">
        <div style="display:none;font-size:12.5px;color:#999;padding:40px 0;">二维码图片未就绪（images/wechat_qr.png）</div>
        <button id="donateClose" style="margin-top:14px;padding:6px 18px;border:1px solid #ccc;border-radius:6px;background:transparent;cursor:pointer;font-size:12.5px;">关闭</button>
      </div>`;
    modal.addEventListener("click", (e) => { if (e.target === modal) modal.style.display = "none"; });
    donateBtn.addEventListener("click", () => { modal.style.display = "flex"; });
    modal.querySelector("#donateClose").addEventListener("click", () => { modal.style.display = "none"; });
    document.body.appendChild(modal);
    bar.appendChild(donateBtn);
  }
});
