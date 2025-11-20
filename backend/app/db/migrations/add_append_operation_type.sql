-- 迁移脚本：为 token_stats 表添加 'append' 操作类型
-- 创建时间: 2025-11-20
-- 说明: 支持追加章节功能的 token 统计

-- SQLite 不支持直接修改 CHECK 约束，需要重建表

-- 1. 创建新表（包含新的约束）
CREATE TABLE IF NOT EXISTS token_stats_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,
    operation_id INTEGER,
    model_name TEXT NOT NULL,
    
    input_tokens INTEGER DEFAULT 0,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER NOT NULL,
    
    estimated_cost REAL DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_operation_type CHECK (operation_type IN ('index', 'query', 'append'))
);

-- 2. 复制旧表数据
INSERT INTO token_stats_new (
    id, operation_type, operation_id, model_name,
    input_tokens, prompt_tokens, completion_tokens, total_tokens,
    estimated_cost, created_at
)
SELECT 
    id, operation_type, operation_id, model_name,
    input_tokens, prompt_tokens, completion_tokens, total_tokens,
    estimated_cost, created_at
FROM token_stats;

-- 3. 删除旧表
DROP TABLE token_stats;

-- 4. 重命名新表
ALTER TABLE token_stats_new RENAME TO token_stats;

-- 5. 重建索引
CREATE INDEX IF NOT EXISTS idx_token_stats_date ON token_stats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_stats_model ON token_stats(model_name);
CREATE INDEX IF NOT EXISTS idx_token_stats_operation ON token_stats(operation_type, operation_id);

