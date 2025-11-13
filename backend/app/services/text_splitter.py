"""
文本分块服务
基于LangChain的RecursiveCharacterTextSplitter，针对中文优化
"""

import logging
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChineseTextSplitter:
    """中文文本分块器"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 块大小（字符数）
            chunk_overlap: 重叠大小（字符数）
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # 中文分隔符优先级（从高到低）
        chinese_separators = [
            "\n\n",      # 段落分隔
            "\n",        # 行分隔
            "。",        # 句号
            "！",        # 感叹号
            "？",        # 问号
            "；",        # 分号
            "，",        # 逗号
            " ",         # 空格
            "",          # 字符级别
        ]
        
        # 创建LangChain分块器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=chinese_separators,
            length_function=len,
            is_separator_regex=False
        )
        
        logger.info(f"✅ 文本分块器初始化 (size={self.chunk_size}, overlap={self.chunk_overlap})")
    
    def split_text(self, text: str) -> List[str]:
        """
        分割文本
        
        Args:
            text: 输入文本
        
        Returns:
            List[str]: 文本块列表
        """
        if not text:
            return []
        
        try:
            chunks = self.splitter.split_text(text)
            logger.info(f"✅ 文本分块完成: {len(chunks)} 块")
            return chunks
        except Exception as e:
            logger.error(f"❌ 文本分块失败: {e}")
            raise
    
    def split_documents(
        self,
        text: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """
        分割文本并生成文档对象
        
        Args:
            text: 输入文本
            metadata: 元数据
        
        Returns:
            List[Dict]: 文档对象列表
        """
        chunks = self.split_text(text)
        metadata = metadata or {}
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                'content': chunk,
                'metadata': {
                    **metadata,
                    'chunk_index': i,
                    'chunk_size': len(chunk)
                }
            }
            documents.append(doc)
        
        return documents
    
    def split_chapter(
        self,
        chapter_content: str,
        novel_id: int,
        chapter_num: int,
        chapter_title: str = None
    ) -> List[Dict]:
        """
        分割章节内容
        
        Args:
            chapter_content: 章节内容
            novel_id: 小说ID
            chapter_num: 章节编号
            chapter_title: 章节标题
        
        Returns:
            List[Dict]: 章节块列表
        """
        metadata = {
            'novel_id': novel_id,
            'chapter_num': chapter_num,
            'chapter_title': chapter_title or f"第{chapter_num}章"
        }
        
        return self.split_documents(chapter_content, metadata)
    
    def get_chunk_stats(self, chunks: List[str]) -> Dict:
        """
        获取分块统计信息
        
        Args:
            chunks: 文本块列表
        
        Returns:
            Dict: 统计信息
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_chars': 0,
                'avg_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0
            }
        
        chunk_sizes = [len(chunk) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_chars': sum(chunk_sizes),
            'avg_chunk_size': sum(chunk_sizes) / len(chunks),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes)
        }


# 全局文本分块器实例
_text_splitter = None


def get_text_splitter() -> ChineseTextSplitter:
    """获取全局文本分块器实例（单例）"""
    global _text_splitter
    if _text_splitter is None:
        _text_splitter = ChineseTextSplitter()
    return _text_splitter

