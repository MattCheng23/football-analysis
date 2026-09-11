// verify_split.js — 验证拆分后 BATCHES 键集合/场次数与源 data.js 完全一致
const fs = require("fs");
const B = "D:\\Cola\\足球分析学习\\_发布_public\\js\\";

function evalWith(files) {
  const code = files.map(f => fs.readFileSync(B + f, "utf8")).join("\n") +
    "\nreturn { BATCHES: BATCHES, TEAM_RATING: TEAM_RATING, GLOBAL_STATS: GLOBAL_STATS };";
  return new Function(code)();
}

const src = evalWith(["data.js"]);
const split = evalWith(["data-core.js", "data-history.js"]);

const ks = Object.keys(src.BATCHES).sort();
const kd = Object.keys(split.BATCHES).sort();
console.log("源批次数:", ks.length, "｜拆分后:", kd.length);
const missing = ks.filter(k => !kd.includes(k));
const extra = kd.filter(k => !ks.includes(k));
console.log("缺失:", missing.length ? missing : "无 ✅");
console.log("多余:", extra.length ? extra : "无 ✅");

let bad = [];
for (const k of ks) {
  const a = src.BATCHES[k], b = split.BATCHES[k];
  if (!b) { bad.push(k + ":缺"); continue; }
  const na = (a.predict && a.predict.matches || []).length;
  const nb = (b.predict && b.predict.matches || []).length;
  if (na !== nb) bad.push(`${k}:场次 ${na}≠${nb}`);
  const ta = a.title || "", tb = b.title || "";
  if (ta !== tb) bad.push(`${k}:title 不一致`);
  // spot check 首个 logic 长度
  const la = (a.predict && a.predict.matches[0] && a.predict.matches[0].logic || "").length;
  const lb = (b.predict && b.predict.matches[0] && b.predict.matches[0].logic || "").length;
  if (la !== lb) bad.push(`${k}:logic 长度 ${la}≠${lb}`);
  // 四数组
  for (const arr of ["coldRisk", "alerts", "bigSeven", "zeroZero"]) {
    const xa = ((a.predict && a.predict[arr]) || []).length, xb = ((b.predict && b.predict[arr]) || []).length;
    if (xa !== xb) bad.push(`${k}:${arr} ${xa}≠${xb}`);
  }
}
console.log("逐批一致性:", bad.length ? bad.slice(0, 12) : "全部一致 ✅");
console.log("TEAM_RATING:", (src.TEAM_RATING || []).length, "→", (split.TEAM_RATING || []).length,
  (src.TEAM_RATING || []).length === (split.TEAM_RATING || []).length ? "✅" : "❌");
console.log("GLOBAL_STATS 键:", Object.keys(src.GLOBAL_STATS || {}).length, "→", Object.keys(split.GLOBAL_STATS || {}).length);
const cur = split.BATCHES["2026-09-12"];
console.log("本批(2026-09-12) 在核心文件:", cur ? "✅ 场次=" + cur.predict.matches.length : "❌ 缺失");

// ---- 档位映射守卫（2026-09-12 新增·避雷页搜索 TypeError 根因：数据出现未登记档位）----
// 规则：TEAM_RATING 的每个 g 档位都必须在 app.js 的 ITEM_DEF 中登记，否则搜索/渲染读属性即崩
const appSrc = fs.readFileSync(B + "app.js", "utf8");
const defKeys = new Set();
for (const m of appSrc.matchAll(/const ITEM_DEF = \{([\s\S]*?)\n\s*\};/g)) {
  for (const k of m[1].matchAll(/(?:^|[{,\s])([A-Za-z_]\w*)\s*:\s*[\[{]/g)) defKeys.add(k[1]);
}
const grades = [...new Set((split.TEAM_RATING || []).map(x => x.g))].sort();
const unreg = grades.filter(g => !defKeys.has(g));
console.log("档位映射: ITEM_DEF[" + [...defKeys].join("/") + "] ｜ 数据档位[" + grades.join("/") + "]",
  unreg.length ? "❌ 未登记: " + unreg.join(",") : "✅ 全覆盖");

// ---- 退出码（2026-09-12 修复：此前只打印不置码 → 内容不一致不会阻断部署）----
const fails = [];
if (missing.length) fails.push("缺失批次 " + missing.length + " 个");
if (extra.length) fails.push("多余批次 " + extra.length + " 个");
if (bad.length) fails.push("逐批不一致 " + bad.length + " 处（" + bad.slice(0, 3).join("; ") + "）");
if ((src.TEAM_RATING || []).length !== (split.TEAM_RATING || []).length) fails.push("TEAM_RATING 数不一致");
if (Object.keys(src.GLOBAL_STATS || {}).length !== Object.keys(split.GLOBAL_STATS || {}).length) fails.push("GLOBAL_STATS 键数不一致");
if (!cur) fails.push("最新批不在核心文件（首屏将空白）");
if (unreg.length) fails.push("档位未登记 ITEM_DEF: " + unreg.join(","));
if (fails.length) {
  console.log("GUARD FAIL: " + fails.join(" ｜ "));
  process.exitCode = 1;
} else {
  console.log("GUARD OK: 拆分包与源等价 + 档位映射完整 ✅");
}

