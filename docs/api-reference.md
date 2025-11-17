# API接口文档

> 网络小说智能问答系统 v0.1.0  
> 基于OpenAPI 3.0规范

---

## 📋 目录

- [接口概览](#接口概览)
- [健康检查 API](#健康检查-api)
- [小说管理 API](#小说管理-api)
- [章节管理 API](#章节管理-api)
- [智能问答 API](#智能问答-api)
- [知识图谱 API](#知识图谱-api)
- [统计信息 API](#统计信息-api)
- [系统配置 API](#系统配置-api)
- [WebSocket API](#websocket-api)
- [数据模型](#数据模型)
- [错误处理](#错误处理)

---

## 接口概览

### 基础信息

| 项目 | 信息 |
|------|------|
| **Base URL** | `http://localhost:8000` |
| **协议** | HTTP/1.1, WebSocket |
| **数据格式** | JSON |
| **字符编码** | UTF-8 |

### 技术栈

- **后端框架**: FastAPI + Python 3.10+
- **向量数据库**: ChromaDB
- **图数据库**: NetworkX
- **关系数据库**: SQLite
- **AI模型**: 智谱AI GLM系列 + Embedding-3

### 接口分类

| 分类 | 端点数 | 描述 |
|------|--------|------|
| 健康检查 | 4 | 服务状态监控 |
| 小说管理 | 6 | 上传、删除、索引 |
| 章节管理 | 4 | 章节查询和搜索 |
| 智能问答 | 5 | 查询、历史、反馈 |
| 知识图谱 | 4 | 图谱、时间线可视化 |
| 统计信息 | 3 | Token和使用统计 |
| 系统配置 | 5 | 配置管理 |
| WebSocket | 1 | 流式问答 |

---

## 健康检查 API

### 1. 基础健康检查

检查API服务是否正常运行。

```http
GET /api/health
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

---

### 2. 数据库健康检查

检查SQLite数据库连接。

```http
GET /api/health/database
```

**响应示例**:
```json
{
  "service": "database",
  "status": "healthy",
  "message": "数据库连接正常",
  "details": {
    "type": "SQLite",
    "novels_count": 5
  }
}
```

---

### 3. ChromaDB健康检查

检查向量数据库连接。

```http
GET /api/health/chromadb
```

---

### 4. 智谱AI健康检查

检查智谱AI API连接。

```http
GET /api/health/zhipu
```

---

## 小说管理 API

### 1. 上传小说

上传小说文件并启动后台索引任务。

```http
POST /api/novels/upload
Content-Type: multipart/form-data
```

**请求参数**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 小说文件（TXT或EPUB） |
| `title` | String | ✅ | 小说标题（1-200字符） |
| `author` | String | ❌ | 作者（最多100字符） |

**响应示例**:
```json
{
  "id": 1,
  "title": "斗破苍穹",
  "author": "天蚕土豆",
  "total_chars": 3500000,
  "total_chapters": 1648,
  "index_status": "processing",
  "index_progress": 0.05,
  "file_format": "txt",
  "total_chunks": 0,
  "total_entities": 0,
  "total_relations": 0,
  "embedding_tokens": 0,
  "upload_date": "2025-11-17T10:30:00",
  "indexed_date": null,
  "created_at": "2025-11-17T10:30:00",
  "updated_at": "2025-11-17T10:30:00"
}
```

**索引过程**（后台异步）:
1. 文件解析（TXT编码检测/EPUB解压）
2. 章节检测
3. 文本分块（RecursiveCharacterTextSplitter）
4. 向量化（ZhipuAI Embedding-3）
5. 实体提取（HanLP NER）
6. 关系构建（NetworkX）
7. 时间线分析
8. PageRank计算

---

### 2. 获取小说列表

分页获取小说列表。

```http
GET /api/novels?skip=0&limit=100&status=completed
```

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `skip` | Integer | 0 | 跳过的记录数 |
| `limit` | Integer | 100 | 返回的最大记录数（1-200） |
| `status` | String | - | 按状态筛选（pending/processing/completed/failed） |

**响应示例**:
```json
[
  {
    "id": 1,
    "title": "斗破苍穹",
    "author": "天蚕土豆",
    "total_chars": 3500000,
    "total_chapters": 1648,
    "index_status": "completed",
    "index_progress": 1.0,
    "file_format": "txt",
    "upload_date": "2025-11-17T10:30:00"
  }
]
```

---

### 3. 获取小说详情

根据ID获取单个小说的完整信息。

```http
GET /api/novels/{novel_id}
```

**路径参数**:
- `novel_id`: 小说ID（Integer）

---

### 4. 获取索引进度

获取小说索引的详细进度。

```http
GET /api/novels/{novel_id}/progress
```

**响应示例**:
```json
{
  "novel_id": 1,
  "status": "processing",
  "progress": 0.65,
  "current_step": "实体提取",
  "steps": [
    {
      "name": "文件解析",
      "status": "completed",
      "progress": 1.0,
      "message": "成功解析3500000字符",
      "started_at": "2025-11-17T10:30:05",
      "completed_at": "2025-11-17T10:30:10"
    },
    {
      "name": "章节检测",
      "status": "completed",
      "progress": 1.0,
      "message": "检测到1648章",
      "started_at": "2025-11-17T10:30:10",
      "completed_at": "2025-11-17T10:30:15"
    },
    {
      "name": "实体提取",
      "status": "processing",
      "progress": 0.65,
      "message": "已处理1071/1648章",
      "started_at": "2025-11-17T10:35:00",
      "completed_at": null
    }
  ],
  "token_stats": {
    "embedding_tokens": 3200000,
    "entity_extraction_tokens": 850000
  },
  "warnings": []
}
```

---

### 5. 重新索引

触发小说的重新索引任务。

```http
POST /api/novels/{novel_id}/reindex
```

---

### 6. 删除小说

删除小说及其所有相关数据。

```http
DELETE /api/novels/{novel_id}
```

**删除内容**:
- 文件
- 向量数据（ChromaDB）
- 知识图谱（NetworkX）
- 章节记录（SQLite）
- 查询历史

---

## 章节管理 API

### 1. 获取章节列表

获取指定小说的所有章节。

```http
GET /api/chapters/{novel_id}?skip=0&limit=100
```

**响应示例**:
```json
[
  {
    "id": 1,
    "novel_id": 1,
    "chapter_num": 1,
    "title": "第一章 陨落的天才",
    "char_count": 2345,
    "created_at": "2025-11-17T10:30:15"
  }
]
```

---

### 2. 获取章节内容

根据章节号获取完整内容。

```http
GET /api/chapters/{novel_id}/{chapter_num}
```

**响应示例**:
```json
{
  "id": 1,
  "novel_id": 1,
  "chapter_num": 1,
  "title": "第一章 陨落的天才",
  "content": "\"斗之力，三段！\"\n\n望着测验魔石碑上面闪亮得甚至有些刺眼的五个大字...",
  "char_count": 2345,
  "created_at": "2025-11-17T10:30:15"
}
```

---

### 3. 搜索章节

按关键词搜索章节。

```http
GET /api/chapters/{novel_id}/search?keyword=萧炎&limit=20
```

---

### 4. 获取章节范围

获取指定章节范围的内容。

```http
GET /api/chapters/{novel_id}/range?start=1&end=10
```

---

## 智能问答 API

### 1. 非流式查询

提交查询并等待完整结果。

```http
POST /api/query
Content-Type: application/json
```

**请求体**:
```json
{
  "novel_id": 1,
  "query": "萧炎在什么时候恢复斗之气的？",
  "model": "GLM-4.5-Air"
}
```

**响应示例**:
```json
{
  "query_id": 123,
  "answer": "萧炎在第3章《分别》中恢复了斗之气。当时他在山洞中遇到了药老（药尘），药老帮助他...",
  "citations": [
    {
      "chapter_id": 3,
      "chapter_num": 3,
      "text": "\"小家伙，你的斗之气被异火吞噬了...\"",
      "similarity": 0.92
    }
  ],
  "graph_info": {
    "related_entities": ["萧炎", "药老", "戒指"],
    "chapter_importance": 0.85
  },
  "contradictions": [],
  "token_stats": {
    "total_tokens": 3580,
    "by_model": {
      "GLM-4.5-Air": {
        "input_tokens": 2800,
        "output_tokens": 780,
        "total_tokens": 3580
      }
    }
  },
  "response_time": 2.35,
  "confidence": "high",
  "model": "GLM-4.5-Air",
  "timestamp": "2025-11-17T14:25:30"
}
```

---

### 2. 获取查询历史

分页获取历史查询记录。

```http
GET /api/query/history?novel_id=1&page=1&page_size=20
```

**查询参数**:
- `novel_id` (可选): 按小说ID过滤
- `page` (默认1): 页码
- `page_size` (默认20): 每页记录数（1-100）

**响应示例**:
```json
{
  "items": [
    {
      "id": 123,
      "novel_id": 1,
      "query": "萧炎在什么时候恢复斗之气的？",
      "answer": "萧炎在第3章《分别》中恢复了斗之气...",
      "model": "GLM-4.5-Air",
      "total_tokens": 3580,
      "confidence": "high",
      "created_at": "2025-11-17T14:25:30",
      "feedback": "positive"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

### 3. 获取查询详情

获取单个查询的完整详情。

```http
GET /api/query/{query_id}
```

---

### 4. 提交用户反馈

对查询结果提交反馈。

```http
POST /api/query/{query_id}/feedback?feedback=positive&note=答案很准确
```

**查询参数**:
- `feedback` (必填): `positive` 或 `negative`
- `note` (可选): 反馈备注（最多500字符）

**响应示例**:
```json
{
  "success": true,
  "message": "感谢您的反馈！",
  "query_id": 123,
  "feedback": "positive"
}
```

---

### 5. 获取Token统计

获取单次查询的详细Token消耗。

```http
GET /api/query/{query_id}/token-stats
```

---

## 知识图谱 API

### 1. 获取关系图谱

获取小说的角色关系图谱。

```http
GET /api/graph/relations/{novel_id}?start_chapter=1&end_chapter=100&max_nodes=50&min_importance=0.1
```

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `start_chapter` | Integer | - | 起始章节（可选） |
| `end_chapter` | Integer | - | 结束章节（可选） |
| `max_nodes` | Integer | 50 | 最大节点数（10-200） |
| `min_importance` | Float | 0.0 | 最小重要性阈值（0.0-1.0） |

**响应示例**:
```json
{
  "nodes": [
    {
      "id": "萧炎",
      "name": "萧炎",
      "type": "character",
      "importance": 0.95
    },
    {
      "id": "纳兰嫣然",
      "name": "纳兰嫣然",
      "type": "character",
      "importance": 0.78
    }
  ],
  "edges": [
    {
      "source": "萧炎",
      "target": "纳兰嫣然",
      "relation_type": "婚约",
      "strength": 0.85
    }
  ],
  "metadata": {
    "total_nodes": 45,
    "total_edges": 120,
    "chapter_range": [1, 100]
  }
}
```

**用途**:
- Plotly.js可视化
- React Flow图谱展示
- D3.js力导向图

---

### 2. 获取时间线

获取小说的时间线事件。

```http
GET /api/graph/timeline/{novel_id}?entity_filter=萧炎&max_events=100
```

**响应示例**:
```json
{
  "events": [
    {
      "chapter_num": 1,
      "narrative_order": 1,
      "description": "萧炎测验斗之力三段",
      "event_type": "character_development",
      "importance": 0.88
    },
    {
      "chapter_num": 3,
      "narrative_order": 3,
      "description": "萧炎遇到药老",
      "event_type": "encounter",
      "importance": 0.92
    }
  ],
  "metadata": {
    "total_events": 85,
    "chapter_range": [1, 1648]
  }
}
```

---

### 3. 获取图谱统计

获取知识图谱的统计信息。

```http
GET /api/graph/statistics/{novel_id}
```

**响应示例**:
```json
{
  "total_chapters": 1648,
  "total_characters": 342,
  "total_chars": 3500000,
  "character_count": 342,
  "relation_count": 1250,
  "average_chapter_length": 2123,
  "top_characters": [
    {
      "name": "萧炎",
      "importance": 0.95,
      "appearances": 1580
    }
  ],
  "chapter_density": [
    {
      "chapter_num": 1,
      "entity_count": 15,
      "relation_count": 8
    }
  ]
}
```

---

### 4. 获取节点详情

获取知识图谱中单个节点的详细信息。

```http
GET /api/graph/relations/{novel_id}/node/{node_id}
```

**路径参数**:
- `node_id`: 节点ID（实体名称，如"萧炎"）

---

## 统计信息 API

### 1. 获取小说Token统计

```http
GET /api/stats/tokens/{novel_id}
```

**响应示例**:
```json
{
  "steps": [
    {
      "step": "embedding",
      "model": "embedding-3",
      "input_tokens": 3200000,
      "output_tokens": 0,
      "total_tokens": 3200000,
      "cost": 0.64
    },
    {
      "step": "entity_extraction",
      "model": "GLM-4.5-Air",
      "input_tokens": 1500000,
      "output_tokens": 250000,
      "total_tokens": 1750000,
      "cost": 1.75
    }
  ],
  "total": {
    "total_tokens": 4950000,
    "total_cost": 2.39
  }
}
```

---

### 2. 获取系统统计

```http
GET /api/stats/system
```

---

### 3. 获取模型使用统计

```http
GET /api/stats/models
```

---

## 系统配置 API

### 1. 获取配置

```http
GET /api/config
```

**响应示例**:
```json
{
  "default_model": "GLM-4.5-Air",
  "top_k": 30,
  "chunk_size": 550,
  "chunk_overlap": 125,
  "enable_self_rag": true,
  "enable_smart_routing": true
}
```

---

### 2. 更新配置

```http
PUT /api/config
Content-Type: application/json
```

**请求体**:
```json
{
  "default_model": "GLM-4-Plus",
  "top_k": 50
}
```

---

### 3. 获取支持的模型列表

```http
GET /api/config/models
```

**响应示例**:
```json
[
  {
    "name": "GLM-4.5-Air",
    "category": "高性价比",
    "max_tokens": 128000,
    "price_input": 1.0,
    "price_output": 1.0,
    "description": "高性价比 - 在推理、编码和智能体任务上表现强劲"
  }
]
```

---

### 4. 测试API连接

```http
POST /api/config/test-connection
Content-Type: application/json
```

**请求体**:
```json
{
  "api_key": "your_zhipu_api_key"
}
```

---

### 5. 获取环境信息

```http
GET /api/config/env
```

---

## WebSocket API

### 流式查询

通过WebSocket建立连接并进行流式问答。

```
ws://localhost:8000/api/query/stream
```

#### 连接流程

1. **建立连接**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/query/stream');
```

2. **发送查询**
```javascript
ws.send(JSON.stringify({
  novel_id: 1,
  query: "萧炎在什么时候恢复斗之气的？",
  model: "GLM-4.5-Air"
}));
```

3. **接收消息**

消息统一格式：
```json
{
  "stage": "understanding|retrieving|generating|validating|complete|error",
  "content": "阶段文本内容",
  "progress": 0.5,
  "data": {}
}
```

#### 消息阶段

1. **understanding** - 查询理解
```json
{
  "stage": "understanding",
  "content": "正在分析查询意图...\n检测到实体: 萧炎, 斗之气\n查询类型: 事实类查询",
  "progress": 0.2,
  "data": {
    "entities": ["萧炎", "斗之气"],
    "query_type": "fact"
  }
}
```

2. **retrieving** - 检索上下文
```json
{
  "stage": "retrieving",
  "content": "正在检索相关章节...\n检索到30个候选片段\nRerank后保留10个最相关片段",
  "progress": 0.4,
  "data": {
    "candidates": 30,
    "reranked": 10
  }
}
```

3. **generating** - 生成答案（流式）
```json
{
  "stage": "generating",
  "content": "萧炎在第3章《分别》中",
  "progress": 0.6,
  "data": {}
}
```

4. **validating** - Self-RAG验证
```json
{
  "stage": "validating",
  "content": "正在验证答案准确性...\n未发现矛盾\n置信度: 高",
  "progress": 0.9,
  "data": {
    "contradictions": 0,
    "confidence": "high"
  }
}
```

5. **complete** - 完成
```json
{
  "stage": "complete",
  "content": "",
  "progress": 1.0,
  "data": {
    "query_id": 123,
    "confidence": "high",
    "response_time": 2.35,
    "token_stats": {
      "total_tokens": 3580
    }
  }
}
```

6. **error** - 错误
```json
{
  "stage": "error",
  "content": "查询失败：超时",
  "progress": 0,
  "data": {
    "error": "Request timeout after 30s"
  }
}
```

---

## 数据模型

### 枚举类型

#### IndexStatus - 索引状态
- `pending` - 等待处理
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 失败

#### FileFormat - 文件格式
- `txt` - 纯文本
- `epub` - EPUB电子书

#### Confidence - 置信度
- `high` - 高
- `medium` - 中
- `low` - 低

#### QueryStage - 查询阶段
- `understanding` - 理解阶段
- `retrieving` - 检索阶段
- `generating` - 生成阶段
- `validating` - 验证阶段
- `complete` - 完成
- `error` - 错误

---

## 错误处理

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "detail": "小说ID=999不存在",
  "error_code": "NOVEL_NOT_FOUND"
}
```

### 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `NOVEL_NOT_FOUND` | 小说不存在 | 检查小说ID |
| `INVALID_FILE_FORMAT` | 不支持的文件格式 | 仅支持TXT/EPUB |
| `INDEXING_IN_PROGRESS` | 索引进行中 | 等待索引完成 |
| `API_KEY_INVALID` | API密钥无效 | 检查智谱AI密钥 |
| `TOKEN_LIMIT_EXCEEDED` | Token超限 | 减少上下文长度 |

---

## 使用示例

### Python示例

```python
import requests

# 1. 上传小说
with open('novel.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/novels/upload',
        files={'file': f},
        data={'title': '斗破苍穹', 'author': '天蚕土豆'}
    )
    novel = response.json()
    novel_id = novel['id']

# 2. 查询
response = requests.post(
    'http://localhost:8000/api/query',
    json={
        'novel_id': novel_id,
        'query': '萧炎在什么时候恢复斗之气的？',
        'model': 'GLM-4.5-Air'
    }
)
result = response.json()
print(result['answer'])
```

### JavaScript示例

```javascript
// 1. WebSocket流式查询
const ws = new WebSocket('ws://localhost:8000/api/query/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    novel_id: 1,
    query: '萧炎在什么时候恢复斗之气的？',
    model: 'GLM-4.5-Air'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`[${message.stage}] ${message.content}`);
  
  if (message.stage === 'complete') {
    console.log('查询完成:', message.data);
    ws.close();
  }
};
```

### cURL示例

```bash
# 1. 健康检查
curl http://localhost:8000/api/health

# 2. 获取小说列表
curl http://localhost:8000/api/novels

# 3. 查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": 1,
    "query": "萧炎在什么时候恢复斗之气的？",
    "model": "GLM-4.5-Air"
  }'
```

---

## 性能指标

### 响应时间

| 操作 | 平均响应时间 | 备注 |
|------|-------------|------|
| 健康检查 | < 10ms | - |
| 小说上传 | < 500ms | 不含索引时间 |
| 小说索引 | 5-30分钟 | 取决于小说长度 |
| 非流式查询 | 2-5秒 | 取决于模型和复杂度 |
| 流式查询首字 | < 1秒 | WebSocket |
| 图谱加载 | < 500ms | 缓存后更快 |

### 并发限制

- 查询并发: 10/秒
- 上传并发: 2/秒
- WebSocket连接: 100个

---

## 版本历史

### v0.1.0 (2025-11-17)
- ✅ 初始版本发布
- ✅ 支持TXT/EPUB上传
- ✅ 智能问答（RAG + GraphRAG + Self-RAG）
- ✅ 知识图谱可视化
- ✅ WebSocket流式问答
- ✅ 用户反馈和历史查询

---

## 相关文档

- [OpenAPI规范](./openapi.yaml)
- [用户指南](./user-guide.md)
- [开发文档](./development.md)
- [部署文档](./deployment.md)
- [查询参数配置](./查询阶段可配置参数说明.md)

---

**文档维护**: AI Assistant  
**最后更新**: 2025-11-17  
**许可证**: MIT

