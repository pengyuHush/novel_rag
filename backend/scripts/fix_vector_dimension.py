#!/usr/bin/env python3
"""
修复向量维度不匹配问题

当遇到 "expected dim: 2048, got 1024" 错误时运行此脚本

运行方式:
    cd backend
    python scripts/fix_vector_dimension.py
"""

import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from qdrant_client import QdrantClient
from app.core.config import settings


def fix_dimension_mismatch():
    """删除旧的Qdrant集合，让系统重新创建正确维度的集合."""
    
    logger.info("🔧 开始修复向量维度不匹配问题")
    logger.info(f"当前配置的向量维度: {settings.EMBEDDING_DIMENSION}")
    
    try:
        # 连接到Qdrant
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        logger.info(f"✅ 成功连接到Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        
        collection_name = settings.QDRANT_COLLECTION
        
        # 检查集合是否存在
        collections = client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if collection_exists:
            # 获取集合信息
            try:
                collection_info = client.get_collection(collection_name)
                current_dim = collection_info.config.params.vectors.size
                logger.info(f"当前集合维度: {current_dim}")
                logger.info(f"配置的维度: {settings.EMBEDDING_DIMENSION}")
                
                if current_dim != settings.EMBEDDING_DIMENSION:
                    logger.warning(
                        f"⚠️  维度不匹配！集合维度={current_dim}, 配置维度={settings.EMBEDDING_DIMENSION}"
                    )
                    
                    # 询问用户确认
                    print(f"\n{'='*60}")
                    print(f"发现维度不匹配:")
                    print(f"  - 集合维度: {current_dim}")
                    print(f"  - 配置维度: {settings.EMBEDDING_DIMENSION}")
                    print(f"\n删除集合后，已处理的小说需要重新上传。")
                    print(f"{'='*60}\n")
                    
                    confirm = input("是否删除旧集合？(yes/no): ").strip().lower()
                    
                    if confirm in ['yes', 'y']:
                        client.delete_collection(collection_name)
                        logger.success(f"✅ 集合 '{collection_name}' 已删除")
                        logger.info(f"💡 下次上传小说时，系统将自动创建 {settings.EMBEDDING_DIMENSION} 维的新集合")
                    else:
                        logger.info("❌ 用户取消操作")
                        logger.info("💡 提示：如果要保留数据，请在 app/core/config.py 中将")
                        logger.info(f"   EMBEDDING_DIMENSION 改回 {current_dim}")
                        sys.exit(0)
                else:
                    logger.success("✅ 维度匹配，无需修复")
                    sys.exit(0)
                    
            except Exception as e:
                logger.error(f"获取集合信息失败: {e}")
                raise
                
        else:
            logger.info(f"ℹ️  集合 '{collection_name}' 不存在")
            logger.info(f"💡 下次上传小说时，系统将自动创建 {settings.EMBEDDING_DIMENSION} 维的新集合")
        
        logger.success("\n🎉 修复完成！现在可以重新上传小说了。")
        
    except Exception as e:
        logger.exception(f"修复失败: {e}")
        logger.error("\n请检查:")
        logger.error("1. Qdrant 服务是否正在运行 (docker-compose ps)")
        logger.error("2. 配置是否正确 (QDRANT_HOST, QDRANT_PORT)")
        sys.exit(1)


if __name__ == "__main__":
    try:
        fix_dimension_mismatch()
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(0)

