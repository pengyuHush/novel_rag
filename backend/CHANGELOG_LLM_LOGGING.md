# LLM API 日志功能实现记录

## 更新时间
2025-11-10

## 更新内容

### 1. 核心日志工具 (`app/utils/llm_logger.py`)

新增统一的LLM API日志记录工具，包含：

#### `LLMCallLogger` 类
- **功能**：统一记录所有智谱AI API调用的入参和出参
- **特性**：
  - 自动脱敏处理（消息内容截断、批量输入限制）
  - 统一的JSON格式输出
  - 支持成功和错误两种状态
  - 记录调用耗时（精确到毫秒）
  - 提取Token使用统计

#### `StreamContentAccumulator` 类
- **功能**：累积流式API的完整输出内容
- **特性**：
  - 分别记录思考过程和答案内容
  - 统计chunk数量和内容长度
  - 在流结束时输出完整的汇总日志
  - 自动计算总耗时

### 2. RAG服务日志集成 (`app/services/rag_service.py`)

在以下方法中集成了日志功能：

#### Embeddings API
- **方法**：`embed_texts()`
- **日志类型**：embeddings
- **记录内容**：
  - 输入文本数量和内容预览
  - 向量维度和数量
  - Token使用统计

#### Chat API（非流式）
- **方法**：`_generate_answer()`
- **日志类型**：chat
- **记录内容**：
  - 完整的messages列表（截断后）
  - thinking配置
  - 生成的答案内容（截断后）
  - Token使用统计

#### Chat Stream API（流式）
- **方法**：`_generate_answer_stream()`
- **日志类型**：chat_stream
- **记录内容**：
  - 请求参数
  - 累积的完整思考过程
  - 累积的完整答案内容
  - chunk统计和Token使用

#### 查询改写
- **方法**：`_rewrite_query()`
- **任务标识**：query_rewriting
- **记录内容**：
  - 原始查询
  - 改写后的查询列表

#### HyDE生成
- **方法**：`_generate_hypothetical_answer()`
- **任务标识**：hyde / hyde_fallback
- **记录内容**：
  - 用户查询
  - 生成的假设性答案
  - 是否使用fallback策略

#### 重排序
- **方法**：`_simple_rerank()`
- **任务标识**：rerank_1, rerank_2, ...
- **记录内容**：
  - 每个候选结果的评分请求
  - LLM给出的相关性分数

### 3. 元数据提取服务日志集成 (`app/services/metadata_extraction_service.py`)

- **方法**：`_extract_with_llm()`
- **日志类型**：chat
- **记录内容**：
  - 待提取的文本内容（截断后）
  - 提取模型（glm-4-flash）
  - 生成的元数据JSON
  - Token使用统计

### 4. 文档和测试

#### 文档
- **文件**：`backend/docs/LLM_API_LOGGING.md`
- **内容**：
  - 日志格式详细说明
  - 使用场景和示例
  - 日志过滤和分析方法
  - 成本计算示例
  - 性能监控建议

#### 测试脚本
- **文件**：`backend/scripts/test_llm_logging.py`
- **功能**：
  - 测试Embeddings API日志
  - 测试Chat API日志（非流式）
  - 测试Chat Stream API日志（流式）
  - 测试查询改写日志
  - 演示日志输出格式

## 日志格式示例

### 成功调用
```json
[LLM API CALL] {
  "api_type": "chat",
  "model": "glm-4.5",
  "timestamp": 1699999999.123,
  "duration_seconds": 2.345,
  "request": {
    "model": "glm-4.5",
    "messages": [...],
    "temperature": 0.3
  },
  "status": "success",
  "response": {
    "usage": {
      "prompt_tokens": 1523,
      "completion_tokens": 245,
      "total_tokens": 1768
    },
    "content": "回答内容...",
    "content_length": 856
  }
}
```

### 错误调用
```json
[LLM API ERROR] {
  "api_type": "chat",
  "model": "glm-4.5",
  "timestamp": 1699999999.123,
  "duration_seconds": 0.123,
  "request": {...},
  "status": "error",
  "error": "API rate limit exceeded"
}
```

### 流式调用汇总
```json
[STREAM SUMMARY] chunks=145, thinking_length=456, answer_length=778, duration=15.678s
```

## 影响范围

### 代码修改
- ✅ 新增文件：`app/utils/llm_logger.py`
- ✅ 修改文件：`app/services/rag_service.py`
- ✅ 修改文件：`app/services/metadata_extraction_service.py`

### 性能影响
- 日志记录开销：< 1ms per call
- 内存占用：流式累积器约占用数KB（取决于响应长度）
- 无显著性能影响

### 向后兼容性
- ✅ 完全向后兼容
- ✅ 不影响现有API功能
- ✅ 只增加日志输出，不改变业务逻辑

## 使用方法

### 查看日志
所有日志会自动输出到标准日志系统，使用INFO级别：

```bash
# 查看所有LLM API调用
grep "LLM API" logs/app.log

# 查看特定类型的调用
grep '"api_type": "embeddings"' logs/app.log

# 查看错误调用
grep "LLM API ERROR" logs/app.log
```

### 运行测试
```bash
cd backend
python scripts/test_llm_logging.py
```

### 成本分析
参考 `backend/docs/LLM_API_LOGGING.md` 中的成本分析脚本。

## 后续优化建议

1. **日志轮转**：配置日志文件自动轮转，避免单个文件过大
2. **日志聚合**：考虑将日志发送到ELK等日志收集系统
3. **实时监控**：基于日志数据建立实时监控告警
4. **成本优化**：定期分析日志，优化高成本的API调用
5. **性能优化**：识别耗时过长的调用，针对性优化

## 相关链接

- 详细文档：`backend/docs/LLM_API_LOGGING.md`
- 测试脚本：`backend/scripts/test_llm_logging.py`
- 日志工具：`backend/app/utils/llm_logger.py`

## 问题反馈

如遇到问题或有改进建议，请：
1. 检查日志输出格式是否正确
2. 验证Token统计是否准确
3. 确认流式日志是否完整记录

