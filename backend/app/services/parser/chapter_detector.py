"""
章节识别算法
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ChapterDetector:
    """章节检测器"""
    
    # 常见章节模式（按优先级排序）
    CHAPTER_PATTERNS = [
        # 中文数字章节
        (r'^第[零一二三四五六七八九十百千万]+章[　\s]*(.*)$', 'chinese_number'),
        (r'^第[零一二三四五六七八九十百千万]+节[　\s]*(.*)$', 'chinese_section'),
        
        # 阿拉伯数字章节
        (r'^第\d+章[　\s]*(.*)$', 'arabic_chapter'),
        (r'^第\d+节[　\s]*(.*)$', 'arabic_section'),
        (r'^\d+\.[　\s]*(.*)$', 'numbered_dot'),
        (r'^\d+、(.*)$', 'numbered_comma'),
        
        # 英文章节
        (r'^Chapter\s+\d+[　\s:：]*(.*)$', 'english_chapter'),
        (r'^CHAPTER\s+\d+[　\s:：]*(.*)$', 'english_chapter_upper'),
        
        # 卷/部分
        (r'^第[零一二三四五六七八九十百千万]+卷[　\s]*(.*)$', 'volume'),
        (r'^第\d+卷[　\s]*(.*)$', 'volume_arabic'),
        
        # 序章/尾声等特殊章节
        (r'^(序章|序言|楔子|引子)[　\s]*(.*)$', 'prologue'),
        (r'^(尾声|后记|结语|番外)[　\s]*(.*)$', 'epilogue'),
    ]
    
    @classmethod
    def detect(
        cls,
        content: str,
        custom_patterns: Optional[List[str]] = None,
        min_chapter_length: int = 100
    ) -> List[Dict]:
        """
        检测章节
        
        Args:
            content: 文本内容
            custom_patterns: 自定义章节模式
            min_chapter_length: 最小章节长度（字符数）
        
        Returns:
            List[Dict]: 章节列表
        """
        patterns = cls.CHAPTER_PATTERNS.copy()
        
        # 添加自定义模式
        if custom_patterns:
            patterns.extend([(p, 'custom') for p in custom_patterns])
        
        chapters = []
        lines = content.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # 跳过空行和过短的行
            if not line_stripped or len(line_stripped) < 2:
                current_pos += len(line) + 1
                continue
            
            # 尝试匹配章节标题
            for pattern, pattern_type in patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    # 提取标题
                    if pattern_type in ['prologue', 'epilogue']:
                        title = line_stripped
                    else:
                        title = match.group(0) if len(match.groups()) == 0 else match.group(0)
                    
                    chapters.append({
                        'chapter_num': len(chapters) + 1,
                        'title': title.strip(),
                        'start_line': i,
                        'start_pos': current_pos,
                        'pattern_type': pattern_type
                    })
                    break
            
            current_pos += len(line) + 1  # +1 for \n
        
        # 如果没检测到章节，将整个文本作为一章
        if not chapters:
            logger.warning("⚠️ 未检测到章节，将整个文本作为单章")
            chapters.append({
                'chapter_num': 1,
                'title': '全文',
                'start_line': 0,
                'start_pos': 0,
                'pattern_type': 'full_text'
            })
        
        # 补充结束位置和字符数
        total_lines = len(lines)
        total_chars = len(content)
        
        for i, chapter in enumerate(chapters):
            if i < len(chapters) - 1:
                chapter['end_line'] = chapters[i + 1]['start_line'] - 1
                chapter['end_pos'] = chapters[i + 1]['start_pos'] - 1
            else:
                chapter['end_line'] = total_lines - 1
                chapter['end_pos'] = total_chars
            
            # 计算章节长度
            chapter['char_count'] = chapter['end_pos'] - chapter['start_pos']
        
        # 过滤过短的章节（可能是误判）
        filtered_chapters = []
        for chapter in chapters:
            if chapter['char_count'] >= min_chapter_length:
                filtered_chapters.append(chapter)
            else:
                logger.debug(f"⚠️ 跳过过短章节: {chapter['title']} ({chapter['char_count']} 字符)")
        
        # 重新编号
        for i, chapter in enumerate(filtered_chapters):
            chapter['chapter_num'] = i + 1
        
        logger.info(f"✅ 检测到 {len(filtered_chapters)} 个有效章节")
        return filtered_chapters
    
    @classmethod
    def extract_chapter_content(
        cls,
        content: str,
        start_pos: int,
        end_pos: int,
        include_title: bool = True
    ) -> str:
        """
        提取章节内容
        
        Args:
            content: 完整文本
            start_pos: 起始位置
            end_pos: 结束位置
            include_title: 是否包含章节标题
        
        Returns:
            str: 章节内容
        """
        chapter_content = content[start_pos:end_pos].strip()
        
        if not include_title:
            # 移除第一行（章节标题）
            lines = chapter_content.split('\n', 1)
            if len(lines) > 1:
                chapter_content = lines[1].strip()
        
        return chapter_content
    
    @classmethod
    def merge_short_chapters(
        cls,
        chapters: List[Dict],
        min_length: int = 500
    ) -> List[Dict]:
        """
        合并过短的章节
        
        Args:
            chapters: 章节列表
            min_length: 最小章节长度
        
        Returns:
            List[Dict]: 合并后的章节列表
        """
        if not chapters:
            return []
        
        merged = []
        current_chapter = chapters[0].copy()
        
        for i in range(1, len(chapters)):
            next_chapter = chapters[i]
            
            # 如果当前章节过短，与下一章合并
            if current_chapter['char_count'] < min_length:
                current_chapter['end_pos'] = next_chapter['end_pos']
                current_chapter['end_line'] = next_chapter['end_line']
                current_chapter['char_count'] = current_chapter['end_pos'] - current_chapter['start_pos']
                current_chapter['title'] += f" + {next_chapter['title']}"
            else:
                merged.append(current_chapter)
                current_chapter = next_chapter.copy()
        
        # 添加最后一章
        merged.append(current_chapter)
        
        # 重新编号
        for i, chapter in enumerate(merged):
            chapter['chapter_num'] = i + 1
        
        logger.info(f"✅ 合并后剩余 {len(merged)} 个章节")
        return merged

