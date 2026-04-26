#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/MuseLinn/video-analyzer-mcp.git"
INSTALL_DIR="$HOME/.mcp/video-analyzer"

info() { echo -e "\033[36m[INFO]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m   $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m  $*"; }

info "Video Analyzer MCP Server — 安装"
echo "========================================"

info "检测 Python..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    err "未找到 Python。请先安装 Python 3: https://python.org"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)
ok "Python: $PYTHON"

info "检测 mcp 包..."
if "$PYTHON" -c "import mcp" 2>/dev/null; then
    ok "mcp 已安装"
else
    warn "mcp 未安装，尝试安装..."
    if ! "$PYTHON" -m pip install mcp 2>/dev/null; then
        err "mcp 安装失败，请手动安装: pip install mcp"
        exit 1
    fi
    ok "mcp 安装成功"
fi

info "检测 git..."
if ! command -v git &>/dev/null; then
    err "未找到 git。请先安装 Git"
    exit 1
fi
ok "git: $(command -v git)"

info "检测 kimi-cli..."
if ! command -v kimi &>/dev/null; then
    err "未找到 kimi 命令。请先安装 kimi-cli: https://github.com/MoonshotAI/kimi-cli"
    exit 1
fi
ok "kimi-cli: $(command -v kimi)"

info "安装代码..."
if [ -d "$INSTALL_DIR/.git" ]; then
    info "目录已存在，尝试更新..."
    cd "$INSTALL_DIR"
    git pull
elif [ -d "$INSTALL_DIR" ]; then
    warn "安装目录存在但不是 git repo，将重新克隆..."
    rm -rf "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo ""
echo "========================================"
ok "安装完成!"
echo ""
echo "📁 代码位置: $INSTALL_DIR"
echo ""
echo "📋 下一步:"
echo "   1. 参照 README 配置你的 Agent"
echo "   2. 重启 Agent"
echo ""
echo "⚠️  重要: 视频分析耗时较长，请确保 MCP timeout >= 300 秒"
echo "========================================"
