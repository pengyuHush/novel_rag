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


# 全局实例
_entity_service = None

def get_entity_service() -> EntityService:
    """获取实体服务单例"""
    global _entity_service
    if _entity_service is None:
        _entity_service = EntityService()
    return _entity_service

