"""
ChromaDB向量数据库客户端封装
"""

import os
# 必须在导入chromadb之前设置，否则不生效
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_DISABLED"] = "1"

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """ChromaDB客户端封装类"""
    
    def __init__(self):
        """初始化ChromaDB客户端"""
        # 确保ChromaDB目录存在
        chroma_path = Path(settings.chromadb_path)
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        # 创建持久化客户端（禁用遥测避免错误日志）
        self.client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(
                anonymized_telemetry=False,  # 禁用遥测
                allow_reset=True if settings.debug else False,
                is_persistent=True
            )
        )
        
        logger.info(f"✅ ChromaDB客户端初始化成功: {chroma_path}")
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """获取或创建Collection"""
        default_metadata = {
            "hnsw:space": "l2",              # L2距离（欧氏距离）
            "hnsw:construction_ef": 200,     # 构建时的ef参数
            "hnsw:M": 16,                    # 每个节点的邻居数
            "hnsw:search_ef": 200,           # 搜索时的ef参数（提升精度）
        }
        
        if metadata:
            default_metadata.update(metadata)
        
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=default_metadata
            )
            logger.info(f"✅ Collection '{name}' 已就绪")
            return collection
        except Exception as e:
            logger.error(f"❌ 创建Collection '{name}' 失败: {e}")
            raise
    
    def get_collection(self, name: str):
        """获取已存在的Collection"""
        try:
            return self.client.get_collection(name=name)
        except Exception as e:
            logger.error(f"❌ 获取Collection '{name}' 失败: {e}")
            raise
    
    def delete_collection(self, name: str):
        """删除Collection"""
        try:
            self.client.delete_collection(name=name)
            logger.info(f"✅ Collection '{name}' 已删除")
        except Exception as e:
            logger.error(f"❌ 删除Collection '{name}' 失败: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """列出所有Collection"""
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"❌ 列出Collection失败: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """添加文档到Collection"""
        try:
            collection = self.get_collection(collection_name)
            collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"✅ 已添加 {len(documents)} 个文档到 '{collection_name}'")
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            raise
    
    def query_documents(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """查询文档"""
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            logger.debug(f"✅ 查询返回 {len(results.get('ids', [[]])[0])} 个结果")
            return results
        except Exception as e:
            logger.error(f"❌ 查询文档失败: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """获取Collection统计信息"""
        try:
            collection = self.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"❌ 获取Collection统计失败: {e}")
            raise
    
    def reset_database(self):
        """重置整个数据库（仅用于开发）"""
        if not settings.debug:
            raise RuntimeError("重置数据库仅允许在DEBUG模式下执行")
        
        logger.warning("⚠️ 正在重置ChromaDB数据库...")
        self.client.reset()
        logger.info("✅ ChromaDB数据库已重置")


# 全局ChromaDB客户端实例
_chroma_client: Optional[ChromaDBClient] = None


def get_chroma_client() -> ChromaDBClient:
    """获取全局ChromaDB客户端实例（单例）"""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaDBClient()
    return _chroma_client

