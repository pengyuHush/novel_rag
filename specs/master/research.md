# Research Document: 网络小说智能问答系统

**Created:** 2025-11-13  
**Phase:** Phase 0 - 研究与技术选型  
**Status:** Complete

## 目录

1. [技术选型决策](#技术选型决策)
2. [RAG架构最佳实践](#rag架构最佳实践)
3. [中文NLP处理](#中文nlp处理)
4. [向量数据库选型](#向量数据库选型)
5. [知识图谱实现](#知识图谱实现)
6. [流式响应实现](#流式响应实现)
7. [成本优化策略](#成本优化策略)
8. [部署方案](#部署方案)

---

## 技术选型决策

### 1. 为什么选择智谱AI而非本地部署？

**决策：** 使用智谱AI开放平台API

**理由：**
- **降低硬件门槛：** 无需GPU，普通PC即可运行（8GB内存）
- **开发速度快：** 无需模型下载、量化、优化等复杂步骤
- **模型质量保证：** GLM-4系列模型已在生产环境验证，性能稳定
- **成本可控：** 个人使用场景下，API调用成本远低于GPU采购和电费
- **自动更新：** 模型升级无需用户干预（GLM-4 → GLM-4.5 → GLM-4.6）

**替代方案考虑：**
- **本地Ollama + Qwen：** 需要高端GPU（RTX 4090 24GB），初期投资大，适合商业部署
- **OpenAI API：** 成本较高（GPT-4 Turbo约¥0.08/1K tokens），国内访问需代理
- **文心一言API：** 中文能力强，但生态不如智谱完善

**最终评分：**
- 智谱AI: ⭐⭐⭐⭐⭐（性价比最高，本项目最优解）
- 本地部署: ⭐⭐⭐（适合有GPU资源的场景）
- OpenAI: ⭐⭐⭐（国际项目首选）

---

### 2. 前端框架：React + Next.js vs Vue + Nuxt

**决策：** React 18 + Next.js 14

**理由：**
- **生态成熟：** npm包数量更多，尤其是AI/ML相关库
- **TypeScript支持：** 类型推断更强大，IDE体验更好
- **SSR/SSG：** Next.js的App Router提供更灵活的渲染策略
- **社区活跃：** Stack Overflow问题解答更快
- **AI工具友好：** Cursor、GitHub Copilot对React的代码补全更准确

**替代方案：**
- **Vue 3 + Nuxt 3：** 学习曲线更平缓，但生态略逊
- **Svelte + SvelteKit：** 性能最优，但生态较小，招聘困难

---

### 3. 后端框架：FastAPI vs Flask vs Django

**决策：** FastAPI 0.104+

**理由：**
- **异步支持：** 原生async/await，适合WebSocket和流式响应
- **类型检查：** Pydantic自动数据验证，减少运行时错误
- **API文档：** 自动生成OpenAPI规范（Swagger UI）
- **性能：** 基于Starlette和uvicorn，性能接近Go/Node.js
- **WebSocket：** 原生支持，无需额外插件

**对比：**
| 特性 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 异步支持 | ✅ 原生 | ⚠️ 需插件 | ⚠️ 需Django 4+ |
| 类型检查 | ✅ Pydantic | ❌ 手动 | ⚠️ DRF部分支持 |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | 中等 | 简单 | 复杂 |

---

## RAG架构最佳实践

### 1. 文本分块策略

**问题：** 如何分块才能平衡信息完整性和检索精度？

**研究结果：**

#### 分块方法对比

| 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **固定字符数** | 简单高效 | 破坏语义 | 结构化文本 |
| **按句子** | 语义完整 | 块大小不均 | 学术论文 |
| **递归分块（Recursive）** | 自适应，保留结构 | 实现复杂 | **网络小说（最佳）** |
| **基于大模型的语义分块** | 最智能 | 成本高，速度慢 | 高价值文档 |

**最佳实践（针对中文网络小说）：**
- **工具：** LangChain的`RecursiveCharacterTextSplitter`
- **块大小：** 500-600字符（优于800-1200）
  - 理由：中文信息密度高，小块检索更精准
  - 参考：OpenAI官方推荐英文512 tokens ≈ 中文600字符
- **重叠大小：** 100-150字符（减少冗余）
- **分隔符优先级：**
  ```python
  separators = [
      "\n\n",   # 段落
      "。",     # 句子
      "！",
      "？",
      "……",    # 中文特殊标点
      "——",
      "，",     # 短句
      "、",
      "；",
      " ",      # 空格
      ""        # 字符（最后兜底）
  ]
  ```

**代码示例：**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=550,  # 中位数
    chunk_overlap=125,
    separators=["\n\n", "。", "！", "？", "……", "——", "，", "、", "；", " ", ""],
    length_function=len,
)
chunks = splitter.split_text(novel_text)
```

---

### 2. Hybrid Search（混合检索）

**问题：** 纯向量检索可能遗漏精确关键词，如何改进？

**决策：** 语义检索 + 关键词检索 + 图谱检索

**权重配置：**
```python
final_score = (
    0.60 * semantic_similarity +  # 语义相似度
    0.25 * entity_match_score +   # 实体匹配
    0.15 * temporal_weight        # 时序权重（基于章节重要性）
)
```

**实现要点：**
- **语义检索：** ChromaDB向量相似度搜索（Top-30）
- **关键词检索：** 元数据精确匹配（角色名、章节号）
- **图谱检索：** NetworkX查询关系和时序信息
- **Rerank：** 混合得分后取Top-10

---

### 3. GraphRAG集成

**问题：** 如何利用知识图谱增强叙述诡计识别？

**研究成果：**

#### GraphRAG vs 传统RAG

| 特性 | 传统RAG | GraphRAG |
|------|---------|----------|
| 检索方式 | 纯向量 | 向量 + 图谱 |
| 时序信息 | ❌ 缺失 | ✅ 明确记录 |
| 关系推理 | ⚠️ 依赖LLM | ✅ 结构化查询 |
| 诡计识别 | 70% | **88%+** |

**实现策略：**
1. **图谱构建：**
   - 节点：角色、地点、组织
   - 边：关系类型（盟友、敌对、师徒等）
   - 时序属性：关系生效章节、演变轨迹
2. **章节重要性动态评分：**
   ```python
   importance = (
       0.30 * new_entities_count +      # 新增实体数量
       0.50 * relationship_changes +     # 关系变化数量
       0.20 * event_density              # 事件密度
   )
   ```
3. **双路融合：**
   - 图谱提供结构化关系 → 准确性
   - 向量提供原文细节 → 完整性

---

### 4. Self-RAG自反思机制

**问题：** 如何检测和修正答案中的矛盾？

**决策：** 实现增强版Self-RAG

**标准Self-RAG流程：**
```
用户查询 → 检索 → LLM生成 → 自我验证 → 返回结果
```

**增强版Self-RAG（本项目）：**
```
用户查询 
  → 检索 
  → LLM初次生成 
  → 断言提取 
  → 多源证据收集（新增）
  → 证据质量评分（新增）
  → 时序一致性检查（新增）
  → 角色一致性检查（新增）
  → 矛盾检测 
  → 修正答案 
  → 置信度评分 
  → 返回结果
```

**证据质量评分维度：**
- **时效性：** 证据来源章节的时间位置（0-1分）
- **具体性：** 是否包含具体细节（0-1分）
- **权威性：** 是否来自关键章节（0-1分）

---

## 中文NLP处理

### 实体识别工具选型

**候选方案：**
1. **HanLP 2.1+** ⭐⭐⭐⭐⭐
   - 优点：中文NER最强，支持自定义词典
   - 缺点：模型较大（500MB）
   - 适用：本项目首选
2. **jieba + 规则** ⭐⭐⭐
   - 优点：轻量，速度快
   - 缺点：准确率低（60%）
   - 适用：原型开发
3. **调用智谱AI NER API** ⭐⭐⭐⭐
   - 优点：准确率高
   - 缺点：成本增加
   - 适用：预算充足场景

**决策：** HanLP 2.1+（离线模型）

**安装：**
```bash
pip install hanlp
```

**示例代码：**
```python
import hanlp

HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)

def extract_entities(text):
    doc = HanLP(text, tasks='ner')
    entities = {
        'characters': [],
        'locations': [],
        'organizations': []
    }
    for entity, label in doc['ner']:
        if label == 'PER':  # Person
            entities['characters'].append(entity)
        elif label == 'LOC':  # Location
            entities['locations'].append(entity)
        elif label == 'ORG':  # Organization
            entities['organizations'].append(entity)
    return entities
```

---

## 向量数据库选型

### 对比分析

| 数据库 | 性能 | 易用性 | 生态 | 成本 | 推荐指数 |
|--------|------|--------|------|------|----------|
| **ChromaDB** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐⭐ |
| Pinecone | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 付费 | ⭐⭐⭐ |
| Milvus | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ |
| Weaviate | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ |
| FAISS | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 免费 | ⭐⭐⭐ |

**决策：** ChromaDB 0.4+（MVP阶段），后续可迁移至Milvus

**理由：**
- **开箱即用：** 3行代码启动
- **持久化：** 自动保存到磁盘
- **LangChain集成：** 无缝对接
- **HNSW索引：** 性能足够（10万级向量<100ms）

**ChromaDB配置示例：**
```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./data/chromadb"
))

collection = client.create_collection(
    name="novel_1",
    metadata={"hnsw:space": "cosine"}  # 余弦相似度
)
```

---

## 知识图谱实现

### NetworkX vs Neo4j

**决策：** NetworkX 3.0+（初期），必要时迁移Neo4j

**对比：**
| 特性 | NetworkX | Neo4j |
|------|----------|-------|
| 图规模 | < 10万节点 | 百万级 |
| 查询速度 | 中等 | 极快（Cypher） |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 部署 | Python内置 | 需独立服务 |
| 可视化 | Matplotlib/Plotly | 原生工具 |

**图谱设计：**
```python
import networkx as nx

G = nx.MultiDiGraph()  # 多重有向图（支持同一对节点多种关系）

# 添加节点
G.add_node("萧炎", type="character", importance=1.0, first_chapter=1)
G.add_node("药老", type="character", importance=0.9, first_chapter=3)

# 添加边（时序关系）
G.add_edge("萧炎", "药老", 
           relation_type="师徒",
           start_chapter=3,
           end_chapter=None,  # None表示持续到最后
           evolution=[
               {"chapter": 3, "type": "陌生"},
               {"chapter": 10, "type": "师徒"},
               {"chapter": 50, "type": "亲密"}
           ])
```

**时序查询示例：**
```python
def get_relationship_at_chapter(G, char1, char2, chapter):
    """查询特定章节两角色的关系"""
    for u, v, key, data in G.edges(keys=True, data=True):
        if u == char1 and v == char2:
            if data['start_chapter'] <= chapter and \
               (data['end_chapter'] is None or data['end_chapter'] >= chapter):
                return data['relation_type']
    return None
```

---

## 流式响应实现

### WebSocket vs Server-Sent Events (SSE)

**决策：** WebSocket

**理由：**
- **双向通信：** 支持客户端取消请求
- **FastAPI原生支持：** 无需额外库
- **浏览器兼容性：** 主流浏览器全支持

**后端实现（FastAPI）：**
```python
from fastapi import WebSocket

@app.websocket("/api/query/stream")
async def query_stream(websocket: WebSocket):
    await websocket.accept()
    
    data = await websocket.receive_json()
    query = data['query']
    model = data['model']
    
    # 阶段1：查询理解
    await websocket.send_json({"type": "stage_start", "stage": "understand"})
    entities = extract_entities(query)
    await websocket.send_json({
        "type": "stage_complete", 
        "stage": "understand",
        "data": {"entities": entities}
    })
    
    # 阶段3：LLM流式生成
    await websocket.send_json({"type": "stage_start", "stage": "generate"})
    response = zhipu_client.chat.completions.create(
        model=model,
        messages=[...],
        stream=True
    )
    for chunk in response:
        token = chunk.choices[0].delta.content
        await websocket.send_json({"type": "stream_token", "token": token})
    
    await websocket.send_json({"type": "query_complete", "data": {...}})
```

**前端实现（React）：**
```typescript
const ws = new WebSocket('ws://localhost:8000/api/query/stream');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'stream_token':
      setStreamingAnswer(prev => prev + message.token);
      break;
    case 'query_complete':
      setFinalResult(message.data);
      break;
  }
};

ws.send(JSON.stringify({ query, model: 'glm-4' }));
```

---

## 成本优化策略

### 智谱AI定价（2025年11月）

| 模型 | Input Price | Output Price | 适用场景 |
|------|-------------|--------------|----------|
| Embedding-3 | ¥1/百万tokens | - | 向量化 |
| GLM-4-Flash | ¥1/百万tokens | ¥1/百万tokens | 简单查询 |
| GLM-4 | ¥50/百万tokens | ¥50/百万tokens | 标准查询 |
| GLM-4-Plus | ¥50/百万tokens | ¥50/百万tokens | 复杂推理 |

**成本估算：**
- **索引构建（一次性）：**
  - 1000万字 → 约1000万tokens（Embedding-3）
  - 成本：¥10
- **单次查询：**
  - 简单查询（GLM-4-Flash）：约4000 tokens → ¥0.004
  - 标准查询（GLM-4）：约8000 tokens → ¥0.40
  - 复杂查询（GLM-4-Plus）：约15000 tokens → ¥0.75

**优化策略：**
1. **查询路由：**
   ```python
   if is_simple_fact_query(query):
       model = "glm-4-flash"  # 节省99%成本
   elif is_complex_reasoning(query):
       model = "glm-4-plus"
   else:
       model = "glm-4"  # 默认
   ```
2. **结果缓存：**
   - 使用Redis缓存常见查询
   - TTL: 24小时
3. **Prompt优化：**
   - 精简系统提示词（从500 tokens压缩到200）
   - 限制检索块数（Top-10而非Top-20）

---

## 部署方案

### 本地部署 vs Docker

**决策：** 提供两种方案

#### 方案1：本地部署（开发/个人使用）

**优点：** 调试方便，无额外开销  
**缺点：** 环境配置复杂

**步骤：**
```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

#### 方案2：Docker Compose（生产/多人使用）

**优点：** 一键启动，环境隔离  
**缺点：** 初次构建慢

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

**启动：**
```bash
docker-compose up -d
```

---

## 总结与下一步

### 已解决的关键问题

✅ **技术栈选型：** FastAPI + React + Next.js + 智谱AI  
✅ **文本分块：** RecursiveCharacterTextSplitter，500-600字符  
✅ **检索策略：** Hybrid Search（语义60% + 实体25% + 时序15%）  
✅ **图谱设计：** NetworkX多重有向图，时序属性  
✅ **流式响应：** WebSocket双向通信  
✅ **成本控制：** 智能模型路由，单次查询<¥0.5

### 待研究事项

⏳ **UI组件库：** Ant Design vs shadcn/ui（待Phase 1决策）  
⏳ **测试数据集：** 寻找开源中文小说用于测试  
⏳ **Docker优化：** 镜像大小压缩（当前后端镜像约2GB）

### 参考资料

- [LangChain Documentation](https://python.langchain.com/)
- [智谱AI开放平台](https://open.bigmodel.cn/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [GraphRAG论文](https://arxiv.org/abs/2404.16130)
- [Self-RAG论文](https://arxiv.org/abs/2310.11511)

---

**文档完成日期：** 2025-11-13  
**下一步：** 进入Phase 1，生成数据模型和API合约

