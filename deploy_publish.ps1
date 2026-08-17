# 一键发布脚本（版本号+部署+验证）—— 防止部署踩坑（2026-08-17 建立）
# 用法：.\deploy_publish.ps1 [验证关键字]
# 默认验证关键字 TEAM_RATING；发布流程：node --check → 版本号更新 → wrangler deploy → curl 验证

param(
    [string]$KeyStr = "TEAM_RATING"
)
$ErrorActionPreference = 'Stop'
$root = "D:\Cola\足球分析学习\_发布_public"
$site = "https://football-analysis-report.pages.dev"

Write-Host "[1/4] 语法检查..." -ForegroundColor Cyan
node --check "$root\js\data.js"; if ($LASTEXITCODE -ne 0) { throw "data.js 语法错误" }
node --check "$root\js\app.js";  if ($LASTEXITCODE -ne 0) { throw "app.js 语法错误" }

Write-Host "[2/4] 更新版本号（防缓存）..." -ForegroundColor Cyan
$v = 'v' + (Get-Date -Format 'yyyyMMddHHmm')
Get-ChildItem $root -Filter '*.html' | ForEach-Object {
    $c = Get-Content $_.FullName -Raw -Encoding UTF8
    if ($c -match '\?v20\d{12}') {
        $c = $c -replace '\?v20\d{12}', "?$v"
        Set-Content -Path $_.FullName -Value $c -Encoding UTF8 -NoNewline
        Write-Host "  $($_.Name) -> $v"
    }
}

Write-Host "[3/4] 部署到 Cloudflare Pages..." -ForegroundColor Cyan
wrangler pages deploy $root --project-name football-analysis-report
if ($LASTEXITCODE -ne 0) { throw "部署失败" }

Write-Host "[4/4] 线上验证（等缓存 60s）..." -ForegroundColor Cyan
Start-Sleep -Seconds 60
$probe = curl.exe -s "$site/js/data.js?v=$v"
if ($probe -match $KeyStr) {
    Write-Host "  OK：线上 data.js 含 [$KeyStr]，版本 $v" -ForegroundColor Green
} else {
    Write-Host "  FAILED：线上未发现 [$KeyStr]（等 1-2 分钟后再查或检查部署日志）" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ 发布完成！访问 $site （Ctrl+F5 强刷）" -ForegroundColor Green
