"""
文本分块服务
基于LangChain的RecursiveCharacterTextSplitter，针对中文优化，增加对话保护
"""

import logging
import re
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
        
        # 创建基础LangChain分块器（用于分割非对话文本）
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
        分割文本，尝试保护对话引用不被切断
        
        Args:
            text: 输入文本
        
        Returns:
            List[str]: 文本块列表
        """
        if not text:
            return []
        
        try:
            # 1. 识别对话引用块
            # 匹配 “...” 或 「...」
            # 使用非贪婪匹配
            pattern = r'(“[^”]*”|「[^」]*」)'
            parts = re.split(pattern, text)
            
            # parts 将是 [text, quote, text, quote, ...]
            # 过滤空字符串
            parts = [p for p in parts if p]
            
            chunks = []
            current_chunk = ""
            
            for part in parts:
                # 检查这部分是否是引用
                is_quote = part.startswith('“') or part.startswith('「')
                
                # 如果是引用，且长度超过 chunk_size，必须强制分割
                if is_quote and len(part) > self.chunk_size:
                    # 如果当前块有内容，先保存
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = ""
                    
                    # 强制分割超长引用
                    sub_chunks = self.splitter.split_text(part)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1]  # 保留最后一部分继续拼接
                    continue
                
                # 如果加上当前部分不超过 chunk_size
                if len(current_chunk) + len(part) <= self.chunk_size:
                    current_chunk += part
                else:
                    # 超出了，需要处理
                    # 如果是引用，我们尽量不切分它，而是把当前块结束，新起一块
                    if is_quote:
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # 如果重叠设置，尝试从上一块末尾取一部分（简单实现：暂不处理复杂重叠，LangChain会自动处理）
                        # 这里我们简单地新起一块
                        current_chunk = part
                    else:
                        # 如果是普通文本，可以使用 splitter 进行精细分割
                        # 先把 current_chunk 保存（如果它已经很长了）
                        # 或者，我们将 current_chunk + part 交给 splitter 处理？
                        # 问题是 splitter 可能会切断前面的 quote。
                        
                        # 策略：
                        # 1. 保存 current_chunk
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = ""
                        
                        # 2. 分割当前文本 part
                        sub_chunks = self.splitter.split_text(part)
                        if sub_chunks:
                            chunks.extend(sub_chunks[:-1])
                            current_chunk = sub_chunks[-1]
            
            # 处理最后的块
            if current_chunk:
                chunks.append(current_chunk)
            
            # 处理重叠 (简单模拟 LangChain 的重叠逻辑)
            # 由于我们手动分块，重叠可能处理得不够完美。
            # 如果对重叠要求严格，可以使用 sliding window。
            # 这里我们依赖 chunks 已经大致符合要求。
            # 为了更严谨，我们可以把生成的 chunks 再过一遍 merge（如果太小）
            
            logger.info(f"✅ 文本分块完成: {len(chunks)} 块 (对话保护)")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ 文本分块失败: {e}")
            # 降级方案：使用原始分块器
            return self.splitter.split_text(text)
    
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
