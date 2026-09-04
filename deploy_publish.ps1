# 一键发布脚本（版本号+部署+验证）—— 防止部署踩坑（2026-08-17 建立；2026-09-05 修复：版本正则+计数断言+验证首页+BOM 兼容）
# 用法：.\deploy_publish.ps1
# 发布流程：node --check → 版本号更新（计数断言）→ wrangler deploy → curl 验证首页版本号

$ErrorActionPreference = 'Stop'
$root = "D:\Cola\足球分析学习\_发布_public"
$site = "https://football-analysis-report.pages.dev"

Write-Host "[1/4] 语法检查..." -ForegroundColor Cyan
node --check "$root\js\data.js"; if ($LASTEXITCODE -ne 0) { throw "data.js 语法错误" }
node --check "$root\js\app.js";  if ($LASTEXITCODE -ne 0) { throw "app.js 语法错误" }

Write-Host "[2/4] 更新版本号（防缓存）..." -ForegroundColor Cyan
$v = 'v' + (Get-Date -Format 'yyyyMMddHHmm')
$cnt = 0
Get-ChildItem $root -Filter '*.html' | ForEach-Object {
    $c = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    $m = [regex]::Matches($c, '\?v\d{12}')
    if ($m.Count -gt 0) {
        $c = [regex]::Replace($c, '\?v\d{12}', '?' + $v)
        [System.IO.File]::WriteAllText($_.FullName, $c, (New-Object System.Text.UTF8Encoding($false)))
        $cnt += $m.Count
        Write-Host "  $($_.Name) -> $v ($($m.Count))"
    }
}
Write-Host "  共替换 $cnt 处版本号"
if ($cnt -eq 0) { throw "无 HTML 含版本号 ?v\d{12}——正则已过期或文件异常，禁止部署" }

Write-Host "[3/4] 部署到 Cloudflare Pages..." -ForegroundColor Cyan
wrangler pages deploy $root --project-name football-analysis-report
if ($LASTEXITCODE -ne 0) { throw "部署失败" }

Write-Host "[4/4] 线上验证（等缓存 60s）..." -ForegroundColor Cyan
Start-Sleep -Seconds 60
$probe = curl.exe -s "$site/index.html"
if ($probe -match [regex]::Escape("?$v")) {
    Write-Host "  OK：线上首页已引用版本 $v（缓存已失效）" -ForegroundColor Green
} else {
    Write-Host "  FAILED：线上首页未发现 ?$v（等 1-2 分钟后再查或检查部署日志）" -ForegroundColor Yellow
    exit 1
}
Write-Host "发布完成！访问 $site （Ctrl+F5 强刷）" -ForegroundColor Green
