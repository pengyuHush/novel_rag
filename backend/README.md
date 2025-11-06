# 小说 RAG 分析系统 - 后端

基于 FastAPI + LangChain + 智谱 GLM-4 的中文小说智能分析系统后端。

## 技术栈

- **Web 框架**: FastAPI 0.121+
- **数据库**: SQLite (异步) + SQLAlchemy 2.0
- **向量数据库**: Qdrant 1.7+
- **缓存**: Redis 7+
- **LLM**: 智谱 GLM-4-Plus
- **Embedding**: 智谱 Embedding-3
- **中文处理**: jieba, chardet

## 快速开始

### 1. 环境准备

```bash
# 确保已安装 Python 3.10+
python --version

# 确保已安装 Poetry
poetry --version

# 启动 Docker 服务 (Redis + Qdrant)
cd backend
docker-compose up -d
```

### 2. 安装依赖

```bash
cd backend
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
# 开发模式
poetry run uvicorn app.main:app --reload --port 8000

# 或使用简化命令
poetry run python -m app.main
```

访问:
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/v1/system/health

## 系统架构
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React + TypeScript)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS + JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  API Routes  │  │  Middleware  │  │   Exception  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Services (Business Logic)                │  │
│  │  - NovelService                                       │  │
│  │  - TextProcessingService (核心)                      │  │
│  │  - RAGService (核心)                                 │  │
│  │  - GraphService                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Repositories (Data Access)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────┬───────────────┬───────────────┬────────────────────┘
       │               │               │
   ┌───▼────┐   ┌─────▼─────┐   ┌────▼─────┐
   │ SQLite │   │   Redis    │   │  Qdrant  │
   │  (DB)  │   │  (Cache)   │   │ (Vector) │
   └────────┘   └────────────┘   └────┬─────┘
                                       │
                                  ┌────▼────────┐
                                  │ 智谱 GLM API │
                                  │ (LLM+Embed) │
                                  └─────────────┘


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
│   │   ├── novel.py
│   │   ├── chapter.py
│   │   ├── character_graph.py
│   │   └── search_cache.py
│   ├── repositories/    # 数据访问层
│   │   ├── novel_repository.py
│   │   ├── chapter_repository.py
│   │   └── ...
│   ├── schemas/         # Pydantic 模型
│   │   ├── novel.py
│   │   ├── search.py
│   │   ├── graph.py
│   │   └── system.py
│   ├── services/        # 业务逻辑
│   │   ├── novel_service.py
│   │   ├── text_processing_service.py  # 文本处理
│   │   ├── rag_service.py              # RAG 搜索
│   │   ├── graph_service.py            # 关系图谱
│   │   └── system_service.py
│   ├── utils/           # 工具函数
│   │   ├── file_storage.py
│   │   ├── text_processing.py
│   │   └── hashing.py
│   └── main.py          # 应用入口
├── scripts/             # 管理脚本
│   ├── verify_env.py        # 环境验证
│   ├── init_db.py           # 数据库初始化
│   ├── start.sh             # 启动脚本
│   ├── run_tests.py         # 测试运行脚本
│   └── run_tests.ps1        # PowerShell测试脚本
├── storage/             # 文件存储 (自动创建)
├── docker-compose.yml   # Docker 服务
├── pyproject.toml       # Poetry 配置
├── pytest.ini           # Pytest 配置
├── README.md            # 主文档
├── TESTING.md           # 测试文档
└── TROUBLESHOOTING.md   # 故障排查
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

- `GET /api/v1/graph/novels/{id}` - 获取关系图谱
- `POST /api/v1/graph/novels/{id}` - 生成关系图谱

### 系统管理

- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/info` - 系统信息

## 核心功能

### 1. 文本处理

- 自动编码检测 (UTF-8/GBK/GB2312)
- 中文内容验证
- 章节自动识别
- 文本清洗和分段

### 2. RAG 搜索

- 智谱 Embedding-3 向量化
- Qdrant 语义检索
- GLM-4-Plus 答案生成
- Redis 结果缓存

### 3. 人物关系图谱

- jieba 中文分词
- 简单 NER 人名识别
- 共现关系提取
- 图谱可视化数据

## 测试

完整的测试指南请查看 [TESTING.md](TESTING.md)

### 快速开始测试

```bash
# 快速单元测试
python scripts/run_tests.py --type unit

# 完整测试(跳过外部服务)
python scripts/run_tests.py --no-external --coverage

# 查看测试覆盖率报告
# 报告位置: backend/htmlcov/index.html
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

### 运行测试

详细测试指南请查看 [TESTING.md](TESTING.md)

```bash
# 使用测试脚本(推荐)
python scripts/run_tests.py --type unit

# 或直接使用pytest
poetry run pytest
```

### 数据库迁移

```bash
# 生成迁移
poetry run alembic revision --autogenerate -m "description"

# 执行迁移
poetry run alembic upgrade head
```

## 常见问题

完整的故障排查指南请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 常见问题速查

- **Qdrant连接失败**: 确保 Docker 服务已启动 `docker-compose ps`
- **智谱API调用失败**: 检查 API Key 是否正确,账户是否已充值
- **文件上传失败**: 检查文件格式(.txt)、大小(<50MB)、编码(UTF-8/GBK)
- **Redis连接失败**: 重启服务 `docker-compose restart redis`
- **环境验证失败**: 运行 `poetry run python scripts/verify_env.py` 检查详情

## 性能优化

- 向量化批量处理 (batch_size=20)
- Redis 搜索结果缓存 (600s)
- 异步文件处理
- 数据库查询优化

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

## 许可证

MIT License

