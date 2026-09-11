# -*- coding: utf-8 -*-
"""split_review.py — 复盘数据拆分（一次性改造·2026-09-12）
① app.js：REVIEW_EXTRA 合并逻辑暴露为 window.mergeReviewExtra()（可重入），供异步到位后再次合并
② review.html：data-review.js → data-review-core.js（首屏） + data-review-history.js?h=<hash>（异步）
（data-review-core/history 由 build_split.py 生成）
"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\Cola\足球分析学习\_发布_public"

# ---- ① app.js 合并函数可重入 ----
ap = os.path.join(B, "js", "app.js")
a = io.open(ap, encoding="utf-8").read()
old = '''/* 复盘数据合并（2026-08-20 拆分：data-review.js 由复盘页加载后并入 BATCHES；首页不加载则 review 为空壳） */
(function(){
  if (typeof REVIEW_EXTRA !== "undefined" && typeof BATCHES !== "undefined") {
    Object.keys(REVIEW_EXTRA).forEach(function(k){
      if (BATCHES[k]) BATCHES[k].review = REVIEW_EXTRA[k];
    });
  }
})();'''
new = '''/* 复盘数据合并（2026-08-20 拆分：data-review.js 由复盘页加载后并入 BATCHES；首页不加载则 review 为空壳）
   2026-09-12：改为可重入全局函数——复盘历史异步到达后需再次合并（mergeReviewExtra） */
function mergeReviewExtra() {
  if (typeof REVIEW_EXTRA !== "undefined" && typeof BATCHES !== "undefined") {
    Object.keys(REVIEW_EXTRA).forEach(function (k) {
      if (BATCHES[k]) BATCHES[k].review = REVIEW_EXTRA[k];
    });
  }
}
window.mergeReviewExtra = mergeReviewExtra;
mergeReviewExtra();'''
if old in a:
    a = a.replace(old, new)
    io.open(ap, "w", encoding="utf-8", newline="\n").write(a)
    print("① app.js 合并函数已改为可重入 ✓")
elif "window.mergeReviewExtra" in a:
    print("① app.js 已是可重入写法，跳过")
else:
    print("① ❌ app.js 未匹配到合并段"); sys.exit(1)

# ---- ② review.html 改异步加载 ----
rp = os.path.join(B, "review.html")
h = io.open(rp, encoding="utf-8").read()
if "data-review-core.js" in h:
    print("② review.html 已是拆分加载，跳过")
else:
    m = re.search(r'<script src="js/data-review\.js\?v\d{12}"></script>', h)
    if not m:
        print("② ❌ 未找到 data-review.js 标签"); sys.exit(1)
    loader = """<script src="js/data-review-core.js?v202609112114"></script>
<script>
/* 复盘历史异步加载（2026-09-12：data-review.js 801KB → core + 首屏后注入 history?h=内容哈希） */
(function () {
  function L() {
    var s = document.createElement("script");
    s.src = "js/data-review-history.js?h=0000000000";
    s.onload = function () {
      try { if (typeof mergeReviewExtra === "function") mergeReviewExtra(); } catch (e) {}
      try { if (typeof renderAll === "function") renderAll(); } catch (e) {}
    };
    document.head.appendChild(s);
  }
  if (document.readyState === "complete") { setTimeout(L, 300); }
  else { window.addEventListener("load", function () { setTimeout(L, 300); }); }
})();
</script>"""
    h = h[:m.start()] + loader + h[m.end():]
    io.open(rp, "w", encoding="utf-8", newline="\n").write(h)
    print("② review.html 已改为 core + 异步 history ✓")
