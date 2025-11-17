"""
向量化服务
调用智谱AI Embedding-3进行文本向量化
"""

import logging
from typing import List, Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.zhipu_client import get_zhipu_client
from app.core.chromadb_client import get_chroma_client
from app.core.config import settings
from app.utils.token_counter import get_token_counter

logger = logging.getLogger(__name__)


class EmbeddingService:
    """向量化服务"""
    
    def __init__(self):
        """初始化向量化服务"""
        self.zhipu_client = get_zhipu_client()
        self.chroma_client = get_chroma_client()
        self.token_counter = get_token_counter()
        self.batch_size = 10  # 批量处理大小
        logger.info("✅ 向量化服务初始化完成")
    
    def embed_texts(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> Tuple[List[List[float]], int]:
        """
        批量向量化文本
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
        
        Returns:
            Tuple[List[List[float]], int]: (向量列表, 消耗的token数)
        """
        if not texts:
            return [], 0
        
        batch_size = batch_size or self.batch_size
        all_embeddings = []
        total_tokens = 0
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"🔄 正在向量化批次 {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
            
            # 计算本批次的token消耗
            batch_tokens = sum(self.token_counter.count_tokens(text) for text in batch)
            total_tokens += batch_tokens
            
            try:
                # 调用智谱AI
                embeddings = self.zhipu_client.embed_texts(batch)
                all_embeddings.extend(embeddings)
                
            except Exception as e:
                logger.error(f"❌ 批次 {i//batch_size + 1} 向量化失败: {e}")
                # 对失败的批次使用零向量
                zero_embeddings = [[0.0] * settings.embedding_dimension for _ in batch]
                all_embeddings.extend(zero_embeddings)
        
        logger.info(f"✅ 完成 {len(all_embeddings)} 个文本的向量化，消耗 {total_tokens} tokens")
        return all_embeddings, total_tokens
    
    def create_collection(self, novel_id: int) -> str:
        """
        为小说创建向量集合
        
        Args:
            novel_id: 小说ID
        
        Returns:
            str: 集合名称
        """
        collection_name = f"novel_{novel_id}"
        
        try:
            self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "novel_id": str(novel_id),
                    "hnsw:space": "cosine",
                    "hnsw:construction_ef": 200,
                    "hnsw:M": 16
                }
            )
            logger.info(f"✅ 创建/获取Collection: {collection_name}")
            return collection_name
            
        except Exception as e:
            logger.error(f"❌ 创建Collection失败: {e}")
            raise
    
    def add_chapter_chunks(
        self,
        collection_name: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata_list: List[Dict]
    ) -> bool:
        """
        添加章节块到向量库
        
        Args:
            collection_name: 集合名称
            chunks: 文本块列表
            embeddings: 向量列表
            metadata_list: 元数据列表
        
        Returns:
            bool: 是否成功
        """
        if not chunks or not embeddings:
            logger.warning("⚠️ 没有内容需要添加")
            return False
        
        try:
            # 生成ID
            ids = [
                f"novel_{metadata['novel_id']}_ch{metadata['chapter_num']}_chunk{metadata['chunk_index']}"
                for metadata in metadata_list
            ]
            
            # 添加到ChromaDB
            self.chroma_client.add_documents(
                collection_name=collection_name,
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadata_list
            )
            
            logger.info(f"✅ 成功添加 {len(chunks)} 个块到 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加到ChromaDB失败: {e}")
            return False
    
    def process_chapter(
        self,
        novel_id: int,
        chapter_num: int,
        chapter_title: str,
        chapter_chunks: List[Dict]
    ) -> Tuple[bool, int]:
        """
        处理单个章节（向量化并存储）
        
        Args:
            novel_id: 小说ID
            chapter_num: 章节编号
            chapter_title: 章节标题
            chapter_chunks: 章节块列表（包含content和metadata）
        
        Returns:
            Tuple[bool, int]: (是否成功, 消耗的token数)
        """
        if not chapter_chunks:
            logger.warning(f"⚠️ 章节 {chapter_num} 没有内容")
            return False, 0
        
        try:
            # 提取文本
            texts = [chunk['content'] for chunk in chapter_chunks]
            
            # 向量化（获取token消耗）
            embeddings, tokens_used = self.embed_texts(texts)
            
            # 准备元数据
            metadata_list = []
            for i, chunk in enumerate(chapter_chunks):
                metadata = {
                    'novel_id': novel_id,
                    'chapter_num': chapter_num,
                    'chapter_title': chapter_title,
                    'chunk_index': i,
                    'char_count': len(chunk['content']),
                }
                # 合并chunk自带的metadata
                if 'metadata' in chunk:
                    metadata.update(chunk['metadata'])
                metadata_list.append(metadata)
            
            # 存储到ChromaDB
            collection_name = f"novel_{novel_id}"
            success = self.add_chapter_chunks(
                collection_name=collection_name,
                chunks=texts,
                embeddings=embeddings,
                metadata_list=metadata_list
            )
            
            return success, tokens_used
            
        except Exception as e:
            logger.error(f"❌ 处理章节 {chapter_num} 失败: {e}")
            return False, 0
    
    def query_similar_chunks(
        self,
        novel_id: int,
        query_text: str,
        top_k: int = 30,
        chapter_filter: Optional[Dict] = None
    ) -> Dict:
        """
        查询相似文本块
        
        Args:
            novel_id: 小说ID
            query_text: 查询文本
            top_k: 返回Top-K结果
            chapter_filter: 章节过滤条件
        
        Returns:
            Dict: 查询结果
        """
        try:
            # 向量化查询文本
            query_embedding = self.zhipu_client.embed_text(query_text)
            
            # 从ChromaDB检索
            collection_name = f"novel_{novel_id}"
            results = self.chroma_client.query_documents(
                collection_name=collection_name,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=chapter_filter
            )
            
            logger.info(f"✅ 检索到 {len(results.get('ids', [[]])[0])} 个相似块")
            return results
            
        except Exception as e:
            logger.error(f"❌ 相似块查询失败: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}


# 全局向量化服务实例
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """获取全局向量化服务实例（单例）"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

