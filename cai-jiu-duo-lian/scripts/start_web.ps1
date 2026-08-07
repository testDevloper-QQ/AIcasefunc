# 启动菜就多练 Web 服务（自动检测 Python，支持局域网）
param(
    [switch]$Lan,
    [int]$Port = 0
)

Set-Location $PSScriptRoot\..

function Resolve-PythonCommand {
    if ($env:CAIJIU_PYTHON -and (Test-Path -LiteralPath $env:CAIJIU_PYTHON)) {
        return @{ Exe = $env:CAIJIU_PYTHON; Args = @() }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Exe = "python"; Args = @() }
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Exe = "py"; Args = @("-3") }
    }
    Write-Error @"
未找到 Python。请任选其一：
  1. 安装 Python 3.10+ 并加入 PATH
  2. 设置环境变量 CAIJIU_PYTHON 指向 python.exe
  3. 安装 Windows Python Launcher (py)
"@
    exit 1
}

$py = Resolve-PythonCommand
$argsList = @($py.Args + "scripts/ensure_web_server.py", "--foreground")
if ($Lan) { $argsList += "--lan" }
if ($Port -gt 0) { $argsList += @("--port", "$Port") }

Write-Host "启动菜就多练 Web 服务..."
if ($Lan) {
    Write-Host "模式: 局域网 (0.0.0.0)"
} else {
    Write-Host "模式: 本机 (127.0.0.1)；手机访问请加 -Lan"
}

& $py.Exe @argsList
exit $LASTEXITCODE
