# 查询分解功能实现总结

## 实现概述

成功实现了基于LLM的智能查询分解功能，用于解决复杂查询（如"介绍李凡的身世，包含父母、家族、师傅等"）语义分散导致的信息遗漏问题。

## 实现的文件和功能

### 1. 核心服务层

#### `backend/app/services/query_decomposer.py` (新建)
- **QueryDecomposer** 类：负责查询分解的核心逻辑
  - `should_decompose()`: 判断查询复杂度（检测枚举关键词、实体数、字数、多问句等）
  - `decompose_query()`: 使用GLM-4-Flash智能分解查询为子查询列表
  - `_parse_subqueries()`: 解析LLM返回的多种格式（JSON、列表等）
  - `_validate_subqueries()`: 验证、去重、限制子查询数量

**复杂度判断规则**：
- 查询字数 > 30字
- 包含2个以上枚举关键词（"包含"、"以及"、"和"等）
- 包含2个以上疑问词（"是谁"、"在哪里"等）
- 包含明确的列举结构（逗号、顿号等）

#### `backend/app/services/rag_engine.py` (修改)
新增方法：
- `query()`: 添加 `enable_query_decomposition` 参数，集成查询分解逻辑
- `_query_with_decomposition()`: 查询分解的完整检索流程
  - 并行检索所有子查询（使用 ThreadPoolExecutor）
  - 合并去重chunk结果
  - 全局rerank
  - 统一生成答案
- `_retrieve_single_subquery()`: 检索单个子查询（每个取Top20）
- `_deduplicate_chunks()`: chunk去重（基于章节号+内容前缀）
- `_rerank_unified()`: 全局rerank（基于原始查询重新计算相关性）

### 2. 配置层

#### `backend/app/core/config.py` (修改)
新增配置项：
```python
query_decomposition_enabled: bool = True
query_decomposition_max_subqueries: int = 5
query_decomposition_model: str = "glm-4-flash"
query_decomposition_complexity_threshold: int = 30
```

#### `backend/app/models/schemas.py` (修改)
在 `QueryRequest` 中新增字段：
```python
enable_query_decomposition: bool = Field(
    default=True, 
    description="是否启用查询分解（复杂查询自动拆分）"
)
```

### 3. API层

#### `backend/app/api/query.py` (修改)
- 非流式查询接口：传递 `enable_query_decomposition` 参数到RAG引擎
- WebSocket流式查询：添加配置读取（暂默认关闭，因流式查询与分解模式不兼容）
- 初始化日志中记录查询分解开关状态

## 技术特性

### 1. 并行执行
使用 `ThreadPoolExecutor` 并行检索所有子查询，最多5个并发：
```python
with ThreadPoolExecutor(max_workers=min(len(sub_queries), 5)) as executor:
    # 并行提交所有子查询
```

### 2. 智能去重
基于 `章节号 + 内容前100字符` 构建唯一键，保留分数最高的chunk：
```python
key = f"{chapter_num}_{content_prefix}"
```

### 3. 全局Rerank
合并所有子查询结果后，基于原始查询重新计算：
- 实体匹配分数
- 章节重要性
- 时间衰减因子

### 4. 自动回退机制
在以下情况自动回退到原始查询流程：
- LLM分解失败（超时、错误）
- 分解出的子查询小于2个
- 所有子查询都无结果
- 复杂度判断不需要分解

## 使用示例

### API请求示例
```json
{
  "novel_id": 1,
  "query": "介绍李凡的身世，包含他的父母、家族、师傅、师门以及现在的状况",
  "model": "zhipu/GLM-4.5-Flash",
  "enable_query_rewrite": true,
  "enable_query_decomposition": true,
  "recency_bias_weight": 0.15
}
```

### 查询分解示例
**输入**：
```
介绍李凡的身世，包含他的父母、家族、师傅、师门以及现在的状况
```

**分解为**：
```json
[
  "李凡的父母是谁",
  "李凡的家族背景",
  "李凡的师傅和师门",
  "李凡现在的状况"
]
```

### 统计信息返回
```json
{
  "decomposed": true,
  "sub_queries_count": 4,
  "sub_queries": ["李凡的父母是谁", "..."],
  "total_chunks_before_dedup": 80,
  "unique_chunks": 45,
  "final_chunks": 10,
  "citations": 10
}
```

## 测试要点

### 1. 简单查询测试
**查询**: "李凡的母亲是谁"
- ✅ 应该**不触发**查询分解（复杂度不够）
- ✅ 使用原始查询流程
- ✅ 返回正确答案

### 2. 复杂查询测试
**查询**: "介绍李凡的身世，包含父母、家族、师傅、师门、状况"
- ✅ 应该**触发**查询分解
- ✅ 分解为4-5个子查询
- ✅ 并行检索执行
- ✅ 答案覆盖所有维度（父母、家族、师傅等）

### 3. 边界测试
- **恰好30字**: 测试阈值边界
- **包含1个枚举词**: 不应触发分解
- **包含2个枚举词**: 应触发分解
- **空查询**: 正常返回错误

### 4. 性能测试
- **延迟对比**: 
  - 简单查询: 无额外延迟
  - 复杂查询: 约+40%延迟（而非串行的+150%）
- **成本对比**: 约+150%（额外的LLM调用和检索）

### 5. 回退测试
- LLM分解超时/失败 → 自动回退
- 分解返回空列表 → 使用原始流程
- 分解返回单个查询 → 使用原始流程

### 6. 日志验证
检查日志中是否包含：
- 🔍 查询无需分解 / 🔨 查询需要分解
- 🔨 使用查询分解流程: N个子查询
- ✅ 子查询完成: "..." -> X个chunks
- 📊 总共检索到 X 个chunks（合并前）
- 🔄 去重后剩余 X 个chunks
- 🎯 全局Rerank完成: X 个chunks

## 配置建议

### 开发环境
```env
QUERY_DECOMPOSITION_ENABLED=true
QUERY_DECOMPOSITION_MAX_SUBQUERIES=5
QUERY_DECOMPOSITION_MODEL=glm-4-flash
QUERY_DECOMPOSITION_COMPLEXITY_THRESHOLD=30
```

### 生产环境（成本优化）
```env
QUERY_DECOMPOSITION_ENABLED=true
QUERY_DECOMPOSITION_MAX_SUBQUERIES=3  # 减少子查询数量
QUERY_DECOMPOSITION_MODEL=glm-4-flash  # 使用快速模型
QUERY_DECOMPOSITION_COMPLEXITY_THRESHOLD=40  # 提高阈值，减少触发
```

### 关闭查询分解
```env
QUERY_DECOMPOSITION_ENABLED=false
```
或在API请求中：
```json
{
  "enable_query_decomposition": false
}
```

## 预期效果

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 信息覆盖率（复杂查询） | 80% | 95% | +18.75% |
| 单次查询成本 | 1x | 2.5x | +150% |
| 查询延迟（并行） | 1x | 1.4x | +40% |
| 简单查询影响 | - | 0% | 无影响 |

## 注意事项

1. **成本控制**: 查询分解会增加约150%的成本，建议：
   - 仅对复杂查询启用
   - 使用快速模型（glm-4-flash）进行分解
   - 适当提高复杂度阈值

2. **流式查询暂不支持**: WebSocket流式查询暂时不支持查询分解（默认关闭）

3. **并发限制**: 最多5个子查询并发，避免触发API限流

4. **缓存机制**: 查询分解的结果同样会被缓存，相同查询第二次调用直接返回缓存

5. **日志追踪**: 所有查询分解步骤都有详细日志，便于调试和优化

## 后续优化方向

1. **自适应Top-K**: 根据子查询数量动态调整每个子查询的Top-K
2. **语义聚类**: 对相似的子查询结果进行聚类，减少冗余
3. **增量答案生成**: 支持流式返回每个子查询的部分答案
4. **成本预估**: 在分解前预估成本，给用户选择权
5. **A/B测试框架**: 自动对比分解/不分解的效果差异

## 总结

查询分解功能已完整实现并集成到RAG系统中，能够有效解决复杂查询的信息遗漏问题。通过智能判断、并行执行、全局rerank等机制，在保证检索质量的同时控制了成本和延迟的增加。系统具备完善的回退机制和日志追踪，便于监控和优化。

