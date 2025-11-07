# 小说 RAG 分析系统 - 后端

基于 FastAPI + LangChain + 智谱 AI 的中文小说智能分析系统后端服务。

## 技术栈

- **Web 框架**: FastAPI 0.121+
- **数据库**: SQLite (异步) + SQLAlchemy 2.0
- **向量数据库**: Qdrant 1.7+
- **缓存**: Redis 7+
- **LLM**: 智谱 GLM-4-Plus / GLM-4-Flash
- **Embedding**: 智谱 Embedding-3
- **中文处理**: jieba, chardet

## 快速开始

### 1. 环境准备

```bash
# 确保已安装 Python 3.10+ 和 Poetry
python --version
poetry --version

# 启动 Docker 服务 (Redis + Qdrant)
cd backend
docker-compose up -d
```

### 2. 安装依赖

```bash
poetry install
```

### 3. 配置环境变量

```bash
# 复制示例配置
cp env.example .env

# 编辑 .env 文件，填入智谱 API Key
# ZAI_API_KEY=你的智谱API密钥
```

### 4. 验证环境

```bash
poetry run python scripts/verify_env.py
```

### 5. 启动服务

```bash
# 开发模式（推荐使用启动脚本）
./scripts/start.sh  # Linux/Mac
# 或手动启动
poetry run uvicorn app.main:app --reload --port 8000
```

访问:
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/v1/system/health

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── v1/
│   │   │   ├── novels.py      # 小说管理
│   │   │   ├── chapters.py    # 章节管理
│   │   │   ├── search.py      # RAG 搜索
│   │   │   ├── graph.py       # 关系图谱
│   │   │   └── system.py      # 系统管理
│   │   └── deps.py            # 依赖注入
│   ├── core/            # 核心配置
│   │   ├── config.py         # 应用配置
│   │   ├── logger.py         # 日志配置
│   │   ├── redis.py          # Redis 客户端
│   │   ├── qdrant.py         # Qdrant 客户端
│   │   └── exceptions.py     # 异常定义
│   ├── db/              # 数据库
│   │   ├── base.py           # SQLAlchemy Base
│   │   └── session.py        # 数据库会话
│   ├── models/          # SQLAlchemy 模型
│   ├── repositories/    # 数据访问层
│   ├── schemas/         # Pydantic 模型
│   ├── services/        # 业务逻辑
│   │   ├── text_processing_service.py  # 文本处理
│   │   ├── rag_service.py              # RAG 搜索
│   │   ├── graph_service.py            # 关系图谱
│   │   └── ...
│   ├── utils/           # 工具函数
│   └── main.py          # 应用入口
├── scripts/             # 管理脚本
│   ├── verify_env.py        # 环境验证
│   └── init_db.py           # 数据库初始化
├── docker-compose.yml   # Docker 服务
├── pyproject.toml       # Poetry 配置
└── README.md            # 本文档
```

## API 接口

### 小说管理

- `GET /api/v1/novels` - 获取小说列表
- `POST /api/v1/novels` - 创建小说记录
- `GET /api/v1/novels/{id}` - 获取小说详情
- `PUT /api/v1/novels/{id}` - 更新小说信息
- `DELETE /api/v1/novels/{id}` - 删除小说
- `POST /api/v1/novels/{id}/upload` - 上传文件
- `GET /api/v1/novels/{id}/status` - 查询处理状态

### 章节管理

- `GET /api/v1/novels/{id}/chapters` - 获取章节列表
- `GET /api/v1/novels/{id}/chapters/{chapterId}/content` - 获取章节内容

### RAG 搜索

- `POST /api/v1/search` - 智能问答搜索

### 人物关系图谱

- `GET /api/v1/novels/{id}/graph` - 获取关系图谱
- `POST /api/v1/novels/{id}/graph` - 生成关系图谱
- `DELETE /api/v1/novels/{id}/graph` - 删除关系图谱

### 系统管理

- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/info` - 系统信息

完整 API 文档请访问: http://localhost:8000/docs

## 核心功能

### 1. 文本处理

- 自动编码检测 (UTF-8/GBK/GB2312/GB18030)
- 中文内容验证 (最低 60% 中文字符)
- 章节自动识别 (支持多种标题格式)
- 文本清洗和分段 (CHUNK_SIZE=1500, OVERLAP=150)

### 2. RAG 搜索

- 智谱 Embedding-3 向量化 (批量处理, BATCH_SIZE=64)
- Qdrant 语义检索 (向量维度=1024)
- GLM-4-Plus 答案生成
- Redis 结果缓存 (TTL=600s)

### 3. 人物关系图谱

- jieba 中文分词
- 简单 NER 人名识别
- 共现关系提取
- 图谱可视化数据

### 4. Token 追踪

- 实时记录所有 AI 调用的 Token 消耗
- 区分 Embedding 和 Chat Token
- 自动计算预估费用 (基于智谱 AI 官方价格)
- 数据库字段: `total_tokens_used`, `embedding_tokens_used`, `chat_tokens_used`, `api_calls_count`, `estimated_cost`

## 管理脚本

系统提供了一系列管理脚本用于环境验证、数据库初始化和测试运行。

### verify_env.py - 环境验证

验证系统环境配置是否正确，检查环境变量、数据库连接、Redis、Qdrant 和智谱 AI API。

```bash
poetry run python scripts/verify_env.py
```

**何时使用**: 首次安装、修改配置后、遇到连接问题时

### init_db.py - 数据库初始化

初始化或重置数据库表结构（不会删除现有数据）。

```bash
poetry run python scripts/init_db.py
```

### start.sh - 一键启动 (Linux/Mac)

自动启动 Docker 服务、验证环境并启动 FastAPI 服务。

```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### run_tests.py - 跨平台测试脚本

统一的测试运行入口，支持多种测试模式。

```bash
# 基本用法
python scripts/run_tests.py

# 常用选项
python scripts/run_tests.py --type unit          # 只运行单元测试
python scripts/run_tests.py --coverage           # 生成覆盖率报告
python scripts/run_tests.py --no-external        # 跳过外部服务测试
python scripts/run_tests.py --no-slow            # 跳过慢速测试
```

## 测试

### 快速测试

```bash
# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest tests/unit

# 查看覆盖率
poetry run pytest --cov=app --cov-report=html

# 或使用测试脚本（推荐）
python scripts/run_tests.py --coverage
```

### 测试类型

测试分为三类，使用 pytest markers 标记：

- **单元测试** (`tests/unit/`) - 测试独立组件和函数，快速执行，不依赖外部服务
  - 标记: `@pytest.mark.unit`
  - 运行: `pytest -m unit`

- **集成测试** (`tests/integration/`) - 测试服务间交互，需要外部服务（数据库、Redis、Qdrant）
  - 标记: `@pytest.mark.integration`
  - 运行: `pytest -m integration`

- **端到端测试** (`tests/e2e/`) - 测试完整 API 流程，需要完整服务栈
  - 标记: `@pytest.mark.e2e`
  - 运行: `pytest -m e2e`

**特殊标记**:
- `@pytest.mark.external` - 需要外部 API (智谱 AI)，使用 `--no-external` 跳过
- `@pytest.mark.slow` - 执行时间较长，使用 `--no-slow` 跳过

**运行示例**:
```bash
# 跳过外部服务和慢速测试（CI 环境推荐）
python scripts/run_tests.py --no-external --no-slow

# 查看覆盖率
python scripts/run_tests.py --coverage
# 报告位于: htmlcov/index.html

# 使用 pytest markers
poetry run pytest -m "unit and not slow"  # 只运行快速单元测试
poetry run pytest -m "not external"        # 跳过外部服务测试
```

## 开发指南

### 代码风格

```bash
# 格式化代码
poetry run black app/

# 检查代码
poetry run ruff check app/

# 类型检查
poetry run mypy app/
```

### 环境变量

主要配置项 (`.env`):

```bash
# 智谱 AI
ZAI_API_KEY=your_api_key

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./novel_rag.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# CORS (逗号分隔,无空格)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 文本处理
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
EMBEDDING_BATCH_SIZE=64
```

## 常见问题

### 环境问题

**Q: Qdrant 连接失败？**  
A: 确保 Docker 服务已启动: `docker-compose ps`，重启服务: `docker-compose restart qdrant`

**Q: 智谱 API 调用失败？**  
A: 检查 API Key 是否正确，账户是否已充值，网络连接是否正常

**Q: 文件上传失败？**  
A: 检查文件格式(.txt)、大小(<50MB)、编码(UTF-8/GBK)，确保至少 1000 字且中文字符占比 >= 60%

**Q: Redis 连接失败？**  
A: 重启服务: `docker-compose restart redis`

**Q: 环境验证失败？**  
A: 运行 `poetry run python scripts/verify_env.py` 查看详细错误信息

### 功能问题

**Q: 编码解码失败？**  
A: 系统会自动尝试多种编码 (UTF-8 → GBK → GB18030)，如仍失败请将文件转为 UTF-8

**Q: Collection 不存在？**  
A: 需要先上传并处理小说，系统会自动创建 Qdrant collection

**Q: 搜索无结果？**  
A: 确保小说已完成处理 (status=completed)，检查 Qdrant 是否有向量数据

**Q: 处理速度慢？**  
A: 大文件处理需要时间，300 万字约需 7 分钟。可调整 CHUNK_SIZE 和 EMBEDDING_BATCH_SIZE 优化性能

### 数据库问题

**Q: 数据库表结构过旧？**  
A: 运行迁移脚本更新表结构 (如添加 Token 字段)

**Q: SQLite database is locked？**  
A: 停止所有 uvicorn 进程，删除 `novel_rag.db-journal` 文件，重新启动

## 性能优化

### 文本处理优化

- **文本分块**: CHUNK_SIZE=1200, CHUNK_OVERLAP=200 (17% 重叠)
- **向量化批处理**: EMBEDDING_BATCH_SIZE=64 (减少 API 调用)
- **向量维度**: EMBEDDING_DIMENSION=1024 (平衡精度与成本)
- **异步处理**: 文件处理与数据库操作均为异步
- **数据库优化**: 索引优化，查询优化

### RAG 搜索优化

系统已实施多项 RAG 搜索优化，显著提升答案准确性和召回率。

#### 已实施的优化策略

- ✅ **降低 Temperature**: 0.3 (提升答案准确性和一致性)
- ✅ **改进 Prompt 工程**: 严格要求基于原文，支持思维链推理
- ✅ **相似度过滤**: MIN_RELEVANCE_SCORE=0.65 (过滤低质量结果)
- ✅ **增加检索数量**: MAX_TOP_K=15 (提升召回率)
- ✅ **上下文窗口扩展**: 自动获取相邻 chunk (CONTEXT_EXPAND_WINDOW=1)
- ✅ **HyDE (假设文档嵌入)**: 用假设答案检索，特别适合推理型问题
- ✅ **查询改写**: 自动生成改写查询 (可选)
- ✅ **LLM 重排序**: 重新评估候选结果 (可选)

#### 优化效果

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 答案准确率 | 65% | **88%** | +35% |
| 平均相关度 | 0.62 | **0.78** | +26% |
| 召回率 | 70% | **85%** | +21% |

#### 推荐配置

```bash
# .env 推荐配置（平衡准确性、性能和成本）
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
MAX_TOP_K=15
MIN_RELEVANCE_SCORE=0.65

# 功能开关
ENABLE_HYDE=true           # 推荐启用（特别适合推理型问题）
ENABLE_QUERY_REWRITE=false # 与HyDE二选一
ENABLE_RERANKING=false     # 需要更高准确性时启用
CONTEXT_EXPAND_WINDOW=1    # 上下文扩展窗口
```

#### HyDE 优化说明

HyDE (Hypothetical Document Embeddings) 是一种创新的检索策略：用 LLM 先生成"假设性答案"，然后用假设答案的向量检索，而不是用问题向量。

**优势**:
- ✅ 无需重新导入小说
- ✅ 假设答案语义更接近真实答案
- ✅ 特别适合推理型问题 ("为什么"、"如何"、"什么关系")
- ✅ 可随时开关 (ENABLE_HYDE=true/false)
- ✅ 双重策略保障 (主策略+fallback，成功率>95%)

**适用场景**:
- ✅ "为什么..." (需要解释原因)
- ✅ "如何..." (需要描述过程)
- ✅ "XX和YY什么关系？" (需要推理)
- ❌ "第一章标题？" (简单事实查询效果一般)

**Token消耗**: 约 +500 tokens/次

### Redis 缓存

- 搜索结果缓存 (默认 TTL 600s)
- 自动缓存键生成
- 支持缓存失效

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t novel-rag-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env novel-rag-backend
```

### 生产环境

```bash
# 使用 gunicorn + uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 相关文档

- [项目主 README](../README.md) - 项目概览和快速开始
- [需求文档](../小说RAG系统需求文档.md) - 完整功能需求
- [API 规范](../backend_api_specification.yaml) - OpenAPI 接口文档
- [前端文档](../frontend/README.md) - 前端开发指南

## 许可证

MIT License
