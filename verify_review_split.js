// verify_review_split.js — 复盘拆分等价性（键集合 + 每批复盘条数 + 文本长度）
const fs = require("fs");
const B = "D:\\Cola\\足球分析学习\\_发布_public\\js\\";
function ev(files) {
  const code = files.map(f => fs.readFileSync(B + f, "utf8")).join("\n") +
    "\nreturn REVIEW_EXTRA;";
  return new Function(code)();
}
const src = ev(["data-review.js"]);
const sp = ev(["data-review-core.js", "data-review-history.js"]);
const ks = Object.keys(src).sort(), kd = Object.keys(sp).sort();
console.log("源复盘批次:", ks.length, "｜拆分后:", kd.length);
console.log("缺失:", ks.filter(k => !kd.includes(k)).length ? ks.filter(k => !kd.includes(k)) : "无 ✅");
console.log("多余:", kd.filter(k => !ks.includes(k)).length ? kd.filter(k => !ks.includes(k)) : "无 ✅");
let bad = [];
for (const k of ks) {
  const a = src[k] || {}, b = sp[k];
  if (!b) { bad.push(k + ":缺"); continue; }
  const ra = (a.results || []).length, rb = (b.results || []).length;
  const ea = (a.evidence || []).length, eb = (b.evidence || []).length;
  if (ra !== rb || ea !== eb) bad.push(`${k}: results ${ra}≠${rb} / evidence ${ea}≠${eb}`);
  const ta = JSON.stringify(a.results || []).length, tb = JSON.stringify(b.results || []).length;
  if (ta !== tb) bad.push(`${k}: results 文本长度 ${ta}≠${tb}`);
  const ga = JSON.stringify(a.evidence || []).length, gb = JSON.stringify(b.evidence || []).length;
  if (ga !== gb) bad.push(`${k}: evidence 文本长度 ${ga}≠${gb}`);
}
console.log("逐批一致性:", bad.length ? bad.slice(0, 8) : "全部一致 ✅");
const core = ev(["data-review-core.js"]);
console.log("core 内含批次:", Object.keys(core).join(","), "（应=最新复盘批）");
