#!/usr/bin/env python3
"""环境验证脚本"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def check_env():
    """检查环境变量"""
    print("📋 检查环境变量...")

    required_vars = [
        "ZAI_API_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "QDRANT_HOST",
        "QDRANT_PORT"
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  ❌ {var} 未设置")
        else:
            # 隐藏敏感信息
            if "KEY" in var or "PASSWORD" in var:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            print(f"  ✅ {var} = {display_value}")

    if missing:
        print(f"\n⚠️  缺少环境变量：{', '.join(missing)}")
        return False

    print("\n✅ 环境变量检查通过\n")
    return True


def check_sqlite():
    """检查 SQLite 连接"""
    print("🗄️ 检查 SQLite 连接...")
    try:
        import sqlite3
        import os

        # 检查数据库文件路径
        db_path = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./novel_rag.db")
        # 提取文件路径 (去掉 URL 前缀)
        if db_path.startswith("sqlite+aiosqlite:///"):
            db_file = db_path.replace("sqlite+aiosqlite:///", "")
        elif db_path.startswith("sqlite:///"):
            db_file = db_path.replace("sqlite:///", "")
        else:
            db_file = "./novel_rag.db"

        # 尝试连接数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 检查 SQLite 版本
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]

        # 检查数据库文件状态
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        conn.close()

        print(f"  ✅ SQLite 连接成功")
        print(f"  版本：{version}")
        print(f"  数据库文件：{os.path.abspath(db_file)}")
        print(f"  表数量：{table_count}\n")
        return True
    except Exception as e:
        print(f"  ❌ SQLite 连接失败：{e}\n")
        print(f"  提示：SQLite 是文件数据库，会自动创建文件\n")
        return False


def check_redis():
    """检查 Redis 连接"""
    print("🔴 检查 Redis 连接...")
    try:
        import redis

        # 解析 Redis URL
        redis_url = os.getenv("REDIS_URL")
        r = redis.from_url(redis_url)

        # 测试连接
        pong = r.ping()
        info = r.info("server")

        print(f"  ✅ Redis 连接成功")
        print(f"  版本：{info['redis_version']}\n")
        return True
    except Exception as e:
        print(f"  ❌ Redis 连接失败：{e}\n")
        return False


def check_qdrant():
    """检查 Qdrant 连接"""
    print("🔍 检查 Qdrant 连接...")
    try:
        from qdrant_client import QdrantClient

        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", 6333))

        client = QdrantClient(host=host, port=port)
        collections = client.get_collections()

        print(f"  ✅ Qdrant 连接成功")
        print(f"  当前集合数：{len(collections.collections)}\n")
        return True
    except Exception as e:
        print(f"  ❌ Qdrant 连接失败：{e}\n")
        return False


def check_zhipu_api():
    """检查智谱 API"""
    print("🤖 检查智谱 GLM API...")
    try:
        from zai import ZhipuAiClient

        api_key = os.getenv("ZAI_API_KEY")
        client = ZhipuAiClient(api_key=api_key)

        # 测试 Embedding API（使用最新的 embedding-3）
        response = client.embeddings.create(
            model="embedding-3",
            input="测试文本"
        )

        print(f"  ✅ 智谱 API 连接成功")
        print(f"  Embedding 模型：embedding-3")
        print(f"  向量维度：{len(response.data[0].embedding)}\n")
        return True
    except Exception as e:
        print(f"  ❌ 智谱 API 连接失败：{e}\n")
        print(f"  请检查 API Key 是否正确，是否已充值\n")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("小说 RAG 分析系统 - 环境验证")
    print("=" * 60)
    print()

    checks = [
        check_env,
        check_sqlite,
        check_redis,
        check_qdrant,
        check_zhipu_api
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ 检查失败：{e}\n")
            results.append(False)

    print("=" * 60)
    if all(results):
        print("🎉 所有检查通过，环境配置完成！")
        print("=" * 60)
        return 0
    else:
        print("⚠️  部分检查未通过，请修复后重试")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())