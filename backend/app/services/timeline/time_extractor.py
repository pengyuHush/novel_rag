"""
时间标记提取器

从文本中提取时间相关信息
"""

import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TimeExtractor:
    """时间标记提取器"""
    
    # 时间关键词
    TIME_KEYWORDS = [
        # 绝对时间
        "年", "月", "日", "时", "分", "秒",
        "春", "夏", "秋", "冬",
        "早晨", "中午", "下午", "傍晚", "晚上", "深夜", "凌晨",
        # 相对时间
        "之前", "之后", "以前", "以后", "过去", "未来",
        "同时", "此时", "那时", "当时",
        "第一天", "第二天", "第三天", "数日后", "数月后", "数年后",
        "不久", "许久", "良久", "片刻", "瞬间",
    ]
    
    # 时间跨度关键词
    SPAN_KEYWORDS = [
        "持续", "经过", "历时", "用了", "花了", "度过",
    ]
    
    def __init__(self):
        """初始化时间提取器"""
        logger.info("✅ 时间提取器初始化完成")
    
    def extract_time_markers(
        self,
        text: str,
        chapter_num: int
    ) -> List[Dict]:
        """
        从文本中提取时间标记
        
        Args:
            text: 文本内容
            chapter_num: 章节号
        
        Returns:
            List[Dict]: 时间标记列表
        """
        markers = []
        
        # 1. 提取显式时间标记
        explicit_markers = self._extract_explicit_time(text, chapter_num)
        markers.extend(explicit_markers)
        
        # 2. 提取相对时间标记
        relative_markers = self._extract_relative_time(text, chapter_num)
        markers.extend(relative_markers)
        
        # 3. 提取时间跨度
        span_markers = self._extract_time_span(text, chapter_num)
        markers.extend(span_markers)
        
        return markers
    
    def _extract_explicit_time(
        self,
        text: str,
        chapter_num: int
    ) -> List[Dict]:
        """
        提取显式时间标记
        
        如："三年后"、"春天"、"中午"
        """
        markers = []
        
        # 匹配"X年后"、"X月后"等模式
        time_patterns = [
            (r'(\d+)[年岁]([之以]?后|前)', 'year_offset'),
            (r'(\d+)[月个]月([之以]?后|前)', 'month_offset'),
            (r'(\d+)[日天]([之以]?后|前)', 'day_offset'),
        ]
        
        for pattern, marker_type in time_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                markers.append({
                    'type': marker_type,
                    'value': match.group(1),
                    'direction': '后' if '后' in match.group(2) else '前',
                    'text': match.group(0),
                    'chapter': chapter_num,
                    'position': match.start()
                })
        
        # 匹配季节、时段
        for keyword in ['春', '夏', '秋', '冬', '早晨', '中午', '下午', '晚上']:
            if keyword in text:
                markers.append({
                    'type': 'time_period',
                    'value': keyword,
                    'text': keyword,
                    'chapter': chapter_num,
                })
        
        return markers
    
    def _extract_relative_time(
        self,
        text: str,
        chapter_num: int
    ) -> List[Dict]:
        """
        提取相对时间标记
        
        如："此时"、"同时"、"不久后"
        """
        markers = []
        
        relative_words = ['此时', '那时', '当时', '同时', '不久', '许久', '片刻']
        
        for word in relative_words:
            if word in text:
                markers.append({
                    'type': 'relative_time',
                    'value': word,
                    'text': word,
                    'chapter': chapter_num,
                })
        
        return markers
    
    def _extract_time_span(
        self,
        text: str,
        chapter_num: int
    ) -> List[Dict]:
        """
        提取时间跨度
        
        如："持续三天"、"经过数月"
        """
        markers = []
        
        # 匹配时间跨度模式
        span_patterns = [
            r'(持续|经过|历时|用了|花了|度过)[了]?(\d+)([年月日天时分])',
        ]
        
        for pattern in span_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                markers.append({
                    'type': 'time_span',
                    'action': match.group(1),
                    'value': match.group(2),
                    'unit': match.group(3),
                    'text': match.group(0),
                    'chapter': chapter_num,
                })
        
        return markers


# 全局实例
_time_extractor: Optional[TimeExtractor] = None


def get_time_extractor() -> TimeExtractor:
    """获取全局时间提取器实例（单例）"""
    global _time_extractor
    if _time_extractor is None:
        _time_extractor = TimeExtractor()
    return _time_extractor

