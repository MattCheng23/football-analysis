# -*- coding: utf-8 -*-
"""③ 等级持续校准：data.js 全批次等级→方向命中率统计（每批更新追踪）
用法：python level_track.py
"""
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = r"D:\Cola\足球分析学习\_发布_public\js\data.js"
src = open(SRC, encoding="utf-8").read()

def parse_lv(dir_s):
    m = re.search(r"（([^）]+级)）", dir_s or "")
    return m.group(1) if m else "无等级"

def parse_score(str_s):
    m = re.search(r"(\d+)-(\d+)（(\d+)-(\d+)）", str_s or "")
    return m.group(1), m.group(2) if m else None

# 用 vm 提取 BATCHES（与 _tmp_analyze 相同方案）
import subprocess
script = r'''
const fs=require("fs");const vm=require("vm");
const src=fs.readFileSync(String.raw`%SRC%`,"utf8");
const sandbox={};vm.createContext(sandbox);
const BATCHES=vm.runInContext(src+"\n; BATCHES",sandbox);
let rows=[];
for(const [date,b] of Object.entries(BATCHES)){
  const rmap={};
  for(const r of ((b.review&&b.review.results)||[])) rmap[r.no]=r;
  for(const m of ((b.predict&&b.predict.matches)||[])){
    const r=rmap[m.no];
    if(!r||!r.d) continue;
    rows.push({d:r.d=== "ok"?1:0, dir:m.dir});
  }
}
console.log(JSON.stringify(rows));
'''.replace("%SRC%", SRC)
r = subprocess.run(["node", "-e", script], capture_output=True)
rows = json.loads(r.stdout.decode("utf-8", errors="replace"))

agg = {}
for row in rows:
    lv = parse_lv(row["dir"])
    a = agg.setdefault(lv, [0, 0])
    a[0] += 1
    a[1] += row["d"]

print("== 等级方向命中率（全批次累计）==")
for lv, (t, h) in sorted(agg.items(), key=lambda x: -x[1][0]):
    print(f"  {lv}: {h}/{t} = {h/t*100:.1f}%")
print(f"  合计 {len(rows)} 场 | 方向 {sum(v[1] for v in agg.values())}/{len(rows)} = {sum(v[1] for v in agg.values())/len(rows)*100:.1f}%")
print("\n> 与 V10.36 参考线对比：A 级应 ≥ B 级（G2 收紧后）；无等级 ≈45%（随机线）")
