# 小说 RAG 分析系统

基于 RAG 技术的中文小说智能分析平台，支持大型 TXT 小说导入、语义搜索问答、人物关系图谱及 Token 成本跟踪。

## 核心功能

- 📚 **小说管理** - 导入 TXT 小说，自动识别章节，支持编辑与删除
- 🔍 **语义搜索 & 问答** - 基于语义向量检索的精确问答，返回原文出处  
- 👥 **人物关系图谱** - 自动抽取主要人物及关系，生成交互式图谱
- ⚡ **Token 追踪** - 实时记录智谱 AI 调用的 Token 与预估费用
- 📖 **章节阅读** - 在线阅读器，支持章节导航和阅读进度

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19 · TypeScript · Vite · Ant Design |
| 后端 | FastAPI · SQLAlchemy 2 · LangChain |
| AI | 智谱 AI GLM-4-Plus · Embedding-3 |
| 数据 | SQLite · Qdrant (向量) · Redis (缓存) |

## 快速开始

### 1. 环境准备

```bash
# 前置要求
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- 智谱 AI API Key
```

### 2. 启动后端

```bash
cd backend

# 启动基础服务 (Redis + Qdrant)
docker-compose up -d

# 安装依赖
poetry install

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填写 ZAI_API_KEY

# 验证环境
poetry run python scripts/verify_env.py

# 启动服务
poetry run uvicorn app.main:app --reload --port 8000
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 确保 VITE_API_BASE_URL=http://localhost:8000/api/v1

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- **前端应用**: http://localhost:5173
- **后端 API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/system/health

## 项目结构

```
novel_rag/
├── backend/              # FastAPI 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── services/    # 业务逻辑
│   │   ├── models/      # 数据模型
│   │   └── schemas/     # Pydantic Schema
│   ├── scripts/         # 管理脚本
│   └── README.md        # 后端文档
│
├── frontend/            # React 前端应用
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   ├── components/  # UI 组件
│   │   ├── store/       # 状态管理
│   │   └── utils/       # 工具函数
│   └── README.md        # 前端文档
│
├── backend_api_specification.yaml  # API 接口规范
├── 小说RAG系统需求文档.md          # 需求文档
└── README.md                       # 本文档
```

## 主要文档

- **[小说RAG系统需求文档.md](./小说RAG系统需求文档.md)** - 完整的功能需求和技术规格
- **[backend_api_specification.yaml](./backend_api_specification.yaml)** - RESTful API 接口定义
- **[backend/README.md](./backend/README.md)** - 后端开发指南和 API 说明
- **[frontend/README.md](./frontend/README.md)** - 前端开发指南和组件文档

## 开发指南

### 后端开发

```bash
cd backend

# 运行测试
poetry run pytest

# 代码格式化
poetry run black app/

# 类型检查
poetry run mypy app/
```

详见 [backend/README.md](./backend/README.md)

### 前端开发

```bash
cd frontend

# 代码检查
npm run lint

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

详见 [frontend/README.md](./frontend/README.md)

## 常见问题

### 环境配置问题

**Q: 智谱 API 调用失败？**  
A: 检查 `.env` 中的 `ZAI_API_KEY` 是否正确，确认账户有足够余额。

**Q: Qdrant/Redis 连接失败？**  
A: 确保 Docker 服务已启动：`cd backend && docker-compose ps`

**Q: 文件编码错误？**  
A: 系统支持 UTF-8、GBK、GB2312 自动检测，如果失败请将文件转为 UTF-8。

### 功能使用问题

**Q: 搜索无结果？**  
A: 确保小说已完成处理（状态为 `completed`），检查 Qdrant 是否有数据。

**Q: 图谱生成失败？**  
A: 图谱生成需要较长时间，建议等待处理完成后再生成。

更多问题请查看各子目录的 README 文档。

## Token 消耗说明

系统会自动追踪所有 AI 调用的 Token 消耗：

- **Embedding**: 0.5 元/百万 tokens
- **Chat (GLM-4-Plus)**: 输入 5 元/百万，输出 10 元/百万

Token 统计包含在 API 响应中，前端实时显示预估费用。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交代码 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 许可证

MIT License

---

**最后更新**: 2025-11-07
