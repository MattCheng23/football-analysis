# -*- coding: utf-8 -*-
"""patch_html_split.py — 三个 HTML 改为「core 首屏 + history 异步」加载（2026-09-12 提速）
index.html / review.html / avoid.html：<script src="js/data.js?v..."> → data-core.js + 首屏后注入 data-history.js
注入完成后自动重渲染（renderAll）或按 ?date= 深链跳到目标批（selectDate）
"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\Cola\足球分析学习\_发布_public"
LOADER = """<script>
/* 历史批次异步加载（2026-09-12 提速改造：data.js 1.8MB 拆为 core 186KB + history 首屏后注入） */
(function () {
  function L() {
    var s = document.createElement("script");
    s.src = "js/data-history.js?v202609112114";
    s.onload = function () {
      try {
        var q = location.search.indexOf("date=");
        if (q >= 0) {
          var d = location.search.substr(q + 5, 10);
          if (window.BATCHES && BATCHES[d] && typeof selectDate === "function") { selectDate(d); return; }
        }
      } catch (e) {}
      try { if (typeof renderAll === "function") renderAll(); } catch (e) {}
    };
    document.head.appendChild(s);
  }
  if (document.readyState === "complete") { setTimeout(L, 300); }
  else { window.addEventListener("load", function () { setTimeout(L, 300); }); }
})();
</script>"""
ok = 0
for f in ("index.html", "review.html", "avoid.html"):
    p = os.path.join(B, f)
    c = io.open(p, encoding="utf-8").read()
    if "data-core.js" in c:
        print("  %-12s 已是新加载策略，跳过" % f); continue
    m = re.search(r'<script src="js/data\.js\?v\d{12}"></script>', c)
    if not m:
        print("  ❌ %s 未找到 data.js script 标签" % f); sys.exit(1)
    c = c[:m.start()] + '<script src="js/data-core.js?v202609112114"></script>\n' + LOADER + c[m.end():]
    io.open(p, "w", encoding="utf-8", newline="\n").write(c)
    ok += 1
    print("  ✅ %-12s → data-core.js + history 异步 loader" % f)
print("HTML 改造完成 %d/3" % ok)
