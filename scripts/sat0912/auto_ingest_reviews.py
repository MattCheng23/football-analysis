# -*- coding: utf-8 -*-
"""auto_ingest_reviews.py — 消费 auto_review_rows.json → 机械入库（无人值守·幂等·带自检回滚）

流程：读 rows → 生成 results/evidence 条目 → 追加进 data-review.js（锚点法·自动逗号）
      → reviewedCount +N → 双日志追加行 → node --check（失败即回滚）
      → 门禁（hole_guard / review_gate_check）→ --deploy 时发布
用法：python auto_ingest_reviews.py [--deploy] [--no-logs]
"""
import io, json, re, shutil, subprocess, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = Path(r"D:\Cola\足球分析学习")
JS = REPO / "_发布_public" / "js"
BAK = REPO / "_backup" / "auto_bak"
O = Path(r"D:\Cola\_tmp_football\sat0912")
LOG_L = REPO / "01_当前模型" / "联赛蒸馏日志_20260906.md"
LOG_G = REPO / "01_当前模型" / "整体蒸馏日志_20260907.md"
DEPLOY = "--deploy" in sys.argv
NOLOG = "--no-logs" in sys.argv
TS = time.strftime("%Y%m%d_%H%M%S")
LG_CN = {"001": "韩职", "002": "韩职", "003": "日职", "004": "日职", "005": "西甲", "006": "意甲",
         "007": "德甲", "008": "德甲", "009": "德甲", "010": "德甲", "011": "德甲", "012": "英超",
         "013": "英超", "014": "英超", "015": "英超", "016": "英超", "017": "西甲", "018": "法甲",
         "019": "沙职", "020": "意甲", "021": "挪超", "022": "英超", "023": "德甲", "024": "西甲",
         "025": "葡超", "026": "荷甲", "027": "意甲", "028": "法甲", "029": "英超", "030": "西甲"}
LG_KEY = {"韩职": "lg-k1", "日职": "lg-j1", "西甲": "lg-laliga", "意甲": "lg-sa", "德甲": "lg-bundes",
          "英超": "lg-eng", "法甲": "lg-ligue1", "沙职": "lg-spl", "挪超": "lg-nor", "葡超": "lg-prime",
          "荷甲": "lg-ered"}
MEDAL = {4: "🟢4/4", 3: "🟡3/4", 2: "🟡2/4", 1: "🟡1/4", 0: "🔴0/4"}


def sh(cmd, timeout=180):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, shell=isinstance(cmd, str))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build(row):
    no, a, v, mt = row["no"], row["act"], row["v"], row["mt"]
    lg = LG_CN.get(no, "")
    st = a["stats"]
    g = lambda k, d="—": ("%s:%s" % (st[k][0], st[k][1])) if k in st else d
    hs, as_ = a["hs"], a["as"]
    goals = "；".join(a["goals"]) or "无"
    cards = "；".join(a["cards"]) or "无"
    pom = a.get("pom") or {}
    pomn = gl = ""
    if isinstance(pom, dict):
        nm = pom.get("name")
        pomn = nm.get("fullName") if isinstance(nm, dict) else (nm or "")
        pomn = "%s（%s·%s）" % (pomn, pom.get("teamName") or "", (pom.get("rating") or {}).get("num") or "")
    sa = a.get("shot_agg") or {}
    rank = "四维：" + " ".join("%s%s" % (k, "✅" if v[k] == "ok" else "❌") for k in ("d", "s", "h", "ou"))
    sig = ("%s（方向%s + 比分%s + ht%s + ou%s）；%s；**红线=末段是否改判**；"
           "归属：**待模型复核**" % (MEDAL[v["n_hit"]],
                                "✅" if v["d"] == "ok" else "❌", "✅" if v["s"] == "ok" else "❌",
                                "✅" if v["h"] == "ok" else "❌", "✅" if v["ou"] == "ok" else "❌", rank))
    teams = "%s %d-%d %s" % (mt["home"], hs, as_, mt["away"])
    stats = ("**主源 FotMob matchDetails id=%s**：控球 %s、射门 %s、射正 %s、**xG %s**、绝佳机会 %s、"
             "角球 %s、黄牌 %s、**红牌 主%s:客%s**、传球 %s、射门图（主 %d 射 xG %.2f / 客 %d 射 xG %.2f）、"
             "阵型 %s vs %s（均分 %s:%s）、POM %s、球场 %s、裁判 %s；"
             "**副源 竞彩官方**：比分/半场双源核验（%s）" % (
                 IDS.get(no, "?"), g("Ball possession"), g("Total shots"), g("Shots on target"),
                 g("Expected goals (xG)"), g("Big chances"), g("Corners"), g("Yellow cards"),
                 a.get("red_h"), a.get("red_a"), g("Passes"),
                 (sa.get("主") or {}).get("n", 0), (sa.get("主") or {}).get("xG", 0),
                 (sa.get("客") or {}).get("n", 0), (sa.get("客") or {}).get("xG", 0),
                 a.get("form_h"), a.get("form_a"), a.get("rating_h"), a.get("rating_a"),
                 pomn or "—", a.get("stadium") or "—", a.get("referee") or "—",
                 "一致" if row.get("dual_ok", True) else "⚠待核"))
    txt = ("全场 %d-%d（半场 %d-%d）：%s。预测 %s %s、ht %s、ou %s：%s＝**%s**。"
           "牌：%s。要点：①**机械复核四维**（本条目由 auto_review_pipeline 自动生成）；"
           "②下一阶段由模型补：错因归属（L 联赛层/G 整体层/M 场级）、联赛条款核对、"
           "让位/冷门/反向槽执行情况、红牌与演戏排查六项。归属：**待模型复核**" % (
               hs, as_, a["ht"][0], a["ht"][1], goals, mt["dir"], mt["sc"], mt["ht"], mt["ou"], rank,
               MEDAL[v["n_hit"]], cards))
    RES = ('        { no: "%s", teams: "%s", league: "%s", lg: "%s", score: "%d-%d（%d-%d）", '
           'd: "%s", s: "%s", h: "%s", ou: "总进球 %s", signal: "%s", sc: "%s" }' % (
               no, teams, lg, LG_KEY.get(lg, "lg-other"), hs, as_, a["ht"][0], a["ht"][1],
               v["d"], v["s"], v["h"], mt["ou"].replace("总进球 ", ""), esc(sig),
               "ok" if v["n_hit"] >= 3 else ("watch" if v["n_hit"] == 2 else "miss")))
    EVI = ('        { no: "%s", teams: "%s", league: "%s", lg: "%s", stats: "%s", signal: "%s", txt: "%s" }' % (
        no, teams, lg, LG_KEY.get(lg, "lg-other"), esc(stats), esc(sig), esc(txt)))
    return RES, EVI, v


IDS = json.load(io.open(O / "fm_ids.json", encoding="utf-8"))
rows = json.load(io.open(O / "auto_review_rows.json", encoding="utf-8"))
main = json.loads("{}")
rows = [r for r in rows if r.get("dual_ok", True)]
if not rows:
    print("无待入库场次（rows 空或全部待核）"); sys.exit(0)
print("准备入库 %d 场：%s" % (len(rows), ",".join(r["no"] for r in rows)))

dr_path = JS / "data-review.js"
dj_path = JS / "data.js"
shutil.copy2(dr_path, BAK / ("data-review.js_%s_preauto.bak" % TS))
shutil.copy2(dj_path, BAK / ("data.js_%s_preauto.bak" % TS))
dr = dr_path.read_text(encoding="utf-8")
dj = dj_path.read_text(encoding="utf-8")

RES_list, EVI_list, verdicts = [], [], {}
b0 = dr.index('"2026-09-12": {')
nxt = re.search(r'\n  "2026-\d\d-\d\d": \{', dr[b0 + 10:])
b1 = b0 + 10 + nxt.start() if nxt else len(dr)
seg0912 = dr[b0:b1]

for r in sorted(rows, key=lambda z: z["no"]):
    if re.search(r'no: "%s", teams: "%s[^"]*"[\s\S]{0,200}?score: "\d+-\d+"' % (r["no"], re.escape(r["mt"]["home"])), seg0912):
        print("  跳过（已入库）：%s" % r["no"]); continue
    RES, EVI, v = build(r)
    RES_list.append(RES); EVI_list.append(EVI); verdicts[r["no"]] = v


def append_before(dr, anchor, entries):
    i = dr.index(anchor, b0)
    head = dr[:i].rstrip()
    assert head.endswith("}"), "锚点前不是条目结尾：%s" % head[-60:]
    tail = dr[len(head):]
    return head + ",\n" + ",\n".join(entries) + "\n" + tail


if RES_list:
    a_res = dr.index("      ],\n      evidence: [", b0)
    dr = append_before(dr, "      ],\n      evidence: [", RES_list)
    a_evi = dr.index("      ],\n      avoidHigh:", b0)
    dr = append_before(dr, "      ],\n      avoidHigh:", EVI_list)
dr_path.write_text(dr, encoding="utf-8", newline="\n")

# reviewedCount = 机器回源（0912 块 results 条目数·防漂移）
dr2 = dr_path.read_text(encoding="utf-8")
b0b = dr2.index('"2026-09-12": {')
nx = re.search(r'\n  "2026-\d\d-\d\d": \{', dr2[b0b + 10:])
b1b = b0b + 10 + nx.start() if nx else len(dr2)
true_cnt = len(re.findall(r'no: "\d+", teams: "[^"]*",[\s\S]{0,200}?score: "\d+-\d+"', dr2[b0b:b1b]))
dj = dj_path.read_text(encoding="utf-8")
# ⚠ 2026-09-12 事故：原用 data-review.js 的偏移 b0b 去索引 data.js → 命中错误批次（曾把 0912 的
#   reviewedCount 写成 09-08 批的值）。此处改为在 data.js 内独立定位 0912 块。
dj0 = dj.index('"2026-09-12": {')
m = re.search(r"reviewedCount: (\d+),", dj[dj0:])
cur = int(m.group(1))
dj = dj[:dj0 + m.start()] + ("reviewedCount: %d," % true_cnt) + dj[dj0 + m.end():]
dj_path.write_text(dj, encoding="utf-8", newline="\n")
print("reviewedCount %d → %d（按 0912 块实际条目数校正）" % (cur, true_cnt))

rc, out = sh(["node", "--check", str(dr_path)])
if rc != 0:
    shutil.copy2(BAK / ("data-review.js_%s_preauto.bak" % TS), dr_path)
    shutil.copy2(BAK / ("data.js_%s_preauto.bak" % TS), dj_path)
    print("❌ node --check 失败 → 已回滚\n%s" % out[-800:]); sys.exit(1)
rc2, out2 = sh(["node", "--check", str(dj_path)])
if rc2 != 0:
    shutil.copy2(BAK / ("data.js_%s_preauto.bak" % TS), dj_path)
    print("❌ data.js 语法失败 → 回滚\n%s" % out2[-600:]); sys.exit(1)
print("✅ 语法检查通过（data-review.js / data.js）")

if not NOLOG and RES_list:
    for no, v in verdicts.items():
        r = [x for x in rows if x["no"] == no][0]
        a = r["act"]
        lg = LG_CN.get(no, "")
        L = ("| 9/12 | %s %s %d-%d %s | %s | %d-%d（%d-%d） | %s；四维 %s＝%s | "
             "【条款核对】待模型复核（auto 入库） |\n" % (
                 no, r["mt"]["home"], a["hs"], a["as"], r["mt"]["away"], lg, a["hs"], a["as"],
                 a["ht"][0], a["ht"][1], "；".join(a["goals"])[:120], MEDAL[v["n_hit"]], MEDAL[v["n_hit"]]))
        with LOG_L.open("a", encoding="utf-8", newline="\n") as f:
            f.write(L)
        G = ("| 9/12 | %s %s %d-%d %s（0912 批） | %s | 待模型复核（auto 入库·四维 %s） | 待归属 |\n" % (
            no, r["mt"]["home"], a["hs"], a["as"], r["mt"]["away"], MEDAL[v["n_hit"]],
            " ".join("%s:%s" % (k, v[k]) for k in ("d", "s", "h", "ou"))))
        with LOG_G.open("a", encoding="utf-8", newline="\n") as f:
            f.write(G)
    print("✅ 双日志已追加 %d 行" % len(verdicts))

print()
for cmd in (["python", r"D:\Cola\_tmp_football\hole_guard.py", str(dr_path)],
            ["python", r"D:\Cola\_tmp_football\review_gate_check.py", "2026-09-12"]):
    rc, out = sh(cmd)
    print("$ %s\n%s" % (" ".join(cmd[1:]), out.strip()[-500:]))
if DEPLOY:
    rc, out = sh(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                  str(REPO / "deploy_publish.ps1")], timeout=600)
    print("部署：\n%s" % out.strip()[-800:])
