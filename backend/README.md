# 网络小说智能问答系统 - 后端

FastAPI后端服务，提供RAG问答、知识图谱、文件解析等核心功能。

## 技术栈

- **Web框架**: FastAPI 0.104+
- **LLM框架**: LangChain 0.1+
- **AI服务**: 智谱AI (GLM-4系列 + Embedding-3)
- **向量数据库**: ChromaDB 0.4+
- **关系数据库**: SQLite 3.40+
- **NLP工具**: HanLP 2.1+
- **图谱库**: NetworkX 3.0+

## 快速开始

### 前置要求

- Python 3.12+
- Poetry 1.7+ ([安装指南](https://python-poetry.org/docs/#installation))

### 1. 安装依赖

```bash
# 使用Poetry安装依赖
poetry install

# 或者仅安装生产依赖（不含开发工具）
poetry install --no-dev
```

Poetry会自动创建和管理虚拟环境。

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填写智谱AI API Key
# ZHIPU_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者激活虚拟环境后直接运行
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务将在以下地址启动：
- API: http://localhost:8000
- 交互式文档: http://localhost:8000/docs
- 备选文档: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── novels.py     # 小说管理
│   │   ├── query.py      # 智能问答
│   │   ├── chapters.py   # 章节管理
│   │   ├── graph.py      # 知识图谱
│   │   └── health.py     # 健康检查
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   └── error_handlers.py  # 异常处理
│   ├── services/         # 业务逻辑
│   │   ├── parser/       # 文件解析
│   │   ├── rag_engine.py # RAG引擎
│   │   ├── graph/        # 知识图谱
│   │   └── zhipu_client.py  # 智谱AI客户端
│   ├── models/           # 数据模型
│   │   ├── database.py   # SQLAlchemy模型
│   │   └── schemas.py    # Pydantic模型
│   ├── utils/            # 工具函数
│   │   ├── file_storage.py
│   │   └── token_counter.py
│   ├── db/               # 数据库
│   │   ├── schema.sql    # SQL Schema
│   │   └── init_db.py    # 数据库初始化
│   └── main.py           # 应用入口
├── data/                 # 数据存储
│   ├── chromadb/        # 向量数据库
│   ├── sqlite/          # SQLite数据库
│   ├── graphs/          # 知识图谱
│   └── uploads/         # 上传文件
├── logs/                # 日志文件
├── tests/               # 测试
├── requirements.txt     # Python依赖
├── Dockerfile          # Docker配置
└── .env.example        # 环境变量示例
```

## API端点

### 健康检查

- `GET /health` - 服务健康状态

### 小说管理

- `POST /api/novels/upload` - 上传小说
- `GET /api/novels` - 获取小说列表
- `GET /api/novels/{id}` - 获取小说详情
- `DELETE /api/novels/{id}` - 删除小说
- `GET /api/novels/{id}/progress` - 获取索引进度

### 智能问答

- `POST /api/query` - 同步查询
- `WS /api/query/stream` - 流式查询（WebSocket）

### 章节管理

- `GET /api/novels/{id}/chapters` - 获取章节列表
- `GET /api/novels/{id}/chapters/{num}` - 获取章节内容

### 知识图谱

- `GET /api/graph/relations/{id}` - 获取关系图数据
- `GET /api/graph/timeline/{id}` - 获取时间线数据

### 统计

- `GET /api/stats/tokens` - Token统计

完整API文档: http://localhost:8000/docs

## 测试

```bash
# 运行所有测试
poetry run pytest tests/ -v

# 生成覆盖率报告（配置在pyproject.toml中）
poetry run pytest

# 查看覆盖率报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## 代码质量

```bash
# 格式化代码
poetry run black app/

# 代码检查
poetry run flake8 app/

# 类型检查
poetry run mypy app/

# 或者激活虚拟环境后直接运行
poetry shell
black app/
flake8 app/
mypy app/
```

## Poetry常用命令

```bash
# 添加新依赖
poetry add <package-name>

# 添加开发依赖
poetry add --group dev <package-name>

# 更新依赖
poetry update

# 查看依赖树
poetry show --tree

# 激活虚拟环境
poetry shell

# 退出虚拟环境
exit

# 查看虚拟环境信息
poetry env info
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱AI API密钥 | 必填 |
| `ZHIPU_DEFAULT_MODEL` | 默认模型 | glm-4 (支持: glm-4-flash, glm-4, glm-4-plus, glm-4-5, glm-4-5-flash, glm-4-5-v, glm-4-5-air, glm-4-6) |
| `DATABASE_URL` | 数据库URL | sqlite:///./data/sqlite/metadata.db |
| `CHROMADB_PATH` | ChromaDB路径 | ./data/chromadb |
| `UPLOAD_DIR` | 上传目录 | ./data/uploads |
| `LOG_LEVEL` | 日志级别 | INFO |

完整配置见 `.env.example`

## 故障排除

### 智谱AI连接失败

```bash
# 测试API Key
python -c "from zhipuai import ZhipuAI; client = ZhipuAI(api_key='your_key'); print(client.models.list())"
```

### ChromaDB初始化失败

```bash
# 删除旧数据重新初始化
rm -rf data/chromadb/*
```

### 数据库锁定错误

```bash
# SQLite并发限制，使用单worker模式
uvicorn app.main:app --workers 1
```

## 性能优化建议

1. **启用缓存**: Redis缓存查询结果
2. **批量处理**: 批量向量化降低API调用
3. **异步任务**: Celery处理长时间索引任务
4. **数据库优化**: 添加合适的索引

## 许可证

MIT License

