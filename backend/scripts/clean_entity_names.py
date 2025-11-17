"""
清洗数据库中已有实体和别名的名称，去除换行符等特殊字符

用法:
    python -m scripts.clean_entity_names [--dry-run]
"""

import sys
import re
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.init_db import get_database_url
from app.models.database import Entity, EntityAlias
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_entity_name(entity_name: str) -> str:
    """
    清洗实体名称，去除特殊字符并过滤无效实体
    
    Args:
        entity_name: 原始实体名
    
    Returns:
        清洗后的实体名，如果无效则返回空字符串
    """
    if not entity_name:
        return ""
    
    # 1. 去除前后空白
    entity_name = entity_name.strip()
    
    # 2. 去除前后的引号（单引号、双引号、中文引号等）
    quote_chars = "'\"\u2018\u2019\u201c\u201d`´"  # '  "  '  '  "  "  `  ´
    entity_name = entity_name.strip(quote_chars)
    entity_name = entity_name.strip()  # 再次去除空白
    
    # 3. 替换换行符、制表符等为空格
    entity_name = entity_name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 4. 压缩连续空格为单个空格
    entity_name = re.sub(r'\s+', ' ', entity_name)
    
    # 5. 再次去除前后空白和引号
    entity_name = entity_name.strip()
    quote_chars = "'\"\u2018\u2019\u201c\u201d`´"
    entity_name = entity_name.strip(quote_chars)
    
    # 5. 基本验证
    if not entity_name or len(entity_name) < 2:
        return ""
    
    # 过滤全是标点或数字的实体
    if re.match(r'^[\d\W]+$', entity_name):
        return ""
    
    # 6. 过滤章节标题模式
    chapter_patterns = [
        r'第[零一二三四五六七八九十百千万\d]+章',  # 第一章、第123章
        r'第[零一二三四五六七八九十百千万\d]+回',  # 第一回、第123回
        r'[Cc]hapter\s*\d+',  # Chapter 1
        r'^\d+[\.、\s]*章',  # 1.章、123章
        r'卷[零一二三四五六七八九十百千万\d]+',  # 卷一
    ]
    
    for pattern in chapter_patterns:
        if re.search(pattern, entity_name):
            logger.debug(f"过滤章节标题: {entity_name}")
            return ""
    
    # 7. 过滤常见噪音词
    noise_words = [
        '作者', '本书', '本章', '正文', '番外', '序章', '楔子', '引子',
        '前言', '后记', '附录', '目录', '简介', '完本', '完结',
        'PS', 'VIP', '月票', '推荐票', '打赏'
    ]
    
    for noise in noise_words:
        if noise in entity_name:
            logger.debug(f"过滤噪音词: {entity_name}")
            return ""
    
    # 8. 过滤过长的实体（超过10个字符的通常不是有效实体名）
    if len(entity_name) > 10:
        logger.debug(f"过滤过长实体: {entity_name} (长度: {len(entity_name)})")
        return ""
    
    # 9. 过滤包含引号的实体（清洗后仍有引号的视为无效）
    quote_chars_check = ["'", '"', '\u2018', '\u2019', '\u201c', '\u201d', '`', '´']
    has_quote = any(q in entity_name for q in quote_chars_check)
    if has_quote:
        logger.debug(f"过滤包含引号的实体: {entity_name}")
        return ""
    
    return entity_name


def clean_entities(db: Session, dry_run: bool = False):
    """清洗 entities 表"""
    logger.info("开始清洗 entities 表...")
    
    entities = db.query(Entity).all()
    cleaned_count = 0
    deleted_count = 0
    
    for entity in entities:
        original_name = entity.entity_name
        cleaned_name = clean_entity_name(original_name)
        
        if original_name != cleaned_name:
            if cleaned_name and len(cleaned_name) >= 2:
                # 名称有效，更新
                logger.info(f"清洗实体: '{original_name}' → '{cleaned_name}'")
                if not dry_run:
                    entity.entity_name = cleaned_name
                cleaned_count += 1
            else:
                # 清洗后无效，删除
                logger.warning(f"删除无效实体: '{original_name}' (清洗后: '{cleaned_name}')")
                if not dry_run:
                    db.delete(entity)
                deleted_count += 1
    
    if not dry_run:
        db.commit()
    
    logger.info(f"entities 表: 清洗 {cleaned_count} 个, 删除 {deleted_count} 个")
    return cleaned_count, deleted_count


def clean_entity_aliases(db: Session, dry_run: bool = False):
    """清洗 entity_aliases 表"""
    logger.info("开始清洗 entity_aliases 表...")
    
    aliases = db.query(EntityAlias).all()
    cleaned_canonical_count = 0
    cleaned_alias_count = 0
    deleted_count = 0
    
    for alias in aliases:
        original_canonical = alias.canonical_name
        original_alias = alias.alias
        
        cleaned_canonical = clean_entity_name(original_canonical)
        cleaned_alias_name = clean_entity_name(original_alias)
        
        # 检查是否需要更新或删除
        canonical_changed = original_canonical != cleaned_canonical
        alias_changed = original_alias != cleaned_alias_name
        
        # 检查清洗后是否有效
        canonical_valid = cleaned_canonical and len(cleaned_canonical) >= 2
        alias_valid = cleaned_alias_name and len(cleaned_alias_name) >= 2
        
        if not canonical_valid or not alias_valid:
            # 清洗后无效，删除
            logger.warning(f"删除无效别名: '{original_alias}' → '{original_canonical}'")
            if not dry_run:
                db.delete(alias)
            deleted_count += 1
        else:
            # 更新
            if canonical_changed:
                logger.info(f"清洗规范名: '{original_canonical}' → '{cleaned_canonical}'")
                if not dry_run:
                    alias.canonical_name = cleaned_canonical
                cleaned_canonical_count += 1
            
            if alias_changed:
                logger.info(f"清洗别名: '{original_alias}' → '{cleaned_alias_name}'")
                if not dry_run:
                    alias.alias = cleaned_alias_name
                cleaned_alias_count += 1
    
    if not dry_run:
        db.commit()
    
    logger.info(f"entity_aliases 表: 清洗规范名 {cleaned_canonical_count} 个, 清洗别名 {cleaned_alias_count} 个, 删除 {deleted_count} 个")
    return cleaned_canonical_count, cleaned_alias_count, deleted_count


def get_session() -> Session:
    """创建数据库会话"""
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def main():
    parser = argparse.ArgumentParser(description='清洗实体名称中的特殊字符')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际修改数据库')
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🔍 预览模式（不会修改数据库）")
    
    db = get_session()
    
    try:
        # 清洗 entities 表
        entity_cleaned, entity_deleted = clean_entities(db, dry_run=args.dry_run)
        
        # 清洗 entity_aliases 表
        alias_canonical_cleaned, alias_alias_cleaned, alias_deleted = clean_entity_aliases(db, dry_run=args.dry_run)
        
        logger.info("\n" + "="*60)
        logger.info("清洗统计:")
        logger.info(f"  entities 表: 清洗 {entity_cleaned} 个, 删除 {entity_deleted} 个")
        logger.info(f"  entity_aliases 表: 清洗规范名 {alias_canonical_cleaned} 个, 清洗别名 {alias_alias_cleaned} 个, 删除 {alias_deleted} 个")
        logger.info("="*60)
        
        if args.dry_run:
            logger.info("✅ 预览完成，使用 --dry-run=false 执行实际清洗")
        else:
            logger.info("✅ 清洗完成")
    
    finally:
        db.close()


if __name__ == '__main__':
    main()

