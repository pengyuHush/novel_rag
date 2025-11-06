# PowerShell测试运行脚本

param(
    [string]$Type = "all",
    [switch]$Verbose,
    [switch]$Coverage,
    [switch]$NoExternal,
    [switch]$NoSlow,
    [string]$Markers
)

Write-Host ""
Write-Host "╔============================================================╗" -ForegroundColor Cyan
Write-Host "║                  小说 RAG 系统测试                         ║" -ForegroundColor Cyan
Write-Host "╚============================================================╝" -ForegroundColor Cyan
Write-Host ""

# 构建pytest命令
$cmd = @("poetry", "run", "pytest")

# 测试类型
switch ($Type) {
    "unit" { $cmd += "tests/unit" }
    "integration" { $cmd += "tests/integration" }
    "e2e" { $cmd += "tests/e2e" }
    default { $cmd += "tests" }
}

# 详细输出
if ($Verbose) {
    $cmd += "-vv"
} else {
    $cmd += "-v"
}

# 代码覆盖率
if ($Coverage) {
    $cmd += "--cov=app", "--cov-report=html", "--cov-report=term-missing"
}

# 跳过外部服务
if ($NoExternal) {
    $cmd += "-m", "not external"
}

# 跳过慢速测试
if ($NoSlow) {
    if ($NoExternal) {
        $cmd[-1] += " and not slow"
    } else {
        $cmd += "-m", "not slow"
    }
}

# 自定义markers
if ($Markers) {
    $cmd += "-m", $Markers
}

# 显示配置
Write-Host "📝 测试类型: $Type" -ForegroundColor Yellow
Write-Host "📊 代码覆盖: $(if ($Coverage) { '是' } else { '否' })" -ForegroundColor Yellow
Write-Host "🌐 外部服务: $(if ($NoExternal) { '跳过' } else { '包含' })" -ForegroundColor Yellow
Write-Host "⏱️  慢速测试: $(if ($NoSlow) { '跳过' } else { '包含' })" -ForegroundColor Yellow
Write-Host ""
Write-Host "💻 执行命令: $($cmd -join ' ')" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 执行测试
& $cmd[0] $cmd[1..($cmd.Length - 1)]

$exitCode = $LASTEXITCODE

# 显示覆盖率报告路径
if ($Coverage -and $exitCode -eq 0) {
    $coveragePath = Join-Path $PWD "htmlcov/index.html"
    Write-Host ""
    Write-Host "📊 覆盖率报告: $coveragePath" -ForegroundColor Green
    Write-Host "   使用浏览器打开查看详细报告" -ForegroundColor Green
}

# 总结
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "🎉 所有测试通过!" -ForegroundColor Green
} else {
    Write-Host "⚠️  部分测试失败，请检查日志" -ForegroundColor Red
}
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode

