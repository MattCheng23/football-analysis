# -*- coding: utf-8 -*-
"""① λ 状态输入自动化：teams API 拉球队近 5 场（分主/客场）进失球均值
用法：python team_form.py <teamId> [--home|--away] [--n 5]
输出：近 N 场场均进球/失球（供 poisson_predict.py 输入）
"""
import sys, io, json, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = "https://www.fotmob.com/api/data/teams?id={}"
HEAD = ["curl.exe", "-s", "-A", "Mozilla/5.0", "-H", "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"]

def main():
    args = sys.argv[1:]
    if not args:
        print("用法：python team_form.py <teamId> [--home|--away] [--n 5]")
        return
    tid = args[0]
    mode = "home" if "--home" in args else ("away" if "--away" in args else "all")
    n = 5
    if "--n" in args:
        n = int(args[args.index("--n") + 1])
    r = subprocess.run(HEAD + [API.format(tid)], capture_output=True)
    d = json.loads(r.stdout.decode("utf-8", errors="replace"))
    team = (d.get("team", {}) or {}).get("name", f"#{tid}")
    fx = (d.get("fixtures", {}) or {}).get("allFixtures", {}) or {}
    fixtures = fx.get("fixtures", []) or []
    matches = []
    for f in fixtures:
        st = (f.get("status") or {})
        if not st.get("finished") or not st.get("scoreStr"):
            continue
        sc = st["scoreStr"].replace(" ", "")
        if not re.match(r"^\d+-\d+$", sc):
            continue
        home_id = ((f.get("home") or {}).get("id"))
        is_home = str(home_id) == str(tid)
        if mode == "home" and not is_home:
            continue
        if mode == "away" and is_home:
            continue
        a, b = sc.split("-")
        gf, ga = (int(a), int(b)) if is_home else (int(b), int(a))
        matches.append({"date": (st.get("utcTime") or "")[:10], "opp": (f.get("away") or {}).get("name") if is_home else (f.get("home") or {}).get("name"),
                        "gf": gf, "ga": ga, "at": "主" if is_home else "客"})
    recent = matches[-n:]
    if not recent:
        print(f"{team}（{tid}）：{mode} 近 {n} 场无已赛数据")
        return
    avg_gf = sum(m["gf"] for m in recent) / len(recent)
    avg_ga = sum(m["ga"] for m in recent) / len(recent)
    print(f"{team}（{tid}）{mode} 近 {len(recent)} 场：进 {avg_gf:.2f} / 失 {avg_ga:.2f}")
    for m in recent:
        print(f"  {m['date']} {'主' if m['at']=='主' else '客'} vs {m['opp']}: {m['gf']}-{m['ga']}")

if __name__ == "__main__":
    main()
