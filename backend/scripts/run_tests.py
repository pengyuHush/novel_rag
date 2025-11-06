#!/usr/bin/env python3
"""统一的测试运行脚本."""

import argparse
import sys
import subprocess
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """运行命令并返回结果.

    Args:
        cmd: 要执行的命令列表
        description: 命令描述

    Returns:
        是否成功
    """
    print(f"\n{'=' * 60}")
    print(f"🔍 {description}")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {description}成功\n")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description}失败\n")
        return False


def main():
    """主函数."""
    parser = argparse.ArgumentParser(description="小说RAG系统测试运行器")

    parser.add_argument(
        "--type",
        "-t",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="测试类型 (default: all)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出",
    )

    parser.add_argument(
        "--coverage",
        "-c",
        action="store_true",
        help="生成代码覆盖率报告",
    )

    parser.add_argument(
        "--no-external",
        action="store_true",
        help="跳过外部服务测试（智谱AI等）",
    )

    parser.add_argument(
        "--no-slow",
        action="store_true",
        help="跳过慢速测试",
    )

    parser.add_argument(
        "--markers",
        "-m",
        help="自定义pytest markers",
    )

    args = parser.parse_args()

    # 构建pytest命令
    cmd = ["poetry", "run", "pytest"]

    # 测试类型
    if args.type == "unit":
        cmd.append("tests/unit")
    elif args.type == "integration":
        cmd.append("tests/integration")
    elif args.type == "e2e":
        cmd.append("tests/e2e")
    else:
        cmd.append("tests")

    # 详细输出
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # 代码覆盖率
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])

    # 跳过外部服务
    if args.no_external:
        cmd.extend(["-m", "not external"])

    # 跳过慢速测试
    if args.no_slow:
        if args.no_external:
            cmd[-1] += " and not slow"
        else:
            cmd.extend(["-m", "not slow"])

    # 自定义markers
    if args.markers:
        cmd.extend(["-m", args.markers])

    # 运行测试
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "小说 RAG 系统测试" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"\n📝 测试类型: {args.type}")
    print(f"📊 代码覆盖: {'是' if args.coverage else '否'}")
    print(f"🌐 外部服务: {'跳过' if args.no_external else '包含'}")
    print(f"⏱️  慢速测试: {'跳过' if args.no_slow else '包含'}")
    print(f"\n💻 执行命令: {' '.join(cmd)}")

    success = run_command(cmd, "运行测试")

    # 显示覆盖率报告路径
    if args.coverage and success:
        coverage_path = Path("htmlcov/index.html").absolute()
        print(f"\n📊 覆盖率报告: {coverage_path}")
        print("   使用浏览器打开查看详细报告")

    # 总结
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("=" * 60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

