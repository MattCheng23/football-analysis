# ============================================================
# resume_wrapup.ps1 — 自愈补跑（08:30 触发）：主任务若未完成则续跑
# 逻辑：①主任务仍在跑 → 直接退出（不打扰）②已完成（marker 存在 + 报告齐）→ 退出
#       ③未完成 → 幂等重跑机械阶段 + headless 判断阶段
# ============================================================
$root = 'D:\Cola'; $repo = 'D:\Cola\足球分析学习'; $tmp = 'D:\Cola\_tmp_football\sat0912'
$logd = Join-Path $tmp 'logs'; New-Item -ItemType Directory -Force -Path $logd | Out-Null
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'; $log = Join-Path $logd "resume_$ts.log"
function W($m) { ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) | Tee-Object -FilePath $log -Append }
$env:PYTHONIOENCODING = 'utf-8'; Set-Location $root
W "=== RESUME 检查 ==="

$busy = (Get-Process -Name node,pwsh,powershell -ErrorAction SilentlyContinue |
         Where-Object { $_.StartTime -gt (Get-Date).AddHours(-6) } | Measure-Object).Count
$marker = Join-Path $logd 'auto_0530_complete.marker'
$report = Join-Path $repo '03_报告复盘\260913_赛前分析_001-009.md'
if ((Test-Path $report) -and (Test-Path $marker)) { W "已完成（报告+marker 齐）→ 退出"; exit 0 }
if (Test-Path $marker) { W "主任务已跑完标记，但周日批报告缺失 → 只补 headless 判断阶段" }

W "busy 进程数（近 6h 启动的 node/powershell）=$busy"
W "阶段A：机械复盘（幂等·只补缺失场次）"
& python "$repo\scripts\sat0912\auto_review_pipeline.py" 2>&1 | ForEach-Object { W "   $_" }
& python "$repo\scripts\sat0912\auto_ingest_reviews.py" --deploy 2>&1 | ForEach-Object { W "   $_" }
& python "$tmp\write_status.py" 2>&1 | ForEach-Object { W "   $_" }

W "阶段B：headless 判断/蒸馏/收尾/周日预测"
$dshBin = 'D:\codex\migrated\npm-roaming\node_modules\@deepseek-ai\dsh\lib\bin.js'
$prompt = '工作目录 D:\Cola。这是补跑：请先读 D:\Cola\足球分析学习\scripts\sat0912\AUTO_STATUS.md 与 AUTO_TASK_0530.md，判断哪些阶段尚未完成（幂等，已完成的不要重做），然后完成剩余阶段（判断补齐→联赛+整体蒸馏→V11.47 定稿→A1/A2/B1-B12 结论→0913 批 001-009 赛前预测与上线）。禁跳步、票面禁改、未部署=未完成。'
& node $dshBin --profile headless $prompt 2>&1 | ForEach-Object { W "   $_" }
W "=== RESUME END ==="
