"""
一致性检查器

检查时序一致性和角色一致性
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self):
        """初始化一致性检查器"""
        logger.info("✅ 一致性检查器初始化完成")
    
    def check_temporal_consistency(
        self,
        assertions: List[Dict],
        evidence_map: Dict[int, List[Dict]]
    ) -> List[Dict]:
        """
        时序一致性检查
        
        验证事件时间线的合理性：
        - 事件发生顺序是否合理
        - 时间标记是否前后矛盾
        - 因果关系是否符合时序
        
        Args:
            assertions: 断言列表
            evidence_map: 断言索引 -> 证据列表的映射
        
        Returns:
            List[Dict]: 一致性问题列表
        """
        issues = []
        
        # 提取带时序信息的断言
        temporal_assertions = [
            a for a in assertions 
            if a.get('chapter_ref') is not None or a.get('type') == 'event'
        ]
        
        # 按章节号排序（处理None值）
        temporal_assertions.sort(
            key=lambda x: x.get('chapter_ref') if x.get('chapter_ref') is not None else 999999
        )
        
        # 检查时序逻辑
        for i in range(len(temporal_assertions) - 1):
            current = temporal_assertions[i]
            next_one = temporal_assertions[i + 1]
            
            current_chapter = current.get('chapter_ref')
            next_chapter = next_one.get('chapter_ref')
            
            if current_chapter and next_chapter:
                # 检查是否存在逻辑矛盾
                issue = self._check_temporal_logic(
                    current, next_one, current_chapter, next_chapter
                )
                if issue:
                    issues.append(issue)
        
        logger.info(f"✅ 时序一致性检查: 发现 {len(issues)} 个问题")
        
        return issues
    
    def check_character_consistency(
        self,
        db: Session,
        novel_id: int,
        assertions: List[Dict],
        evidence_map: Dict[int, List[Dict]]
    ) -> List[Dict]:
        """
        角色一致性检查
        
        验证角色行为和设定的逻辑连贯性：
        - 角色能力是否突然改变
        - 角色立场是否前后矛盾
        - 角色关系是否合理演变
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            assertions: 断言列表
            evidence_map: 断言索引 -> 证据列表的映射
        
        Returns:
            List[Dict]: 一致性问题列表
        """
        issues = []
        
        # 按实体分组断言
        entity_assertions = {}
        for assertion in assertions:
            entities = assertion.get('entities', [])
            for entity in entities:
                if entity not in entity_assertions:
                    entity_assertions[entity] = []
                entity_assertions[entity].append(assertion)
        
        # 检查每个实体的断言一致性
        for entity, entity_asserts in entity_assertions.items():
            if len(entity_asserts) < 2:
                continue  # 至少需要2个断言才能检查一致性
            
            # 按章节排序（处理None值）
            entity_asserts.sort(
                key=lambda x: x.get('chapter_ref') if x.get('chapter_ref') is not None else 999999
            )
            
            # 检查相邻断言的一致性
            for i in range(len(entity_asserts) - 1):
                current = entity_asserts[i]
                next_one = entity_asserts[i + 1]
                
                issue = self._check_character_logic(
                    entity, current, next_one
                )
                if issue:
                    issues.append(issue)
        
        logger.info(f"✅ 角色一致性检查: 发现 {len(issues)} 个问题")
        
        return issues
    
    def _check_temporal_logic(
        self,
        assertion1: Dict,
        assertion2: Dict,
        chapter1: int,
        chapter2: int
    ) -> Optional[Dict]:
        """
        检查两个断言之间的时序逻辑
        
        Args:
            assertion1: 第一个断言
            assertion2: 第二个断言
            chapter1: 第一个章节
            chapter2: 第二个章节
        
        Returns:
            Optional[Dict]: 问题描述或None
        """
        text1 = assertion1.get('assertion', '')
        text2 = assertion2.get('assertion', '')
        
        # 检测逻辑矛盾关键词
        contradiction_pairs = [
            ('死亡', '复活'),
            ('死了', '活着'),
            ('离开', '到达'),
            ('结束', '开始'),
            ('失去', '拥有'),
        ]
        
        for word1, word2 in contradiction_pairs:
            if word1 in text1 and word2 in text2:
                # 如果后续章节发生了矛盾的事件，可能有问题
                if chapter2 > chapter1:
                    return {
                        'type': 'temporal_inconsistency',
                        'severity': 'high',
                        'assertion1': assertion1,
                        'assertion2': assertion2,
                        'description': f"时序矛盾：第{chapter1}章'{word1}'，第{chapter2}章'{word2}'"
                    }
        
        return None
    
    def _check_character_logic(
        self,
        entity: str,
        assertion1: Dict,
        assertion2: Dict
    ) -> Optional[Dict]:
        """
        检查角色相关断言的逻辑一致性
        
        Args:
            entity: 实体名称
            assertion1: 第一个断言
            assertion2: 第二个断言
        
        Returns:
            Optional[Dict]: 问题描述或None
        """
        text1 = assertion1.get('assertion', '')
        text2 = assertion2.get('assertion', '')
        chapter1 = assertion1.get('chapter_ref', 0)
        chapter2 = assertion2.get('chapter_ref', 0)
        
        # 检测角色立场/关系矛盾
        relationship_contradictions = [
            ('盟友', '敌人'),
            ('朋友', '仇人'),
            ('喜欢', '讨厌'),
            ('信任', '背叛'),
            ('师傅', '敌人'),
        ]
        
        for rel1, rel2 in relationship_contradictions:
            if rel1 in text1 and rel2 in text2:
                # 检查是否有合理解释（如"背叛"、"误会"等）
                transition_keywords = ['背叛', '误会', '发现', '真相', '变化']
                has_explanation = any(kw in text2 for kw in transition_keywords)
                
                if not has_explanation:
                    return {
                        'type': 'character_inconsistency',
                        'severity': 'medium',
                        'entity': entity,
                        'assertion1': assertion1,
                        'assertion2': assertion2,
                        'description': f"{entity}的关系变化缺少解释：{rel1} -> {rel2}"
                    }
        
        return None
    
    def consolidate_checks(
        self,
        temporal_issues: List[Dict],
        character_issues: List[Dict]
    ) -> Dict:
        """
        整合一致性检查结果
        
        Args:
            temporal_issues: 时序问题列表
            character_issues: 角色问题列表
        
        Returns:
            Dict: 整合报告
        """
        report = {
            'temporal_issues': temporal_issues,
            'character_issues': character_issues,
            'total_issues': len(temporal_issues) + len(character_issues),
            'severity_counts': {
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        # 统计严重程度
        all_issues = temporal_issues + character_issues
        for issue in all_issues:
            severity = issue.get('severity', 'low')
            report['severity_counts'][severity] += 1
        
        return report


# 全局实例
_consistency_checker: Optional[ConsistencyChecker] = None


def get_consistency_checker() -> ConsistencyChecker:
    """获取全局一致性检查器实例（单例）"""
    global _consistency_checker
    if _consistency_checker is None:
        _consistency_checker = ConsistencyChecker()
    return _consistency_checker

