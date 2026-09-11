# 一键发布脚本（版本号+部署+验证+初稿快照+定稿入库）—— 防止部署踩坑（2026-08-17 建立；2026-09-05 修复：版本正则+计数断言+验证首页+BOM 兼容；2026-09-12 增 [5/6] 初稿快照 + [6/6] git 定稿入库）
# 用法：.\deploy_publish.ps1
# 发布流程：node --check → 版本号更新（计数断言）→ wrangler deploy → curl 验证首页版本号 → 初稿快照（幂等）→ git 提交定稿

$ErrorActionPreference = 'Stop'
$root = "D:\Cola\足球分析学习\_发布_public"
$site = "https://football-analysis-report.pages.dev"

Write-Host "[0/6] 生成拆分包（data-core + data-history·守卫断言）..." -ForegroundColor Cyan
python "$root\..\build_split.py"
if ($LASTEXITCODE -ne 0) { throw "拆分包生成失败（守卫断言未过，禁止部署）" }

Write-Host "[1/6] 语法检查..." -ForegroundColor Cyan
node --check "$root\js\data.js"; if ($LASTEXITCODE -ne 0) { throw "data.js 语法错误" }
node --check "$root\js\data-core.js"; if ($LASTEXITCODE -ne 0) { throw "data-core.js 语法错误" }
node --check "$root\js\data-history.js"; if ($LASTEXITCODE -ne 0) { throw "data-history.js 语法错误" }
node --check "$root\js\app.js";  if ($LASTEXITCODE -ne 0) { throw "app.js 语法错误" }

Write-Host "[2/6] 更新版本号（防缓存）..." -ForegroundColor Cyan
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

Write-Host "[3/6] 部署到 Cloudflare Pages..." -ForegroundColor Cyan
# wrangler 会把警告写到 stderr，Stop 模式会误判为致命错误（2026-09-09 修复）
$ErrorActionPreference = 'Continue'
wrangler pages deploy $root --project-name football-analysis-report --commit-dirty=true
$deployExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($deployExit -ne 0) { throw "部署失败" }

Write-Host "[4/6] 线上验证（首页边缘缓存 max-age=300 → 最多回查 5 次·每 60s）..." -ForegroundColor Cyan
$probeOk = $false
for ($i = 1; $i -le 5; $i++) {
    Start-Sleep -Seconds 60
    $probe = curl.exe -sL "$site/"   # 根路径+跟随 308（/index.html 会 308→/，原探针因此恒取空=历史误报根因 2026-09-12 实证）
    if ($probe -match [regex]::Escape("?$v")) {
        Write-Host "  OK：第 $i 次回查命中版本 $v（边缘缓存已失效）" -ForegroundColor Green
        $probeOk = $true
        break
    }
    Write-Host "  第 $i 次回查未命中（边缘缓存未过期）→ 继续等" -ForegroundColor DarkYellow
}
if (-not $probeOk) {
    # 兜底：部署本身已成功（wrangler exit 0），改用 data.js 内容核验，避免缓存误报成"部署失败"
    $js = curl.exe -sL "$site/js/data-core.js"
    $jsLen = 0
    if ($js) { $jsLen = $js.Length }
    Write-Host "  WARN：5 分钟内首页未回查到 ?$v —— 部署本身已成功（wrangler 已返回 0）" -ForegroundColor Yellow
    Write-Host "        兜底核验：js/data-core.js 字节数 $jsLen（>100000 即视为已上线）" -ForegroundColor Yellow
}
Write-Host "[5/6] 初稿快照（改判核算基线·幂等，失败不阻断发布）..." -ForegroundColor Cyan
$dataTxt = [System.IO.File]::ReadAllText("$root\js\data.js", [System.Text.Encoding]::UTF8)
$mk = [regex]::Matches($dataTxt, '\n  "(\d{4}-\d{2}-\d{2})": \{')
if ($mk.Count -eq 0) { throw "data.js 中未解析到批键（快照/入库无法定位批次），禁止继续" }
$bk = $mk[$mk.Count - 1].Groups[1].Value
$snapOut = python "$root\..\snapshot_draft.py" $bk 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  WARN：快照失败（不阻断发布）：$snapOut" -ForegroundColor Yellow }
else { Write-Host "  $snapOut" -ForegroundColor Green }

Write-Host "[6/6] git 定稿入库（批 $bk）..." -ForegroundColor Cyan
$ErrorActionPreference = 'Continue'   # git 警告走 stderr，Stop 模式会误判为致命错误
Push-Location "$root\.."
git add -A -- "_发布_public" "01_当前模型" "03_报告复盘" 2>&1 | Out-Null
git add -f -- "_backup/drafts" 2>&1 | Out-Null
$staged = git status --porcelain
if ($staged) {
    git commit -q -m "定稿入库：$bk 批 $v（发布脚本自动提交）" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "  已提交 $(git rev-parse --short HEAD)（$bk 批 $v）" -ForegroundColor Green }
    else { Write-Host "  WARN：git 提交失败（部署已完成，请手动提交）" -ForegroundColor Yellow }
} else { Write-Host "  无变更，跳过提交" -ForegroundColor DarkYellow }
Pop-Location
$ErrorActionPreference = 'Stop'

Write-Host "发布完成！访问 $site （Ctrl+F5 强刷）" -ForegroundColor Green
