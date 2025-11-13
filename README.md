# 网络小说智能问答系统

基于RAG（Retrieval-Augmented Generation）架构的网络小说智能问答系统，支持千万字级长篇小说的准确索引、检索和智能问答。

## ✨ 核心特性

- 📚 **小说管理**: 支持TXT/EPUB格式上传，自动解析章节结构
- 🔍 **智能问答**: 基于GraphRAG和Self-RAG的高准确率问答系统
- 📖 **在线阅读**: 分章节浏览，支持10万字超长章节
- 🕸️ **知识图谱**: 角色关系自动提取，时序演变分析
- 🎭 **诡计识别**: 检测叙述诡计、矛盾信息、非线性叙事
- 📊 **可视化**: 角色关系图、时间线可视化
- 💰 **成本控制**: 详细Token统计，多模型切换

## 🏗️ 技术栈

### 前端
- React 18 + Next.js 14 + TypeScript
- Ant Design 5.x (UI组件库)
- Zustand + TanStack Query (状态管理)
- Plotly.js (数据可视化)

### 后端
- FastAPI 0.104+ + Python 3.10+
- LangChain (RAG编排)
- ChromaDB 0.4+ (向量数据库)
- SQLite 3.40+ (元数据库)
- NetworkX 3.0+ (知识图谱)
- HanLP 2.1+ (中文NLP)

### AI服务
- 智谱AI GLM-4系列 (生成模型)
- 智谱AI Embedding-3 (向量化模型)

## 🚀 快速开始

### 前置要求

- Python 3.12+ 
- Poetry 1.7+ ([安装指南](https://python-poetry.org/docs/#installation))
- Node.js 18+
- 智谱AI API Key ([获取地址](https://open.bigmodel.cn/))

### 方式一：本地开发模式

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd novel_rag_spec_kit
```

#### 2. 后端设置

```bash
cd backend

# 使用Poetry安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写智谱AI API Key

# 启动后端服务
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者先激活虚拟环境
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

### 方式二：Docker Compose (推荐)

```bash
# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，填写智谱AI API Key

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📖 使用指南

### 1. 上传小说

1. 访问 http://localhost:3000
2. 进入"小说管理"页面
3. 点击"上传小说"，选择TXT或EPUB文件
4. 等待系统自动解析和索引（千万字小说约需3-5小时）

### 2. 智能问答

1. 索引完成后，进入"智能问答"页面
2. 选择小说和AI模型
3. 输入问题，系统将实时流式返回答案
4. 查看引用来源、矛盾检测结果、Token消耗统计

### 3. 在线阅读

1. 进入"在线阅读"页面
2. 选择小说，浏览章节列表
3. 点击章节进行阅读
4. 使用搜索功能快速定位章节

### 4. 知识图谱

1. 进入"知识图谱"页面
2. 查看角色关系图（力导向图）
3. 查看时间线（时序可视化）
4. 使用时间滑块查看关系演变

## 📊 性能指标

### 准确率目标

- 事实查询准确率: MVP 80% → 优化后 92%+
- 诡计识别率: MVP 72% → 优化后 88%+
- 矛盾检测召回率: MVP 77% → 优化后 90%+

### 响应时间

- 简单查询: < 30秒
- 复杂查询: < 3分钟
- 章节切换: < 1秒
- 前端首屏加载: < 1.5秒

### 资源占用

- 内存峰值: < 8GB (无需GPU)
- 存储空间: 50GB+ (索引数据)

## 🛠️ 开发指南

### 项目结构

```
novel_rag_spec_kit/
├── backend/              # 后端FastAPI服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── services/    # 业务逻辑
│   │   ├── models/      # 数据模型
│   │   ├── utils/       # 工具函数
│   │   └── main.py      # 应用入口
│   ├── data/            # 数据存储
│   │   ├── chromadb/    # 向量数据库
│   │   ├── sqlite/      # SQLite数据库
│   │   ├── graphs/      # 知识图谱
│   │   └── uploads/     # 上传文件
│   ├── tests/           # 测试
│   └── requirements.txt # Python依赖
├── frontend/            # 前端Next.js应用
│   ├── app/            # 页面路由
│   ├── components/     # UI组件
│   ├── lib/           # 工具库
│   ├── store/         # 状态管理
│   └── types/         # TypeScript类型
├── specs/             # 设计文档
└── docker-compose.yml # Docker配置
```

### 运行测试

```bash
# 后端测试
cd backend
pytest tests/ -v --cov=app --cov-report=html

# 前端测试
cd frontend
npm run test
```

### 代码规范

```bash
# Python代码格式化
cd backend
black app/
flake8 app/

# TypeScript代码格式化
cd frontend
npm run lint
npm run format
```

## 🗺️ 开发路线图

### Phase 1: Setup ✅ (已完成)
- 项目初始化
- 基础架构搭建

### Phase 2: Foundational (进行中)
- 数据库设计
- API基础设施
- 智谱AI集成

### Phase 3: MVP - 小说管理与基础问答
- 文件上传与解析
- 向量索引构建
- 基础RAG问答

### Phase 4-9: 功能增强
- 在线阅读
- 知识图谱
- Self-RAG增强
- 可视化分析
- 模型管理
- Token统计

### Phase 10: 打磨优化
- 性能优化
- 测试完善
- 文档补充

详见 [tasks.md](specs/master/tasks.md)

## 📄 文档

- [技术方案](specs/master/plan.md)
- [数据模型](specs/master/data-model.md)
- [API合约](specs/master/contracts/openapi.yaml)
- [研究笔记](specs/master/research.md)
- [任务清单](specs/master/tasks.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 许可证

本项目采用 MIT 许可证

## 🙏 致谢

- [智谱AI](https://open.bigmodel.cn/) - 提供GLM-4系列和Embedding-3模型
- [LangChain](https://www.langchain.com/) - RAG框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [HanLP](https://hanlp.hankcs.com/) - 中文NLP工具

## 📧 联系方式

如有问题或建议，请通过Issue联系我们。

---

**Status**: Phase 1 Setup ✅ 完成

**Last Updated**: 2025-11-13
