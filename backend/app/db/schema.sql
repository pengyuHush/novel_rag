-- ========================================
-- 网络小说智能问答系统 - SQLite数据库Schema
-- Created: 2025-11-13
-- Version: 1.0.0
-- ========================================

-- ========================================
-- 1. novels（小说表）
-- ========================================
CREATE TABLE IF NOT EXISTS novels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    total_chars INTEGER NOT NULL,
    total_chapters INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_date TIMESTAMP,
    index_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    index_progress REAL DEFAULT 0.0,  -- 0.0 ~ 1.0
    file_path TEXT NOT NULL,
    file_format TEXT NOT NULL,  -- 'txt', 'epub'
    
    -- 索引统计
    total_chunks INTEGER DEFAULT 0,
    total_entities INTEGER DEFAULT 0,
    total_relations INTEGER DEFAULT 0,
    
    -- Token统计
    embedding_tokens INTEGER DEFAULT 0,  -- Embedding-3消耗
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_status CHECK (index_status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_novels_status ON novels(index_status);
CREATE INDEX IF NOT EXISTS idx_novels_title ON novels(title);
CREATE INDEX IF NOT EXISTS idx_novels_upload_date ON novels(upload_date DESC);

-- ========================================
-- 2. chapters（章节表）
-- ========================================
CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    novel_id INTEGER NOT NULL,
    chapter_num INTEGER NOT NULL,
    chapter_title TEXT,
    char_count INTEGER NOT NULL,
    word_count INTEGER,
    
    -- 文件位置
    start_pos INTEGER NOT NULL,  -- 在原文件中的起始位置
    end_pos INTEGER NOT NULL,    -- 在原文件中的结束位置
    
    -- 分块信息
    chunk_count INTEGER DEFAULT 0,  -- 本章生成的块数
    
    -- 重要性评分（用于检索权重）
    importance_score REAL DEFAULT 0.5,  -- 0.0 ~ 1.0
    
    -- 章节特征
    has_new_character BOOLEAN DEFAULT FALSE,
    has_plot_twist BOOLEAN DEFAULT FALSE,
    has_time_jump BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE(novel_id, chapter_num)
);

CREATE INDEX IF NOT EXISTS idx_chapters_novel ON chapters(novel_id);
CREATE INDEX IF NOT EXISTS idx_chapters_num ON chapters(novel_id, chapter_num);
CREATE INDEX IF NOT EXISTS idx_chapters_importance ON chapters(importance_score DESC);

-- ========================================
-- 3. entities（实体表）
-- ========================================
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    novel_id INTEGER NOT NULL,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- 'character', 'location', 'organization', 'item'
    first_chapter INTEGER NOT NULL,
    last_chapter INTEGER,
    mention_count INTEGER DEFAULT 1,
    
    -- 角色特征（仅character类型）
    is_protagonist BOOLEAN DEFAULT FALSE,
    is_antagonist BOOLEAN DEFAULT FALSE,
    
    -- PageRank重要性
    importance REAL DEFAULT 0.5,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    FOREIGN KEY (first_chapter) REFERENCES chapters(id),
    UNIQUE(novel_id, entity_name, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_entities_novel ON entities(novel_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(novel_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(novel_id, entity_name);

-- ========================================
-- 4. queries（查询记录表）
-- ========================================
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    novel_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    
    -- 模型信息
    model_used TEXT NOT NULL,  -- 'glm-4-flash', 'glm-4', 'glm-4-plus', etc.
    
    -- Token统计
    embedding_tokens INTEGER DEFAULT 0,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    self_rag_tokens INTEGER DEFAULT 0,  -- Self-RAG验证额外消耗
    
    -- 性能指标
    response_time REAL NOT NULL,  -- 秒
    retrieve_time REAL,           -- 检索耗时
    generate_time REAL,           -- 生成耗时
    
    -- 质量指标
    confidence TEXT,  -- 'high', 'medium', 'low'
    has_contradiction BOOLEAN DEFAULT FALSE,
    contradiction_count INTEGER DEFAULT 0,
    
    -- 用户反馈
    user_feedback INTEGER DEFAULT 0,  -- 1: 准确, -1: 不准确, 0: 未反馈
    feedback_note TEXT,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    CONSTRAINT check_feedback CHECK (user_feedback IN (-1, 0, 1)),
    CONSTRAINT check_confidence CHECK (confidence IN ('high', 'medium', 'low'))
);

CREATE INDEX IF NOT EXISTS idx_queries_novel ON queries(novel_id);
CREATE INDEX IF NOT EXISTS idx_queries_date ON queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queries_feedback ON queries(user_feedback);
CREATE INDEX IF NOT EXISTS idx_queries_model ON queries(model_used);

-- ========================================
-- 5. token_stats（Token统计汇总表）
-- ========================================
CREATE TABLE IF NOT EXISTS token_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,  -- 'index', 'query'
    operation_id INTEGER NOT NULL, -- novels.id 或 queries.id
    model_name TEXT NOT NULL,
    
    -- Token消耗
    input_tokens INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER NOT NULL,
    
    -- 成本估算（基于智谱AI定价）
    estimated_cost REAL,  -- 人民币
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_operation_type CHECK (operation_type IN ('index', 'query'))
);

CREATE INDEX IF NOT EXISTS idx_token_stats_date ON token_stats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_stats_model ON token_stats(model_name);
CREATE INDEX IF NOT EXISTS idx_token_stats_operation ON token_stats(operation_type, operation_id);

-- ========================================
-- 初始化完成标记
-- ========================================
-- 用于检查数据库是否已初始化
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES ('1.0.0');

