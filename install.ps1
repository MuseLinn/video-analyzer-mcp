# Video Analyzer MCP Server — PowerShell 安装脚本
# 用法: irm https://raw.githubusercontent.com/MoonshotAI/video-analyzer-mcp/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }

$InstallDir = Join-Path $env:USERPROFILE ".mcp" "video-analyzer"
$RepoUrl = "https://github.com/MoonshotAI/video-analyzer-mcp.git"

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Find-Python {
    $candidates = @("python", "python3", "py")
    foreach ($c in $candidates) {
        if (Test-Command $c) {
            return (Get-Command $c).Source
        }
    }
    Write-Error "未找到 Python。请先安装 Python: https://python.org"
    exit 1
}

function Find-Kimi {
    if (Test-Command "kimi") {
        return (Get-Command "kimi").Source
    }
    Write-Error "未找到 kimi 命令。请先安装 kimi-cli: https://github.com/MoonshotAI/kimi-cli"
    exit 1
}

function Install-McpServer {
    Write-Info "Video Analyzer MCP Server — 安装"
    Write-Host "========================================" -ForegroundColor Cyan

    # 1. Check Python
    Write-Info "检测 Python..."
    $python = Find-Python
    Write-Success "Python: $python"

    # 2. Check kimi
    Write-Info "检测 kimi-cli..."
    $kimi = Find-Kimi
    Write-Success "kimi: $kimi"

    # 3. Check git
    if (-not (Test-Command "git")) {
        Write-Error "未找到 git。请先安装 Git: https://git-scm.com/download/win"
        exit 1
    }

    # 4. Clone or update
    $gitDir = Join-Path $InstallDir ".git"
    if (Test-Path $gitDir) {
        Write-Info "目录已存在，尝试更新..."
        Push-Location $InstallDir
        git pull
        Pop-Location
    } elseif (Test-Path $InstallDir) {
        Write-Warn "安装目录存在但不是 git repo，将重新克隆..."
        Remove-Item -Recurse -Force $InstallDir
        git clone $RepoUrl $InstallDir
    } else {
        Write-Info "克隆仓库到 $InstallDir..."
        git clone $RepoUrl $InstallDir
    }

    # 5. Run Python install script
    Write-Info "运行安装脚本..."
    & $python (Join-Path $InstallDir "install.py") install

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Success "安装完成!"
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Cyan
    Write-Host "  1. 参照 README 配置你的 Agent"
    Write-Host "  2. 重启 Agent"
    Write-Host ""
    Write-Warn "安装脚本不修改 Agent 配置，请手动配置"
    Write-Host "========================================" -ForegroundColor Green
}

function Update-McpServer {
    if (-not (Test-Path $InstallDir)) {
        Write-Error "未找到安装目录。请先运行安装。"
        exit 1
    }

    Write-Info "Video Analyzer MCP Server — 更新"
    Push-Location $InstallDir
    git pull
    $python = Find-Python
    & $python (Join-Path $InstallDir "install.py") update
    Pop-Location
}

function Uninstall-McpServer {
    if (-not (Test-Path $InstallDir)) {
        Write-Warn "未找到安装目录，无需卸载"
        return
    }

    $confirm = Read-Host "确认删除 $InstallDir 吗? [y/N]"
    if ($confirm -ne "y") {
        Write-Info "已取消"
        return
    }

    Remove-Item -Recurse -Force $InstallDir
    Write-Success "已卸载"
    Write-Warn "请手动从 Agent 配置中删除 video-analyzer 相关配置"
}

# Parse arguments from $args (when invoked via iex, $args is empty, default to install)
$Command = if ($args.Count -gt 0) { $args[0] } else { "install" }

switch ($Command) {
    "install" { Install-McpServer }
    "update" { Update-McpServer }
    "uninstall" { Uninstall-McpServer }
    default {
        Write-Host "用法: install.ps1 [install|update|uninstall]"
        Write-Host "默认执行 install"
    }
}
