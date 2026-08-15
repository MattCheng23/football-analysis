/* ============================================================
   足球分析预测站 · 应用逻辑（日历 + 动态渲染）
   ============================================================ */

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
  for (let d = 1; d <= daysInMonth; d++) {
    const key = fmtKey(new Date(calYear, calMonth, d));
    const batch = BATCHES[key];
    const has = !!batch;
    const reviewed = batch && batch.reviewed;
    const isCur = key === currentKey;
    html += `<div class="cal-cell ${has ? "has-data" : ""} ${isCur ? "current" : ""}" ${has ? `onclick="selectDate('${key}')" title="${fmtDate(key)}"` : ""}>
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
  document.querySelector(".batch-header").scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ---------- 渲染：预测 ---------- */
function renderPredict(batch) {
  const el = document.getElementById("predict-view");
  if (!el) return; // 复盘页无预测视图，跳过
  const p = batch.predict;

  // 预测清单（含假赛评分列）；按北京时间开球排序
  const tMin = t => { if (!t) return 9999; const d = t.indexOf("次日") >= 0 ? 1440 : 0; const m = t.match(/(\d+):(\d+)/); return d + (m ? +m[1] * 60 + +m[2] : 0); };
  const sorted = p.matches.slice().sort((a, b) => tMin(a.time) - tMin(b.time));
  const riskTag = r => r >= 7 ? `<span class="tag tag-red">🔴 ${r}</span>`
    : r >= 5 ? `<span class="tag tag-orange">🟠 ${r}</span>`
    : `<span class="tag tag-green">🟢 ${r}</span>`;
  const rows = sorted.map(m => {
    const revHtml = m.scores.replace(/(\d+-\d+)\*/g, '<span class="rev-score">$1*</span>');
    const revHt = m.ht.replace(/([胜负平]{2})\*/g, '<span class="rev-score">$1*</span>');
    return `<tr>
    <td><span class="no-badge">${m.no}</span></td>
    <td>${m.home} vs ${m.away}<br><span class="mt-line"><span class="lg ${m.lg}">${m.league}</span><span class="match-time">🕐 ${m.time || "-"}</span></span></td>
    <td class="${m.dc}">${m.dir}</td>
    <td class="score-nums">${revHtml}</td>
    <td>${revHt}</td>
    <td>${m.ou}</td>
    <td>${riskTag(m.risk || 0)}</td>
  </tr>`;
  }).join("");

  // 冷门风险（精简：前6条，无逻辑列）
  const coldRows = p.coldRisk.slice(0, 6).map(c => `<tr>
    <td>${c.rank}</td><td>${c.no} ${c.teams}</td><td>${c.dir}</td>
    <td><span class="tag ${c.lv}">${c.lvTxt}</span></td>
  </tr>`).join("");

  // 高价值预警：只显示 中等偏高/中等，其余（中等偏低及以下）隐藏
  const alertRows = p.alerts
    .filter(a => a.lvTxt === "中等偏高" || a.lvTxt === "中等")
    .map(a => `<tr>
    <td>${a.script}</td><td>${a.no} ${a.teams}</td>
    <td><span class="tag ${a.lv}">${a.lvTxt}</span></td>
    <td>${a.logic}</td>
  </tr>`).join("");

  // 0-0 预警：取概率最高的 3 场（保证列表有信息量）
  const zzRows = (p.zeroZero || [])
    .slice()
    .sort((a, z) => z.p - a.p)
    .slice(0, 3)
    .map(z => `<tr>
    <td>${z.no} ${z.teams}</td>
    <td><div class="prob-bar"><div class="prob-track"><div class="prob-fill" style="width:${z.p}%"></div></div><span class="prob-txt num">${z.p}%</span></div></td>
    <td><span class="tag ${z.lv}">${z.lvTxt}</span></td>
  </tr>`).join("");

  // 核心逻辑速览（一句话/场）
  const logicRows = sorted.map(m => `<tr>
    <td><span class="no-badge">${m.no}</span></td>
    <td>${m.home} vs ${m.away}${m.time ? `<br><span class="mt-line"><span class="lg ${m.lg}">${m.league}</span><span class="match-time">🕐 ${m.time}</span></span>` : ""}</td>
    <td>${m.logic || "-"}</td>
  </tr>`).join("");

  el.innerHTML = `
    <div class="card">
      <h2><span class="icon">📋</span> 一、完整预测清单（${batch.title}）</h2>
      <div style="display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--sub);margin-bottom:6px;">
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#dcf5e5"></span> 胜倾向</span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#fdf3d0"></span> 胜/平</span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#fee4e2"></span> 平/负</span>
        <span style="margin-left:auto">A 级 = 高置信正路 ｜ B 级 = 中置信正路 ｜ C 级 = 低置信（含 1 反向比分，标 <span class="rev-score">*</span>）</span>
      </div>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>对阵（北京时间）</th><th>方向</th><th>比分 TOP3</th><th>半全场 TOP3</th><th>总进球</th><th>假赛分</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <h2><span class="icon">🌡️</span> 冷门风险 Top6</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>排名</th><th>场次</th><th>冷门方向</th><th>风险等级</th></tr></thead>
        <tbody>${coldRows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <h2><span class="icon">🚨</span> 高价值预警</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>剧本</th><th>场次</th><th>概率</th><th>核心逻辑</th></tr></thead>
        <tbody>${alertRows}</tbody>
      </table></div>
      <div class="note">仅显示中等偏高 / 中等概率的剧本，其余已过滤。</div>
    </div>

    <div class="card">
      <h2><span class="icon">🛡️</span> 0-0 预警</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>0-0 概率</th><th>等级</th></tr></thead>
        <tbody>${zzRows}</tbody>
      </table></div>
      <div class="note">取 0-0 概率最高的 3 场（泊松计算）。</div>
    </div>

    <div class="card">
      <h2><span class="icon">💡</span> 各场核心逻辑（一句话）</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>对阵</th><th>核心逻辑</th></tr></thead>
        <tbody>${logicRows}</tbody>
      </table></div>
    </div>`;
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
    const i = (listStr || "").split("/").map(s => s.trim()).indexOf(actual);
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
    if (batch.zeroZero) {
      const z = batch.zeroZero.find(x => x.no === m.no);
      if (z && scoreMain === "0-0") return `🎯 0-0（预警${z.p}%）`;
    }
    return "";
  };

  const totalN = batch.predict.matches.length;
  const confirmedN = r.results.length;
  const alertCount = r.results.filter(m => alertOf(m) !== "").length;
  const alertKpi = `<div class="kpi" style="background:rgba(217,119,6,.08);border-color:#d97706"><div class="num">${alertCount}</div><div class="lbl">🎯 预警命中（不计正式）</div></div>`;
  const statusTag = batch.reviewed
    ? `<span class="tag tag-green">完整复盘</span>`
    : `<span class="tag tag-yellow">部分复盘（已确认 ${confirmedN}/${totalN} 场）</span>`;
  const kpiHtml = batch.reviewed ? `
        <div class="kpi"><div class="num">${batch.stats.dir}</div><div class="lbl">方向命中率 ${batch.stats.dirPct}</div></div>
        <div class="kpi"><div class="num">${batch.stats.score}</div><div class="lbl">比分 TOP3 ${batch.stats.scorePct}</div></div>
        <div class="kpi"><div class="num">${batch.stats.ht}</div><div class="lbl">半全场 TOP3 ${batch.stats.htPct}</div></div>
        ${alertKpi}` : `
        <div class="kpi"><div class="num">${confirmedN}/${totalN}</div><div class="lbl">已确认场次</div></div>
        <div class="kpi"><div class="num">${r.results.filter(m => m.d === "ok").length}</div><div class="lbl">方向已命中</div></div>
        <div class="kpi"><div class="num">${r.results.filter(m => m.s === "ok").length}</div><div class="lbl">比分已命中</div></div>
        <div class="kpi"><div class="num">${r.results.filter(m => m.h === "ok").length}</div><div class="lbl">半全场已命中</div></div>
        ${alertKpi}`;

  const rows = r.results.map(m => {
    const pm = batch.predict.matches.find(x => x.no === m.no);
    const scoreMain = m.score.split("（")[0];
    const sTop = pm ? topOf(scoreMain, pm.scores) : null;
    const hTop = pm ? topOf(htFromScore(m.score), pm.ht) : null;
    const hCell = hTop ? hitTag(hTop) : (m.h === "ok" ? okT : noT); // 无半场数据时按 h 判定
    const aw = alertOf(m);
    return `<tr>
      <td><span class="no-badge">${m.no}</span></td>
      <td>${m.teams} <span class="lg ${m.lg}">${m.league}</span></td>
      <td><b>${m.score}</b></td>
      <td>${dTag(m.d)}</td>
      <td>${hitTag(sTop)}</td>
      <td>${hCell}</td>
      <td>${aw ? `<span class="tag tag-yellow">${aw}</span>` : `<span class="tag tag-gray">—</span>`}</td>
      <td><span class="tag ${m.sc === "danger" ? "tag-red" : m.sc === "watch" ? "tag-yellow" : "tag-green"}">${m.signal}</span></td>
    </tr>`;
  }).join("");

  // 控分排查结论仅本地保留（合规），网页只展示演戏排查部分
  const cleanTxt = t => (t || "").split("控分排查：")[0].trim();
  const evRows = r.evidence.map(e => `<tr>
    <td><b>${e.no} ${e.teams}</b><br><span class="lg ${e.lg}">${e.league}</span></td>
    <td>${e.stats}</td>
    <td><span class="tag ${e.sc === "danger" ? "tag-red" : e.sc === "watch" ? "tag-yellow" : "tag-green"}">${e.signal}</span> ${cleanTxt(e.txt)}</td>
  </tr>`).join("");

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
          <th data-sortable>方向</th><th data-sortable>比分</th><th data-sortable>半全场</th><th data-sortable>预警命中</th><th>演戏信号</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <h2><span class="icon">🔎</span> 关键场次技术统计（演戏信号实证）</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>场次</th><th>技术统计</th><th>信号解读</th></tr></thead>
        <tbody>${evRows}</tbody>
      </table></div>
    </div>`;
}

/* ---------- 站点总览统计条 ---------- */
function renderSiteStats() {
  const el = document.getElementById("site-stats");
  if (!el) return;
  const keys = Object.keys(BATCHES).sort();
  const totalBatches = keys.length;
  const reviewed = keys.filter(k => BATCHES[k].reviewed).length;
  let totalMatches = 0, dirHit = 0;
  keys.forEach(k => {
    const b = BATCHES[k];
    if (b.reviewed && b.review.results) {
      b.review.results.forEach(m => { totalMatches++; if (m.d === "ok") dirHit++; });
    }
  });
  const dirPct = totalMatches ? Math.round(100 * dirHit / totalMatches) + "%" : "—";
  el.innerHTML = `
    <div class="site-stat"><span class="ss-num">${totalBatches}</span><span class="ss-lbl">总批次</span></div>
    <div class="site-stat"><span class="ss-num">${totalMatches}</span><span class="ss-lbl">已复盘场次</span></div>
    <div class="site-stat"><span class="ss-num">${dirPct}</span><span class="ss-lbl">批次方向命中</span></div>
    <div class="site-stat"><span class="ss-num">${GLOBAL_STATS.dirPct}</span><span class="ss-lbl">累计方向命中</span></div>
    <div class="site-stat"><span class="ss-num">${reviewed}/${totalBatches}</span><span class="ss-lbl">已复盘批次</span></div>
    <div class="site-stat"><span class="ss-num">${GLOBAL_STATS.updated.slice(5)}</span><span class="ss-lbl">最后更新</span></div>`;
}

/* ---------- 预测级别表现分析 ---------- */
function levelAnalysis(b) {
  // 方向字符串 → 级别（A/B/C）与主倾向
  const grade = d => (d.includes("C") ? "C级" : d.includes("A") ? "A级" : "B级");
  const res = { "A级": { t: 0, h: 0 }, "B级": { t: 0, h: 0 }, "C级": { t: 0, h: 0 } };
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
    return `<tr><td class="num">${g}</td><td class="num">${r.h}/${r.t}</td><td><div class="prob-bar"><div class="prob-track"><div class="prob-fill" style="width:${pct}%"></div></div><span class="prob-txt num">${pct}%</span></div></td></tr>`;
  };
  el.innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>预测级别</th><th>方向命中</th><th>命中率</th></tr></thead>
      <tbody>${row("A级")}${row("B级")}${row("C级")}</tbody>
    </table></div>
    <div class="note">A级 = 高置信正路；B级 = 中置信正路；C级 = 低置信（2主+1反向比分）。用于检验"高置信更可靠"假设。</div>`;
}

/* ---------- 联赛表现统计 ---------- */
function renderLeagueStats() {
  const el = document.getElementById("league-stats");
  if (!el || !BATCHES[currentKey] || !BATCHES[currentKey].reviewed) return;
  const b = BATCHES[currentKey];
  const map = {};
  b.review.results.forEach(m => {
    const pm = b.predict.matches.find(x => x.no === m.no);
    const lg = (pm && pm.league) || m.league || "其他";
    if (!map[lg]) map[lg] = { t: 0, h: 0 };
    map[lg].t++;
    if (m.d === "ok") map[lg].h++;
  });
  const rows = Object.keys(map).sort((a, z) => map[z].t - map[a].t).map(lg => {
    const r = map[lg];
    const pct = Math.round(100 * r.h / r.t);
    return `<tr><td>${lg}</td><td class="num">${r.h}/${r.t}</td><td><div class="prob-bar"><div class="prob-track"><div class="prob-fill" style="width:${pct}%"></div></div><span class="prob-txt num">${pct}%</span></div></td></tr>`;
  }).join("");
  el.innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>联赛</th><th>方向命中</th><th>命中率</th></tr></thead>
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

/* ---------- 全局统计 + 批次头 ---------- */
function renderGlobal() {
  const el = document.getElementById("global-kpi");
  if (el) el.innerHTML = `
    <div class="kpi"><div class="num">${GLOBAL_STATS.dir}</div><div class="lbl">累计方向 ${GLOBAL_STATS.dirPct}</div></div>
    <div class="kpi"><div class="num">${GLOBAL_STATS.score}</div><div class="lbl">累计比分 ${GLOBAL_STATS.scorePct}</div></div>
    <div class="kpi"><div class="num">${GLOBAL_STATS.ht}</div><div class="lbl">累计半全场 ${GLOBAL_STATS.htPct}</div></div>`;
}

function renderBatchHeader() {
  const b = BATCHES[currentKey];
  const el = document.getElementById("batch-header");
  if (el && b) {
    el.innerHTML = `
      <span class="badge badge-soft">📅 ${fmtDate(currentKey)}</span>
      <span class="badge badge-solid">${b.title}</span>
      <span class="badge badge-soft" style="margin-left:auto">模型 ${b.model}</span>
      ${b.reviewed ? `<span class="badge badge-solid" style="background:linear-gradient(135deg,#15803d,#22a55a)">✅ 已复盘</span>`
                   : `<span class="badge badge-gold">📋 待复盘</span>`}`;
  }
}

/* ---------- 避雷名单（独立子页面，跨批次聚合） ---------- */
function renderAvoid() {
  const el = document.getElementById("avoid-view");
  if (!el) return;
  // 跨批次聚合 avoidHigh / avoidWatch，按队伍去重（保留最新 reason）
  const highMap = {}, watchMap = {};
  Object.keys(BATCHES).forEach(k => {
    const r = BATCHES[k].review;
    if (!r) return;
    (r.avoidHigh || []).forEach(a => { highMap[a.team] = a; });
    (r.avoidWatch || []).forEach(a => { watchMap[a.team] = a; });
  });
  const highList = Object.values(highMap), watchList = Object.values(watchMap);
  const card = (a, kind) => `<div class="avoid-card ${kind}">
    <div class="team-icon">${kind === "high" ? "🚫" : "👀"}</div><div>
      <div class="team-name">${a.team} <span class="tag ${kind === "high" ? "tag-red" : "tag-yellow"}">${kind === "high" ? "🔴 高" : "🟡 观察"}</span></div>
      <div class="team-league">${a.league}</div>
      <div class="team-reason">${a.reason}</div>
    </div></div>`;
  const srcCount = Object.keys(BATCHES).filter(k => BATCHES[k].review && ((BATCHES[k].review.avoidHigh && BATCHES[k].review.avoidHigh.length) || (BATCHES[k].review.avoidWatch && BATCHES[k].review.avoidWatch.length))).length;
  el.innerHTML = `
    <div class="card">
      <h2><span class="icon">🚨</span> 队伍级避雷名单（全联赛统一）</h2>
      <div class="note">避雷队伍参与的比赛预测置信度降一级 + 强制"避雷预警"标记；名单动态维护，跨批次累计（当前 ${highList.length + watchList.length} 队，来自 ${srcCount} 个批次）。</div>
      <h3>🔴 高信号（${highList.length}）</h3>
      <div class="avoid-grid">${highList.map(a => card(a, "high")).join("") || '<div class="note">暂无</div>'}</div>
      <h3>🟡 观察（${watchList.length}）</h3>
      <div class="avoid-grid">${watchList.map(a => card(a, "watch")).join("") || '<div class="note">暂无</div>'}</div>
    </div>`;
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

  // 主题切换按钮
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    const html = document.documentElement;
    const syncIcon = () => { toggle.textContent = html.classList.contains("dark") ? "☀" : "🌙"; };
    toggle.addEventListener("click", () => {
      const dark = html.classList.toggle("dark");
      try { localStorage.setItem("dsh-theme", dark ? "dark" : "light"); } catch (e) {}
      syncIcon();
    });
    syncIcon();
  }
});
