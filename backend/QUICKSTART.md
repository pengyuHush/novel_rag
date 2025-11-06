# 快速开始指南

## 第一步：环境准备

### 1. 检查依赖

```bash
# Python 版本
python --version  # 需要 >= 3.10

# Poetry
poetry --version  # 需要 >= 1.7

# Docker
docker --version
docker-compose --version
```

### 2. 启动 Docker 服务

```bash
cd backend
docker-compose up -d

# 检查服务状态
docker-compose ps
```

应该看到 Redis 和 Qdrant 都在运行。

## 第二步：安装依赖

```bash
cd backend
poetry install
```

这会安装所有依赖，包括:
- FastAPI + Uvicorn
- SQLAlchemy + aiosqlite  
- Redis + Qdrant 客户端
- 智谱 AI SDK
- LangChain
- jieba, chardet 等中文处理工具

## 第三步：配置环境变量

```bash
# 复制示例配置
cp env.example .env

# 编辑 .env 文件
nano .env  # 或用你喜欢的编辑器
```

**必填项**:
```bash
ZAI_API_KEY="你的智谱AI API密钥"
```

获取 API Key: https://open.bigmodel.cn/

其他配置项通常使用默认值即可。

## 第四步：验证环境

```bash
poetry run python verify_env.py
```

这会检查:
- ✅ 环境变量配置
- ✅ SQLite 连接
- ✅ Redis 连接
- ✅ Qdrant 连接  
- ✅ 智谱 API 连接

如果所有检查都通过，说明环境配置正确！

## 第五步：启动后端服务

### 方式 1: 使用启动脚本 (推荐)

```bash
chmod +x start.sh
./start.sh
```

### 方式 2: 手动启动

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

启动成功后，访问:
- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/system/health

## 第六步：测试 API

### 方式 1: 使用测试脚本

```bash
# 确保后端服务已启动
poetry run python test_api.py
```

这会自动测试:
- 健康检查
- 系统信息
- 小说 CRUD 操作
- RAG 搜索功能

### 方式 2: 使用 Swagger UI

访问 http://localhost:8000/docs

1. 点击 **POST /api/v1/novels** 创建小说
2. 点击 **GET /api/v1/novels** 查看列表
3. 点击 **POST /api/v1/search** 测试搜索

### 方式 3: 使用 curl

```bash
# 健康检查
curl http://localhost:8000/api/v1/system/health

# 创建小说
curl -X POST http://localhost:8000/api/v1/novels \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试小说",
    "author": "测试作者",
    "tags": ["测试"]
  }'

# 获取小说列表
curl http://localhost:8000/api/v1/novels
```

## 第七步：完整功能测试

### 1. 上传小说文件

准备一个中文 TXT 小说文件（至少 1000 字）。

```bash
# 1. 创建小说记录
NOVEL_ID=$(curl -X POST http://localhost:8000/api/v1/novels \
  -H "Content-Type: application/json" \
  -d '{"title":"测试小说","author":"作者"}' \
  | jq -r '.id')

echo "小说 ID: $NOVEL_ID"

# 2. 上传文件
curl -X POST http://localhost:8000/api/v1/novels/$NOVEL_ID/upload \
  -F "file=@your_novel.txt"

# 3. 查询处理状态
curl http://localhost:8000/api/v1/novels/$NOVEL_ID/status
```

### 2. 测试 RAG 搜索

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "主角是谁？",
    "top_k": 5
  }'
```

### 3. 生成人物关系图谱

```bash
# 触发生成
curl -X POST http://localhost:8000/api/v1/graph/novels/$NOVEL_ID

# 等待几秒后获取
curl http://localhost:8000/api/v1/graph/novels/$NOVEL_ID
```

## 常见问题

### Q1: Docker 服务启动失败

```bash
# 查看日志
docker-compose logs redis
docker-compose logs qdrant

# 重启服务
docker-compose down
docker-compose up -d
```

### Q2: 智谱 API 调用失败

- 检查 API Key 是否正确
- 确认账户已充值
- 检查网络连接

### Q3: 文件上传失败

- 确保文件是 UTF-8/GBK/GB2312 编码的 TXT 文件
- 文件大小 < 50MB
- 中文字符占比 >= 60%
- 文本长度 >= 1000 字

### Q4: SQLite 数据库位置

数据库文件: `backend/novel_rag.db`

查看数据:
```bash
sqlite3 novel_rag.db
.tables
SELECT * FROM novels;
```

### Q5: 清空数据重新开始

```bash
# 停止服务
# 删除数据库文件
rm novel_rag.db

# 删除向量数据
docker-compose down -v
docker-compose up -d

# 重启服务
```

## 下一步

- 启动前端服务 (在 frontend 目录执行 `npm run dev`)
- 阅读完整 API 文档
- 查看技术架构文档

## 开发模式

### 启用调试日志

编辑 `.env`:
```bash
DEBUG=true
```

### 热重载

uvicorn 的 `--reload` 参数会自动检测代码变化并重启。

### 查看日志

所有日志会输出到终端，使用 loguru 格式化。

---

**问题反馈**: 如有问题，请检查日志输出或提交 Issue。

