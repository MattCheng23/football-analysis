# -*- coding: utf-8 -*-
"""check_all_done.py — 全批终场门（030 完赛判定）
①刷新官方快照（WebBridge）②解析官方状态＋FotMob finished ③全部终场 → exit 0；否则 exit 1（打印待完赛场次）
用法：python check_all_done.py [--no-refresh]
"""
import importlib.util, io, json, subprocess, sys, time
from pathlib import Path

O = Path(r"D:\Cola\_tmp_football\sat0912")
REFRESH = "--no-refresh" not in sys.argv

if REFRESH:
    r = subprocess.run([sys.executable, str(O / "fetch_official_snap.py")], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    print("官方快照刷新：rc=%s（%s）" % (r.returncode, (r.stdout or "")[-120:].replace("\n", " ")))

spec = importlib.util.spec_from_file_location("arp", r"D:\Cola\足球分析学习\scripts\sat0912\auto_review_pipeline.py")
m = importlib.util.module_from_spec(spec)
sys.argv = ["arp", "--dry-run"]
spec.loader.exec_module(m)
off = m.official_scores()
IDS = json.load(io.open(O / "fm_ids.json", encoding="utf-8"))
HDR = "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34"
pending, done = [], []
for no in sorted(IDS):
    o = off.get(no) or {}
    fm_fin = False
    try:
        r = subprocess.run(["curl.exe", "-s", "-m", "25", "-H", HDR,
                            "https://www.fotmob.com/api/data/matchDetails?matchId=%s" % IDS[no]],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=40)
        fm_fin = bool((json.loads(r.stdout).get("general") or {}).get("finished"))
    except Exception:
        pass
    (done if (o.get("done") or fm_fin) else pending).append(no)
print("已终场 %d 场：%s" % (len(done), ",".join(done)))
print("待完赛 %d 场：%s" % (len(pending), ",".join(pending)))
sys.exit(0 if not pending else 1)
