"""
时间轴构建器

构建完整的时间线，标注叙述顺序vs真实顺序
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TimelineBuilder:
    """时间轴构建器"""
    
    def __init__(self):
        """初始化时间轴构建器"""
        logger.info("✅ 时间轴构建器初始化完成")
    
    def build_timeline(
        self,
        time_markers: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        构建完整时间线
        
        Args:
            time_markers: 时间标记列表
            events: 事件列表
        
        Returns:
            Dict: 时间线数据
                - narrative_order: 叙述顺序（章节顺序）
                - chronological_order: 真实顺序（时间顺序）
                - non_linear_segments: 非线性叙事片段
        """
        # 1. 按叙述顺序排列（章节顺序）
        narrative_order = sorted(events, key=lambda x: x.get('chapter', 0))
        
        # 2. 尝试推断真实时间顺序
        chronological_order = self._infer_chronological_order(
            events, time_markers
        )
        
        # 3. 检测非线性叙事片段
        non_linear_segments = self._detect_non_linear_segments(
            narrative_order, chronological_order
        )
        
        timeline = {
            'narrative_order': narrative_order,
            'chronological_order': chronological_order,
            'non_linear_segments': non_linear_segments,
            'metadata': {
                'total_events': len(events),
                'non_linear_count': len(non_linear_segments),
                'is_linear': len(non_linear_segments) == 0
            }
        }
        
        logger.info(
            f"✅ 时间线构建完成: {len(events)} 事件, "
            f"{len(non_linear_segments)} 非线性片段"
        )
        
        return timeline
    
    def _infer_chronological_order(
        self,
        events: List[Dict],
        time_markers: List[Dict]
    ) -> List[Dict]:
        """
        推断真实时间顺序
        
        基于时间标记推断事件的真实发生顺序
        
        Args:
            events: 事件列表
            time_markers: 时间标记列表
        
        Returns:
            List[Dict]: 按真实时间排序的事件列表
        """
        # 为每个事件分配真实时间戳
        events_with_time = []
        
        for event in events:
            chapter = event.get('chapter', 0)
            
            # 查找该章节的时间标记
            chapter_markers = [
                m for m in time_markers 
                if m.get('chapter') == chapter
            ]
            
            # 推断真实时间
            inferred_time = self._infer_real_time(
                chapter, chapter_markers
            )
            
            event_copy = event.copy()
            event_copy['inferred_time'] = inferred_time
            event_copy['has_time_marker'] = len(chapter_markers) > 0
            events_with_time.append(event_copy)
        
        # 按推断的真实时间排序
        chronological = sorted(
            events_with_time,
            key=lambda x: x.get('inferred_time', x.get('chapter', 0))
        )
        
        return chronological
    
    def _infer_real_time(
        self,
        chapter: int,
        markers: List[Dict]
    ) -> float:
        """
        推断真实时间
        
        Args:
            chapter: 章节号
            markers: 该章节的时间标记
        
        Returns:
            float: 推断的真实时间（相对值）
        """
        # 默认假设真实时间 = 章节号（线性叙事）
        real_time = float(chapter)
        
        # 如果有时间标记，调整真实时间
        for marker in markers:
            marker_type = marker.get('type')
            
            if marker_type == 'year_offset':
                # "X年后" 或 "X年前"
                offset_years = int(marker.get('value', 0))
                direction = marker.get('direction', '后')
                
                if direction == '后':
                    real_time += offset_years * 365
                else:
                    real_time -= offset_years * 365
            
            elif marker_type == 'month_offset':
                offset_months = int(marker.get('value', 0))
                direction = marker.get('direction', '后')
                
                if direction == '后':
                    real_time += offset_months * 30
                else:
                    real_time -= offset_months * 30
            
            elif marker_type == 'day_offset':
                offset_days = int(marker.get('value', 0))
                direction = marker.get('direction', '后')
                
                if direction == '后':
                    real_time += offset_days
                else:
                    real_time -= offset_days
        
        return real_time
    
    def _detect_non_linear_segments(
        self,
        narrative_order: List[Dict],
        chronological_order: List[Dict]
    ) -> List[Dict]:
        """
        检测非线性叙事片段
        
        对比叙述顺序和真实顺序，找出倒叙、插叙等非线性片段
        
        Args:
            narrative_order: 叙述顺序
            chronological_order: 真实顺序
        
        Returns:
            List[Dict]: 非线性片段列表
        """
        non_linear_segments = []
        
        # 为每个事件分配叙述索引和真实索引
        narrative_index = {
            event.get('description', ''): i
            for i, event in enumerate(narrative_order)
        }
        
        chronological_index = {
            event.get('description', ''): i
            for i, event in enumerate(chronological_order)
        }
        
        # 检测顺序不一致的片段
        for i, event in enumerate(narrative_order):
            desc = event.get('description', '')
            if desc not in chronological_index:
                continue
            
            narr_idx = narrative_index[desc]
            chrono_idx = chronological_index[desc]
            
            # 如果叙述顺序和真实顺序相差较大，标记为非线性
            if abs(narr_idx - chrono_idx) > 5:
                non_linear_segments.append({
                    'chapter': event.get('chapter'),
                    'event': desc,
                    'narrative_position': narr_idx,
                    'chronological_position': chrono_idx,
                    'type': self._classify_non_linear_type(narr_idx, chrono_idx),
                    'severity': abs(narr_idx - chrono_idx)
                })
        
        return non_linear_segments
    
    def _classify_non_linear_type(
        self,
        narrative_pos: int,
        chronological_pos: int
    ) -> str:
        """
        分类非线性叙事类型
        
        Args:
            narrative_pos: 叙述位置
            chronological_pos: 真实位置
        
        Returns:
            str: 非线性类型（倒叙/插叙/预叙）
        """
        diff = chronological_pos - narrative_pos
        
        if diff > 5:
            return '倒叙'  # 叙述早于真实发生
        elif diff < -5:
            return '预叙'  # 叙述晚于真实发生
        else:
            return '插叙'


# 全局实例
_timeline_builder: Optional[TimelineBuilder] = None


def get_timeline_builder() -> TimelineBuilder:
    """获取全局时间轴构建器实例（单例）"""
    global _timeline_builder
    if _timeline_builder is None:
        _timeline_builder = TimelineBuilder()
    return _timeline_builder

