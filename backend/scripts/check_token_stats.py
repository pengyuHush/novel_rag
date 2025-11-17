"""
检查Token统计数据
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.init_db import SessionLocal
from app.models.database import TokenStat, Novel, Query
from sqlalchemy import func

def check_token_stats():
    """检查Token统计数据"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("Token统计数据检查")
        print("="*60 + "\n")
        
        # 1. 检查token_stats表的记录数
        total_records = db.query(TokenStat).count()
        print(f"📊 Token统计记录总数: {total_records}")
        
        if total_records == 0:
            print("\n⚠️  数据库中没有Token统计记录！")
            print("   可能原因：")
            print("   1. 小说导入时token统计功能未正常工作")
            print("   2. 还没有进行过任何查询或索引操作")
            return
        
        # 2. 按操作类型统计
        print(f"\n📈 按操作类型分类:")
        by_operation = db.query(
            TokenStat.operation_type,
            func.count(TokenStat.id).label('count'),
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.estimated_cost).label('total_cost')
        ).group_by(TokenStat.operation_type).all()
        
        for result in by_operation:
            print(f"   {result.operation_type}:")
            print(f"      记录数: {result.count}")
            print(f"      Token总数: {result.total_tokens or 0}")
            print(f"      成本: ¥{result.total_cost or 0:.4f}")
        
        # 3. 按模型统计
        print(f"\n🤖 按模型分类:")
        by_model = db.query(
            TokenStat.model_name,
            func.count(TokenStat.id).label('count'),
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.estimated_cost).label('total_cost')
        ).group_by(TokenStat.model_name).all()
        
        for result in by_model:
            print(f"   {result.model_name}:")
            print(f"      记录数: {result.count}")
            print(f"      Token总数: {result.total_tokens or 0}")
            print(f"      成本: ¥{result.total_cost or 0:.4f}")
        
        # 4. 查看最近的10条记录
        print(f"\n📝 最近10条记录:")
        recent_stats = db.query(TokenStat).order_by(TokenStat.created_at.desc()).limit(10).all()
        
        for i, stat in enumerate(recent_stats, 1):
            print(f"\n   {i}. {stat.operation_type} #{stat.operation_id}")
            print(f"      模型: {stat.model_name}")
            print(f"      Token: {stat.total_tokens}")
            print(f"      成本: ¥{stat.estimated_cost:.4f}")
            print(f"      时间: {stat.created_at}")
        
        # 5. 检查Novel表的统计数据
        print(f"\n📚 小说统计数据:")
        novels = db.query(Novel).all()
        for novel in novels:
            print(f"\n   《{novel.title}》")
            print(f"      embedding_tokens: {novel.embedding_tokens or 0}")
            print(f"      total_chunks: {novel.total_chunks or 0}")
        
        # 6. 检查Query表的统计数据
        print(f"\n❓ 查询统计数据:")
        queries = db.query(Query).order_by(Query.created_at.desc()).limit(5).all()
        for query in queries:
            print(f"\n   查询 #{query.id}")
            print(f"      问题: {query.query_text[:50]}...")
            print(f"      total_tokens: {query.total_tokens or 0}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_token_stats()

