"""
T087: 实体去重与合并 (User Story 3: 知识图谱与GraphRAG)

功能:
- 合并相似实体名称(如"萧炎"和"小炎子")
- 处理简称和全称(如"药老"和"药尘")
- 使用编辑距离和包含关系判断相似度
"""

import logging
from typing import List, Dict, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class EntityMerger:
    """实体合并器"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Args:
            similarity_threshold: 相似度阈值(0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def merge_entities(self, entities: List[str]) -> Dict[str, List[str]]:
        """
        合并相似实体
        
        Args:
            entities: 实体名称列表
        
        Returns:
            {
                '萧炎': ['萧炎', '小炎子', '炎子'],
                '药老': ['药老', '药尘'],
                ...
            }
        """
        if not entities:
            return {}
        
        # 去重并排序(按长度降序,优先保留长名称)
        unique_entities = sorted(set(entities), key=len, reverse=True)
        
        # 合并结果
        merged = {}
        used = set()
        
        for entity in unique_entities:
            if entity in used:
                continue
            
            # 查找相似实体
            similar = [entity]
            used.add(entity)
            
            for other in unique_entities:
                if other in used:
                    continue
                
                if self._is_similar(entity, other):
                    similar.append(other)
                    used.add(other)
            
            # 使用最长的名称作为主名称
            main_name = max(similar, key=len)
            merged[main_name] = similar
        
        logger.info(f"实体合并: {len(entities)} → {len(merged)} (去重{len(entities) - len(merged)})")
        
        return merged
    
    def _is_similar(self, entity1: str, entity2: str) -> bool:
        """
        判断两个实体是否相似
        
        策略:
        1. 完全相同 → 相似
        2. 一个是另一个的子串 → 相似(如"药老"和"药尘药老")
        3. 编辑距离小于阈值 → 相似
        """
        if entity1 == entity2:
            return True
        
        # 包含关系(短名称在长名称中)
        if entity1 in entity2 or entity2 in entity1:
            return True
        
        # 编辑距离
        similarity = self._similarity_score(entity1, entity2)
        return similarity >= self.similarity_threshold
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """
        计算字符串相似度(基于编辑距离)
        
        Returns:
            0-1的相似度分数
        """
        if not s1 or not s2:
            return 0.0
        
        # Levenshtein距离
        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        # 归一化到0-1
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算Levenshtein编辑距离
        
        Args:
            s1: 字符串1
            s2: 字符串2
        
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_canonical_name(self, entity: str, merged_dict: Dict[str, List[str]]) -> str:
        """
        获取实体的规范名称(主名称)
        
        Args:
            entity: 实体名称
            merged_dict: 合并结果字典
        
        Returns:
            规范名称
        """
        for main_name, aliases in merged_dict.items():
            if entity in aliases:
                return main_name
        return entity


# 全局实例
_entity_merger = None

def get_entity_merger() -> EntityMerger:
    """获取实体合并器单例"""
    global _entity_merger
    if _entity_merger is None:
        _entity_merger = EntityMerger()
    return _entity_merger

