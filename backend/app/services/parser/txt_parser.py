"""
TXT文件解析器
"""

import logging
from pathlib import Path
from typing import List, Tuple, Dict
import re

from app.utils.encoding_detector import EncodingDetector

logger = logging.getLogger(__name__)


class TXTParser:
    """TXT文件解析器"""
    
    def __init__(self):
        """初始化TXT解析器"""
        self.encoding_detector = EncodingDetector()
    
    def parse_file(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析TXT文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            Tuple[str, Dict]: (文本内容, 元数据)
        """
        try:
            # 读取文件内容（自动检测编码）
            content = self.encoding_detector.read_text_file(file_path)
            
            # 统计基本信息
            metadata = {
                'total_chars': len(content),
                'total_lines': content.count('\n') + 1,
                'file_size': Path(file_path).stat().st_size
            }
            
            logger.info(f"✅ TXT文件解析完成: {metadata['total_chars']} 字符")
            return content, metadata
            
        except Exception as e:
            logger.error(f"❌ TXT文件解析失败: {e}")
            raise
    
    def detect_chapters(
        self,
        content: str,
        patterns: List[str] = None
    ) -> List[Dict]:
        """
        检测章节
        
        Args:
            content: 文本内容
            patterns: 章节标题正则模式列表
        
        Returns:
            List[Dict]: 章节列表
        """
        if patterns is None:
            # 默认章节模式（支持多种常见格式）
            patterns = [
                r'^第[零一二三四五六七八九十百千万\d]+章[　\s]*(.*)$',  # 第一章 标题
                r'^第[零一二三四五六七八九十百千万\d]+节[　\s]*(.*)$',  # 第一节 标题
                r'^[零一二三四五六七八九十百千万\d]+[、\s]+(.*)$',      # 1、标题
                r'^Chapter\s+[\d]+[　\s]*(.*)$',  # Chapter 1
                r'^\d+[　\s]*(.*)$',  # 纯数字章节
            ]
        
        chapters = []
        lines = content.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 尝试匹配章节标题
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # 找到章节
                    title = line
                    chapter_num = len(chapters) + 1
                    
                    chapters.append({
                        'chapter_num': chapter_num,
                        'title': title,
                        'start_line': i,
                        'start_pos': current_pos
                    })
                    break
            
            current_pos += len(line) + 1  # +1 for \n
        
        # 补充结束位置
        for i, chapter in enumerate(chapters):
            if i < len(chapters) - 1:
                chapter['end_line'] = chapters[i + 1]['start_line'] - 1
                chapter['end_pos'] = chapters[i + 1]['start_pos'] - 1
            else:
                chapter['end_line'] = len(lines) - 1
                chapter['end_pos'] = len(content)
        
        logger.info(f"✅ 检测到 {len(chapters)} 个章节")
        return chapters
    
    def extract_chapter_content(
        self,
        content: str,
        start_pos: int,
        end_pos: int
    ) -> str:
        """
        提取章节内容
        
        Args:
            content: 完整文本
            start_pos: 起始位置
            end_pos: 结束位置
        
        Returns:
            str: 章节内容
        """
        chapter_content = content[start_pos:end_pos].strip()
        return chapter_content

