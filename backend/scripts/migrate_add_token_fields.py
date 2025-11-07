#!/usr/bin/env python3
"""
数据库迁移脚本：添加Token统计字段到novels表

运行方式:
    cd backend
    python scripts/migrate_add_token_fields.py
"""

import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine
from loguru import logger


def migrate():
    """添加token统计字段到novels表."""
    
    logger.info("开始数据库迁移：添加Token统计字段")
    
    migrations = [
        (
            "total_tokens_used",
            "ALTER TABLE novels ADD COLUMN total_tokens_used INTEGER DEFAULT 0",
        ),
        (
            "embedding_tokens_used",
            "ALTER TABLE novels ADD COLUMN embedding_tokens_used INTEGER DEFAULT 0",
        ),
        (
            "chat_tokens_used",
            "ALTER TABLE novels ADD COLUMN chat_tokens_used INTEGER DEFAULT 0",
        ),
        (
            "api_calls_count",
            "ALTER TABLE novels ADD COLUMN api_calls_count INTEGER DEFAULT 0",
        ),
        (
            "estimated_cost",
            "ALTER TABLE novels ADD COLUMN estimated_cost REAL DEFAULT 0.0",
        ),
    ]
    
    success_count = 0
    skip_count = 0
    
    with engine.connect() as conn:
        for field_name, sql in migrations:
            try:
                logger.info(f"添加字段: {field_name}")
                conn.execute(text(sql))
                conn.commit()
                success_count += 1
                logger.success(f"✅ 字段 {field_name} 添加成功")
            except Exception as e:
                error_msg = str(e)
                if "duplicate column name" in error_msg.lower() or "already exists" in error_msg.lower():
                    skip_count += 1
                    logger.info(f"⏭️  字段 {field_name} 已存在，跳过")
                else:
                    logger.error(f"❌ 添加字段 {field_name} 失败: {e}")
                    raise
    
    logger.success(
        f"\n数据库迁移完成！\n"
        f"  - 成功添加: {success_count} 个字段\n"
        f"  - 已存在跳过: {skip_count} 个字段"
    )
    
    # 验证迁移
    logger.info("\n验证迁移结果...")
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(novels)"))
        columns = [row[1] for row in result]
        
        required_fields = [
            "total_tokens_used",
            "embedding_tokens_used",
            "chat_tokens_used",
            "api_calls_count",
            "estimated_cost",
        ]
        
        missing_fields = [f for f in required_fields if f not in columns]
        
        if missing_fields:
            logger.error(f"❌ 缺少字段: {missing_fields}")
            sys.exit(1)
        else:
            logger.success("✅ 所有字段验证通过！")
            logger.info(f"novels表当前包含字段: {columns}")


if __name__ == "__main__":
    try:
        migrate()
        logger.success("\n🎉 迁移成功！现在可以启动后端服务了。")
    except Exception as e:
        logger.exception("迁移失败")
        sys.exit(1)

