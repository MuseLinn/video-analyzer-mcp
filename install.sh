#!/usr/bin/env bash
set -euo pipefail

# Video Analyzer MCP Server — Bash 安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/MoonshotAI/video-analyzer-mcp/main/install.sh | bash

REPO_URL="https://github.com/MoonshotAI/video-analyzer-mcp.git"
INSTALL_DIR="$HOME/.mcp/video-analyzer"

info() { echo -e "\033[36m[INFO]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m   $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m  $*"; }

# 1. 检测必要依赖
info "检测环境..."

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    err "未找到 Python。请先安装 Python 3: https://python.org"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)
ok "Python: $PYTHON"

if ! command -v git &>/dev/null; then
    err "未找到 git。请先安装 Git"
    exit 1
fi
ok "git: $(command -v git)"

if ! command -v kimi &>/dev/null; then
    err "未找到 kimi 命令。Video Analyzer MCP 依赖 kimi-cli，请先安装:"
    err "   https://github.com/MoonshotAI/kimi-cli"
    exit 1
fi
ok "kimi-cli: $(command -v kimi)"

if [ -d "$INSTALL_DIR/.git" ]; then
    info "目录已存在，尝试更新..."
    cd "$INSTALL_DIR"
    git pull
elif [ -d "$INSTALL_DIR" ]; then
    warn "安装目录存在但不是 git repo，将重新克隆..."
    rm -rf "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
else
    info "克隆仓库到 $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

info "运行安装脚本..."
cd "$INSTALL_DIR"
"$PYTHON" install.py install

ok "安装流程完成!"
info "请参照 README 配置你的 Agent，然后重启 Agent 生效。"
