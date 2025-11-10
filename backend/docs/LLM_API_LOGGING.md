# LLM API 调用日志说明

## 概述

本项目已在所有智谱AI API调用位置集成了统一的日志记录功能，包括：
- **Embeddings API** - 文本向量化
- **Chat API** - 对话/文本生成（非流式）
- **Chat Stream API** - 流式对话/文本生成

## 日志位置

所有API调用相关的服务：
1. `backend/app/services/rag_service.py` - RAG搜索服务
   - `embed_texts()` - Embeddings API
   - `_generate_answer()` - Chat API（非流式）
   - `_generate_answer_stream()` - Chat Stream API（流式）
   - `_rewrite_query()` - 查询改写
   - `_generate_hypothetical_answer()` - HyDE生成
   - `_simple_rerank()` - 重排序

2. `backend/app/services/metadata_extraction_service.py` - 元数据提取服务
   - `_extract_with_llm()` - 元数据提取

## 日志格式

### 非流式API调用日志

```json
[LLM API CALL] {
  "api_type": "chat",
  "model": "glm-4.5",
  "timestamp": 1699999999.123,
  "duration_seconds": 2.345,
  "request": {
    "model": "glm-4.5",
    "messages": [
      {
        "role": "system",
        "content": "你是专业的中文小说分析助手..."
      },
      {
        "role": "user",
        "content": "主角是谁？（前200字）..."
      }
    ],
    "thinking": {"type": "enabled"},
    "temperature": 0.3,
    "top_p": 0.8
  },
  "status": "success",
  "response": {
    "usage": {
      "prompt_tokens": 1523,
      "completion_tokens": 245,
      "total_tokens": 1768
    },
    "content": "根据原文内容分析，主角是...(前500字)",
    "content_length": 856
  }
}
```

### Embeddings API 日志

```json
[LLM API CALL] {
  "api_type": "embeddings",
  "model": "embedding-3",
  "timestamp": 1699999999.123,
  "duration_seconds": 1.234,
  "request": {
    "model": "embedding-3",
    "input": [
      "第一段文本内容（前100字）...",
      "第二段文本内容（前100字）...",
      "第三段文本内容（前100字）...",
      "... and 5 more"
    ],
    "dimensions": 1024,
    "input_count": 8
  },
  "status": "success",
  "response": {
    "usage": {
      "prompt_tokens": 456,
      "completion_tokens": 0,
      "total_tokens": 456
    },
    "vector_count": 8,
    "vector_dimension": 1024
  }
}
```

### 流式API调用日志

流式API会在所有chunk处理完成后输出汇总日志：

```json
[LLM API CALL] {
  "api_type": "chat_stream",
  "model": "glm-4.5",
  "timestamp": 1699999999.123,
  "duration_seconds": 15.678,
  "request": {
    "model": "glm-4.5",
    "messages": [
      {
        "role": "system",
        "content": "你是专业的中文小说分析助手..."
      },
      {
        "role": "user",
        "content": "详细描述主角的性格特点（前200字）..."
      }
    ],
    "stream": true,
    "thinking": {"type": "enabled"},
    "temperature": 0.3,
    "top_p": 0.8
  },
  "status": "success",
  "response": {
    "usage": {
      "prompt_tokens": 2341,
      "completion_tokens": 567,
      "total_tokens": 2908
    },
    "content": "【思考过程】\n首先分析原文中的描述...\n\n【答案】\n主角的性格特点主要体现在...(前500字)",
    "content_length": 1234
  }
}

[STREAM SUMMARY] chunks=145, thinking_length=456, answer_length=778, duration=15.678s
```

### 错误日志

```json
[LLM API ERROR] {
  "api_type": "chat",
  "model": "glm-4.5",
  "timestamp": 1699999999.123,
  "duration_seconds": 0.123,
  "request": {
    "model": "glm-4.5",
    "messages": [...]
  },
  "status": "error",
  "error": "API rate limit exceeded"
}
```

## 日志特性

### 1. 自动脱敏
- **消息内容截断**：超过200字的消息内容自动截断，避免日志过大
- **批量输入限制**：embeddings的input列表只显示前3条，其余显示计数
- **响应内容截断**：响应内容超过500字时截断显示

### 2. 性能统计
- **调用耗时**：精确到毫秒级（`duration_seconds`）
- **Token统计**：包含prompt、completion和total tokens
- **流式统计**：chunk数量、思考过程长度、答案长度

### 3. 任务标识
为不同的API调用场景添加了`task`标识：
- `query_rewriting` - 查询改写
- `hyde` - HyDE假设答案生成
- `hyde_fallback` - HyDE备用策略
- `rerank_1`, `rerank_2`, ... - 重排序（带序号）

### 4. 流式内容累积
流式API使用`StreamContentAccumulator`累积完整内容：
- 分别记录思考过程和答案内容
- 在流结束时输出完整日志
- 包含总chunk数和内容长度统计

## 使用建议

### 1. 日志级别
- **INFO级别**：记录所有成功的API调用
- **ERROR级别**：记录API调用失败
- **DEBUG级别**：原有的详细响应日志

### 2. 日志过滤
可以使用以下方式过滤特定类型的API调用：

```bash
# 只查看Embeddings调用
grep '"api_type": "embeddings"' app.log

# 只查看流式调用
grep '"api_type": "chat_stream"' app.log

# 只查看某个任务
grep '"task": "hyde"' app.log

# 查看耗时超过5秒的调用
grep -A 50 '"duration_seconds"' app.log | grep -B 5 '"duration_seconds": [5-9]'
```

### 3. 成本分析
基于日志可以分析API使用成本：

```python
import json
import re

total_tokens = 0
total_cost = 0.0

with open('app.log', 'r') as f:
    for line in f:
        if '[LLM API CALL]' in line:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', line, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if 'response' in data and 'usage' in data['response']:
                    usage = data['response']['usage']
                    
                    # 根据不同API计算成本
                    if data['api_type'] == 'embeddings':
                        # Embedding-3: 0.5元/百万tokens
                        cost = usage['total_tokens'] * 0.5 / 1_000_000
                    elif data['api_type'] in ['chat', 'chat_stream']:
                        # GLM-4-Plus: 输入5元/百万 + 输出10元/百万
                        cost = (
                            usage['prompt_tokens'] * 5 / 1_000_000 +
                            usage['completion_tokens'] * 10 / 1_000_000
                        )
                    
                    total_tokens += usage['total_tokens']
                    total_cost += cost

print(f"Total tokens: {total_tokens}")
print(f"Estimated cost: ¥{total_cost:.4f}")
```

### 4. 性能监控
可以监控各类API调用的平均耗时：

```bash
# 提取所有duration并计算平均值
grep '"duration_seconds"' app.log | \
  grep -oP '"duration_seconds": \K[0-9.]+' | \
  awk '{sum+=$1; count++} END {print "Average duration:", sum/count, "seconds"}'
```

## 示例场景

### 场景1：调试HyDE功能
当HyDE生成效果不佳时，可以通过日志查看：
- HyDE的prompt构建是否合理
- 生成的假设答案内容
- 是否触发了fallback策略
- 生成耗时是否正常

### 场景2：优化流式输出性能
通过流式日志可以分析：
- 总chunk数是否合理
- 思考过程和答案的比例
- 流式输出的总耗时
- 是否有异常的长耗时

### 场景3：成本控制
定期分析日志可以：
- 统计各类API的调用频率
- 计算Token消耗趋势
- 识别高成本的调用场景
- 优化prompt长度和参数

## 日志工具类

### `LLMCallLogger`
统一的日志记录器，提供：
- `log_api_call()` - 记录单次API调用
- 自动脱敏处理
- 统一的JSON格式输出

### `StreamContentAccumulator`
流式内容累积器，提供：
- `add_thinking_chunk()` - 添加思考过程片段
- `add_answer_chunk()` - 添加答案片段
- `set_usage()` - 设置Token使用信息
- `log_summary()` - 输出汇总日志

## 注意事项

1. **日志大小**：由于API调用日志包含请求和响应内容，建议配置日志轮转
2. **敏感信息**：虽然已做脱敏处理，但请勿在日志中包含用户隐私数据
3. **性能影响**：日志记录本身的开销很小（<1ms），不会显著影响性能
4. **存储空间**：建议定期清理或归档旧日志文件

## 未来扩展

可以考虑的增强功能：
- [ ] 将日志发送到专门的日志收集系统（如ELK）
- [ ] 添加实时监控告警（如耗时异常、错误率过高）
- [ ] 支持按用户维度统计API使用情况
- [ ] 集成分布式追踪（如OpenTelemetry）

