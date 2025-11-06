# 常见问题解决指南

## 配置相关

### ❌ 错误: `error parsing value for field "CORS_ORIGINS"`

**原因**: 环境变量 `CORS_ORIGINS` 格式不正确。

**解决方法**:

在 `.env` 文件中，**不要**使用引号和不必要的空格：

```bash
# ❌ 错误写法
CORS_ORIGINS="http://localhost:5173, http://localhost:3000"

# ✅ 正确写法
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

### ❌ 错误: `ValidationError: ZAI_API_KEY / ZHIPU_API_KEY`

**原因**: 智谱 API Key 未配置。

**解决方法**:

1. 访问 https://open.bigmodel.cn/ 获取 API Key
2. 在 `.env` 文件中添加:

```bash
ZAI_API_KEY=你的API密钥
```

## Docker 相关

### ❌ 错误: Redis/Qdrant 连接失败

**检查服务状态**:

```bash
cd backend
docker-compose ps
```

**重启服务**:

```bash
docker-compose down
docker-compose up -d
```

**查看日志**:

```bash
docker-compose logs redis
docker-compose logs qdrant
```

### ❌ 端口冲突

如果 6379(Redis) 或 6333(Qdrant) 端口被占用:

```bash
# 修改 docker-compose.yml
services:
  redis:
    ports:
      - "6380:6379"  # 改为其他端口
  qdrant:
    ports:
      - "6334:6333"  # 改为其他端口
```

然后更新 `.env`:

```bash
REDIS_URL=redis://localhost:6380/0
QDRANT_PORT=6334
```

## 导入错误

### ❌ 错误: `ModuleNotFoundError`

**确认虚拟环境已激活**:

```bash
poetry shell
poetry install
```

### ⚠️ 警告: 第三方库兼容性

如果看到以下警告，可以忽略，不影响功能：

1. **jieba/zai 警告**: 第三方库的 Python 3.14 兼容性警告
2. **Qdrant 版本警告**: 
   ```
   Qdrant client version 1.15.1 is incompatible with server version 1.7.4
   ```
   这是因为客户端和服务器的小版本不同，实际功能正常。如果想消除警告，可以：
   - 升级 Qdrant 服务器: `docker-compose down && docker pull qdrant/qdrant:latest && docker-compose up -d`
   - 或者接受警告（不影响使用）

## 运行时错误

### ❌ 错误: `MissingGreenlet: greenlet_spawn has not been called`

**原因**: SQLAlchemy 异步会话中，在 `commit()` 后访问对象属性时出现异步上下文问题。

**已修复**: 在代码中添加了 `session.refresh()` 来确保对象在同一会话中刷新。

如果仍然出现此错误，请确保已更新到最新代码。

### ❌ 错误: `no such column: novels.processing_progress`

**原因**: 数据库表结构过旧，缺少新添加的字段。

**解决方法**:

1. 停止 uvicorn
2. 运行重置脚本:

```bash
poetry run python reset_db.py
```

3. 重新启动 uvicorn

### ❌ 错误: `SQLite database is locked`

**原因**: 数据库被多个进程同时访问。

**解决方法**:

1. 停止所有 uvicorn 进程
2. 删除 `novel_rag.db-journal` 文件（如果存在）
3. 重新启动

### ❌ 错误: 文件上传失败

**检查项**:

1. 文件格式是否为 `.txt`
2. 文件大小是否 < 50MB
3. 文本是否至少 1000 字
4. 中文字符占比是否 >= 60%

**测试文件**:

创建一个简单的测试文件 `test.txt`:

```
第一章 开始

这是一个测试小说。主角张三来到了一个陌生的城市。
他遇到了李四，两人成为了好朋友。
接下来发生了很多有趣的事情......

（重复几段以达到 1000 字）
```

### ❌ 错误: `Collection 'novel_embeddings' doesn't exist!`

**原因**: Qdrant 向量数据库中还没有数据，因为还没有上传和处理小说。

**解决方法**:

1. **创建小说记录**:
```bash
curl -X POST http://localhost:8000/api/v1/novels \
  -H "Content-Type: application/json" \
  -d '{"title":"测试小说","author":"测试"}'
```

2. **上传TXT文件** (准备一个至少1000字的中文TXT文件):
```bash
curl -X POST http://localhost:8000/api/v1/novels/{novel_id}/upload \
  -F "file=@your_novel.txt"
```

3. **等待处理完成** (查看状态):
```bash
curl http://localhost:8000/api/v1/novels/{novel_id}/status
```

4. **处理完成后即可搜索**:
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"主角是谁？"}'
```

**注意**: 代码已修复，现在即使没有数据，搜索也会返回友好提示而不是错误。

### ❌ 错误: RAG 搜索无响应

**检查**:

1. 智谱 API Key 是否正确
2. 网络连接是否正常
3. Qdrant 是否有数据 (需要先上传并处理小说)

**测试 API**:

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"测试问题","top_k":3}'
```

## Windows 特定问题

### ❌ PowerShell 执行策略

如果无法运行 poetry:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ 路径问题

使用绝对路径或确保在正确的目录:

```powershell
# 使用 PowerShell
cd D:\code\my\novel_rag\backend
poetry run uvicorn app.main:app --reload
```

## 性能问题

### 📊 处理速度慢

**优化建议**:

1. **向量化**: 默认 batch_size=20，可以在 `text_processing_service.py` 中调整
2. **缓存**: 确保 Redis 运行正常
3. **文件大小**: 大文件(>3MB)会较慢，考虑拆分

### 📊 内存占用高

**检查**:

```bash
# 查看进程
poetry run python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

**优化**:
- 减小 `CHUNK_SIZE` (默认 500)
- 限制同时处理的小说数量

## 调试技巧

### 启用详细日志

在 `.env` 中:

```bash
DEBUG=true
```

### 查看数据库内容

```bash
# 安装 sqlite3
poetry add --group dev sqlite-utils

# 查看表
sqlite3 novel_rag.db ".tables"

# 查看小说
sqlite3 novel_rag.db "SELECT id, title, status FROM novels;"
```

### 检查 Qdrant 集合

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
collections = client.get_collections()
print(collections)
```

### API 测试工具

使用提供的测试脚本:

```bash
poetry run python test_api.py
```

或使用 Swagger UI:

```
http://localhost:8000/docs
```

## 还是无法解决？

1. **查看完整日志**: 启动时的所有输出
2. **检查环境**: 运行 `poetry run python verify_env.py`
3. **清理重试**:

```bash
# 停止所有服务
docker-compose down -v

# 删除数据库
rm novel_rag.db

# 重新安装
poetry install

# 重新启动
docker-compose up -d
poetry run uvicorn app.main:app --reload
```

4. **查看文档**:
   - README.md - 完整文档
   - QUICKSTART.md - 快速开始
   - 后端开发完成说明.md - 功能说明

## 联系支持

如果问题依然存在，请提供:

1. 完整的错误堆栈
2. `.env` 配置 (隐藏敏感信息)
3. `poetry run python verify_env.py` 的输出
4. Docker 服务状态 `docker-compose ps`
5. Python 版本 `python --version`

