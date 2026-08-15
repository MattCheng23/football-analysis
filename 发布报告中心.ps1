# 一键发布足球分析预测站到 Cloudflare Pages
# 用法：右键"使用 PowerShell 运行"，或 .\发布报告中心.ps1
# 前提：已安装 wrangler 并登录（wrangler login）

$ErrorActionPreference = 'Stop'

$siteRoot = "D:\Cola\足球分析学习\_发布_public"
$project = "football-analysis-report"

if (-not (Test-Path "$siteRoot\index.html")) { throw "未找到网站主页: $siteRoot\index.html" }

Write-Host "[1/2] 部署站点目录（主页 + 批次子页面 + 样式）..." -ForegroundColor Cyan
$files = (Get-ChildItem $siteRoot -Recurse -File).Count
Write-Host "  共 $files 个文件"

Write-Host "[2/2] 部署到 Cloudflare Pages ..." -ForegroundColor Cyan
wrangler pages deploy $siteRoot --project-name $project
if ($LASTEXITCODE -ne 0) { throw "部署失败" }

Write-Host ""
Write-Host "✅ 发布完成！访问: https://$project.pages.dev" -ForegroundColor Green
Write-Host "（部署缓存约 1-2 分钟生效，如看到旧版请稍等刷新）"
