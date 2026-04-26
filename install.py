#!/usr/bin/env python3
"""
Video Analyzer MCP Server — 一键安装脚本

自动检测环境、安装依赖、生成配置。
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

REPO_DIR = Path(__file__).parent.resolve()
INSTALL_DIR = Path.home() / ".mcp" / "video-analyzer"


def run(cmd, **kwargs):
    """Run a shell command and return stdout."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def find_kimi_cli():
    """Find kimi-cli executable and its Python interpreter."""
    kimi_path = shutil.which("kimi")
    if not kimi_path:
        print("❌ 错误: 未找到 kimi 命令。请先安装 kimi-cli: https://github.com/MoonshotAI/kimi-cli")
        sys.exit(1)
    
    # Resolve symlink to find the real python interpreter
    kimi_path = Path(kimi_path).resolve()
    # Typical path: ~/.local/share/uv/tools/kimi-cli/bin/kimi
    python_path = kimi_path.parent.parent / "bin" / "python"
    if not python_path.exists():
        # Fallback: try python3 in same directory
        python_path = shutil.which("python3") or shutil.which("python")
    
    return str(kimi_path), str(python_path)


def check_mcp_installed(python_path):
    """Check if mcp package is available."""
    stdout, stderr, rc = run(f'"{python_path}" -c "import mcp; print(mcp.__file__)"')
    return rc == 0


def install_files():
    """Copy source files to install directory."""
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    src_dir = REPO_DIR / "src" / "video_analyzer"
    if src_dir.exists():
        for f in ["analyzer.py", "server.py", "__init__.py"]:
            src = src_dir / f
            if src.exists():
                shutil.copy2(src, INSTALL_DIR / f)
    else:
        # Fallback: copy from repo root
        for f in ["analyzer.py", "server.py"]:
            src = REPO_DIR / f
            if src.exists():
                shutil.copy2(src, INSTALL_DIR / f)
    
    print(f"✅ 代码已安装到: {INSTALL_DIR}")


def detect_agents():
    """Detect which agents are installed."""
    agents = []
    
    if (Path.home() / ".hermes" / "config.yaml").exists():
        agents.append("hermes")
    
    if (Path.home() / ".opencode" / "opencode.jsonc").exists():
        agents.append("opencode")
    
    if (Path.home() / ".config" / "claude" / "settings.json").exists():
        agents.append("claude-desktop")
    
    return agents


def generate_config(agent: str, python_path: str):
    """Generate MCP config snippet for the given agent."""
    server_path = INSTALL_DIR / "server.py"
    
    if agent == "hermes":
        return f"""
# 添加到 ~/.hermes/config.yaml 的 mcp_servers 下:

  video-analyzer:
    command: "{python_path}"
    args: ["{server_path}"]
    timeout: 300  # ⚠️ 视频分析可能耗时数分钟
"""
    elif agent == "opencode":
        return (
            '# 添加到 ~/.opencode/opencode.jsonc 的 mcp 下:\n\n'
            '    "video-analyzer": {\n'
            '      "type": "local",\n'
            f'      "command": ["{python_path}", "{server_path}"]\n'
            '    }\n'
        )
    elif agent == "claude-desktop":
        return (
            '# 添加到 Claude Desktop 的 MCP 配置:\n\n'
            '{\n'
            '  "mcpServers": {\n'
            '    "video-analyzer": {\n'
            f'      "command": "{python_path}",\n'
            f'      "args": ["{server_path}"]\n'
            '    }\n'
            '  }\n'
            '}\n'
        )
    return ""


def write_config_files(agent: str, config: str):
    """Write config snippet to a file for easy copy-paste."""
    config_file = INSTALL_DIR / f"config-{agent}.txt"
    config_file.write_text(config.strip(), encoding="utf-8")
    return config_file


def main():
    print("🎬 Video Analyzer MCP Server 安装脚本")
    print("=" * 50)
    
    # 1. Find kimi-cli
    print("\n1️⃣  检测 kimi-cli...")
    kimi_path, python_path = find_kimi_cli()
    print(f"   ✅ kimi: {kimi_path}")
    print(f"   ✅ python: {python_path}")
    
    # 2. Check mcp package
    print("\n2️⃣  检测 mcp 包...")
    if check_mcp_installed(python_path):
        print("   ✅ mcp 已安装")
    else:
        print("   ⚠️  mcp 未安装，尝试安装...")
        run(f'"{python_path}" -m pip install mcp')
        if check_mcp_installed(python_path):
            print("   ✅ mcp 安装成功")
        else:
            print("   ❌ mcp 安装失败，请手动安装: pip install mcp")
            sys.exit(1)
    
    # 3. Install files
    print("\n3️⃣  安装代码...")
    install_files()
    
    # 4. Detect agents
    print("\n4️⃣  检测已安装的 Agent...")
    agents = detect_agents()
    if agents:
        print(f"   ✅ 检测到: {', '.join(agents)}")
    else:
        print("   ⚠️  未检测到已知 Agent，将生成通用配置")
        agents = ["generic"]
    
    # 5. Generate configs
    print("\n5️⃣  生成配置...")
    for agent in agents:
        config = generate_config(agent, python_path)
        if config:
            config_file = write_config_files(agent, config)
            print(f"   ✅ {agent} 配置已保存到: {config_file}")
    
    # 6. Summary
    print("\n" + "=" * 50)
    print("🎉 安装完成!")
    print(f"\n📁 代码位置: {INSTALL_DIR}")
    print("\n📋 配置方法:")
    print("   1. 查看上方生成的 config-*.txt 文件")
    print("   2. 将内容复制到你的 Agent MCP 配置中")
    print("   3. 重启 Agent")
    print("\n⚠️  重要: 视频分析耗时较长，请确保 MCP timeout >= 300 秒")
    print("\n🚀 使用方法: 对 Agent 说 '分析这个视频 ~/video.mp4'")
    print("=" * 50)


if __name__ == "__main__":
    main()
