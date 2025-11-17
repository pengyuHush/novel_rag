"""
T088: 存储实体到SQLite (User Story 3: 知识图谱与GraphRAG)

功能:
- 保存提取的实体到entities表
- 更新实体统计信息(出现频率、首次/最后出现章节)
- 标记主要角色
"""

import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from collections import Counter

from app.models.database import Entity, Novel

logger = logging.getLogger(__name__)


class EntityService:
    """实体存储服务"""
    
    def __init__(self):
        """初始化服务，创建别名缓存"""
        self._alias_cache = {}  # 实例级别的缓存：{cache_key: canonical_name}
        self._cache_max_size = 1000  # 最大缓存条目数
    
    def _clear_cache_if_needed(self):
        """如果缓存过大，清除旧条目（简单LRU策略）"""
        if len(self._alias_cache) > self._cache_max_size:
            # 清除最旧的50%条目（简化版LRU）
            keys_to_remove = list(self._alias_cache.keys())[:self._cache_max_size // 2]
            for key in keys_to_remove:
                del self._alias_cache[key]
            logger.debug(f"清除了 {len(keys_to_remove)} 个缓存条目")
    
    def save_entities(
        self,
        db: Session,
        novel_id: int,
        entity_counters: Dict[str, Counter],
        chapter_ranges: Dict[str, Tuple[int, int]]
    ) -> int:
        """
        保存实体到数据库
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entity_counters: 实体频率统计 {'characters': Counter(...), ...}
            chapter_ranges: 实体出现章节范围 {'萧炎': (1, 1500), ...}
        
        Returns:
            保存的实体总数
        """
        total_saved = 0
        
        # 保存角色实体
        total_saved += self._save_entity_type(
            db, novel_id, 
            entity_counters.get('characters', Counter()),
            chapter_ranges,
            'character'
        )
        
        # 保存地点实体
        total_saved += self._save_entity_type(
            db, novel_id,
            entity_counters.get('locations', Counter()),
            chapter_ranges,
            'location'
        )
        
        # 保存组织实体
        total_saved += self._save_entity_type(
            db, novel_id,
            entity_counters.get('organizations', Counter()),
            chapter_ranges,
            'organization'
        )
        
        # 更新小说表的实体统计
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if novel:
            novel.total_entities = total_saved
        
        db.commit()
        
        logger.info(f"小说{novel_id}: 保存实体{total_saved}个")
        return total_saved
    
    def _save_entity_type(
        self,
        db: Session,
        novel_id: int,
        entity_counter: Counter,
        chapter_ranges: Dict[str, Tuple[int, int]],
        entity_type: str
    ) -> int:
        """
        保存特定类型的实体
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entity_counter: 实体频率统计
            chapter_ranges: 章节范围
            entity_type: 实体类型('character', 'location', 'organization')
        
        Returns:
            保存数量
        """
        saved_count = 0
        
        for entity_name, mention_count in entity_counter.items():
            # 获取章节范围
            first_chapter, last_chapter = chapter_ranges.get(
                entity_name, 
                (1, None)
            )
            
            # 检查实体是否已存在
            existing = db.query(Entity).filter(
                Entity.novel_id == novel_id,
                Entity.entity_name == entity_name,
                Entity.entity_type == entity_type
            ).first()
            
            if existing:
                # 更新现有实体
                existing.mention_count = mention_count
                existing.last_chapter = last_chapter
            else:
                # 创建新实体
                entity = Entity(
                    novel_id=novel_id,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    first_chapter=first_chapter,
                    last_chapter=last_chapter,
                    mention_count=mention_count,
                    importance=0.5  # 默认重要性,后续通过PageRank更新
                )
                db.add(entity)
            
            saved_count += 1
        
        return saved_count
    
    def mark_protagonists(
        self,
        db: Session,
        novel_id: int,
        top_n: int = 5
    ):
        """
        标记主角(基于出现频率)
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            top_n: 前N个角色标记为主角
        """
        # 获取角色实体,按出现频率排序
        characters = db.query(Entity).filter(
            Entity.novel_id == novel_id,
            Entity.entity_type == 'character'
        ).order_by(Entity.mention_count.desc()).limit(top_n).all()
        
        for char in characters:
            char.is_protagonist = True
        
        db.commit()
        
        logger.info(
            f"小说{novel_id}: 标记主角 {[c.entity_name for c in characters]}"
        )
    
    def get_entities_by_chapter(
        self,
        db: Session,
        novel_id: int,
        chapter_num: int
    ) -> List[Entity]:
        """
        获取指定章节出现的实体
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            chapter_num: 章节号
        
        Returns:
            实体列表
        """
        return db.query(Entity).filter(
            Entity.novel_id == novel_id,
            Entity.first_chapter <= chapter_num,
            (Entity.last_chapter >= chapter_num) | (Entity.last_chapter.is_(None))
        ).all()
    
    def save_entity_aliases(
        self,
        db: Session,
        novel_id: int,
        merged_entities: Dict[str, Dict[str, List[str]]]
    ) -> int:
        """
        保存实体别名映射
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            merged_entities: {'characters': {'萧炎': ['萧炎', '小炎子', '炎子']}, ...}
        
        Returns:
            保存的别名总数
        """
        from app.models.database import EntityAlias
        
        total_saved = 0
        
        for entity_type_plural, merge_mapping in merged_entities.items():
            # 转换为单数形式
            entity_type = entity_type_plural.rstrip('s')
            
            for canonical_name, aliases in merge_mapping.items():
                for alias in aliases:
                    # 检查别名是否已存在
                    existing = db.query(EntityAlias).filter(
                        EntityAlias.novel_id == novel_id,
                        EntityAlias.alias == alias,
                        EntityAlias.entity_type == entity_type
                    ).first()
                    
                    if existing:
                        # 更新现有别名
                        existing.canonical_name = canonical_name
                        existing.confidence = 1.0
                    else:
                        # 创建新别名
                        db.add(EntityAlias(
                            novel_id=novel_id,
                            canonical_name=canonical_name,
                            alias=alias,
                            entity_type=entity_type,
                            confidence=1.0
                        ))
                    total_saved += 1
        
        db.commit()
        logger.info(f"小说{novel_id}: 保存实体别名{total_saved}个")
        return total_saved
    
    def get_canonical_name(
        self,
        db: Session,
        novel_id: int,
        entity: str,
        entity_type: str = None
    ) -> str:
        """
        根据别名查找规范名称（增强版，支持模糊匹配 + LRU缓存）
        
        查找策略：
        0. 检查缓存
        1. 精确匹配别名
        2. 包含匹配（实体包含在规范名称中）
        3. 被包含匹配（规范名称包含在实体中）
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entity: 实体名称（可能是别名）
            entity_type: 实体类型（可选，如果提供则更精确）
        
        Returns:
            规范名称（如果没找到映射则返回原名）
        """
        # 策略0：检查缓存
        cache_key = f"{novel_id}:{entity}:{entity_type or 'all'}"
        if cache_key in self._alias_cache:
            return self._alias_cache[cache_key]
        
        from app.models.database import EntityAlias, Entity
        
        # 策略1：精确匹配别名表
        query = db.query(EntityAlias).filter(
            EntityAlias.novel_id == novel_id,
            EntityAlias.alias == entity
        )
        if entity_type:
            query = query.filter(EntityAlias.entity_type == entity_type)
        
        alias_record = query.first()
        if alias_record:
            result = alias_record.canonical_name
            # 更新缓存
            self._alias_cache[cache_key] = result
            self._clear_cache_if_needed()
            return result
        
        # 策略2：在 entities 表中查找包含关系（仅对长度≥2的实体）
        if len(entity) >= 2:
            # 2a. 实体包含在规范名称中（如"炎"可能匹配"萧炎"）
            entity_query = db.query(Entity).filter(
                Entity.novel_id == novel_id,
                Entity.entity_name.like(f'%{entity}%')
            )
            if entity_type:
                entity_query = entity_query.filter(Entity.entity_type == entity_type)
            
            # 按相似度排序（优先完全匹配、次之前缀/后缀匹配）
            candidates = entity_query.all()
            if candidates:
                # 完全匹配
                for candidate in candidates:
                    if candidate.entity_name == entity:
                        # 更新缓存
                        self._alias_cache[cache_key] = entity
                        self._clear_cache_if_needed()
                        return entity
                
                # 包含匹配 - 返回最短的（最可能的匹配）
                best_match = min(candidates, key=lambda c: len(c.entity_name))
                logger.info(f"🔍 模糊匹配: '{entity}' → '{best_match.entity_name}'")
                # 更新缓存
                self._alias_cache[cache_key] = best_match.entity_name
                self._clear_cache_if_needed()
                return best_match.entity_name
        
        # 未找到映射，返回原名（也缓存这个结果）
        self._alias_cache[cache_key] = entity
        self._clear_cache_if_needed()
        return entity


# 全局实例
_entity_service = None

def get_entity_service() -> EntityService:
    """获取实体服务单例"""
    global _entity_service
    if _entity_service is None:
        _entity_service = EntityService()
    return _entity_service

