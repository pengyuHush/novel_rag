"""
T086: 实体提取服务 (User Story 3: 知识图谱与GraphRAG)

功能:
- 从章节文本中批量提取实体
- 统计实体出现频率
- 识别主要角色(高频实体)
"""

import logging
from typing import List, Dict, Set, Tuple
from collections import Counter

from .hanlp_client import get_hanlp_client

logger = logging.getLogger(__name__)


class EntityExtractor:
    """实体提取器"""
    
    def __init__(self):
        self.hanlp_client = get_hanlp_client()
    
    def extract_from_chapter(
        self, 
        chapter_text: str,
        chapter_num: int
    ) -> Dict[str, List[str]]:
        """
        从单个章节提取实体
        
        Args:
            chapter_text: 章节文本
            chapter_num: 章节号
        
        Returns:
            {
                'characters': ['萧炎', '药老'],
                'locations': ['乌坦城'],
                'organizations': ['云岚宗']
            }
        """
        # 分段提取(避免文本过长)
        chunks = self._split_text(chapter_text, max_length=500)
        
        all_entities = {
            'characters': [],
            'locations': [],
            'organizations': []
        }
        
        logger.debug(f"章节{chapter_num}: 文本长度 {len(chapter_text)}, 分为 {len(chunks)} 段")
        
        for i, chunk in enumerate(chunks):
            entities = self.hanlp_client.extract_entities(chunk)
            for key in all_entities:
                all_entities[key].extend(entities.get(key, []))
            
            # 输出前几段的提取结果用于调试
            if i < 3:
                chunk_total = sum(len(entities[k]) for k in entities)
                if chunk_total > 0:
                    logger.debug(f"  段{i+1}: 提取到 {chunk_total} 个实体")
        
        # 去重
        for key in all_entities:
            all_entities[key] = list(set(all_entities[key]))
        
        total_count = sum(len(all_entities[k]) for k in all_entities)
        if total_count == 0 and chapter_num <= 3:
            # 前3章如果提取不到实体，输出警告和文本样例
            logger.warning(f"章节{chapter_num}: 未提取到任何实体")
            logger.warning(f"  文本样例: {chapter_text[:200]}...")
        
        logger.info(
            f"章节{chapter_num}: 提取实体 "
            f"角色{len(all_entities['characters'])} "
            f"地点{len(all_entities['locations'])} "
            f"组织{len(all_entities['organizations'])}"
        )
        
        return all_entities
    
    def extract_from_novel(
        self,
        chapters: List[Tuple[int, str]]
    ) -> Dict[str, Counter]:
        """
        从整本小说提取实体并统计频率
        
        Args:
            chapters: [(chapter_num, chapter_text), ...]
        
        Returns:
            {
                'characters': Counter({'萧炎': 1500, '药老': 800, ...}),
                'locations': Counter({'乌坦城': 300, ...}),
                'organizations': Counter({'云岚宗': 250, ...})
            }
        """
        entity_counters = {
            'characters': Counter(),
            'locations': Counter(),
            'organizations': Counter()
        }
        
        for chapter_num, chapter_text in chapters:
            entities = self.extract_from_chapter(chapter_text, chapter_num)
            
            for key in entity_counters:
                entity_counters[key].update(entities[key])
        
        logger.info(
            f"全书实体统计: "
            f"角色{len(entity_counters['characters'])} "
            f"地点{len(entity_counters['locations'])} "
            f"组织{len(entity_counters['organizations'])}"
        )
        
        return entity_counters
    
    def get_main_characters(
        self,
        character_counter: Counter,
        min_mentions: int = 10,
        top_n: int = 50
    ) -> List[Tuple[str, int]]:
        """
        识别主要角色
        
        Args:
            character_counter: 角色频率统计
            min_mentions: 最小出现次数
            top_n: 返回前N个
        
        Returns:
            [('萧炎', 1500), ('药老', 800), ...]
        """
        # 过滤低频角色
        main_chars = [
            (name, count) 
            for name, count in character_counter.items()
            if count >= min_mentions
        ]
        
        # 按频率排序
        main_chars.sort(key=lambda x: x[1], reverse=True)
        
        return main_chars[:top_n]
    
    def _split_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        分割长文本
        
        Args:
            text: 输入文本
            max_length: 最大长度
        
        Returns:
            文本块列表
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            chunk = text[current_pos:current_pos + max_length]
            chunks.append(chunk)
            current_pos += max_length
        
        return chunks


# 全局实例
_entity_extractor = None

def get_entity_extractor() -> EntityExtractor:
    """获取实体提取器单例"""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor

