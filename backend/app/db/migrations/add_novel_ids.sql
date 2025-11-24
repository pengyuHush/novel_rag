-- 添加 novel_ids 字段到 queries 表
-- 用于支持多本小说查询功能
-- 存储格式：JSON数组，例如 "[1, 2, 3]"

ALTER TABLE queries ADD COLUMN novel_ids TEXT;

