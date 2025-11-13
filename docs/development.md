# 网络小说智能问答系统 - 开发文档

## 📋 目录

1. [项目概述](#项目概述)
2. [架构设计](#架构设计)
3. [环境搭建](#环境搭建)
4. [开发指南](#开发指南)
5. [测试](#测试)
6. [部署](#部署)
7. [维护](#维护)

---

## 项目概述

### 技术栈

#### 后端
- **框架**: FastAPI 0.104+
- **语言**: Python 3.12+
- **依赖管理**: Poetry
- **数据库**: SQLite (SQLAlchemy ORM)
- **向量数据库**: ChromaDB
- **AI服务**: 智谱AI (zhipuai)
- **图谱**: NetworkX
- **NLP**: HanLP
- **文本处理**: LangChain, tiktoken

#### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript 5+
- **UI库**: React 18
- **样式**: Tailwind CSS 3
- **状态管理**: React Hooks
- **数据可视化**: ECharts, Cytoscape.js
- **HTTP客户端**: Fetch API

#### 开发工具
- **代码格式化**: Black (Python), Prettier (TypeScript)
- **代码检查**: Flake8, ESLint
- **类型检查**: MyPy, TypeScript
- **测试**: Pytest, Jest, Playwright
- **容器化**: Docker, Docker Compose

### 项目结构

```
novel_rag_spec_kit/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── health.py      # 健康检查
│   │   │   ├── novels.py      # 小说管理
│   │   │   ├── query.py       # 智能问答
│   │   │   ├── chapters.py    # 章节管理
│   │   │   ├── graph.py       # 图谱可视化
│   │   │   ├── config.py      # 模型配置
│   │   │   ├── stats.py       # 统计分析
│   │   │   └── websocket.py   # WebSocket
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── chromadb_client.py  # 向量数据库
│   │   │   ├── error_handlers.py   # 异常处理
│   │   │   └── logging.py     # 日志系统
│   │   ├── db/                # 数据库
│   │   │   ├── models.py      # ORM模型
│   │   │   └── init_db.py     # 数据库初始化
│   │   ├── middleware/        # 中间件
│   │   │   └── logging.py     # 请求日志
│   │   ├── schemas/           # Pydantic模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── novel_service.py      # 小说管理
│   │   │   ├── index_service.py      # 索引构建
│   │   │   ├── rag_engine.py         # RAG引擎
│   │   │   ├── graph_service.py      # 图谱服务
│   │   │   ├── embedding_service.py  # Embedding
│   │   │   ├── token_counter.py      # Token计数
│   │   │   └── nlp/           # NLP模块
│   │   │       ├── hanlp_client.py   # HanLP
│   │   │       └── entity_extractor.py
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试
│   ├── scripts/               # 工具脚本
│   ├── pyproject.toml         # Poetry配置
│   └── .env.example           # 环境变量示例
├── frontend/                  # 前端代码
│   ├── app/                   # Next.js App Router
│   │   ├── page.tsx           # 首页
│   │   ├── novels/            # 小说管理页面
│   │   ├── query/             # 问答页面
│   │   ├── reader/            # 阅读器页面
│   │   ├── graph/             # 可视化页面
│   │   └── settings/          # 设置页面
│   ├── components/            # React组件
│   ├── lib/                   # 工具函数
│   ├── types/                 # TypeScript类型
│   ├── public/                # 静态资源
│   ├── package.json           # NPM配置
│   └── tsconfig.json          # TypeScript配置
├── docs/                      # 文档
│   ├── user-guide.md          # 用户手册
│   ├── development.md         # 开发文档
│   └── deployment.md          # 部署文档
├── docker-compose.yml         # Docker编排
└── README.md                  # 项目说明
```

---

## 架构设计

### 系统架构

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       ├───────────────────┐
       │                   │
┌──────▼───────┐   ┌──────▼──────┐
│  Next.js     │   │   FastAPI   │
│  Frontend    │   │   Backend   │
└──────────────┘   └──────┬──────┘
                          │
                ┌─────────┼─────────┐
                │         │         │
         ┌──────▼───┐ ┌──▼────┐ ┌─▼──────┐
         │ ChromaDB │ │SQLite │ │HanLP   │
         └──────────┘ └───────┘ └────────┘
                │
         ┌──────▼───────┐
         │  ZhipuAI API │
         └──────────────┘
```

### RAG工作流程

1. **索引阶段**（小说上传时）
   ```
   小说文件 → 文本提取 → 章节分割 → 文本分块 → 
   Embedding生成 → ChromaDB存储 → 实体提取 → 
   知识图谱构建 → 元数据索引
   ```

2. **查询阶段**（用户提问时）
   ```
   用户问题 → 查询路由 → 多路检索:
     ├─ 语义检索 (ChromaDB)
     ├─ 关键词检索 (BM25)
     └─ 图谱检索 (NetworkX)
   → 结果融合 → 上下文构建 → Self-RAG处理:
     ├─ 断言提取
     ├─ 证据收集
     ├─ 一致性检查
     └─ 矛盾检测
   → LLM生成 → 答案修正 → 流式返回
   ```

### 数据模型

#### SQLite数据库

**novels表**（小说基本信息）
```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    word_count INTEGER,
    chapter_count INTEGER,
    file_path TEXT,
    file_type TEXT,
    uploaded_at DATETIME,
    indexed_at DATETIME,
    index_status TEXT
);
```

**chapters表**（章节信息）
```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    chapter_number INTEGER,
    title TEXT,
    content TEXT,
    word_count INTEGER,
    FOREIGN KEY (novel_id) REFERENCES novels(id)
);
```

**query_history表**（查询历史）
```sql
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    query_text TEXT,
    answer TEXT,
    created_at DATETIME,
    model TEXT,
    token_usage JSON
);
```

#### ChromaDB集合

- **collection名称**: `novel_{novel_id}`
- **文档ID**: `{chapter_id}_{chunk_id}`
- **元数据**:
  ```python
  {
      "novel_id": int,
      "chapter_id": int,
      "chapter_number": int,
      "chapter_title": str,
      "chunk_index": int,
      "start_position": int,
      "end_position": int
  }
  ```

#### 知识图谱

- **节点类型**: Character（角色）、Location（地点）、Event（事件）
- **边类型**: Relationship（关系）、Interaction（交互）、Sequence（时序）
- **属性**:
  ```python
  # 节点
  {
      "name": str,
      "type": str,
      "first_appearance": int,  # 章节号
      "description": str,
      "mentions": int
  }
  
  # 边
  {
      "relation_type": str,
      "strength": float,  # 0-1
      "chapters": List[int],  # 出现章节
      "evidence": List[str]
  }
  ```

---

## 环境搭建

### 1. 克隆代码

```bash
git clone <repository-url>
cd novel_rag_spec_kit
```

### 2. 后端环境

#### 安装Python 3.12+

```bash
# Windows (使用Python官网安装器)
# macOS (使用Homebrew)
brew install python@3.12
# Linux (Ubuntu/Debian)
sudo apt install python3.12 python3.12-venv
```

#### 安装Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### 安装依赖

```bash
cd backend
poetry install
```

#### 配置环境变量

```bash
cp .env.example .env
```

编辑`.env`文件：
```ini
# 智谱AI配置
ZHIPU_API_KEY=your_api_key_here

# 应用配置
APP_NAME="网络小说智能问答系统"
APP_VERSION="0.1.0"
DEBUG=true
LOG_LEVEL=INFO

# 服务端口
HOST=0.0.0.0
PORT=8000

# 数据目录
DATA_DIR=./data
UPLOAD_DIR=./data/uploads
DB_PATH=./data/database.db

# ChromaDB配置
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_PERSIST_DIR=./data/chromadb

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 初始化数据库

```bash
poetry run python -m app.db.init_db
```

### 3. 前端环境

#### 安装Node.js 18+

```bash
# 使用nvm
nvm install 18
nvm use 18
```

#### 安装依赖

```bash
cd frontend
npm install
```

#### 配置环境变量

```bash
cp .env.example .env.local
```

编辑`.env.local`文件：
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 4. 启动开发服务器

#### 启动后端

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端

```bash
cd frontend
npm run dev
```

访问：
- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/docs

---

## 开发指南

### 后端开发

#### 添加新的API端点

1. 在`app/schemas/`中定义请求/响应模型
   ```python
   # app/schemas/example.py
   from pydantic import BaseModel
   
   class ExampleRequest(BaseModel):
       query: str
       limit: int = 10
   
   class ExampleResponse(BaseModel):
       result: str
       count: int
   ```

2. 在`app/api/`中创建路由
   ```python
   # app/api/example.py
   from fastapi import APIRouter, Depends
   from app.schemas.example import ExampleRequest, ExampleResponse
   from app.core.logging import get_logger
   
   router = APIRouter(prefix="/example", tags=["示例"])
   logger = get_logger(__name__)
   
   @router.post("/action", response_model=ExampleResponse)
   async def perform_action(request: ExampleRequest):
       logger.info("Processing request", query=request.query)
       # 业务逻辑
       return ExampleResponse(result="success", count=1)
   ```

3. 在`app/main.py`中注册路由
   ```python
   from app.api import example
   app.include_router(example.router)
   ```

#### 使用日志系统

```python
from app.core.logging import get_logger, log_llm_call, log_db_query

logger = get_logger(__name__)

# 基础日志
logger.info("操作成功", user_id=123, action="upload")
logger.error("操作失败", error=str(e))

# 专用日志
log_llm_call(
    model="glm-4-flash",
    prompt_tokens=100,
    completion_tokens=50,
    duration_ms=1200.5
)

log_db_query(
    operation="select",
    collection="novels",
    duration_ms=45.2,
    result_count=10
)
```

#### 错误处理

```python
from app.core.error_handlers import (
    CustomException, 
    DatabaseError, 
    ModelNotFoundError
)

# 抛出自定义异常
if not novel:
    raise DatabaseError("小说不存在")

if model_name not in SUPPORTED_MODELS:
    raise ModelNotFoundError(model_name)
```

#### 添加新的Service

```python
# app/services/example_service.py
from app.core.logging import get_logger
from app.db.models import Novel
from sqlalchemy.orm import Session

logger = get_logger(__name__)

class ExampleService:
    def __init__(self, db: Session):
        self.db = db
    
    def process(self, novel_id: int) -> dict:
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise ValueError(f"Novel {novel_id} not found")
        
        # 处理逻辑
        logger.info("Processing novel", novel_id=novel_id)
        return {"status": "success"}
```

### 前端开发

#### 创建新页面

```tsx
// app/example/page.tsx
'use client';

import { useState } from 'react';

export default function ExamplePage() {
  const [data, setData] = useState(null);
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold">示例页面</h1>
      {/* 页面内容 */}
    </div>
  );
}
```

#### 创建新组件

```tsx
// components/ExampleComponent.tsx
import { FC } from 'react';

interface ExampleProps {
  title: string;
  onAction: () => void;
}

export const ExampleComponent: FC<ExampleProps> = ({ title, onAction }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-semibold">{title}</h2>
      <button 
        onClick={onAction}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        执行操作
      </button>
    </div>
  );
};
```

#### API调用

```typescript
// lib/api/example.ts
import { API_BASE_URL } from '@/lib/config';

export interface ExampleRequest {
  query: string;
  limit?: number;
}

export interface ExampleResponse {
  result: string;
  count: number;
}

export async function performAction(
  request: ExampleRequest
): Promise<ExampleResponse> {
  const response = await fetch(`${API_BASE_URL}/example/action`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}
```

#### 类型定义

```typescript
// types/example.ts
export interface ExampleData {
  id: number;
  name: string;
  created_at: string;
}

export type ExampleStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ExampleState {
  data: ExampleData[];
  status: ExampleStatus;
  error: string | null;
}
```

---

## 测试

### 后端测试

#### 单元测试

```bash
cd backend
poetry run pytest tests/unit/ -v
```

示例测试：
```python
# tests/unit/test_token_counter.py
import pytest
from app.services.token_counter import count_tokens

def test_count_tokens():
    text = "这是一个测试"
    count = count_tokens(text)
    assert count > 0
    assert isinstance(count, int)
```

#### 集成测试

```bash
poetry run pytest tests/integration/ -v
```

示例测试：
```python
# tests/integration/test_novel_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_novel():
    with open("test_data/sample.txt", "rb") as f:
        response = client.post(
            "/novels/upload",
            files={"file": ("sample.txt", f, "text/plain")}
        )
    assert response.status_code == 200
    assert "id" in response.json()
```

#### 覆盖率

```bash
poetry run pytest --cov=app --cov-report=html
```

查看报告：`backend/htmlcov/index.html`

### 前端测试

#### 单元测试（Jest）

```bash
cd frontend
npm run test
```

示例测试：
```typescript
// __tests__/components/ExampleComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ExampleComponent } from '@/components/ExampleComponent';

describe('ExampleComponent', () => {
  it('renders correctly', () => {
    const onAction = jest.fn();
    render(<ExampleComponent title="Test" onAction={onAction} />);
    
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
  
  it('calls onAction when button is clicked', () => {
    const onAction = jest.fn();
    render(<ExampleComponent title="Test" onAction={onAction} />);
    
    fireEvent.click(screen.getByText('执行操作'));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
});
```

#### E2E测试（Playwright）

```bash
npm run test:e2e
```

示例测试：
```typescript
// tests/e2e/query.spec.ts
import { test, expect } from '@playwright/test';

test('智能问答流程', async ({ page }) => {
  await page.goto('http://localhost:3000/query');
  
  // 选择小说
  await page.selectOption('#novel-select', '1');
  
  // 输入问题
  await page.fill('#query-input', '主角是谁？');
  
  // 点击提交
  await page.click('#submit-button');
  
  // 等待答案
  await page.waitForSelector('.answer-box');
  
  // 验证答案
  const answer = await page.textContent('.answer-box');
  expect(answer).not.toBeNull();
  expect(answer.length).toBeGreaterThan(0);
});
```

---

## 部署

参见 [deployment.md](./deployment.md) 详细部署指南。

### Docker部署（快速）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 维护

### 日志管理

日志位置：
- 开发环境：控制台输出
- 生产环境：`backend/logs/app.log`（JSON格式）

日志级别：
- `DEBUG`: 详细调试信息
- `INFO`: 常规操作信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 数据备份

```bash
# 备份SQLite数据库
cp backend/data/database.db backend/data/database.db.backup

# 备份ChromaDB
cp -r backend/data/chromadb backend/data/chromadb.backup

# 备份上传文件
tar -czf uploads_backup.tar.gz backend/data/uploads
```

### 性能监控

关键指标：
- API响应时间（中位数<500ms）
- LLM调用延迟（中位数<3s）
- 数据库查询时间（中位数<100ms）
- 内存使用（<4GB）
- 磁盘使用（监控增长趋势）

监控工具：
- 后端日志中的`duration_ms`字段
- FastAPI `/health/detailed` 端点
- 系统资源监控（htop/Activity Monitor）

### 常见问题排查

#### 1. ChromaDB无法启动
```bash
# 清理锁文件
rm backend/data/chromadb/chroma.sqlite3-wal
rm backend/data/chromadb/chroma.sqlite3-shm
```

#### 2. HanLP下载失败
```bash
# 设置镜像源
export HANLP_HOME=/path/to/hanlp_cache
# 手动下载模型到缓存目录
```

#### 3. Token消耗异常
```bash
# 检查日志中的LLM调用
grep "llm.call" backend/logs/app.log | jq .total_tokens
```

---

## 代码风格

### Python（Black + Flake8）

```bash
# 格式化代码
poetry run black app/

# 检查代码
poetry run flake8 app/
```

### TypeScript（Prettier + ESLint）

```bash
# 格式化代码
npm run format

# 检查代码
npm run lint
```

---

## 贡献指南

1. Fork项目
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送分支（`git push origin feature/AmazingFeature`）
5. 提交Pull Request

---

**最后更新**: 2025-11-13  
**文档版本**: v1.0  
**维护者**: Development Team

