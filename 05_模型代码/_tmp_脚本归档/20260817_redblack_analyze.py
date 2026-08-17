# -*- coding: utf-8 -*-
"""红黑榜全量分析 v3：解析 data.js 全部批次 results/avoid，按队伍聚合红黑积分（合并同队异名+league）"""
import re, io

path = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 同队异名归一化（按历史批次实际出现的名字）
NORM = {
    "富川": "富川FC", "仁川": "仁川联", "索尔纳": "AIK索尔纳",
    "塞伊奈约基": "塞伊奈约基SJK", "塞那乔其": "塞伊奈约基SJK", "赫尔辛基": "HJK赫尔辛基",
    "米拉索": "米拉索尔", "图尔库国际": "国际图尔库", "盖斯": "哥德堡盖斯",
    "KFUM奥斯陆": "奥斯陆KFUM", "格风暴": "格拉茨风暴", "哈姆斯塔德": "哈尔姆斯",
}

def norm(t):
    return NORM.get(t, t)

batch_re = re.compile(r'^  "(\d{4}-\d{2}-\d{2})": \{')
batches = []
for i, ln in enumerate(lines):
    m = batch_re.match(ln)
    if m:
        batches.append((m.group(1), i))
batches.append(("__END__", len(lines)))

res_re = re.compile(r'\{ no: "\d+", teams: "([^"]+)", league: "([^"]+)", .*?score: "([^"]+)", d: "(ok|no)", s: "(ok|no)", h: "(ok|no)", signal: "([^"]*)", sc: "([^"]*)" \}')
avoid_re = re.compile(r'\{ team: "([^"]+)", league: "([^"]+)", reason: "([^"]*)" \}')
# 演戏/剧本关键词（signal 中出现且 sc=watch 时计嫌疑；裸 🟡/观察 不算）
SUS_WORDS = ["演", "剧本", "嫌疑", "倒挂", "惨败", "绝杀", "收缩", "放水", "跨线", "收割", "控分", "闪击", "爆冷", "逆转"]

teams = {}

def rec(t):
    return teams.setdefault(norm(t), {"league": set(), "play": 0, "triple": 0, "score_hit": 0, "dir_hit": 0,
                                      "susp": 0, "danger": 0, "red": 0, "black": 0, "avoid_high": 0, "avoid_watch": 0})

for bi in range(len(batches) - 1):
    date, start = batches[bi]
    end = batches[bi + 1][1]
    seg = lines[start:end]
    for ln in seg:
        m = res_re.search(ln)
        if m:
            teams_name, league, score, d, s, h, signal, sc = m.groups()
            home, away = [x.strip() for x in teams_name.split("vs")]
            for t in (home, away):
                rec(t)["play"] += 1
                rec(t)["league"].add(league)
            is_susp = (sc == "danger") or (sc == "watch" and any(w in signal for w in SUS_WORDS))
            if d == "ok":
                for t in (home, away): rec(t)["dir_hit"] += 1
            if s == "ok":
                for t in (home, away): rec(t)["score_hit"] += 1
            if d == "ok" and s == "ok" and h == "ok":
                for t in (home, away): rec(t)["triple"] += 1
            if is_susp:
                for t in (home, away):
                    rec(t)["susp"] += 1
                    if sc == "danger":
                        rec(t)["danger"] += 1
                        rec(t)["black"] += 2
                    else:
                        rec(t)["black"] += 1
            else:
                for t in (home, away):
                    if d == "ok" and s == "ok" and h == "ok":
                        rec(t)["red"] += 2
                    elif s == "ok":
                        rec(t)["red"] += 1
        m2 = avoid_re.search(ln)
        if m2:
            team, league, reason = m2.groups()
            before = "".join(seg[:seg.index(ln)])
            kind = "high" if before.rfind("avoidHigh:") > before.rfind("avoidWatch:") else "watch"
            r = rec(team)
            r["league"].add(league)
            r["reason"] = reason  # 保留最新 reason（黑榜展示用）
            if kind == "high":
                r["black"] += 2
                r["avoid_high"] += 1
            else:
                r["black"] += 1
                r["avoid_watch"] += 1

def rating(r):
    if r["avoid_high"] or r["danger"] >= 2 or r["black"] >= 3:
        return "🔴黑榜"
    if r["avoid_watch"] or r["black"] >= 1:
        return "🟡偏黑"
    if r["triple"] >= 2:
        return "⭐红榜·稳定"
    if r["triple"] >= 1:
        return "🟢偏红"
    return "⚪中性"

rows = []
for t, r in teams.items():
    rows.append((t, ",".join(sorted(r["league"])), r["play"], r["triple"], r["score_hit"], r["dir_hit"],
                 r["susp"], r["danger"], r["red"], r["black"], rating(r)))

order = {"⭐红榜·稳定": 0, "🟢偏红": 1, "⚪中性": 2, "🟡偏黑": 3, "🔴黑榜": 4}
rows.sort(key=lambda r: (order[r[10]], -(r[8] - r[9]), -r[3]))

out = io.StringIO()
out.write("# 全量红黑榜（2026-07-21 ~ 08-16 全部 26 批次，按队伍聚合）\n\n")
out.write("> 红分：三指标全中 +2 / 比分命中(正路) +1；黑分：演戏嫌疑 danger +2 / watch+剧本信号 +1 / 避雷🔴 +2 / 避雷🟡 +1。\n")
out.write("> 评级：⭐红榜·稳定=三指标全中≥2 且 0 演戏信号；🟢偏红=1 次三指标全中且干净；🔴黑榜=danger≥2 或黑分≥3；🟡偏黑=黑分≥1；⚪中性。\n")
out.write("> 注：早期批次（8/14 前）results 未标 danger/watch，演戏信号以避雷名单兜底；同队异名已合并。\n\n")
out.write("| 队伍 | 联赛 | 场次 | 三指标全中 | 比分命中 | 方向命中 | 演戏嫌疑 | 红分 | 黑分 | 评级 |\n")
out.write("|---|---|---|---|---|---|---|---|---|---|\n")
for r in rows:
    out.write("| %s | %s | %d | %d | %d | %d | %d | %d | %d | %s |\n" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[8], r[9], r[10]))

outpath = r"D:\Cola\足球分析学习\03_报告复盘\红黑榜_全量_20260817.md"
with open(outpath, "w", encoding="utf-8") as f:
    f.write(out.getvalue())

# ===== 生成网页 TEAM_RATING 段 =====
gcode = {"⭐红榜·稳定": "R2", "🟢偏红": "R1", "⚪中性": "N", "🟡偏黑": "B1", "🔴黑榜": "B2"}
js = io.StringIO()
js.write("/* 红黑总榜（队伍评级，R358，由 redblack_analyze.py 自动生成） */\n")
js.write("const TEAM_RATING = [\n")
for r in rows:
    t, league, play, triple, sh, dh, susp, danger, red, black, g = r
    reason = teams[t].get("reason", "")
    rs = (', rs: "' + reason.replace('"', "'") + '"') if (reason and gcode[g] in ("B1", "B2")) else ""
    js.write('  { t: "%s", lg: "%s", p: %d, tp: %d, sh: %d, sp: %d, r: %d, b: %d, g: "%s"%s },\n'
             % (t.replace('"', "'"), league, play, triple, sh, susp, red, black, gcode[g], rs))
js.write("];\n")
with open(r"D:\Cola\_tmp_football\team_rating.js", "w", encoding="utf-8") as f:
    f.write(js.getvalue())
print("team_rating.js saved, entries:", len(rows))

print("saved OK, teams:", len(rows))

from collections import Counter
c = Counter(r[10] for r in rows)
for k in ["⭐红榜·稳定", "🟢偏红", "⚪中性", "🟡偏黑", "🔴黑榜"]:
    print(k, c.get(k, 0))
print("\n== STAR_RED ==")
for r in rows:
    if r[10] == "⭐红榜·稳定":
        print(f"{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[8]}")
print("\n== BLACK ==")
for r in rows:
    if r[10] == "🔴黑榜":
        print(f"{r[0]}|{r[1]}|{r[2]}|{r[6]}|{r[9]}")
print("\n== GRAY_BLACK ==")
for r in rows:
    if r[10] == "🟡偏黑":
        print(f"{r[0]}|{r[1]}|{r[2]}|{r[6]}|{r[9]}")
print("\n== P_RED ==")
for r in rows:
    if r[10] == "🟢偏红":
        print(f"{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[8]}")
