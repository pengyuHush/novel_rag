# 小说 RAG 分析系统 - Web 前端

<div align="center">

[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7.1.7-646CFF.svg)](https://vitejs.dev/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-5.28.0-1890FF.svg)](https://ant.design/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个专注于**中文长篇小说**的智能检索与分析平台

[功能特性](#功能特性) • [快速开始](#快速开始) • [技术架构](#技术架构) • [开发指南](#开发指南) • [部署说明](#部署说明)

</div>

---

## 📖 项目简介

小说 RAG 分析系统是一个基于 RAG（Retrieval Augmented Generation）技术的中文小说智能分析平台，为小说爱好者和内容创作者提供强大的文本检索、智能问答、人物关系分析等功能。

### 核心亮点

- 📚 **海量支持**：支持处理 300 万字以上的超长篇小说
- 🔍 **智能检索**：基于语义理解的自然语言问答
- 🎨 **关系图谱**：自动生成交互式人物关系网络
- 📱 **响应式设计**：完美适配桌面和移动设备
- 🌐 **后端集成**：与 FastAPI 后端完全集成，支持大文件处理
- 🎯 **精准定位**：搜索结果直接定位到原文段落和章节
- 🔄 **异步处理**：基于小说ID的状态轮询机制
- 💾 **后端存储**：所有数据存储在后端，支持跨设备同步

---

## ✨ 功能特性

### 1. 小说管理

- ✅ 支持 TXT 格式中文小说导入（UTF-8、GBK、GB2312 编码）
- ✅ 自动检测文件编码
- ✅ 智能识别章节结构（第X章、第X回等格式）
- ✅ 小说信息编辑（书名、作者、简介、标签）
- ✅ 存储空间管理和统计
- ✅ 拖拽上传支持

### 2. 智能搜索与问答

- ✅ 自然语言问题输入
- ✅ 多小说联合检索
- ✅ 最近查询记录（简单存储）
- ✅ 搜索结果展示：
  - 智能回答生成
  - 原文段落引用
  - 章节位置定位
  - 一键跳转阅读

### 3. 人物关系图谱

- ✅ 交互式力导向图可视化
- ✅ 人物节点：
  - 姓名、角色、描述
  - 出场次数统计
  - 节点大小反映重要程度
- ✅ 关系边：
  - 关系类型（朋友、敌人、师徒等）
  - 关系强度可视化
- ✅ 图谱操作：
  - 拖拽移动
  - 缩放控制
  - 节点筛选
  - 悬停查看详情

### 4. 章节阅读器

- ✅ 左侧章节目录导航
- ✅ 自定义阅读体验：
  - 字体大小调节（14px - 24px）
  - 行高调节（1.5 - 2.5）
  - 多种主题色（米黄、护眼绿、淡蓝、纸白、暗夜）
- ✅ 阅读进度记忆
- ✅ 段落高亮定位（支持从搜索结果跳转）
- ✅ 章节快速切换

### 5. 响应式设计

- ✅ 桌面端：多栏布局，侧边栏导航
- ✅ 移动端：
  - 底部抽屉式导航
  - 悬浮按钮快速访问
  - 触摸友好的交互设计
  - 自适应字体和间距

---

## 🏗️ 技术架构

### 技术栈

```
前端框架：React 19.1.1 + TypeScript 5.9.3
构建工具：Vite 7.1.7
UI 组件库：Ant Design 5.28.0
状态管理：Zustand 5.0.8
路由管理：React Router 7.9.5
数据可视化：React Force Graph 2D 1.29.0
文件处理：jschardet 3.1.4
API 客户端：Fetch API + 自定义封装（支持 Mock 模式）
时间处理：dayjs 1.11.19
后端集成：FastAPI + LangChain API
开发模式：Mock API 系统（预置数据 + 模拟延迟）
```

### 架构设计

```
frontend/
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 根组件（路由配置、主题配置）
│   ├── App.css               # 全局样式
│   ├── index.css             # 基础样式
│   │
│   ├── pages/                # 页面组件
│   │   ├── SearchPage.tsx    # 搜索与问答主页（含小说管理）
│   │   ├── GraphPage.tsx     # 人物关系图谱页
│   │   └── ReaderPage.tsx    # 章节阅读器页
│   │
│   ├── components/           # 通用组件
│   │   ├── ImportNovelModal.tsx    # 导入小说弹窗（支持状态轮询）
│   │   └── EditNovelModal.tsx      # 编辑小说信息弹窗
│   │
│   ├── store/                # 状态管理
│   │   └── useStore.ts       # Zustand 全局状态
│   │
│   ├── types/                # TypeScript 类型定义
│   │   └── index.ts          # 数据模型类型（匹配后端API）
│   │
│   └── utils/                # 工具函数
│       ├── api.ts            # API 客户端（支持 Mock/真实 API 切换）
│       ├── mockApi.ts        # Mock API 实现（前端独立开发用）
│       ├── mockData.ts       # Mock 数据生成器（预置小说、搜索结果等）
│       ├── textProcessing.ts # 文本处理（编码检测、章节识别）
│       └── constants.ts      # 常量配置
│
├── public/                   # 静态资源
├── index.html                # HTML 模板
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── package.json              # 项目依赖
└── README.md                 # 项目文档
```

### 数据模型

#### Novel（小说）- 匹配后端API
```typescript
interface Novel {
  id: string;                    // 唯一标识符
  title: string;                 // 书名
  author?: string;               // 作者
  description?: string;          // 简介
  tags: string[];                // 标签
  wordCount: number;             // 总字数
  chapterCount: number;          // 章节数量
  status: 'pending' | 'processing' | 'completed' | 'failed'; // 处理状态
  importedAt: string;            // 导入时间 (ISO 8601)
  updatedAt: string;             // 更新时间 (ISO 8601)
  hasGraph: boolean;             // 是否已生成关系图谱
}
```

#### Chapter（章节）- 匹配后端API
```typescript
interface Chapter {
  id: string;              // 章节标识符
  novelId: string;         // 所属小说ID
  chapterNumber: number;   // 章节序号
  title: string;           // 章节标题
  startPosition: number;   // 起始位置
  endPosition: number;     // 结束位置
  wordCount: number;       // 章节字数
}
```

#### NovelProcessingStatus（小说处理状态）
```typescript
interface NovelProcessingStatus {
  novelId: string;                    // 小说ID
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;                   // 处理进度 0-100
  message: string;                    // 当前状态描述
  stage: 'uploading' | 'detecting_chapters' | 'vectorizing' | 'completed';
  processedWords: number;             // 已处理字数
  totalWords: number;                 // 总字数
  estimatedTimeRemaining: number;     // 预计剩余时间
  updatedAt: string;                  // 更新时间 (ISO 8601)
}
```

#### CharacterGraph（人物关系图）- 匹配后端API
```typescript
interface CharacterGraph {
  id: string;                         // 图谱标识符
  novelId: string;                    // 所属小说ID
  characters: Character[];            // 人物列表
  relationships: Relationship[];      // 关系列表
  generatedAt: string;                // 生成时间 (ISO 8601)
  version: string;                    // 版本号
}

interface Character {
  id: string;                         // 人物标识符
  name: string;                       // 姓名
  aliases: string[];                  // 别名/称号
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  description: string;                // 人物描述
  appearances: number;                // 出场次数
  importance: number;                 // 重要程度 0-1
  firstAppearance: {                  // 首次出场
    chapterId: string;
    chapterTitle: string;
  };
  attributes: Record<string, any>;    // 自定义属性
}

interface Relationship {
  id: string;                         // 关系标识符
  source: string;                     // 源人物ID
  target: string;                     // 目标人物ID
  type: 'family' | 'friend' | 'enemy' | 'master-disciple' | 'lover' | 'ally' | 'rival';
  description: string;                // 关系描述
  strength: number;                   // 关系强度 0-10
  evidence: Array<{                   // 关系证据
    chapterId: string;
    context: string;
  }>;
}
```

### 状态管理

使用 Zustand 管理全局状态：

```typescript
interface AppState {
  novels: Novel[];                        // 小说列表
  selectedNovelIds: string[];             // 当前选中的小说ID
  currentSearchResult: SearchResult | null; // 当前搜索结果
  recentQueries: string[];                 // 最近查询记录
  processingStatuses: Record<string, NovelProcessingStatus>; // 处理状态

  // 状态
  loading: boolean;                       // 全局加载状态
  searching: boolean;                      // 搜索状态

  // Actions
  setNovels: (novels: Novel[]) => void;
  setSelectedNovelIds: (ids: string[]) => void;
  setCurrentSearchResult: (result: SearchResult | null) => void;
  addRecentQuery: (query: string) => void;
  setProcessingStatus: (novelId: string, status: NovelProcessingStatus) => void;
}
```

### API 客户端架构

使用自定义的 API 客户端与后端 FastAPI 集成：

```typescript
// API 模块
- novelAPI: 小说管理
  - createNovel: 创建小说记录
  - uploadNovelFile: 上传文件到已创建的小说
  - uploadNovel: 便捷方法（一步完成创建+上传）
  - getAllNovels: 获取所有小说
  - getNovel: 获取单个小说详情
  - updateNovel: 更新小说信息
  - deleteNovel: 删除小说
  - getProcessingStatus: 获取处理状态
  - validateFile: 文件预验证（新增）
  - getChapters: 获取章节列表
  - getChapter: 获取章节内容（含段落信息）
  
- searchAPI: 搜索与问答
  - search: 智能搜索（POST方法，支持语义和关键词搜索）
  
- graphAPI: 人物关系图谱
  - getGraph: 获取图谱
  - generateGraph: 生成图谱
  - deleteGraph: 删除图谱
  - getCharacters: 获取人物列表
  
- systemAPI: 系统管理（新增）
  - checkHealth: 健康检查
  - getSystemInfo: 系统信息
  
- apiUtils: 通用工具
  - formatFileSize: 格式化文件大小
  - formatWordCount: 格式化字数
  - getStorageInfo: 获取存储统计
  - pollStatus: 轮询任务状态
```

**特点：**
- 基于 Fetch API 的现代化 HTTP 客户端
- 统一的错误处理机制（APIError）
- 类型安全的请求/响应处理
- 自动状态轮询机制
- 支持匿名访问（MVP版本）
- RESTful API 设计（包含 `/api/v1` 版本前缀）
- POST方法用于搜索和上传操作
- 完全后端数据存储，无 IndexedDB 依赖

---

## 🚀 快速开始

### 前置要求

确保你的开发环境已安装：

- **Node.js** >= 18.0.0
- **npm** >= 9.0.0 或 **yarn** >= 1.22.0 或 **pnpm** >= 8.0.0

### 安装依赖

```bash
# 进入前端项目目录
cd frontend

# 使用 npm 安装
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

### 环境配置

**重要：** 在启动开发服务器前，必须配置后端API地址。

```bash
# 方式一：复制示例配置文件
cp .env.example .env

# 方式二：手动创建环境配置文件
```

创建 `.env` 文件并配置：
```env
# 后端API服务地址（包含 /api/v1 版本前缀）
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Mock API 模式（可选，用于前端独立开发）
# true: 使用 Mock 数据，无需后端服务
# false: 使用真实后端 API（默认）
VITE_USE_MOCK_API=false

# 应用标题
VITE_APP_TITLE=小说RAG分析系统
```

**注意：** 确保后端服务正在运行，并且CORS配置正确。

### Mock API 模式（前端独立开发）

如果后端尚未开发完成，可以启用 Mock 模式进行前端开发和功能预览：

**1. 创建 `.env.development` 文件**：
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API=true
```

**2. 启动开发服务器**：
```bash
npm run dev
```

**Mock 模式特性**：
- ✅ **预置数据**：包含 3 部示例小说（修仙传奇、都市风云、星际争霸）
- ✅ **完整功能**：支持所有前端功能（导入、搜索、关系图、阅读）
- ✅ **模拟延迟**：200ms-1000ms 网络延迟，模拟真实体验
- ✅ **异步任务**：模拟文件上传、图谱生成等长任务
- ⚠️ **数据重置**：刷新页面后数据恢复为预置状态

**切换到真实 API**：
```env
# 修改 .env.development
VITE_USE_MOCK_API=false
```

重启开发服务器即可。

### 开发模式运行

```bash
# 启动开发服务器
npm run dev

# 或
yarn dev

# 或
pnpm dev
```

开发服务器将在 `http://localhost:5173` 启动（端口可能因环境而异）。

页面会自动打开，任何代码修改都会触发**热更新**（HMR）。

### 代码检查

```bash
# 运行 ESLint 检查
npm run lint

# 或
yarn lint
```

### 构建生产版本

```bash
# 构建生产版本
npm run build

# 或
yarn build
```

构建产物将输出到 `dist/` 目录。

### 本地预览生产版本

```bash
# 预览构建后的版本
npm run preview

# 或
yarn preview
```

---

## 🛠️ 开发指南

### 项目初始化流程

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd novel_rag/frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

4. **浏览器访问**
   - 打开 `http://localhost:5173`
   - 使用"导入新小说"功能上传 TXT 文件测试

### 开发建议

#### 代码风格

项目使用 **ESLint** + **TypeScript** 确保代码质量：

- 遵循 React Hooks 规范
- 使用函数式组件和 Hooks
- 优先使用 TypeScript 类型注解
- 组件和函数使用清晰的命名

#### 组件开发规范

```typescript
// ✅ 推荐：函数式组件 + TypeScript + 解构 props
interface MyComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onSubmit }) => {
  // 组件逻辑
  return <div>{title}</div>;
};
```

#### 状态管理最佳实践

- **局部状态**：使用 `useState`、`useReducer`
- **全局状态**：使用 Zustand store
- **持久化数据**：通过 Dexie.js 存入 IndexedDB

#### 性能优化建议

- 使用 `React.memo` 避免不必要的重渲染
- 使用 `useMemo` 和 `useCallback` 缓存计算结果和回调函数
- 大列表使用虚拟滚动（如需要可引入 `react-window`）
- 图片和资源使用懒加载

### 添加新页面

1. 在 `src/pages/` 创建新页面组件
2. 在 `App.tsx` 的路由配置中添加路由
3. 更新导航菜单（如需要）

示例：

```typescript
// src/pages/NewPage.tsx
export const NewPage: React.FC = () => {
  return <div>新页面</div>;
};

// src/App.tsx
<Routes>
  {/* 现有路由 */}
  <Route path="/new-page" element={<NewPage />} />
</Routes>
```

### 添加新功能

1. 定义 TypeScript 类型（`src/types/index.ts`）
2. 添加数据库表（如需要，`src/utils/db.ts`）
3. 实现工具函数（`src/utils/`）
4. 更新 Zustand store（如需全局状态）
5. 开发 UI 组件

### 调试技巧

#### React DevTools

安装浏览器扩展：
- [React Developer Tools](https://react.dev/learn/react-developer-tools)

#### IndexedDB 调试

1. 打开浏览器开发者工具
2. 切换到 **Application** 标签（Chrome）或 **Storage** 标签（Firefox）
3. 查看 **IndexedDB** → `NovelDatabase`

#### Vite 开发服务器配置

编辑 `vite.config.ts` 自定义开发服务器：

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,        // 自定义端口
    open: true,        // 自动打开浏览器
    host: '0.0.0.0',   // 允许局域网访问
  },
});
```

---

## 📦 部署说明

### 方式一：使用 Vercel 部署（推荐）

**步骤：**

1. 在 [Vercel](https://vercel.com) 注册账号
2. 连接 GitHub 仓库
3. 配置构建设置：
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. 点击 **Deploy**

**优势：**
- 自动 CI/CD
- 全球 CDN 加速
- HTTPS 支持
- 自定义域名

### 方式二：使用 Netlify 部署

**步骤：**

1. 在 [Netlify](https://www.netlify.com) 注册账号
2. 连接 GitHub 仓库
3. 配置构建设置：
   - **Base Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `frontend/dist`
4. 点击 **Deploy**

### 方式三：传统服务器部署

#### 1. 构建生产版本

```bash
cd frontend
npm run build
```

#### 2. 部署到服务器

将 `dist/` 目录内容上传到服务器（如通过 FTP、SCP）：

```bash
# 使用 scp 上传
scp -r dist/* user@your-server.com:/var/www/html/
```

#### 3. 配置 Nginx

创建 Nginx 配置文件：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    # 支持 React Router 的单页应用路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 压缩传输
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

重启 Nginx：

```bash
sudo nginx -t          # 检查配置
sudo systemctl restart nginx
```

#### 4. 配置 Apache

创建 `.htaccess` 文件在 `dist/` 目录：

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

### 方式四：使用 Docker 容器化部署

#### 1. 创建 Dockerfile

在 `frontend/` 目录创建 `Dockerfile`：

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建 nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

#### 3. 构建和运行容器

```bash
# 构建镜像
docker build -t novel-rag-frontend .

# 运行容器
docker run -d -p 80:80 --name novel-rag-app novel-rag-frontend
```

#### 4. 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: unless-stopped
```

运行：

```bash
docker-compose up -d
```

### 环境变量配置

**必须配置**后端 API 地址，创建 `.env` 文件：

#### 开发环境配置

**方式一：使用预设环境文件**
```bash
# 复制开发环境配置文件
cp .env.example .env.development

# 或直接创建 .env.development 文件
```

**方式二：手动创建 `.env` 文件**
```env
# 后端API服务地址（包含 /api/v1 版本前缀）
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用标题
VITE_APP_TITLE=小说RAG分析系统
```

#### 生产环境配置

创建生产环境配置文件 `.env.production`：
```env
# 生产环境API地址（包含 /api/v1 版本前缀）
VITE_API_BASE_URL=https://your-api-domain.com/api/v1

# 生产环境应用标题
VITE_APP_TITLE=小说RAG分析系统
```

#### 环境变量说明

| 变量名 | 说明 | 开发环境默认值 | 生产环境示例 |
|--------|------|---------------|-------------|
| `VITE_API_BASE_URL` | 后端API服务地址（含版本前缀） | `http://localhost:8000/api/v1` | `https://your-api-domain.com/api/v1` |
| `VITE_APP_TITLE` | 应用标题 | `小说RAG分析系统` | `小说RAG分析系统` |

#### 在代码中使用

```typescript
// 获取API基础地址
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

// 获取应用标题
const appTitle = import.meta.env.VITE_APP_TITLE;

// 环境检测
const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;
```

#### 配置文件优先级

Vite 按以下优先级加载环境变量：
1. `.env.production`（生产环境）
2. `.env.development`（开发环境）
3. `.env`（通用配置）
4. `.env.example`（示例配置，不会被加载）

#### CORS 配置说明

**重要：** 后端API必须配置正确的 CORS 策略以支持前端跨域访问。

**开发环境 CORS 配置**（后端需要配置）：
```python
# FastAPI CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:3000",  # 备用端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**常见问题解决**：

1. **CORS 错误**：确保前端域名在后端 CORS 允许列表中
2. **API 连接失败**：检查 `VITE_API_BASE_URL` 配置是否正确
3. **环境变量不生效**：确保变量名以 `VITE_` 开头，重启开发服务器

#### **重要提示：**
- ✅ 必须配置 `VITE_API_BASE_URL` 指向后端服务
- ✅ 环境变量必须以 `VITE_` 开头才能被 Vite 识别
- ✅ 生产环境需要替换为实际的API域名
- ⚠️ 前端环境变量会暴露在浏览器中，不要存储敏感信息
- ✅ 修改环境变量后需要重启开发服务器才能生效
- ✅ 使用 `npm run dev` 启动时自动加载开发环境配置

---

## 🌐 浏览器兼容性

### 支持的浏览器

| 浏览器 | 最低版本 | 推荐版本 |
|--------|---------|---------|
| Chrome | 90+ | 最新版 |
| Firefox | 88+ | 最新版 |
| Safari | 14+ | 最新版 |
| Edge | 90+ | 最新版 |

### 核心功能依赖

- **Fetch API**：HTTP 请求（所有现代浏览器支持）
- **File API**：用于文件上传
- **ES2020**：现代 JavaScript 特性
- **CSS Grid & Flexbox**：响应式布局
- **后端 API 连接**：需要运行 FastAPI 后端服务

### 已知限制

- ❌ 不支持 IE 11 及更早版本
- ⚠️ Safari 旧版本可能在文件编码检测上有兼容问题
- ⚠️ 移动端浏览器建议使用 Chrome 或 Safari
- ⚠️ 需要稳定的网络连接与后端 API 通信
- ⚠️ 大文件上传受网络环境和服务端限制

---

## 📱 移动端适配

### 响应式断点

```css
/* 移动端 */
@media (max-width: 768px) {
  /* 移动端样式 */
}

/* 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  /* 平板样式 */
}

/* 桌面 */
@media (min-width: 1025px) {
  /* 桌面样式 */
}
```

### 移动端特性

- 侧边栏转为底部抽屉（Drawer）
- 悬浮按钮（FloatButton）快速访问
- 触摸友好的按钮和交互区域
- 自适应字体和间距
- 禁用桌面端悬停效果

### 测试设备

推荐在以下设备测试：

- iPhone 12/13/14（iOS Safari）
- Samsung Galaxy S21/S22（Chrome Android）
- iPad Pro（Safari）
- 各种 Android 平板

---

## 🔧 常见问题

### Q1：导入的小说显示乱码怎么办？

**A**：项目支持自动检测编码（UTF-8、GBK、GB2312），如果仍然乱码：
1. 检查文件是否为纯文本 TXT 格式
2. 尝试使用文本编辑器转换为 UTF-8 编码
3. 确保文件没有损坏

### Q2：小说上传失败或处理卡住？

**A**：检查以下几点：
1. 确认后端服务正在运行（`http://localhost:8000`）
2. 检查网络连接是否稳定
3. 文件大小是否超过后端限制（默认50MB）
4. 查看浏览器控制台的错误信息

### Q3：上传后一直显示"处理中"？

**A**：大文件处理需要时间：
1. 系统会自动轮询处理状态，请耐心等待
2. 处理过程中可以看到进度条和状态信息
3. 如果长时间无响应，检查后端服务状态

### Q4：搜索功能无结果？

**A**：确保以下条件满足：
1. 至少选择一部小说进行搜索
2. 小说必须完成处理（状态为"completed"）
3. 后端搜索服务正常运行
4. 网络连接正常

### Q5：人物关系图谱无法生成？

**A**：图谱生成需要：
1. 小说已完成向量化处理
2. 后端图谱生成服务运行正常
3. 处理时间可能较长，请等待完成

### Q6：如何配置后端地址？

**A**：在项目根目录创建 `.env` 文件：
```env
VITE_API_BASE_URL=http://your-backend-url:8000/api/v1
```

### Q7：前端的小说数据存储在哪里？

**A**：所有数据存储在后端服务器：
- 小说内容存储在服务器数据库中（SQLite）
- 前端仅缓存UI配置和临时状态
- 数据更安全，支持跨设备同步

### Q8：为什么开发服务器启动慢？

**A**：Vite 首次启动需要预构建依赖：
```bash
# 手动预构建
npm run dev -- --force
```

### Q9：生产构建后样式丢失？

**A**：检查部署配置：
- 确保 `dist/` 目录完整上传
- 检查服务器是否正确处理静态资源
- 验证 CSS 文件路径是否正确

### Q10：移动端体验不佳？

**A**：
- 确保使用现代浏览器（Chrome/Safari）
- 检查视口设置：`<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- 关闭浏览器的"桌面网站"模式

---

## 🎨 主题定制

### 修改主题色

编辑 `src/App.tsx` 中的 `ConfigProvider` 配置：

```typescript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#8B7355',      // 主色调
      colorBgBase: '#F5E6D3',        // 背景色
      fontFamily: "'Noto Serif SC', 'Source Han Serif SC', serif",
    },
    components: {
      Layout: {
        headerBg: '#E8D5C4',         // 头部背景
        bodyBg: '#F5E6D3',           // 主体背景
      },
    },
  }}
>
```

### 修改阅读器主题

编辑 `src/pages/ReaderPage.tsx` 中的 `THEME_STYLES`：

```typescript
const THEME_STYLES = {
  cream: { background: '#F5E6D3', color: '#2C2416' },
  green: { background: '#E8F5E9', color: '#1B5E20' },
  blue: { background: '#E3F2FD', color: '#0D47A1' },
  white: { background: '#FFFFFF', color: '#212121' },
  dark: { background: '#1E1E1E', color: '#E0E0E0' },
};
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. **Fork 项目**
2. **创建分支**：`git checkout -b feature/your-feature`
3. **提交更改**：`git commit -m 'Add some feature'`
4. **推送分支**：`git push origin feature/your-feature`
5. **创建 Pull Request**

### 代码规范

- 遵循 ESLint 规则
- 编写清晰的提交信息
- 添加必要的注释和文档
- 确保代码通过 `npm run lint`

### 报告问题

在 GitHub Issues 中报告问题时，请提供：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 浏览器和版本信息
- 截图（如适用）

---

## 📝 开发路线图

### 当前版本（v2.0）- MVP 后端集成版

- ✅ 完整的后端 API 集成（FastAPI + LangChain）
- ✅ 真实的语义搜索和问答
- ✅ 基于小说ID的状态轮询机制
- ✅ 后端数据存储（SQLite + Qdrant）
- ✅ 匿名访问（简化用户体验）
- ✅ 异步文件处理和进度跟踪
- ✅ 响应式设计
- ✅ 移除 IndexedDB 依赖

### 未来版本

#### v2.1 - 功能完善

- [ ] 章节内容加载优化
- [ ] 人物关系图谱实时生成
- [ ] 搜索结果相关性优化

#### v2.2 - 用户体验增强

- [ ] 用户认证系统（可选）
- [ ] 个人收藏和书签
- [ ] 阅读历史记录
- [ ] 搜索历史管理

#### v2.3 - 高级分析功能

- [ ] 多小说关联分析
- [ ] 情节时间线可视化
- [ ] 阅读统计和报告
- [ ] 情感分析

#### v3.0 - 平台化

- [ ] 社区分享功能
- [ ] 小说推荐系统
- [ ] 评论和讨论
- [ ] 移动端原生应用

---

## 📄 许可证

本项目采用 **MIT 许可证**，详见 [LICENSE](../LICENSE) 文件。

---

## 👥 维护者

- **项目维护者**：[您的名字](https://github.com/your-username)
- **联系方式**：your-email@example.com

---

## 🙏 致谢

感谢以下开源项目和社区：

- [React](https://reactjs.org/) - 用户界面构建库
- [Vite](https://vitejs.dev/) - 下一代前端构建工具
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言
- [React Force Graph](https://github.com/vasturiano/react-force-graph) - 力导向图可视化
- [jschardet](https://github.com/aadsm/jschardet) - 字符编码检测
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架

---

## 📚 相关文档

- [小说RAG系统需求文档](../小说RAG系统需求文档.md)
- [Web前端开发需求文档](../web前端开发需求文档.md)
- [React 官方文档](https://react.dev/)
- [Ant Design 组件库](https://ant.design/components/overview-cn/)
- [Vite 配置指南](https://vitejs.dev/config/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)

---

<div align="center">

**如有问题或建议，欢迎提出 Issue 或 Pull Request！**

⭐ 如果这个项目对你有帮助，请给个 Star！

</div>
