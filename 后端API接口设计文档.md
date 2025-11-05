# 小说 RAG 分析系统 - 后端 API 接口设计文档

## 📋 文档概述

本文档详细说明了小说 RAG 分析系统后端 API 的设计规范，完整覆盖前端所有功能需求。

- **API 版本**：v1.0.0（简化版）
- **规范标准**：OpenAPI 3.0.3
- **认证方式**：无（MVP阶段匿名访问）
- **数据格式**：JSON
- **字符编码**：UTF-8

---

## 🎯 设计原则

### 1. RESTful 架构

- 使用标准 HTTP 方法（GET、POST、PUT、DELETE）
- 资源路径清晰、语义化
- 返回标准 HTTP 状态码

### 2. 数据校验优先

后端对所有输入数据进行严格校验：

- **文件格式验证**：仅支持 TXT 格式
- **编码检测**：自动检测 UTF-8、GBK、GB2312
- **内容验证**：
  - 中文字符占比 ≥ 60%
  - 最少字数 ≥ 1000
  - 文件大小 ≤ 50MB
- **业务验证**：章节识别、去重、合法性检查

### 3. 异步处理

耗时操作（文件上传、向量化、关系图谱生成）采用异步模式：

1. 接口立即返回小说 ID（HTTP 202）
2. 客户端轮询 `/novels/{novelId}/status` 查询进度
3. 任务完成后返回结果

### 4. 简化安全机制（MVP阶段）

- 无用户认证，匿名访问
- 基础速率限制
- 文件大小限制
- 基础错误处理

### 5. 错误处理

统一错误响应格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "用户友好的错误描述",
    "details": "详细技术信息（可选）",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

---

## 📚 核心功能模块（MVP简化版）

**API概览**：
```
/api/v1/
├── novels/
│   ├── GET    /           # 获取小说列表
│   ├── POST   /           # 创建小说记录
│   ├── GET    /{id}       # 获取小说详情
│   ├── PUT    /{id}       # 更新小说信息
│   ├── DELETE /{id}       # 删除小说
│   ├── POST   /{id}/upload # 上传文件
│   └── GET    /{id}/status # 获取处理状态
├── search/
│   └── POST   /           # 搜索问答
├── graph/
│   ├── GET    /novels/{id} # 获取人物关系图谱
│   └── POST   /novels/{id} # 生成图谱（异步）
├── chapters/
│   └── GET    /novels/{id}/chapters # 获取章节列表
└── system/
    └── GET    /health     # 健康检查
```

**说明**：MVP阶段采用匿名访问，无需认证机制，专注于核心功能实现。

### 1. 小说管理（Novels）

#### 1.1 小说 CRUD

| 接口 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/v1/novels` | GET | 获取小说列表 | page, pageSize, sortBy, search, tags |
| `/api/v1/novels` | POST | 创建小说记录 | title, author, description, tags |
| `/api/v1/novels/{novelId}` | GET | 获取小说详情 | - |
| `/api/v1/novels/{novelId}` | PUT | 更新小说信息 | title, author, description, tags |
| `/api/v1/novels/{novelId}` | DELETE | 删除小说 | - |

#### 1.2 小说列表响应示例

```json
{
  "data": [
    {
      "id": "novel_abc123",
      "title": "斗破苍穹",
      "author": "天蚕土豆",
      "description": "这是一部玄幻小说...",
      "tags": ["玄幻", "修仙", "热血"],
      "wordCount": 1250000,
      "chapterCount": 450,
      "status": "completed",
      "importedAt": "2024-01-01T12:00:00Z",
      "updatedAt": "2024-01-02T15:30:00Z",
      "hasGraph": true
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 15,
    "totalPages": 1
  }
}
```

#### 1.3 小说状态说明

| 状态 | 说明 |
|------|------|
| `pending` | 已创建记录，等待上传文件 |
| `processing` | 文件上传成功，正在处理中 |
| `completed` | 处理完成，可正常使用 |
| `failed` | 处理失败 |

---

### 2. 文本处理（Text Processing）

#### 2.1 文件上传与处理

**接口**：`POST /api/v1/novels/{novelId}/upload`

**处理流程**：

```
1. 文件上传（multipart/form-data）
   ↓
2. 格式和大小验证
   ↓
3. 编码检测和转换（UTF-8/GBK/GB2312）
   ↓
4. 内容验证（中文占比、字数）
   ↓
5. 章节自动识别
   ↓
6. 文本分段和清洗
   ↓
7. 向量化和索引构建
   ↓
8. 完成（状态更新为 completed）
```

**请求示例**：

```bash
curl -X POST https://api.novel-rag.com/api/v1/novels/novel_123/upload \
  -F "file=@斗破苍穹.txt" \
  -F "autoDetectChapters=true"
```

**响应示例**（HTTP 202）：

```json
{
  "message": "文件上传成功，正在处理中",
  "novelId": "novel_123",
  "status": "processing",
  "estimatedTime": 120
}
```

#### 2.2 文件验证规则

| 验证项 | 规则 | 错误代码 |
|--------|------|----------|
| 文件格式 | 必须为 `.txt` | `INVALID_FILE_FORMAT` |
| 文件大小 | ≤ 50MB | `FILE_TOO_LARGE` |
| 编码格式 | UTF-8/GBK/GB2312 | `INVALID_ENCODING` |
| 中文占比 | ≥ 60% | `INVALID_CONTENT` |
| 最少字数 | ≥ 1000 字 | `CONTENT_TOO_SHORT` |

#### 2.3 验证接口（预检查）

**接口**：`POST /api/v1/novels/{novelId}/validate`

用于上传前快速验证文件是否合格，返回：

```json
{
  "valid": true,
  "encoding": "UTF-8",
  "wordCount": 1250000,
  "chineseRatio": 0.92,
  "estimatedChapters": 450,
  "warnings": ["检测到部分非标准章节标题"],
  "errors": []
}
```

#### 2.4 处理状态查询

**接口**：`GET /api/v1/novels/{novelId}/status`

**状态说明**：

| 状态 | 说明 | 前端行为 |
|------|------|----------|
| `pending` | 已创建记录，等待上传文件 | 显示"待上传" |
| `processing` | 正在处理文件 | 显示进度条（progress: 0-100） |
| `completed` | 处理完成，可正常使用 | 显示"完成" |
| `failed` | 处理失败 | 显示错误信息，允许重试 |

**响应示例**：

```json
{
  "novelId": "novel_abc123",
  "status": "processing",
  "progress": 65,
  "message": "正在构建向量索引...",
  "stage": "vectorizing",  // uploading, detecting_chapters, vectorizing, completed
  "processedWords": 812500,
  "totalWords": 1250000,
  "estimatedTimeRemaining": 45,
  "updatedAt": "2024-01-01T12:02:30Z"
}
```

---

### 3. 章节管理（Chapters）

#### 3.1 章节相关接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/novels/{novelId}/chapters` | GET | 获取章节列表 |
| `/api/v1/novels/{novelId}/chapters` | POST | 手动添加章节 |
| `/api/v1/novels/{novelId}/chapters/{chapterId}` | GET | 获取章节内容 |
| `/api/v1/novels/{novelId}/chapters/{chapterId}` | PUT | 更新章节信息 |
| `/api/v1/novels/{novelId}/chapters/{chapterId}` | DELETE | 删除章节 |
| `/api/v1/novels/{novelId}/chapters/redetect` | POST | 重新识别章节 |

#### 3.2 章节数据结构

```json
{
  "id": "chapter_123",
  "novelId": "novel_abc123",
  "chapterNumber": 1,
  "title": "第一章 初入江湖",
  "startPosition": 0,
  "endPosition": 5230,
  "wordCount": 5230
}
```

#### 3.3 章节自动识别

**支持的章节格式**：

- `第X章`、`第X回`
- `第X节`、`第X话`
- `Chapter X`、`章节 X`
- 支持标题后带名称：`第一章 开端`

**正则表达式示例**：

```regex
第[零一二三四五六七八九十百千万\d]+[章回节话]
Chapter\s+\d+
```

**自定义章节识别**：

```bash
# 请求
POST /api/v1/novels/novel_123/chapters/redetect
{
  "chapterPattern": "第[\\d]+章",
  "clearExisting": true
}

# 响应（HTTP 202）
{
  "message": "章节重新识别任务已启动"
}
```

#### 3.4 获取章节内容

**接口**：`GET /api/v1/novels/{novelId}/chapters/{chapterId}`

**响应示例**：

```json
{
  "chapter": {
    "id": "chapter_123",
    "novelId": "novel_abc123",
    "chapterNumber": 1,
    "title": "第一章 初入江湖",
    "startPosition": 0,
    "endPosition": 5230,
    "wordCount": 5230
  },
  "content": "章节完整文本内容...",
  "paragraphs": [
    {
      "index": 0,
      "content": "第一段内容...",
      "startPosition": 0
    },
    {
      "index": 1,
      "content": "第二段内容...",
      "startPosition": 120
    }
  ]
}
```

---

### 4. RAG 搜索与问答（RAG Search）

#### 4.1 智能搜索接口

**接口**：`POST /api/v1/search`

**核心功能**：

1. 自然语言问题理解
2. 语义相似度检索（向量搜索）
3. 多文档联合检索
4. 基于 LLM 的答案生成
5. 原文引用和定位

**请求示例**：

```json
{
  "query": "萧炎的师父是谁？",
  "novelIds": ["novel_123"],
  "topK": 5,
  "includeReferences": true
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `query` | string | ✅ | 搜索问题 | - |
| `novelIds` | array | ❌ | 搜索范围（空=全部） | [] |
| `topK` | integer | ❌ | 返回结果数 | 5 |
| `includeReferences` | boolean | ❌ | 是否包含引用 | true |

**响应示例**：

```json
{
  "query": "萧炎的师父是谁？",
  "answer": "萧炎的师父是药尘，原名药尊者，曾是丹塔巨头之一...",
  "confidence": 0.92,
  "references": [
    {
      "novelId": "novel_123",
      "novelTitle": "斗破苍穹",
      "chapterId": "chapter_15",
      "chapterTitle": "第十五章 拜师",
      "chapterNumber": 15,
      "paragraphIndex": 3,
      "content": "\"老师，徒儿拜见！\" 萧炎恭恭敬敬地对着药尘行了一礼。",
      "relevanceScore": 0.89,
      "startPosition": 1250,
      "highlightText": "药尘"
    }
  ],
  "relatedQuestions": [
    "药尘是如何成为萧炎师父的？",
    "萧炎还有其他师父吗？"
  ],
  "searchTime": 245.6
}
```

#### 4.2 RAG 处理流程

```
用户问题
   ↓
1. 问题理解（意图识别）
   ↓
2. 问题向量化（Embedding）
   ↓
3. 向量相似度检索（从指定小说）
   ↓
4. 召回 Top-K 相关段落
   ↓
5. 重排序（Rerank）
   ↓
6. 构建 Prompt（问题 + 上下文）
   ↓
7. LLM 生成答案
   ↓
8. 答案后处理（格式化、引用标注）
   ↓
返回结果
```

---

### 5. 人物关系图谱（Character Graph）

#### 5.1 图谱相关接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/novels/{novelId}/graph` | GET | 获取关系图谱 |
| `/api/v1/novels/{novelId}/graph` | POST | 生成关系图谱 |
| `/api/v1/novels/{novelId}/graph` | DELETE | 删除关系图谱 |
| `/api/v1/novels/{novelId}/characters` | GET | 获取人物列表 |
| `/api/v1/novels/{novelId}/characters/{characterId}` | GET | 获取人物详情 |

#### 5.2 生成关系图谱

**接口**：`POST /api/v1/novels/{novelId}/graph`

**处理流程**：

```
1. 命名实体识别（NER）
   ↓
2. 人物筛选（去重、合并别名）
   ↓
3. 出场统计（频次、位置）
   ↓
4. 关系抽取（基于规则 + 模型）
   ↓
5. 关系强度计算
   ↓
6. 图谱构建
   ↓
完成
```

**请求示例**：

```json
{
  "minAppearances": 5,
  "maxCharacters": 50,
  "includeMinorRelationships": false
}
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `minAppearances` | 最少出场次数（过滤次要角色） | 5 |
| `maxCharacters` | 最多保留人物数 | 50 |
| `includeMinorRelationships` | 是否包含次要关系 | false |

**响应**（HTTP 202）：

```json
{
  "message": "人物关系图谱生成任务已启动",
  "taskId": "task_graph_123",
  "estimatedTime": 300
}
```

#### 5.3 图谱数据结构

**完整图谱**：

```json
{
  "id": "graph_123",
  "novelId": "novel_abc123",
  "characters": [
    {
      "id": "char_123",
      "name": "萧炎",
      "aliases": ["炎帝", "萧门门主"],
      "role": "protagonist",
      "description": "主角，修炼斗气，逆天崛起...",
      "appearances": 856,
      "importance": 1.0,
      "firstAppearance": {
        "chapterId": "chapter_1",
        "chapterTitle": "第一章 落魄天才"
      },
      "attributes": {
        "gender": "男",
        "faction": "萧家",
        "level": "斗帝"
      }
    }
  ],
  "relationships": [
    {
      "id": "rel_123",
      "source": "char_456",
      "target": "char_123",
      "type": "master-disciple",
      "description": "师徒关系，药尘是萧炎的师父",
      "strength": 9.5,
      "evidence": [
        {
          "chapterId": "chapter_15",
          "context": "\"老师，徒儿拜见！\"..."
        }
      ]
    }
  ],
  "generatedAt": "2024-01-01T12:00:00Z",
  "version": "1.0"
}
```

#### 5.4 关系类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `family` | 家族/亲属关系 | 父子、兄弟 |
| `friend` | 朋友 | 挚友、好友 |
| `enemy` | 敌人 | 仇敌、对手 |
| `master-disciple` | 师徒 | 师父、徒弟 |
| `lover` | 情侣/配偶 | 恋人、夫妻 |
| `ally` | 盟友 | 战友、合作者 |
| `rival` | 竞争对手 | 同门、竞争者 |

#### 5.5 人物详情

**接口**：`GET /api/v1/novels/{novelId}/characters/{characterId}`

**响应**：

```json
{
  "character": {
    "id": "char_123",
    "name": "萧炎",
    "aliases": ["炎帝"],
    "role": "protagonist",
    "appearances": 856,
    "importance": 1.0
  },
  "relationships": [
    {
      "id": "rel_123",
      "source": "char_456",
      "target": "char_123",
      "type": "master-disciple",
      "strength": 9.5
    }
  ],
  "appearances": [
    {
      "chapterId": "chapter_1",
      "chapterTitle": "第一章 落魄天才",
      "context": "少年萧炎站在..."
    }
  ],
  "relatedCharacters": [
    {
      "id": "char_456",
      "name": "药尘",
      "relationshipType": "master-disciple"
    }
  ]
}
```

---

### 6. 系统管理（System）

#### 6.1 系统接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/system/info` | GET | 系统信息 |

#### 6.2 健康检查

**接口**：`GET /api/v1/health`

**响应示例**：

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": {
      "status": "healthy",
      "responseTime": 12
    },
    "redis": {
      "status": "healthy",
      "responseTime": 5
    },
    "qdrant": {
      "status": "healthy",
      "responseTime": 23,
      "collections": 2
    },
    "zhipu_api": {
      "status": "healthy",
      "responseTime": 156
    }
  }
}
```

#### 6.3 系统信息

**接口**：`GET /api/v1/system/info`

**响应示例**：

```json
{
  "system": {
    "name": "小说RAG分析系统",
    "version": "1.0.0",
    "environment": "development"
  },
  "limits": {
    "maxFileSize": 52428800,
    "supportedFormats": ["txt"],
    "maxNovels": 100,
    "maxWordCount": 5000000
  },
  "features": {
    "search": true,
    "graph": true,
    "upload": true,
    "multiNovel": true
  }
}
```

---

## 🚦 简化速率限制（MVP阶段）

### 基础限流规则

| 接口类型 | 限制 | 时间窗口 |
|----------|------|----------|
| 普通接口 | 60 次 | 1 分钟 |
| 文件上传 | 5 次 | 1 分钟 |
| RAG 问答 | 15 次 | 1 分钟 |
| 图谱生成 | 3 次 | 1 分钟 |

### 限流响应

**HTTP 429 Too Many Requests**：

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁，请稍后再试",
    "retryAfter": 60
  }
}
```

**说明**：MVP阶段采用简单的IP级别限流，无需复杂的用户级限流。

---

## ❌ 错误码参考

### 通用错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| `BAD_REQUEST` | 400 | 请求参数错误 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `CONFLICT` | 409 | 资源冲突 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求过于频繁 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

### 业务错误码

#### 文件上传相关

| 错误码 | 说明 |
|--------|------|
| `INVALID_FILE_FORMAT` | 文件格式不正确 |
| `FILE_TOO_LARGE` | 文件大小超过限制 |
| `INVALID_ENCODING` | 无法识别文件编码 |
| `INVALID_CONTENT` | 文件内容不符合要求 |
| `CONTENT_TOO_SHORT` | 文本内容过短 |

#### 小说相关

| 错误码 | 说明 |
|--------|------|
| `NOVEL_NOT_FOUND` | 小说不存在 |
| `NOVEL_NOT_READY` | 小说处理未完成 |
| `SYSTEM_LIMIT_EXCEEDED` | 超过系统限制 |

#### 搜索相关

| 错误码 | 说明 |
|--------|------|
| `QUERY_TOO_SHORT` | 查询关键词过短 |
| `QUERY_TOO_LONG` | 查询关键词过长 |
| `NO_RESULTS_FOUND` | 未找到相关结果 |

#### 关系图谱相关

| 错误码 | 说明 |
|--------|------|
| `GRAPH_NOT_FOUND` | 关系图谱不存在 |
| `GRAPH_GENERATING` | 关系图谱生成中 |
| `GRAPH_GENERATION_FAILED` | 关系图谱生成失败 |

---

## 📊 数据模型说明

### 小说（Novel）

```typescript
interface Novel {
  id: string;              // 唯一标识符
  title: string;           // 书名
  author: string;          // 作者
  description: string;     // 简介
  tags: string[];          // 标签
  wordCount: number;       // 总字数
  chapterCount: number;    // 章节数
  status: 'pending' | 'processing' | 'completed' | 'failed';
  importedAt: string;      // 导入时间（ISO 8601）
  updatedAt: string;       // 更新时间
  hasGraph: boolean;       // 是否已生成关系图谱
}
```

### 章节（Chapter）

```typescript
interface Chapter {
  id: string;              // 章节标识符
  novelId: string;         // 所属小说ID
  chapterNumber: number;   // 章节序号
  title: string;           // 章节标题
  startPosition: number;   // 起始位置
  endPosition: number;     // 结束位置
  wordCount: number;       // 章节字数
}
```

### 搜索引用（SearchReference）

```typescript
interface SearchReference {
  novelId: string;         // 来源小说ID
  novelTitle: string;      // 来源小说标题
  chapterId: string;       // 来源章节ID
  chapterTitle: string;    // 来源章节标题
  chapterNumber: number;   // 章节序号
  paragraphIndex: number;  // 段落索引
  content: string;         // 原文内容片段
  relevanceScore: number;  // 相关度评分（0-1）
  startPosition: number;   // 段落在章节中的起始位置
  highlightText: string;   // 高亮文本
}
```

### 人物（Character）

```typescript
interface Character {
  id: string;              // 人物标识符
  name: string;            // 姓名
  aliases: string[];       // 别名/称号
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  description: string;     // 人物描述
  appearances: number;     // 出场次数
  importance: number;      // 重要程度（0-1）
  firstAppearance: {       // 首次出场
    chapterId: string;
    chapterTitle: string;
  };
  attributes: Record<string, any>; // 自定义属性
}
```

### 关系（Relationship）

```typescript
interface Relationship {
  id: string;              // 关系标识符
  source: string;          // 源人物ID
  target: string;          // 目标人物ID
  type: 'family' | 'friend' | 'enemy' | 'master-disciple' | 'lover' | 'ally' | 'rival';
  description: string;     // 关系描述
  strength: number;        // 关系强度（0-10）
  evidence: Array<{        // 关系证据
    chapterId: string;
    context: string;
  }>;
}
```

---

## 🔄 前后端交互流程

### 流程1：导入小说（简化版）

```
前端                             后端
  |                               |
  | POST /novels                  |
  |------------------------------>|
  |                               | 创建小说记录
  |<------------------------------|
  | 201 Created (novel_123)       |
  |                               |
  | POST /novels/novel_123/upload |
  |------------------------------>|
  |                               | 验证文件
  |                               | 启动后台处理
  |<------------------------------|
  | 202 Accepted                   |
  |                               |
  | 轮询 GET /novels/novel_123/status|
  |------------------------------>|
  |<------------------------------|
  | { status: "processing", progress: 30% }
  |                               |
  | 轮询 GET /novels/novel_123/status|
  |------------------------------>|
  |<------------------------------|
  | { status: "completed" }       |
  |                               |
  | GET /novels/novel_123         |
  |------------------------------>|
  |<------------------------------|
  | 小说详情（含章节列表）          |
```

### 流程2：RAG 搜索

```
前端                             后端
  |                               |
  | POST /search                  |
  | {                             |
  |   query: "萧炎的师父是谁？",  |
  |   novelIds: ["novel_123"]     |
  | }                             |
  |------------------------------>|
  |                               | 1. 问题向量化
  |                               | 2. 向量检索
  |                               | 3. 重排序
  |                               | 4. LLM 生成答案
  |<------------------------------|
  | {                             |
  |   answer: "萧炎的师父是药尘...",|
  |   references: [...]           |
  | }                             |
```

### 流程3：生成关系图谱（简化版）

```
前端                             后端
  |                               |
  | POST /novels/novel_123/graph  |
  |------------------------------>|
  |                               | 启动图谱生成任务
  |<------------------------------|
  | 202 Accepted                   |
  |                               |
  | 轮询 GET /novels/novel_123/status|
  |------------------------------>|
  |<------------------------------|
  | { status: "processing", stage: "graph_generation" }
  |                               |
  | 轮询（完成后）                  |
  |------------------------------>|
  |<------------------------------|
  | { status: "completed", hasGraph: true }
  |                               |
  | GET /novels/novel_123/graph   |
  |------------------------------>|
  |<------------------------------|
  | 完整关系图谱数据                |
```

---

## 🛠️ 简化技术实现建议（MVP版本）

### 核心技术栈（按后端技术文档）

#### 后端框架
- **Python 3.10+**：FastAPI（异步高性能，自动文档）

#### 数据库
- **主数据库**：SQLite（零配置，适合MVP）
- **向量数据库**：Qdrant（轻量级，易部署）
- **缓存**：Redis（基础缓存）

#### RAG 相关
- **Embedding 模型**：智谱 Embedding-3（与LLM配套）
- **LLM 模型**：智谱 GLM-4.6（中文优化，性价比高）
- **RAG 框架**：简化版 LangChain（仅核心功能）

#### 文本处理
- **编码检测**：chardet
- **中文分词**：jieba
- **章节识别**：正则表达式 + 启发式规则

#### 异步处理
- **后台任务**：FastAPI BackgroundTasks（无需Celery）

#### 部署和运维
- **容器化**：Docker + Docker Compose
- **监控**：基础健康检查
- **日志**：Loguru

#### 跨域配置（CORS）
- **开发环境**：允许本地开发服务器跨域访问
- **生产环境**：需要配置具体的域名白名单
- **配置方式**：FastAPI CORSMiddleware

**CORS 配置示例**：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发服务器
        "http://localhost:3000",  # 备用开发端口
        # 生产环境需要添加实际域名
        # "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### MVP vs 完整版对比

| 组件 | MVP版本 | 完整版本 |
|------|---------|----------|
| 数据库 | SQLite | PostgreSQL |
| 用户系统 | ❌ 简化无认证 | ✅ JWT + 用户管理 |
| 任务队列 | BackgroundTasks | Celery + Redis |
| 监控系统 | 基础健康检查 | Prometheus + Grafana |
| 缓存策略 | Redis基础缓存 | 多级缓存策略 |
| 部署复杂度 | ⭐⭐ 简单 | ⭐⭐⭐⭐ 复杂 |

---

## 📖 简化API使用示例（MVP版本）

### 基础流程示例（Python）

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# 1. 创建小说记录（无需认证）
response = requests.post(f"{BASE_URL}/api/v1/novels", json={
    "title": "斗破苍穹",
    "author": "天蚕土豆",
    "tags": ["玄幻", "修仙"]
})
novel_id = response.json()["id"]

# 2. 上传文件
with open("斗破苍穹.txt", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/novels/{novel_id}/upload",
        files=files
    )

# 3. 轮询处理状态
while True:
    response = requests.get(f"{BASE_URL}/novels/{novel_id}/status")
    status = response.json()["status"]
    if status == "completed":
        print("处理完成！")
        break
    elif status == "failed":
        print("处理失败！")
        break
    print(f"处理中... {response.json()['progress']}%")
    time.sleep(2)

# 4. RAG 搜索
response = requests.post(f"{BASE_URL}/search", json={
    "query": "萧炎的师父是谁？",
    "novelIds": [novel_id],
    "topK": 5
})
answer = response.json()["answer"]
print(f"答案：{answer}")

# 5. 生成关系图谱
response = requests.post(f"{BASE_URL}/novels/{novel_id}/graph", json={
    "minAppearances": 5
})
# 等待生成完成后获取结果...
```

---

**总结**：本API设计文档基于简化的MVP架构，移除了复杂的用户认证和任务管理系统，专注于核心RAG功能的实现，适合快速原型开发和验证。
  api:
    image: novel-rag-api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/novel_rag
      - REDIS_URL=redis://redis:6379
      - MILVUS_HOST=milvus
    depends_on:
      - db
      - redis
      - milvus

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: novel_rag
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"

volumes:
  postgres_data:
```

---

## 📞 联系方式

- **API 文档**：https://api.novel-rag.com/docs
- **技术支持**：support@novel-rag.com
- **GitHub**：https://github.com/your-org/novel-rag

---

## 📄 附录

### A. OpenAPI 规范文件

完整的 OpenAPI 3.0 规范文件：`backend_api_specification.yaml`

可用于：
- Swagger UI 可视化
- Postman 导入测试
- 自动生成客户端 SDK
- API 文档生成

### B. 相关文档

- [小说RAG系统需求文档](./小说RAG系统需求文档.md)
- [Web前端开发需求文档](./web前端开发需求文档.md)
- [前端 README](./frontend/README.md)

---

<div align="center">

**小说 RAG 分析系统后端 API 设计文档**

v1.0.0 | 2024

</div>

