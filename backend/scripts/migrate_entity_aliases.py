"""
批量为已导入的小说生成实体别名映射

用法:
    python -m scripts.migrate_entity_aliases [--novel-id NOVEL_ID]
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.init_db import get_database_url
from app.models.database import Novel
from app.services.nlp.entity_merger import EntityMerger
from app.services.entity_service import EntityService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_session() -> Session:
    """创建数据库会话"""
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def migrate_novel_aliases(db: Session, novel_id: int):
    """为单个小说生成别名映射"""
    from app.models.database import Entity, EntityAlias
    
    logger.info(f"开始处理小说 {novel_id}...")
    
    # 检查是否已有别名
    existing_count = db.query(EntityAlias).filter(
        EntityAlias.novel_id == novel_id
    ).count()
    
    if existing_count > 0:
        logger.warning(f"小说 {novel_id} 已有 {existing_count} 个别名记录，跳过")
        return 0
    
    # 获取该小说的所有实体
    entities = db.query(Entity).filter(Entity.novel_id == novel_id).all()
    
    if not entities:
        logger.warning(f"小说 {novel_id} 没有实体数据")
        return 0
    
    # 按类型分组
    entity_by_type = {}
    for entity in entities:
        entity_type_plural = entity.entity_type + 's'
        if entity_type_plural not in entity_by_type:
            entity_by_type[entity_type_plural] = []
        entity_by_type[entity_type_plural].append(entity.entity_name)
    
    # 使用 EntityMerger 生成别名映射
    merger = EntityMerger()
    entity_service = EntityService()
    
    alias_mapping = {}
    for entity_type_plural, entity_names in entity_by_type.items():
        merge_mapping = merger.merge_entities(entity_names)
        alias_mapping[entity_type_plural] = merge_mapping
        logger.info(f"{entity_type_plural}: {len(entity_names)} → {len(merge_mapping)} (合并了 {len(entity_names) - len(merge_mapping)} 个)")
    
    # 保存别名
    alias_count = entity_service.save_entity_aliases(db, novel_id, alias_mapping)
    logger.info(f"✅ 小说 {novel_id} 生成了 {alias_count} 个别名映射")
    
    return alias_count


def main():
    parser = argparse.ArgumentParser(description='批量生成实体别名映射')
    parser.add_argument('--novel-id', type=int, help='指定小说ID（不指定则处理所有小说）')
    args = parser.parse_args()
    
    db = get_session()
    
    try:
        if args.novel_id:
            # 处理单个小说
            migrate_novel_aliases(db, args.novel_id)
        else:
            # 处理所有小说
            novels = db.query(Novel).all()
            logger.info(f"找到 {len(novels)} 个小说")
            
            total_aliases = 0
            for novel in novels:
                count = migrate_novel_aliases(db, novel.id)
                total_aliases += count
            
            logger.info(f"✅ 总共生成了 {total_aliases} 个别名映射")
    
    finally:
        db.close()


if __name__ == '__main__':
    main()

