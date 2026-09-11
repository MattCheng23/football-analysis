# -*- coding: utf-8 -*-
"""build_split.py — 把 js/data.js 拆成「首屏核心 + 历史批次」两份部署文件（2026-09-12 提速改造）
背景：data.js 已 1.8MB（54 批历史，含 1032 段 logic 文本），手机端每次部署后需重新下载 ~488KB(br)。
方案：首屏只加载 data-core.js（BATCH_META + 最新批 + TEAM_RATING + GLOBAL_STATS）≈185KB；
     其余批次 → data-history.js（首屏 load 后 300ms 异步注入，注入后重渲染）。
     源文件 js/data.js 保持不变（检查器/插入脚本/发布脚本仍读写它=单一真源）。
断言：批次数/每批场次/四数组长度/标题 与源逐一相等，否则退出码 1（阻断部署）。
"""
import hashlib, io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\Cola\足球分析学习\_发布_public\js"
SRC = os.path.join(B, "data.js")

src = io.open(SRC, encoding="utf-8").read()
i0 = src.index("const BATCHES = {")
i_team = src.index("const TEAM_RATING = [")
body = src[i0 + len("const BATCHES = {"):src.rindex("};", i0, i_team)]

keys = [(m.start(), m.group(1)) for m in re.finditer(r'\n\s{0,4}"(\d{4}-\d{2}-\d{2})": \{', body)]
blocks = []
for idx, (pos, key) in enumerate(keys):
    end = keys[idx + 1][0] if idx + 1 < len(keys) else len(body)
    blocks.append((key, body[pos:end]))
if len(blocks) < 2:
    print("❌ 未解析到批次块（结构变化）"); sys.exit(1)
newest = sorted(k for k, _ in blocks)[-1]

meta = []
for k, b in blocks:
    t = re.search(r'title: "([^"]*)"', b)
    m = re.search(r'model: "([^"]*)"', b)
    rv = re.search(r'reviewed: (true|false)', b)
    up = re.search(r'updated: "([^"]*)"', b)
    n = len(re.findall(r'\{ no: "\d+"', b))
    meta.append('  "%s": { title: "%s", model: "%s", reviewed: %s, updated: "%s", n: %d },'
                % (k, t.group(1) if t else "", m.group(1) if m else "", rv.group(1) if rv else "false",
                   up.group(1) if up else "", n))

head = src[:i0]
tail = src[i_team:]
core = head + "const BATCH_META = {\n" + "\n".join(meta) + "\n};\n\nconst BATCHES = {" + \
       [b for k, b in blocks if k == newest][0] + "};\n\n" + tail
hist = ("/* 历史批次（首屏后异步加载·build_split.py 生成，勿手改） */\n"
        "Object.assign(BATCHES, {" + "".join(b for k, b in blocks if k != newest) + "});\n")
io.open(os.path.join(B, "data-core.js"), "w", encoding="utf-8", newline="\n").write(core)
io.open(os.path.join(B, "data-history.js"), "w", encoding="utf-8", newline="\n").write(hist)

# ---- 守卫：调用 Node 深比对（verify_split.js = 键集合/场次/四数组/标题 逐批等价）----
import subprocess
_vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_split.js")
_r = subprocess.run(["node", _vp], capture_output=True, text=True, encoding="utf-8", errors="replace")
_out = (_r.stdout or "") + (_r.stderr or "")
print("拆分包: core %.1f KB / history %.1f KB" % (
    os.path.getsize(os.path.join(B, "data-core.js")) / 1024,
    os.path.getsize(os.path.join(B, "data-history.js")) / 1024))
print("\n".join([l for l in _out.strip().splitlines() if l.strip()][-6:]))
# ---- 站点头部版本号与最新批 model 同步（防陈旧：index/review/avoid 的 V11.x 字样）----
_mv = re.search(r'model: "规则驱动模型 (V[\d.]+)"', [b for k, b in blocks if k == newest][0])
if _mv:
    _ver = _mv.group(1)
    _vc = 0
    for _f in ("index.html", "review.html", "avoid.html"):
        _fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_发布_public", _f)
        _c = io.open(_fp, encoding="utf-8").read()
        _c2, _k = re.subn(r'V11\.\d+(?:\.\d+)?', _ver, _c)
        if _k:
            io.open(_fp, "w", encoding="utf-8", newline="\n").write(_c2)
            _vc += _k
    print("站点头部版本号同步为 %s（HTML 更新 %d 处）" % (_ver, _vc))

# ---- 复盘数据拆分（data-review.js → core + history·各自内容哈希）----
_rp = os.path.join(B, "data-review.js")
if os.path.exists(_rp):
    _rs = io.open(_rp, encoding="utf-8").read()
    _j0 = _rs.index("const REVIEW_EXTRA = {")
    _rb = _rs[_j0 + len("const REVIEW_EXTRA = {"):_rs.rindex("};")]
    _rk = [(m.start(), m.group(1)) for m in re.finditer(r'\n\s{0,4}"(\d{4}-\d{2}-\d{2})": \{', _rb)]
    _rblk = [(k, _rb[pp:(_rk[i + 1][0] if i + 1 < len(_rk) else len(_rb))]) for i, (pp, k) in enumerate(_rk)]
    _rn = sorted(k for k, _ in _rblk)[-1]
    _rcore = _rs[:_j0] + "const REVIEW_EXTRA = {" + [b for k, b in _rblk if k == _rn][0] + "};\n"
    _rhist = ("/* 复盘历史（首屏后异步加载·build_split.py 生成，勿手改） */\n"
              "Object.assign(REVIEW_EXTRA, {" + "".join(b for k, b in _rblk if k != _rn) + "});\n")
    io.open(os.path.join(B, "data-review-core.js"), "w", encoding="utf-8", newline="\n").write(_rcore)
    io.open(os.path.join(B, "data-review-history.js"), "w", encoding="utf-8", newline="\n").write(_rhist)
    print("复盘分包: core %.1f KB（最新 %s）+ history %.1f KB ｜ 复盘批次数 %d"
          % (os.path.getsize(os.path.join(B, "data-review-core.js")) / 1024, _rn,
             os.path.getsize(os.path.join(B, "data-review-history.js")) / 1024, len(_rblk)))
    _rh = hashlib.md5(io.open(os.path.join(B, "data-review-history.js"), "rb").read()).hexdigest()[:10]
    _rfp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_发布_public", "review.html")
    _rc = io.open(_rfp, encoding="utf-8").read()
    _rc2, _rk2 = re.subn(r'data-review-history\.js\?(?:h=[0-9a-f]+|v\d{12})', 'data-review-history.js?h=' + _rh, _rc)
    if _rk2:
        io.open(_rfp, "w", encoding="utf-8", newline="\n").write(_rc2)
    print("data-review-history.js 内容哈希 ?h=%s（review.html 更新 %d 处）" % (_rh, _rk2))

# ---- 历史文件内容哈希版本（跨部署缓存：内容不变则 URL 不变，浏览器/边缘不重下）----
_h = hashlib.md5(io.open(os.path.join(B, "data-history.js"), "rb").read()).hexdigest()[:10]
_hp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_发布_public")
_n = 0
for _f in ("index.html", "review.html", "avoid.html"):
    _fp = os.path.join(_hp, _f)
    _c = io.open(_fp, encoding="utf-8").read()
    _c2, _k = re.subn(r'data-history\.js\?(?:h=[0-9a-f]+|v\d{12})', 'data-history.js?h=' + _h, _c)
    if _k:
        io.open(_fp, "w", encoding="utf-8", newline="\n").write(_c2)
        _n += _k
print("data-history.js 内容哈希 ?h=%s（HTML 更新 %d 处）" % (_h, _n))

sys.exit(0 if _r.returncode == 0 else 1)
