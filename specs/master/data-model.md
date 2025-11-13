# Data Model: 网络小说智能问答系统

**Created:** 2025-11-13  
**Phase:** Phase 1 - 设计与合约  
**Status:** Complete

## 目录

1. [概述](#概述)
2. [SQLite元数据库](#sqlite元数据库)
3. [ChromaDB向量库](#chromadb向量库)
4. [NetworkX知识图谱](#networkx知识图谱)
5. [业务实体模型](#业务实体模型)
6. [数据流转](#数据流转)

---

## 概述

系统采用**多数据源架构**，不同类型的数据存储在最适合的数据库中：

| 数据类型 | 存储方案 | 用途 |
|---------|----------|------|
| **结构化元数据** | SQLite | 小说信息、章节索引、用户反馈 |
| **向量数据** | ChromaDB | 文本嵌入、语义检索 |
| **图数据** | NetworkX (Pickle) | 角色关系、时序演变 |
| **原始文件** | 本地文件系统 | 小说原文（TXT/EPUB） |

---

## SQLite元数据库

### 数据库文件

**路径：** `backend/data/sqlite/metadata.db`

### 表结构

#### 1. novels（小说表）

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    total_chars INTEGER NOT NULL,
    total_chapters INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_date TIMESTAMP,
    index_status TEXT NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
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

CREATE INDEX idx_novels_status ON novels(index_status);
CREATE INDEX idx_novels_title ON novels(title);
```

**字段说明：**
- `index_status`: 索引状态，控制UI显示
- `index_progress`: 进度百分比，用于进度条
- `embedding_tokens`: 索引构建时Embedding-3消耗的tokens

#### 2. chapters（章节表）

```sql
CREATE TABLE chapters (
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

CREATE INDEX idx_chapters_novel ON chapters(novel_id);
CREATE INDEX idx_chapters_num ON chapters(novel_id, chapter_num);
CREATE INDEX idx_chapters_importance ON chapters(importance_score DESC);
```

**字段说明：**
- `importance_score`: 章节重要性评分，用于GraphRAG检索权重
- `has_*`: 章节特征标记，用于诡计检测

#### 3. entities（实体表）

```sql
CREATE TABLE entities (
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

CREATE INDEX idx_entities_novel ON entities(novel_id);
CREATE INDEX idx_entities_type ON entities(novel_id, entity_type);
CREATE INDEX idx_entities_name ON entities(novel_id, entity_name);
```

#### 4. queries（查询记录表）

```sql
CREATE TABLE queries (
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

CREATE INDEX idx_queries_novel ON queries(novel_id);
CREATE INDEX idx_queries_date ON queries(created_at DESC);
CREATE INDEX idx_queries_feedback ON queries(user_feedback);
```

**字段说明：**
- `*_tokens`: 详细的Token消耗统计
- `confidence`: 系统对答案的置信度评分
- `contradiction_count`: 检测到的矛盾数量

#### 5. token_stats（Token统计汇总表）

```sql
CREATE TABLE token_stats (
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

CREATE INDEX idx_token_stats_date ON token_stats(created_at DESC);
CREATE INDEX idx_token_stats_model ON token_stats(model_name);
CREATE INDEX idx_token_stats_operation ON token_stats(operation_type, operation_id);
```

---

## ChromaDB向量库

### Collection结构

每本小说对应一个独立的Collection：

**Collection命名：** `novel_{novel_id}`

### 文档结构

```python
{
    "id": "novel_1_chapter_10_block_5",  # 唯一标识
    "embedding": [0.123, -0.456, ...],    # 1024维向量（Embedding-3）
    "document": "萧炎看着手中的...",      # 原文文本（500-600字符）
    "metadata": {
        "novel_id": 1,
        "chapter_num": 10,
        "chapter_title": "第十章 云岚宗",
        "block_num": 5,
        "char_start": 12000,
        "char_end": 12550,
        "entities": ["萧炎", "云韵", "云岚宗"],  # 包含的实体
        "importance": 0.75,  # 块重要性（基于章节重要性）
        "has_dialogue": true,  # 是否包含对话
        "has_action": false
    }
}
```

**索引配置：**
```python
collection = client.create_collection(
    name="novel_1",
    metadata={
        "hnsw:space": "cosine",      # 余弦相似度
        "hnsw:construction_ef": 200, # 构建时的ef参数
        "hnsw:M": 16                 # 每个节点的邻居数
    }
)
```

### 检索示例

```python
# 语义检索
results = collection.query(
    query_embeddings=[query_vector],
    n_results=30,
    where={"chapter_num": {"$gte": 1, "$lte": 100}},  # 章节范围过滤
    where_document={"$contains": "萧炎"}              # 文档内容过滤
)
```

---

## NetworkX知识图谱

### 文件存储

**路径：** `backend/data/graphs/novel_{novel_id}_graph.pkl`

### 图谱结构

#### 节点（Node）

```python
{
    "name": "萧炎",           # 节点ID（实体名称）
    "type": "character",     # 节点类型
    "attributes": {
        "first_chapter": 1,
        "last_chapter": 1600,
        "gender": "男",
        "faction": "主角方",
        "importance": 1.0,   # PageRank分数
        "is_protagonist": true
    }
}
```

**节点类型：**
- `character`: 角色
- `location`: 地点
- `organization`: 组织
- `item`: 关键物品

#### 边（Edge）

```python
{
    "source": "萧炎",
    "target": "药老",
    "relation_type": "师徒",
    "attributes": {
        "start_chapter": 3,
        "end_chapter": None,  # None表示持续到最后
        "strength": 0.9,      # 关系强度 0.0~1.0
        "evolution": [        # 关系演变轨迹
            {"chapter": 3, "type": "陌生"},
            {"chapter": 10, "type": "初识"},
            {"chapter": 50, "type": "师徒"},
            {"chapter": 200, "type": "亲密"}
        ],
        "is_public": false,   # 是否公开（用于识别隐藏关系）
        "reveal_chapter": 50  # 关系揭示章节
    }
}
```

**关系类型：**
- `盟友`, `敌对`, `中立`, `师徒`, `亲属`, `恋人`, `主仆`, `竞争`, `复杂`

### 图谱操作

#### 创建图谱

```python
import networkx as nx

G = nx.MultiDiGraph()

# 添加节点
G.add_node("萧炎", type="character", importance=1.0, first_chapter=1)
G.add_node("药老", type="character", importance=0.9, first_chapter=3)

# 添加边
G.add_edge("萧炎", "药老",
           relation_type="师徒",
           start_chapter=3,
           end_chapter=None,
           strength=0.9)
```

#### 时序查询

```python
def get_relationship_at_chapter(G, char1, char2, chapter):
    """查询特定章节的关系"""
    for u, v, key, data in G.edges(keys=True, data=True):
        if u == char1 and v == char2:
            if data['start_chapter'] <= chapter and \
               (data['end_chapter'] is None or data['end_chapter'] >= chapter):
                return data['relation_type']
    return None
```

#### 演变追踪

```python
def get_relationship_evolution(G, char1, char2):
    """获取关系演变历史"""
    for u, v, key, data in G.edges(keys=True, data=True):
        if u == char1 and v == char2:
            return data.get('evolution', [])
    return []
```

---

## 业务实体模型

### Pydantic模型（后端API）

#### NovelModel

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NovelCreate(BaseModel):
    """小说上传请求"""
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    file_format: str = Field(..., pattern="^(txt|epub)$")

class NovelResponse(BaseModel):
    """小说详情响应"""
    id: int
    title: str
    author: Optional[str]
    total_chars: int
    total_chapters: int
    index_status: str
    index_progress: float  # 0.0 ~ 1.0
    
    # 索引统计
    total_chunks: int
    total_entities: int
    total_relations: int
    embedding_tokens: int
    
    upload_date: datetime
    indexed_date: Optional[datetime]
    
    class Config:
        from_attributes = True
```

#### QueryModel

```python
class QueryRequest(BaseModel):
    """查询请求"""
    novel_id: int
    query: str = Field(..., min_length=1, max_length=1000)
    model: str = Field(default="glm-4", pattern="^(glm-4-flash|glm-4|glm-4-plus|glm-4-5|glm-4-6)$")

class Citation(BaseModel):
    """原文引用"""
    chapter_num: int
    chapter_title: Optional[str]
    text: str

class Contradiction(BaseModel):
    """矛盾检测结果"""
    type: str  # '时间线矛盾', '角色设定矛盾', '情节不一致'
    early_description: str
    early_chapter: int
    late_description: str
    late_chapter: int
    analysis: str
    confidence: str

class TokenStats(BaseModel):
    """Token统计"""
    total_tokens: int
    by_model: dict  # {model_name: {input_tokens, prompt_tokens, ...}}

class QueryResponse(BaseModel):
    """查询响应"""
    query_id: int
    answer: str
    citations: list[Citation]
    graph_info: Optional[dict]
    contradictions: list[Contradiction]
    token_stats: TokenStats
    response_time: float
    confidence: str  # 'high', 'medium', 'low'
    model: str
    timestamp: datetime
```

#### ChapterModel

```python
class ChapterListItem(BaseModel):
    """章节列表项"""
    num: int
    title: Optional[str]
    char_count: int

class ChapterContent(BaseModel):
    """章节内容"""
    chapter_num: int
    title: Optional[str]
    content: str
    prev_chapter: Optional[int]
    next_chapter: Optional[int]
    total_chapters: int
```

### TypeScript类型（前端）

```typescript
// types/novel.ts
export interface Novel {
  id: number;
  title: string;
  author?: string;
  totalChars: number;
  totalChapters: number;
  indexStatus: 'pending' | 'processing' | 'completed' | 'failed';
  indexProgress: number;  // 0-1
  
  totalChunks: number;
  totalEntities: number;
  totalRelations: number;
  embeddingTokens: number;
  
  uploadDate: string;
  indexedDate?: string;
}

// types/query.ts
export interface QueryRequest {
  novelId: number;
  query: string;
  model: 'glm-4-flash' | 'glm-4' | 'glm-4-plus' | 'glm-4-5' | 'glm-4-6';
}

export interface Citation {
  chapterNum: number;
  chapterTitle?: string;
  text: string;
}

export interface Contradiction {
  type: string;
  earlyDescription: string;
  earlyChapter: number;
  lateDescription: string;
  lateChapter: number;
  analysis: string;
  confidence: string;
}

export interface TokenStats {
  totalTokens: number;
  byModel: Record<string, {
    inputTokens?: number;
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  }>;
}

export interface QueryResponse {
  queryId: number;
  answer: string;
  citations: Citation[];
  graphInfo?: {
    entities: string[];
    relations: Array<{
      source: string;
      target: string;
      type: string;
    }>;
  };
  contradictions: Contradiction[];
  tokenStats: TokenStats;
  responseTime: number;
  confidence: 'high' | 'medium' | 'low';
  model: string;
  timestamp: string;
}

// types/chapter.ts
export interface Chapter {
  num: number;
  title?: string;
  charCount: number;
}

export interface ChapterContent {
  chapterNum: number;
  title?: string;
  content: string;
  prevChapter?: number;
  nextChapter?: number;
  totalChapters: number;
}
```

---

## 数据流转

### 小说上传流程

```
1. 用户上传文件（TXT/EPUB）
    ↓
2. FastAPI保存文件到 /data/uploads/
    ↓
3. 插入 novels 表（status='pending'）
    ↓
4. 后台任务开始处理：
    a. 文件解析 → 章节识别
    b. 插入 chapters 表
    c. 文本分块（RecursiveCharacterTextSplitter）
    d. 批量向量化（智谱Embedding-3）
    e. 保存到ChromaDB
    f. NER实体提取（HanLP）
    g. 插入 entities 表
    h. 构建知识图谱（NetworkX）
    i. 保存图谱pickle文件
    j. 更新 novels 表（status='completed'）
    ↓
5. WebSocket通知前端进度更新
```

### 查询流程

```
1. 前端发起WebSocket连接
    ↓
2. 阶段1：查询理解
    - HanLP提取实体
    - 智谱Embedding-3向量化
    ↓
3. 阶段2：双路检索
    - ChromaDB语义检索（Top-30）
    - NetworkX图谱检索
    - 混合Rerank（Top-10）
    ↓
4. 阶段3：LLM生成（流式）
    - 智谱GLM-4系列
    - 实时推送token
    ↓
5. 阶段4：Self-RAG验证
    - 断言提取
    - 多源证据收集
    - 矛盾检测
    ↓
6. 阶段5：结果汇总
    - 插入 queries 表
    - 插入 token_stats 表
    - 返回最终结果
    ↓
7. 前端展示答案和统计
```

---

## 数据备份策略

### 自动备份

```python
# backend/app/core/backup.py
import shutil
from pathlib import Path
from datetime import datetime

def backup_data():
    """每日自动备份"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"./data/backups/{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份SQLite
    shutil.copy("./data/sqlite/metadata.db", backup_dir / "metadata.db")
    
    # 备份ChromaDB
    shutil.copytree("./data/chromadb", backup_dir / "chromadb")
    
    # 备份图谱
    shutil.copytree("./data/graphs", backup_dir / "graphs")
    
    print(f"Backup completed: {backup_dir}")
```

### 手动导出

- **SQLite：** 使用 `sqlite3 .dump` 导出SQL
- **ChromaDB：** 已持久化到磁盘，直接复制目录
- **图谱：** Pickle文件，直接复制

---

## 总结

### 关键设计决策

✅ **多数据源：** SQLite（元数据） + ChromaDB（向量） + NetworkX（图谱）  
✅ **时序支持：** 章节重要性、关系演变轨迹  
✅ **统计详尽：** Token消耗、性能指标、用户反馈  
✅ **可扩展性：** 支持多本小说、历史查询、增量更新

### 下一步

进入API合约设计（contracts/），定义OpenAPI规范。

---

**文档完成日期：** 2025-11-13  
**相关文档：** research.md, plan.md

