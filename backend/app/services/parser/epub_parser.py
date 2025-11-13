"""
EPUB文件解析器
"""

import logging
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class EPUBParser:
    """EPUB文件解析器"""
    
    def parse_file(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析EPUB文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            Tuple[str, Dict]: (文本内容, 元数据)
        """
        try:
            # 读取EPUB文件
            book = epub.read_epub(file_path)
            
            # 提取元数据
            metadata = {
                'title': book.get_metadata('DC', 'title'),
                'author': book.get_metadata('DC', 'creator'),
                'language': book.get_metadata('DC', 'language'),
            }
            
            # 提取所有文本内容
            content_parts = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 解析HTML内容
                    html_content = item.get_content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 提取纯文本
                    text = soup.get_text(separator='\n', strip=True)
                    if text:
                        content_parts.append(text)
            
            # 合并所有内容
            full_content = '\n\n'.join(content_parts)
            
            metadata['total_chars'] = len(full_content)
            metadata['total_sections'] = len(content_parts)
            
            logger.info(f"✅ EPUB文件解析完成: {metadata['total_chars']} 字符, {metadata['total_sections']} 节")
            return full_content, metadata
            
        except Exception as e:
            logger.error(f"❌ EPUB文件解析失败: {e}")
            raise
    
    def detect_chapters(self, book_path: str) -> List[Dict]:
        """
        检测EPUB章节
        
        Args:
            book_path: EPUB文件路径
        
        Returns:
            List[Dict]: 章节列表
        """
        try:
            book = epub.read_epub(book_path)
            chapters = []
            current_pos = 0
            
            for i, item in enumerate(book.get_items()):
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 解析HTML
                    html_content = item.get_content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 提取标题（通常在h1, h2标签中）
                    title_tag = soup.find(['h1', 'h2', 'h3'])
                    title = title_tag.get_text(strip=True) if title_tag else f"第{i+1}章"
                    
                    # 提取文本
                    text = soup.get_text(separator='\n', strip=True)
                    
                    if text:
                        chapters.append({
                            'chapter_num': len(chapters) + 1,
                            'title': title,
                            'start_pos': current_pos,
                            'end_pos': current_pos + len(text),
                            'char_count': len(text)
                        })
                        
                        current_pos += len(text) + 2  # +2 for \n\n
            
            logger.info(f"✅ EPUB检测到 {len(chapters)} 个章节")
            return chapters
            
        except Exception as e:
            logger.error(f"❌ EPUB章节检测失败: {e}")
            raise

