# ============================================================
# auto_0530.ps1 — 0912 批无人值守收尾 + 0913 周日批 001-009 赛前预测
# 由 Windows 计划任务 DSH_Auto_0912_Wrapup 在 05:30 启动
# 流程：①终场门轮询 → ②机械复盘入库+发布 → ③headless 会话做判断/蒸馏/收尾/周日预测
# 日志：D:\Cola\_tmp_football\sat0912\logs\auto_0530_<ts>.log
# ============================================================
$ErrorActionPreference = 'Continue'
$root = 'D:\Cola'
$repo = 'D:\Cola\足球分析学习'
$tmp  = 'D:\Cola\_tmp_football\sat0912'
$logd = Join-Path $tmp 'logs'
New-Item -ItemType Directory -Force -Path $logd | Out-Null
$ts   = Get-Date -Format 'yyyyMMdd_HHmmss'
$log  = Join-Path $logd "auto_0530_$ts.log"
function W($m) { $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m; $line | Tee-Object -FilePath $log -Append }
$env:PYTHONIOENCODING = 'utf-8'
Set-Location $root
W "=== AUTO 0530 START（真实时间 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')）==="

# ---------- ① 终场门：全部 30 场终场才继续（最多等 4 小时）----------
$ready = $false
for ($i = 1; $i -le 24; $i++) {
  W "终场门第 $i 次检查…"
  $out = & python "$repo\scripts\sat0912\check_all_done.py" 2>&1 | Out-String
  $code = $LASTEXITCODE
  ($out -split "`n" | Where-Object { $_.Trim() }) | ForEach-Object { W "   $_" }
  if ($code -eq 0) { $ready = $true; W "✅ 全批终场"; break }
  W "   未全终场 → 等 10 分钟后重试"
  Start-Sleep -Seconds 600
}
if (-not $ready) { W "⚠ 4 小时内未全部终场 —— 继续对已终场场次执行（缺口将在报告中标注）" }

# ---------- ② 机械复盘：抓数 → 判定 → 入库 → 门禁 → 发布 ----------
W "阶段1：机械复盘流水线"
$p1 = & python "$repo\scripts\sat0912\auto_review_pipeline.py" 2>&1 | Out-String
($p1 -split "`n" | Where-Object { $_.Trim() }) | ForEach-Object { W "   $_" }
W "阶段1：入库 + 门禁 + 发布"
$p2 = & python "$repo\scripts\sat0912\auto_ingest_reviews.py" --deploy 2>&1 | Out-String
($p2 -split "`n" | Where-Object { $_.Trim() }) | ForEach-Object { W "   $_" }

# ---------- ②b 状态快照（无论后续 headless 是否成功·都留下可核对的落盘状态）----------
W "写 AUTO_STATUS.md 状态快照"
$statusPy = @'
import io, re, sys
from pathlib import Path
R = Path(r"D:\Cola\足球分析学习"); JS = R / "_发布_public" / "js"; O = Path(r"D:\Cola\_tmp_football\sat0912")
dr = (JS / "data-review.js").read_text(encoding="utf-8")
i = dr.index('"2026-09-12": {'); nx = re.search(r'\n  "2026-\d\d-\d\d": \{', dr[i+10:])
seg = dr[i:(i+10+nx.start()) if nx else len(dr)]
nos = sorted(set(re.findall(r'no: "(\d+)", teams: "[^"]*"', seg.split("evidence: [")[0])))
dj = (JS / "data.js").read_text(encoding="utf-8"); j = dj.index('"2026-09-12": {')
rc = re.search(r"reviewedCount: (\d+),", dj[j:]); rv = re.search(r"reviewed: (\w+),", dj[j:])
lines = ["# AUTO_STATUS（脚本自动生成·机器回源）", "",
         "- 复盘入库场次：**%d 场**（%s）" % (len(nos), ",".join(nos)),
         "- data.js：reviewedCount=%s｜reviewed=%s" % (rc.group(1) if rc else "?", rv.group(1) if rv else "?"),
         "- 双日志：联赛/整体各见当日追加行",
         "- 下一步（headless 阶段 2-5）：判断补齐（归属/条款核对）→ 联赛+整体蒸馏 → V11.47 定稿 → A1/A2/B1-B12 结论 → 0913 批 001-009 赛前预测",
         "- 若本文件时间戳之后无 AUTO_TASK 报告产出 → headless 环节未完成，需人工续跑（数据与发布已完成，不会丢）", ""]
(O / "AUTO_STATUS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("AUTO_STATUS.md 已写：%d 场" % len(nos))
'@
$statusPy | Out-File -FilePath (Join-Path $tmp 'write_status.py') -Encoding utf8
& python (Join-Path $tmp 'write_status.py') 2>&1 | ForEach-Object { W "   $_" }

# ---------- ③ headless 会话：判断补齐 + 蒸馏 + 收尾 + 周日预测 ----------
W "阶段2-5：启动 headless 会话执行 AUTO_TASK_0530.md"
$dshBin = 'D:\codex\migrated\npm-roaming\node_modules\@deepseek-ai\dsh\lib\bin.js'
$prompt = '工作目录 D:\Cola。请完整执行规格文件 D:\Cola\足球分析学习\scripts\sat0912\AUTO_TASK_0530.md 的阶段 2-5（阶段 0-1 已由脚本完成，先读该文件了解全貌与已完成状态）。要求：禁跳步、每步落盘证据、只报真实数字、票面禁改、未部署=未完成；最后按阶段5 输出交付消息。'
$p3 = & node $dshBin --profile headless $prompt 2>&1 | Out-String
($p3 -split "`n" | Where-Object { $_.Trim() }) | ForEach-Object { W "   $_" }

W "=== AUTO 0530 END ==="
"COMPLETE $ts" | Out-File -FilePath (Join-Path $logd 'auto_0530_complete.marker') -Encoding utf8
