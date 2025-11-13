"""
矛盾检测器

基于断言、证据和一致性检查结果检测矛盾
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.schemas import Contradiction

logger = logging.getLogger(__name__)


class ContradictionDetector:
    """矛盾检测器"""
    
    def __init__(self):
        """初始化矛盾检测器"""
        logger.info("✅ 矛盾检测器初始化完成")
    
    def detect_contradictions(
        self,
        db: Session,
        novel_id: int,
        assertions: List[Dict],
        evidence_map: Dict[int, List[Dict]],
        consistency_report: Dict
    ) -> List[Contradiction]:
        """
        综合检测矛盾
        
        结合多种信息源：
        1. 一致性检查发现的问题
        2. 断言之间的直接冲突
        3. 断言与证据之间的不匹配
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            assertions: 断言列表
            evidence_map: 证据映射
            consistency_report: 一致性检查报告
        
        Returns:
            List[Contradiction]: 矛盾列表
        """
        contradictions = []
        
        # 1. 从一致性检查中提取矛盾
        for issue in consistency_report.get('temporal_issues', []):
            contradiction = self._issue_to_contradiction(issue, 'temporal')
            if contradiction:
                contradictions.append(contradiction)
        
        for issue in consistency_report.get('character_issues', []):
            contradiction = self._issue_to_contradiction(issue, 'character')
            if contradiction:
                contradictions.append(contradiction)
        
        # 2. 直接检测断言之间的冲突
        direct_conflicts = self._detect_direct_conflicts(assertions)
        contradictions.extend(direct_conflicts)
        
        # 3. 检测证据支持度不足
        weak_support = self._detect_weak_support(assertions, evidence_map)
        contradictions.extend(weak_support)
        
        # 去重和排序
        contradictions = self._deduplicate_contradictions(contradictions)
        
        logger.info(f"✅ 矛盾检测: 发现 {len(contradictions)} 个矛盾")
        
        return contradictions
    
    def _issue_to_contradiction(
        self,
        issue: Dict,
        issue_type: str
    ) -> Optional[Contradiction]:
        """
        将一致性问题转换为矛盾对象
        
        Args:
            issue: 一致性问题
            issue_type: 问题类型（temporal/character）
        
        Returns:
            Optional[Contradiction]: 矛盾对象
        """
        try:
            assertion1 = issue.get('assertion1', {})
            assertion2 = issue.get('assertion2', {})
            
            contradiction_type_map = {
                'temporal': '时间线矛盾',
                'character': '角色设定矛盾'
            }
            
            return Contradiction(
                type=contradiction_type_map.get(issue_type, '情节不一致'),
                early_description=assertion1.get('assertion', ''),
                early_chapter=assertion1.get('chapter_ref', 0),
                late_description=assertion2.get('assertion', ''),
                late_chapter=assertion2.get('chapter_ref', 0),
                analysis=issue.get('description', '检测到矛盾'),
                confidence='high' if issue.get('severity') == 'high' else 'medium'
            )
        except Exception as e:
            logger.error(f"转换矛盾失败: {e}")
            return None
    
    def _detect_direct_conflicts(
        self,
        assertions: List[Dict]
    ) -> List[Contradiction]:
        """
        检测断言之间的直接冲突
        
        使用语义相似度和关键词匹配
        
        Args:
            assertions: 断言列表
        
        Returns:
            List[Contradiction]: 冲突列表
        """
        conflicts = []
        
        # 定义冲突词对
        conflict_pairs = [
            ('是', '不是'),
            ('有', '没有'),
            ('能', '不能'),
            ('会', '不会'),
            ('成功', '失败'),
            ('胜利', '失败'),
            ('活着', '死了'),
        ]
        
        # 两两比较断言
        for i in range(len(assertions)):
            for j in range(i + 1, len(assertions)):
                assert1 = assertions[i]
                assert2 = assertions[j]
                
                text1 = assert1.get('assertion', '')
                text2 = assert2.get('assertion', '')
                
                # 提取共同实体
                entities1 = set(assert1.get('entities', []))
                entities2 = set(assert2.get('entities', []))
                common_entities = entities1 & entities2
                
                if not common_entities:
                    continue  # 无共同实体，无法判断冲突
                
                # 检测冲突词
                for word1, word2 in conflict_pairs:
                    if word1 in text1 and word2 in text2:
                        # 发现潜在冲突
                        chapter1 = assert1.get('chapter_ref', 0)
                        chapter2 = assert2.get('chapter_ref', 0)
                        
                        if chapter1 and chapter2 and abs(chapter2 - chapter1) > 10:
                            # 章节相隔较远，可能是真正的矛盾
                            conflicts.append(Contradiction(
                                type='情节不一致',
                                early_description=text1,
                                early_chapter=min(chapter1, chapter2),
                                late_description=text2,
                                late_chapter=max(chapter1, chapter2),
                                analysis=f"关于{','.join(common_entities)}的描述前后不一致",
                                confidence='medium'
                            ))
        
        return conflicts
    
    def _detect_weak_support(
        self,
        assertions: List[Dict],
        evidence_map: Dict[int, List[Dict]]
    ) -> List[Contradiction]:
        """
        检测证据支持度不足的断言
        
        如果断言缺乏证据支持，可能存在问题
        
        Args:
            assertions: 断言列表
            evidence_map: 证据映射
        
        Returns:
            List[Contradiction]: 弱支持问题列表
        """
        weak_support_list = []
        
        for idx, assertion in enumerate(assertions):
            evidence_list = evidence_map.get(idx, [])
            
            # 如果高置信度断言缺少证据，标记为潜在问题
            if assertion.get('confidence', 0) > 0.7 and len(evidence_list) == 0:
                weak_support_list.append(Contradiction(
                    type='证据不足',
                    early_description=assertion.get('assertion', ''),
                    early_chapter=assertion.get('chapter_ref', 0),
                    late_description='缺少证据支持',
                    late_chapter=assertion.get('chapter_ref', 0),
                    analysis='该断言缺少证据支持，可能存在错误',
                    confidence='low'
                ))
        
        return weak_support_list
    
    def _deduplicate_contradictions(
        self,
        contradictions: List[Contradiction]
    ) -> List[Contradiction]:
        """
        去重矛盾
        
        Args:
            contradictions: 矛盾列表
        
        Returns:
            List[Contradiction]: 去重后的列表
        """
        # 简单去重：基于章节号和类型
        seen = set()
        unique = []
        
        for contradiction in contradictions:
            key = (
                contradiction.type,
                contradiction.early_chapter,
                contradiction.late_chapter
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(contradiction)
        
        # 按置信度和章节号排序
        confidence_order = {'high': 3, 'medium': 2, 'low': 1}
        unique.sort(
            key=lambda x: (
                -confidence_order.get(x.confidence, 0),
                x.early_chapter
            )
        )
        
        return unique


# 全局实例
_contradiction_detector: Optional[ContradictionDetector] = None


def get_contradiction_detector() -> ContradictionDetector:
    """获取全局矛盾检测器实例（单例）"""
    global _contradiction_detector
    if _contradiction_detector is None:
        _contradiction_detector = ContradictionDetector()
    return _contradiction_detector

