#!/usr/bin/env python3
"""验证测试系统是否正常工作."""

import sys
from pathlib import Path

# 设置UTF-8输出（Windows兼容）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def check_file(file_path: str, description: str) -> bool:
    """检查文件是否存在."""
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists


def check_directory(dir_path: str, description: str) -> bool:
    """检查目录是否存在."""
    path = Path(dir_path)
    exists = path.exists() and path.is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dir_path}")
    return exists


def main():
    """主函数."""
    print("\n" + "=" * 60)
    print("🔍 验证测试系统")
    print("=" * 60 + "\n")

    checks = []

    print("📁 检查目录结构:")
    checks.append(check_directory("tests", "测试根目录"))
    checks.append(check_directory("tests/unit", "单元测试目录"))
    checks.append(check_directory("tests/integration", "集成测试目录"))
    checks.append(check_directory("tests/e2e", "端到端测试目录"))
    checks.append(check_directory("tests/helpers", "测试工具目录"))
    checks.append(check_directory("tests/fixtures", "测试数据目录"))

    print("\n📄 检查配置文件:")
    checks.append(check_file("pytest.ini", "Pytest配置"))
    checks.append(check_file("tests/conftest.py", "全局fixtures"))
    checks.append(check_file("run_tests.py", "Python测试脚本"))
    checks.append(check_file("run_tests.ps1", "PowerShell测试脚本"))

    print("\n📝 检查测试文件:")
    checks.append(check_file("tests/unit/test_schemas.py", "Schema测试"))
    checks.append(check_file("tests/unit/test_repositories.py", "Repository测试"))
    checks.append(check_file("tests/unit/test_utils.py", "工具函数测试"))
    checks.append(check_file("tests/integration/test_rag_service.py", "RAG服务测试"))
    checks.append(check_file("tests/integration/test_external_services.py", "外部服务测试"))
    checks.append(check_file("tests/e2e/test_api_endpoints.py", "API端点测试"))

    print("\n🔧 检查工具文件:")
    checks.append(check_file("tests/helpers/__init__.py", "Helpers初始化"))
    checks.append(check_file("tests/helpers/factories.py", "数据工厂"))
    checks.append(check_file("tests/helpers/assertions.py", "自定义断言"))
    checks.append(check_file("tests/helpers/utils.py", "工具函数"))

    print("\n📚 检查文档文件:")
    checks.append(check_file("TESTING.md", "测试系统说明"))
    checks.append(check_file("QUICKSTART_TESTING.md", "快速入门指南"))
    checks.append(check_file("tests/README.md", "详细测试文档"))
    checks.append(check_file("TEST_SYSTEM_SUMMARY.md", "重构总结"))

    # 统计结果
    passed = sum(checks)
    total = len(checks)

    print("\n" + "=" * 60)
    print("📊 验证结果")
    print("=" * 60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 所有检查通过！测试系统已正确安装。")
        print("\n💡 下一步:")
        print("   1. 运行测试: python run_tests.py --type unit")
        print("   2. 查看文档: cat QUICKSTART_TESTING.md")
        print("   3. 编写测试: 参考 tests/unit/test_schemas.py")
        return 0
    else:
        print("\n⚠️  部分检查失败，请检查缺失的文件或目录。")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        sys.exit(1)

