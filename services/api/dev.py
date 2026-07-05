#!/usr/bin/env python3
"""
后端开发脚本
提供常用的开发命令
"""

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def run_command(cmd: str, description: str) -> int:
    """运行命令并显示描述"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"命令: {cmd}\n")

    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print(f"\n✅ {description} - 成功")
    else:
        print(f"\n❌ {description} - 失败")

    return result.returncode


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(
            """
后端开发脚本

用法: python dev.py <command>

可用命令:
  test          运行所有测试
  test-cov      运行测试并生成覆盖率报告
  lint          运行代码检查
  format        格式化代码
  format-check  检查代码格式（不修改）
  type-check    运行类型检查
  all           运行所有检查（lint + format-check + type-check + test）
  install       安装开发依赖
  migrate       运行数据库迁移
  start         启动开发服务器
        """
        )
        return 1

    command = sys.argv[1]

    # 确保在后端目录
    backend_dir = Path(__file__).parent
    import os

    os.chdir(backend_dir)

    if command == "test":
        return run_command("pytest", "运行测试")

    elif command == "test-cov":
        return run_command(
            "pytest --cov-report=html:../../runtime/test-results/api/htmlcov --cov-report=term",
            "运行测试并生成覆盖率报告",
        )

    elif command == "lint":
        return run_command("ruff check .", "代码检查")

    elif command == "format":
        code = run_command("ruff format .", "格式化代码")
        if code == 0:
            run_command("ruff check --fix .", "修复可自动修复的问题")
        return code

    elif command == "format-check":
        return run_command("ruff format --check .", "检查代码格式")

    elif command == "type-check":
        return run_command("mypy app", "类型检查")

    elif command == "all":
        commands = [
            ("ruff check .", "代码检查"),
            ("ruff format --check .", "格式检查"),
            ("mypy app", "类型检查"),
            ("pytest", "运行测试"),
        ]

        for cmd, desc in commands:
            code = run_command(cmd, desc)
            if code != 0:
                print("\n❌ 检查失败，请修复后重试")
                return code

        print(f"\n{'='*60}")
        print("🎉 所有检查通过！")
        print(f"{'='*60}\n")
        return 0

    elif command == "install":
        return run_command("pip install -r requirements_dev.txt", "安装开发依赖")

    elif command == "migrate":
        return run_command("alembic upgrade head", "运行数据库迁移")

    elif command == "start":
        return run_command(
            "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000", "启动开发服务器"
        )

    else:
        print(f"❌ 未知命令: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
