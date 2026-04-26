#!/usr/bin/env python3
"""
Video Analyzer MCP Server — 安装/更新/卸载脚本

用法:
    python install.py install    # 安装或重新安装（默认）
    python install.py update     # 从 git 更新
    python install.py uninstall  # 卸载

不修改任何 Agent 配置文件。安装完成后请参照 README 手动配置。
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

REPO_DIR = Path(__file__).parent.resolve()
INSTALL_DIR = Path.home() / ".mcp" / "video-analyzer"


def run(cmd, **kwargs):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def check_kimi():
    kimi_path = shutil.which("kimi")
    if not kimi_path:
        print("❌ 错误: 未找到 kimi 命令。请先安装 kimi-cli:")
        print("   https://github.com/MoonshotAI/kimi-cli")
        sys.exit(1)
    return str(Path(kimi_path).resolve())


def find_mcp_python():
    candidates = [Path(sys.executable)]
    for name in ("python3", "python"):
        p = shutil.which(name)
        if p:
            candidates.append(Path(p))

    for python_path in candidates:
        stdout, stderr, rc = run(f'"{python_path}" -c "import mcp; print(mcp.__file__)"')
        if rc == 0:
            return str(python_path)

    return None


def is_installed():
    return INSTALL_DIR.exists() and (INSTALL_DIR / "server.py").exists()


def is_running_from_repo():
    return (REPO_DIR / ".git").exists() and REPO_DIR != INSTALL_DIR


def copy_files():
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    src_dir = REPO_DIR / "src" / "video_analyzer"
    if src_dir.exists():
        for f in ["analyzer.py", "server.py", "__init__.py"]:
            src = src_dir / f
            if src.exists():
                shutil.copy2(src, INSTALL_DIR / f)
    else:
        for f in ["analyzer.py", "server.py"]:
            src = REPO_DIR / f
            if src.exists():
                shutil.copy2(src, INSTALL_DIR / f)

    shutil.copy2(REPO_DIR / "install.py", INSTALL_DIR / "install.py")
    print(f"✅ 代码已安装到: {INSTALL_DIR}")


def cmd_install(args):
    print("🎬 Video Analyzer MCP Server — 安装")
    print("=" * 50)

    print("\n1️⃣  检测 kimi-cli...")
    kimi_path = check_kimi()
    print(f"   ✅ kimi: {kimi_path}")

    print("\n2️⃣  检测 Python + mcp...")
    python_path = find_mcp_python()
    if python_path:
        print(f"   ✅ python: {python_path}")
        print("   ✅ mcp 已安装")
    else:
        print("   ⚠️  mcp 未安装，尝试安装...")
        python_path = shutil.which("python3") or shutil.which("python")
        if not python_path:
            print("   ❌ 未找到可用的 Python")
            sys.exit(1)
        run(f'"{python_path}" -m pip install mcp')
        python_path = find_mcp_python()
        if python_path:
            print(f"   ✅ python: {python_path}")
            print("   ✅ mcp 安装成功")
        else:
            print("   ❌ mcp 安装失败，请手动安装: pip install mcp")
            sys.exit(1)
    
    print("\n3️⃣  安装代码...")
    if is_running_from_repo():
        print(f"   从 repo 复制到 {INSTALL_DIR}...")
        copy_files()
    elif REPO_DIR == INSTALL_DIR:
        print(f"   已在安装目录，跳过复制")
        if not (INSTALL_DIR / "install.py").exists():
            shutil.copy2(REPO_DIR / "install.py", INSTALL_DIR / "install.py")
    else:
        copy_files()
    
    print("\n" + "=" * 50)
    print("🎉 安装完成!")
    print(f"\n📁 代码位置: {INSTALL_DIR}")
    print("\n📋 下一步:")
    print("   1. 参照 README 配置你的 Agent")
    print("   2. 重启 Agent")
    print("\n⚠️  重要: 视频分析耗时较长，请确保 MCP timeout >= 300 秒")
    print("\n📝 后续更新: python install.py update")
    print("=" * 50)


def cmd_update(args):
    print("🔄 Video Analyzer MCP Server — 更新")
    print("=" * 50)
    
    if not is_installed():
        print("❌ 尚未安装，请先运行: python install.py install")
        sys.exit(1)
    
    git_dir = INSTALL_DIR / ".git"
    if not git_dir.exists():
        print("❌ 安装目录不是 git repo，无法自动更新")
        print(f"   请手动删除 {INSTALL_DIR} 后重新克隆并安装")
        sys.exit(1)
    
    print("\n1️⃣  从 git 拉取更新...")
    stdout, stderr, rc = run("git pull", cwd=str(INSTALL_DIR))
    if rc != 0:
        print(f"   ❌ git pull 失败:\n{stderr}")
        sys.exit(1)
    
    if "Already up to date" in stdout:
        print("   ✅ 已经是最新版本")
    else:
        print(f"   ✅ 更新成功:\n{stdout}")
    
    print("\n2️⃣  重新安装文件...")
    if is_running_from_repo():
        copy_files()
    
    print("\n" + "=" * 50)
    print("🎉 更新完成!")
    print("\n⚠️  请重启你的 Agent 以使更新生效")
    print("=" * 50)


def cmd_uninstall(args):
    print("🗑️  Video Analyzer MCP Server — 卸载")
    print("=" * 50)
    
    if not is_installed():
        print("❌ 未找到安装目录，无需卸载")
        return
    
    confirm = input(f"\n确认删除 {INSTALL_DIR} 吗? [y/N]: ")
    if confirm.lower() != "y":
        print("已取消")
        return
    
    print(f"\n删除 {INSTALL_DIR}...")
    shutil.rmtree(INSTALL_DIR)
    print("✅ 已卸载")
    
    print("\n⚠️  请手动从 Agent 配置中删除 video-analyzer 相关配置")


def main():
    parser = argparse.ArgumentParser(
        description="Video Analyzer MCP Server 安装/更新/卸载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python install.py install    # 安装
    python install.py update     # 从 git 更新
    python install.py uninstall  # 卸载
    python install.py            # 默认执行 install
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="install",
        choices=["install", "update", "uninstall"],
        help="要执行的命令 (默认: install)"
    )
    
    args = parser.parse_args()
    
    commands = {
        "install": cmd_install,
        "update": cmd_update,
        "uninstall": cmd_uninstall,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
