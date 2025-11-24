"""
BM25 检索器
实现基于关键词的精确检索，弥补向量检索在专有名词上的不足
"""

import os
import pickle
import logging
import jieba
from typing import List, Dict, Any, Optional
from pathlib import Path
from rank_bm25 import BM25Okapi

from app.core.config import settings

logger = logging.getLogger(__name__)

class BM25Retriever:
    """
    BM25 检索器
    负责构建、存储、加载和检索 BM25 索引
    """
    
    def __init__(self, novel_id: int):
        """
        初始化 BM25 检索器
        
        Args:
            novel_id: 小说ID
        """
        self.novel_id = novel_id
        self.bm25 = None
        self.documents = []  # 存储原始文档内容（或引用），用于检索返回
        self.metadatas = []  # 存储元数据
        
        # 索引存储路径
        self.index_dir = Path(settings.data_dir) / "indices"
        self.index_path = self.index_dir / f"novel_{novel_id}_bm25.pkl"
        
        # 确保目录存在
        if not self.index_dir.exists():
            self.index_dir.mkdir(parents=True, exist_ok=True)
            
    def _tokenize(self, text: str) -> List[str]:
        """
        对中文文本进行分词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 分词结果
        """
        # 使用 jieba 进行搜索引擎模式分词
        return list(jieba.cut_for_search(text))
        
    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        构建 BM25 索引
        
        Args:
            chunks: 文本块列表，每个元素包含 'content' 和 'metadata'
        """
        logger.info(f"🏗️ 开始构建 BM25 索引 (Novel ID: {self.novel_id})...")
        
        texts = [chunk['content'] for chunk in chunks]
        self.documents = texts
        self.metadatas = [chunk.get('metadata', {}) for chunk in chunks]
        
        # 分词
        tokenized_corpus = [self._tokenize(text) for text in texts]
        
        # 构建索引
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        logger.info(f"✅ BM25 索引构建完成，共 {len(texts)} 个文档")
        
        # 保存索引
        self.save_index()
        
    def save_index(self):
        """保存索引到磁盘"""
        try:
            data = {
                'bm25': self.bm25,
                'documents': self.documents,
                'metadatas': self.metadatas
            }
            with open(self.index_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"💾 BM25 索引已保存至: {self.index_path}")
        except Exception as e:
            logger.error(f"❌ 保存 BM25 索引失败: {e}")
            raise
            
    def load_index(self) -> bool:
        """
        从磁盘加载索引
        
        Returns:
            bool: 是否加载成功
        """
        if not self.index_path.exists():
            logger.warning(f"⚠️ BM25 索引文件不存在: {self.index_path}")
            return False
            
        try:
            with open(self.index_path, 'rb') as f:
                data = pickle.load(f)
                self.bm25 = data['bm25']
                self.documents = data['documents']
                self.metadatas = data['metadatas']
            logger.info(f"✅ BM25 索引加载成功 (Novel ID: {self.novel_id})")
            return True
        except Exception as e:
            logger.error(f"❌ 加载 BM25 索引失败: {e}")
            return False
            
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        执行关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict]: 检索结果列表，包含 content, metadata, score
        """
        if not self.bm25:
            if not self.load_index():
                return []
                
        tokenized_query = self._tokenize(query)
        
        # 获取分数
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取 top_k 索引
        # argsort 返回从小到大的索引，所以取最后 k 个并反转
        top_n_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for i in top_n_indices:
            score = scores[i]
            if score > 0:  # 只返回正相关结果
                results.append({
                    'content': self.documents[i],
                    'metadata': self.metadatas[i],
                    'score': float(score),  # 转换为 float 以便序列化
                    'rank': len(results) + 1
                })
                
        return results

    def delete_index(self):
        """删除索引文件"""
        if self.index_path.exists():
            try:
                os.remove(self.index_path)
                logger.info(f"🗑️ BM25 索引已删除: {self.index_path}")
            except Exception as e:
                logger.error(f"❌ 删除 BM25 索引失败: {e}")

