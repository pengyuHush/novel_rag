#!/usr/bin/env python3
"""
迁移脚本：为 token_stats 表添加 'append' 操作类型支持

使用方法：
    python migrate_token_stats.py

注意：此脚本会自动检测是否需要迁移，如果约束已更新则跳过。
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.init_db import get_database_url


def check_need_migration(conn):
    """检查是否需要迁移"""
    cursor = conn.cursor()
    
    # 获取表的 SQL 定义
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='token_stats'")
    result = cursor.fetchone()
    
    if not result:
        print("❌ token_stats 表不存在")
        return False
    
    table_sql = result[0]
    
    # 检查是否已经包含 'append'
    if "'append'" in table_sql or '"append"' in table_sql:
        print("✅ token_stats 表约束已包含 'append'，无需迁移")
        return False
    
    print("📋 检测到需要迁移 token_stats 表约束")
    return True


def migrate(conn):
    """执行迁移"""
    cursor = conn.cursor()
    
    try:
        print("🔄 开始迁移...")
        
        # 1. 创建新表
        print("  1/5 创建新表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_stats_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                operation_id INTEGER,
                model_name TEXT NOT NULL,
                
                input_tokens INTEGER DEFAULT 0,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER NOT NULL,
                
                estimated_cost REAL DEFAULT 0.0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT check_operation_type CHECK (operation_type IN ('index', 'query', 'append'))
            )
        """)
        
        # 2. 复制数据
        print("  2/5 复制数据...")
        cursor.execute("""
            INSERT INTO token_stats_new (
                id, operation_type, operation_id, model_name,
                input_tokens, prompt_tokens, completion_tokens, total_tokens,
                estimated_cost, created_at
            )
            SELECT 
                id, operation_type, operation_id, model_name,
                input_tokens, prompt_tokens, completion_tokens, total_tokens,
                estimated_cost, created_at
            FROM token_stats
        """)
        
        rows_copied = cursor.rowcount
        print(f"  ✓ 已复制 {rows_copied} 行数据")
        
        # 3. 删除旧表
        print("  3/5 删除旧表...")
        cursor.execute("DROP TABLE token_stats")
        
        # 4. 重命名新表
        print("  4/5 重命名新表...")
        cursor.execute("ALTER TABLE token_stats_new RENAME TO token_stats")
        
        # 5. 重建索引
        print("  5/5 重建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_stats_date ON token_stats(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_stats_model ON token_stats(model_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_stats_operation ON token_stats(operation_type, operation_id)")
        
        # 提交事务
        conn.commit()
        
        print("✅ 迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Token Stats 表迁移工具")
    print("=" * 60)
    
    # 获取数据库路径
    db_url = get_database_url()
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
    else:
        print(f"❌ 不支持的数据库类型: {db_url}")
        return 1
    
    print(f"📁 数据库路径: {db_path}")
    
    # 检查数据库文件是否存在
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return 1
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    
    try:
        # 检查是否需要迁移
        if not check_need_migration(conn):
            return 0
        
        # 确认迁移
        print("\n⚠️  即将修改数据库表结构，建议先备份数据库文件")
        response = input("是否继续？(y/N): ").strip().lower()
        
        if response != 'y':
            print("❌ 用户取消迁移")
            return 0
        
        # 执行迁移
        if migrate(conn):
            print("\n✅ 所有操作完成！现在可以使用追加章节功能了")
            return 0
        else:
            print("\n❌ 迁移失败")
            return 1
            
    finally:
        conn.close()


if __name__ == '__main__':
    exit(main())

