#!/usr/bin/env python3
"""
Video Analyzer MCP Server — CLI 工具

提供独立于 Agent 的命令行操作：
    python cli.py update       # 更新 MCP
    python cli.py uninstall    # 卸载 MCP
    python cli.py analyze ~/video.mp4 --detail smart

用法:
    直接运行: python ~/.mcp/video-analyzer/cli.py <command>
    或添加 alias: alias video-analyzer="python ~/.mcp/video-analyzer/cli.py"
"""

import sys
import subprocess
from pathlib import Path

INSTALL_DIR = Path.home() / ".mcp" / "video-analyzer"


def run_install_py(cmd):
    install_py = INSTALL_DIR / "install.py"
    if not install_py.exists():
        print(f"❌ 未找到安装目录: {INSTALL_DIR}")
        print("   请先运行安装脚本")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(install_py), cmd])
    return result.returncode


def cmd_update():
    return run_install_py("update")


def cmd_uninstall():
    return run_install_py("uninstall")


def cmd_analyze():
    analyzer_py = INSTALL_DIR / "analyzer.py"
    if not analyzer_py.exists():
        print(f"❌ 未找到 analyzer.py")
        sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("analyzer", analyzer_py)
    analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer)

    if len(sys.argv) < 3:
        print("用法: python cli.py analyze <视频路径> [--detail brief|smart|detailed|frames]")
        sys.exit(1)

    video_path = sys.argv[2]
    detail = "smart"

    if "--detail" in sys.argv:
        idx = sys.argv.index("--detail")
        if idx + 1 < len(sys.argv):
            detail = sys.argv[idx + 1]

    print(f"🎬 分析视频: {video_path}")
    print(f"📊 详细程度: {detail}")
    print("=" * 50)

    result = analyzer.analyze_video(video_path, detail=detail)

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    commands = {
        "update": cmd_update,
        "uninstall": cmd_uninstall,
        "analyze": cmd_analyze,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Video Analyzer MCP — CLI 工具")
        print("=" * 50)
        print("")
        print("用法: python cli.py <command>")
        print("")
        print("命令:")
        print("  update              更新 MCP server")
        print("  uninstall           卸载 MCP server")
        print("  analyze <视频路径>  直接分析视频（不通过 Agent）")
        print("")
        print("示例:")
        print('  python cli.py update')
        print('  python cli.py analyze "~/Videos/demo.mp4" --detail smart')
        print("")
        print(f"安装目录: {INSTALL_DIR}")
        sys.exit(1)

    sys.exit(commands[sys.argv[1]]())


if __name__ == "__main__":
    main()
