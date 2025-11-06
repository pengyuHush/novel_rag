# 重新处理失败的小说
# 用法：
#   .\reprocess_failed.ps1              # 重新处理所有失败的小说
#   .\reprocess_failed.ps1 <novel_id>   # 重新处理指定的小说

param(
    [string]$NovelId = ""
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "重新处理失败的小说" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 切换到backend目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查是否在虚拟环境中
$poetryEnv = poetry env info --path 2>$null
if (-not $poetryEnv) {
    Write-Host "错误: 未找到Poetry虚拟环境" -ForegroundColor Red
    Write-Host "请先运行: poetry install" -ForegroundColor Yellow
    exit 1
}

Write-Host "使用虚拟环境: $poetryEnv" -ForegroundColor Green
Write-Host ""

if ($NovelId) {
    Write-Host "重新处理小说ID: $NovelId" -ForegroundColor Yellow
    poetry run python reprocess_failed.py $NovelId
} else {
    Write-Host "重新处理所有失败的小说" -ForegroundColor Yellow
    poetry run python reprocess_failed.py
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "处理完成" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

