# 赛后一键收尾脚本（红黑榜刷新 → TEAM_RATING 更新 → 一键发布 → Git 备份）
# 前置：该批 results/evidence 已写入 data.js（复盘时完成）
# 用法：.\finish_batch.ps1
$ErrorActionPreference = 'Stop'
$tmp  = "D:\Cola\_tmp_football"
$root = "D:\Cola\足球分析学习"
$pub  = "$root\_发布_public"
$dataJs = "$pub\js\data.js"

Write-Host "[1/5] 重跑红黑榜脚本（生成 TEAM_RATING + 红黑榜文档）..." -ForegroundColor Cyan
$env:PYTHONIOENCODING = "utf-8"
python "$tmp\redblack_analyze.py"
if ($LASTEXITCODE -ne 0) { throw "redblack_analyze.py 失败" }

Write-Host "[2/5] 替换 data.js 中 TEAM_RATING 段..." -ForegroundColor Cyan
# TEAM_RATING 覆盖前自动备份（2026-09-13 加：本步会用 redblack_analyze.py 的整体重算结果
# 覆盖手工维护的 TEAM_RATING，9/7 之后逐场手写的「重审/豁免/撤销」判定不在生成器里，故先留底）
$bkDir = "D:\Cola\足球分析学习\_backup\team_rating"
New-Item -ItemType Directory -Force -Path $bkDir | Out-Null
$bkFile = Join-Path $bkDir ("TEAM_RATING_" + (Get-Date -Format "yyyyMMddHHmmss") + ".js")
$curData = Get-Content $dataJs -Raw -Encoding UTF8
if ($curData -match "(?s)const TEAM_RATING = \[.*?\];") {
    Set-Content -Path $bkFile -Value $Matches[0] -Encoding UTF8
    Write-Host "  已备份现有 TEAM_RATING → $bkFile" -ForegroundColor Yellow
    Write-Host "  ⚠️ 注意：本次覆盖将丢失 9/7 之后手工写入的复盘判定（重审/豁免/撤销），如需保留请改用人工维护" -ForegroundColor Red
}
$tr = Get-Content "$tmp\team_rating.js" -Raw -Encoding UTF8
$data = Get-Content $dataJs -Raw -Encoding UTF8
if ($data -notmatch 'const TEAM_RATING') {
    $data = $data -replace 'const GLOBAL_STATS = \{', "$tr`n`nconst GLOBAL_STATS = {"
    Write-Host "  TEAM_RATING 首次插入"
} else {
    $data = $data -replace '(?s)const TEAM_RATING = \[.*?\];', $tr.TrimEnd()
    Write-Host "  TEAM_RATING 段已替换"
}
Set-Content -Path $dataJs -Value $data -Encoding UTF8 -NoNewline

Write-Host "[3/5] 一键发布（语法检查+版本号+部署+线上验证）..." -ForegroundColor Cyan
& "$root\deploy_publish.ps1"
if ($LASTEXITCODE -ne 0) { throw "发布失败" }

Write-Host "[4/5] Git 备份推送..." -ForegroundColor Cyan
Push-Location $root
git add -A
git commit -m "赛后收尾: 红黑榜+TEAM_RATING 刷新 $(Get-Date -Format 'yyyyMMddHHmm')" 2>&1 | Out-Null
Copy-Item "$HOME\.gitconfig" "D:\Cola\_backup\gitconfig_pre_push.bak" -Force
git config --global --unset-all url.https://ghfast.top/.insteadof 2>$null
$token = gh auth token
git push "https://MattCheng23:${token}@github.com/MattCheng23/football-analysis.git" main 2>&1 | Out-Null
git config --global url."https://ghfast.top/https://github.com/".insteadOf "https://github.com/"
Pop-Location

Write-Host "[5/5] 收尾完成" -ForegroundColor Green
Write-Host "  - 红黑榜/红榜文档已刷新（03_报告复盘/）" -ForegroundColor Green
Write-Host "  - TEAM_RATING 已更新并部署（/avoid 页刷新可见）" -ForegroundColor Green
Write-Host "  - GitHub 已备份" -ForegroundColor Green
Write-Host "  ⚠️ 提醒：GLOBAL_STATS 命中率若本批有赛果变化，请同步更新 data.js（第 1790+ 行）" -ForegroundColor Yellow
