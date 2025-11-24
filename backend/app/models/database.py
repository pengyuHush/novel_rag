"""
SQLAlchemy数据库模型定义
"""

from sqlalchemy import (
    Boolean, Column, Integer, String, Text, Float, ForeignKey,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Novel(Base):
    """小说表"""
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100))
    total_chars = Column(Integer, nullable=False)
    total_chapters = Column(Integer, nullable=False)
    upload_date = Column(String, default=lambda: datetime.utcnow().isoformat())
    indexed_date = Column(String)
    index_status = Column(
        String(20),
        nullable=False,
        default='pending',
        index=True
    )
    index_progress = Column(Float, default=0.0)
    file_path = Column(Text, nullable=False)
    file_format = Column(String(10), nullable=False)
    
    # 索引统计
    total_chunks = Column(Integer, default=0)
    total_entities = Column(Integer, default=0)
    total_relations = Column(Integer, default=0)
    
    # Token统计
    embedding_tokens = Column(Integer, default=0)
    
    # 元数据
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="novel", cascade="all, delete-orphan")
    entity_aliases = relationship("EntityAlias", back_populates="novel", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="novel", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "index_status IN ('pending', 'processing', 'completed', 'failed')",
            name='check_status'
        ),
    )
    
    def __repr__(self):
        return f"<Novel(id={self.id}, title='{self.title}', status='{self.index_status}')>"


class Chapter(Base):
    """章节表"""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey('novels.id', ondelete='CASCADE'), nullable=False)
    chapter_num = Column(Integer, nullable=False)
    chapter_title = Column(String(200))
    char_count = Column(Integer, nullable=False)
    word_count = Column(Integer)
    
    # 文件位置
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)
    
    # 分块信息
    chunk_count = Column(Integer, default=0)
    
    # 重要性评分
    importance_score = Column(Float, default=0.5, index=True)
    
    # 章节特征
    has_new_character = Column(Boolean, default=False)
    has_plot_twist = Column(Boolean, default=False)
    has_time_jump = Column(Boolean, default=False)
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    novel = relationship("Novel", back_populates="chapters")
    
    __table_args__ = (
        UniqueConstraint('novel_id', 'chapter_num', name='uq_novel_chapter'),
        Index('idx_chapters_novel', 'novel_id'),
        Index('idx_chapters_num', 'novel_id', 'chapter_num'),
    )
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, novel_id={self.novel_id}, num={self.chapter_num})>"


class Entity(Base):
    """实体表"""
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey('novels.id', ondelete='CASCADE'), nullable=False)
    entity_name = Column(String(100), nullable=False)
    entity_type = Column(String(20), nullable=False)
    first_chapter = Column(Integer, nullable=False)
    last_chapter = Column(Integer)
    mention_count = Column(Integer, default=1)
    
    # 角色特征
    is_protagonist = Column(Boolean, default=False)
    is_antagonist = Column(Boolean, default=False)
    
    # PageRank重要性
    importance = Column(Float, default=0.5)
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    novel = relationship("Novel", back_populates="entities")
    
    __table_args__ = (
        UniqueConstraint('novel_id', 'entity_name', 'entity_type', name='uq_novel_entity'),
        Index('idx_entities_novel', 'novel_id'),
        Index('idx_entities_type', 'novel_id', 'entity_type'),
        Index('idx_entities_name', 'novel_id', 'entity_name'),
    )
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.entity_name}', type='{self.entity_type}')>"


class EntityAlias(Base):
    """实体别名表"""
    __tablename__ = "entity_aliases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey('novels.id', ondelete='CASCADE'), nullable=False)
    canonical_name = Column(String(100), nullable=False)  # 规范名称
    alias = Column(String(100), nullable=False)  # 别名
    entity_type = Column(String(20), nullable=False)
    confidence = Column(Float, default=1.0)  # 映射置信度（0-1），支持后期调整
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    novel = relationship("Novel", back_populates="entity_aliases")
    
    __table_args__ = (
        UniqueConstraint('novel_id', 'alias', 'entity_type', name='uq_novel_alias'),
        Index('idx_entity_aliases_novel', 'novel_id'),
        Index('idx_entity_aliases_lookup', 'novel_id', 'alias', 'entity_type'),
    )
    
    def __repr__(self):
        return f"<EntityAlias(id={self.id}, alias='{self.alias}', canonical='{self.canonical_name}')>"


class Query(Base):
    """查询记录表"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey('novels.id', ondelete='CASCADE'), nullable=False)
    novel_ids = Column(Text, nullable=True)  # JSON数组，存储多个小说ID
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    
    # 模型信息
    model_used = Column(String(50), nullable=False, index=True)
    
    # Token统计
    embedding_tokens = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    self_rag_tokens = Column(Integer, default=0)
    
    # 性能指标
    response_time = Column(Float, nullable=False)
    retrieve_time = Column(Float)
    generate_time = Column(Float)
    
    # 质量指标
    confidence = Column(String(10))
    has_contradiction = Column(Boolean, default=False)
    contradiction_count = Column(Integer, default=0)
    
    # 用户反馈
    user_feedback = Column(Integer, default=0)
    feedback_note = Column(Text)
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat(), index=True)
    
    # 关系
    novel = relationship("Novel", back_populates="queries")
    
    __table_args__ = (
        CheckConstraint("user_feedback IN (-1, 0, 1)", name='check_feedback'),
        CheckConstraint("confidence IN ('high', 'medium', 'low')", name='check_confidence'),
        Index('idx_queries_novel', 'novel_id'),
        Index('idx_queries_date', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Query(id={self.id}, novel_id={self.novel_id}, model='{self.model_used}')>"


class TokenStat(Base):
    """Token统计汇总表"""
    __tablename__ = "token_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_type = Column(String(10), nullable=False)
    operation_id = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False, index=True)
    
    # Token消耗
    input_tokens = Column(Integer)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer, nullable=False)
    
    # 成本估算
    estimated_cost = Column(Float)
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat(), index=True)
    
    __table_args__ = (
        CheckConstraint("operation_type IN ('index', 'query')", name='check_operation_type'),
        Index('idx_token_stats_operation', 'operation_type', 'operation_id'),
    )
    
    def __repr__(self):
        return f"<TokenStat(id={self.id}, type='{self.operation_type}', model='{self.model_name}')>"


class SchemaVersion(Base):
    """Schema版本管理"""
    __tablename__ = "schema_version"
    
    version = Column(String(20), primary_key=True)
    applied_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f"<SchemaVersion(version='{self.version}')>"

