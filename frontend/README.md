# 小说 RAG 分析系统 - Web 前端

基于 React + TypeScript + Vite 的中文小说智能分析平台前端应用。

## 技术栈

```
前端框架: React 19.1.1 + TypeScript 5.9.3
构建工具: Vite 7.1.7
UI 组件库: Ant Design 5.28.0
状态管理: Zustand 5.0.8
路由管理: React Router 7.9.5
数据可视化: React Force Graph 2D 1.29.0
文件处理: jschardet 3.1.4
```

## 核心功能

### 1. 小说管理
- ✅ 支持 TXT 格式中文小说导入 (UTF-8, GBK, GB2312)
- ✅ 自动检测文件编码
- ✅ 智能识别章节结构
- ✅ 小说信息编辑 (书名、作者、简介、标签)
- ✅ 拖拽上传支持
- ✅ 导入进度跟踪和状态轮询

### 2. 智能搜索与问答
- ✅ 自然语言问题输入
- ✅ 多小说联合检索
- ✅ 搜索结果展示:
  - 智能回答生成 (Markdown 格式渲染)
  - 原文段落引用
  - 章节位置定位
  - 一键跳转阅读
  - Token 消耗统计 (总 Token/Embedding/Chat/预估费用/耗时)
- ✅ 搜索历史管理:
  - 自动保存搜索记录 (问题、答案、选中的小说)
  - 左侧栏历史记录浏览
  - 一键恢复历史搜索
  - 支持删除单条或清空全部历史
  - 本地持久化存储 (localStorage)

### 3. 人物关系图谱
- ✅ 交互式力导向图可视化
- ✅ 人物节点: 姓名、角色、描述、出场次数
- ✅ 关系边: 关系类型、关系强度
- ✅ 图谱操作: 拖拽、缩放、筛选、悬停详情

### 4. 章节阅读器
- ✅ 左侧章节目录导航
- ✅ 自定义阅读体验:
  - 字体大小调节 (14px - 24px)
  - 行高调节 (1.5 - 2.5)
  - 多种主题色 (米黄、护眼绿、淡蓝、纸白、暗夜)
- ✅ 阅读进度记忆
- ✅ 段落高亮定位
- ✅ 章节快速切换

### 5. 响应式设计
- ✅ 桌面端: 多栏布局，侧边栏导航
- ✅ 移动端: 底部抽屉导航，悬浮按钮，触摸友好

## 使用指南

### 搜索历史功能

**自动保存**
- 每次成功搜索后，系统会自动保存完整的搜索记录
- 记录包括：问题、答案、选中的小说、搜索模式、Token统计、时间戳

**查看历史**
1. 在搜索页面左侧栏，点击"搜索历史"标签
2. 查看所有历史记录，按时间倒序排列
3. 每条记录显示：
   - 搜索问题
   - 搜索时间 (相对时间，如"2分钟前")
   - 选中的小说标题
   - 搜索模式 (语义/关键词)
   - Token消耗量

**恢复历史搜索**
- 点击任意历史记录卡片
- 系统会自动恢复该次搜索的完整状态：
  - 搜索框填充原问题
  - 自动选中当时的小说
  - 恢复搜索模式
  - 显示原答案和引用

**管理历史**
- **删除单条**: 点击记录卡片右下角的删除按钮
- **清空全部**: 点击右上角"清空"按钮，需确认操作

**数据存储**
- 历史记录保存在浏览器本地 (localStorage)
- 最多保存 50 条记录 (自动清理最旧的记录)
- 不会占用后端存储空间
- 清除浏览器数据会删除历史记录

## 快速开始

### 前置要求

- Node.js >= 18.0.0
- npm >= 9.0.0 (或 yarn, pnpm)

### 安装依赖

```bash
cd frontend
npm install
```

### 环境配置

创建 `.env` 文件:

```env
# 后端 API 服务地址 (包含 /api/v1 版本前缀)
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Mock API 模式 (可选，用于前端独立开发)
# true: 使用 Mock 数据，无需后端服务
# false: 使用真实后端 API (默认)
VITE_USE_MOCK_API=false

# 应用标题
VITE_APP_TITLE=小说RAG分析系统
```

**重要**: 
- 确保后端服务正在运行
- 确保后端 CORS 配置正确 (允许 `http://localhost:5173`)

### 开发模式运行

```bash
npm run dev
```

开发服务器将在 `http://localhost:5173` 启动，支持热更新 (HMR)。

### 代码检查

```bash
npm run lint
```

### 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录。

### 本地预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 根组件 (路由配置、主题配置)
│   ├── App.css               # 全局样式
│   ├── index.css             # 基础样式
│   │
│   ├── pages/                # 页面组件
│   │   ├── SearchPage.tsx    # 搜索与问答主页 (含小说管理)
│   │   ├── GraphPage.tsx     # 人物关系图谱页
│   │   └── ReaderPage.tsx    # 章节阅读器页
│   │
│   ├── components/           # 通用组件
│   │   ├── ImportNovelModal.tsx    # 导入小说弹窗 (支持状态轮询)
│   │   ├── EditNovelModal.tsx      # 编辑小说信息弹窗
│   │   └── NovelProcessingResultModal.tsx  # 处理结果弹窗
│   │
│   ├── store/                # 状态管理
│   │   └── useStore.ts       # Zustand 全局状态
│   │
│   ├── types/                # TypeScript 类型定义
│   │   └── index.ts          # 数据模型类型 (匹配后端 API)
│   │
│   └── utils/                # 工具函数
│       ├── api.ts            # API 客户端 (支持 Mock/真实 API 切换)
│       ├── mockApi.ts        # Mock API 实现 (前端独立开发用)
│       ├── mockData.ts       # Mock 数据生成器
│       └── textProcessing.ts # 文本处理 (编码检测、章节识别)
│
├── public/                   # 静态资源
├── index.html                # HTML 模板
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── package.json              # 项目依赖
└── README.md                 # 本文档
```

## API 集成

### API 客户端架构

使用自定义的 API 客户端与后端 FastAPI 集成:

- **novelAPI**: 小说管理 (创建、上传、查询、更新、删除)
- **searchAPI**: 智能搜索与问答
- **graphAPI**: 人物关系图谱
- **systemAPI**: 系统管理

**特点**:
- 基于 Fetch API 的现代化 HTTP 客户端
- 统一的错误处理机制 (APIError)
- 类型安全的请求/响应处理
- 自动状态轮询机制
- RESTful API 设计 (包含 `/api/v1` 版本前缀)

### Mock API 模式

如果后端尚未开发完成，可以启用 Mock 模式进行前端开发:

**启用方式**: 在 `.env` 中设置 `VITE_USE_MOCK_API=true`

**Mock 模式特性**:
- ✅ 预置数据: 包含 3 部示例小说
- ✅ 完整功能: 支持所有前端功能
- ✅ 模拟延迟: 200ms-1000ms 网络延迟
- ✅ 异步任务: 模拟文件上传、图谱生成等长任务
- ⚠️ 数据重置: 刷新页面后数据恢复为预置状态

**切换到真实 API**: 修改 `.env` 中 `VITE_USE_MOCK_API=false`，重启开发服务器。

## 数据模型

### Novel (小说)

```typescript
interface Novel {
  id: string;
  title: string;
  author?: string;
  description?: string;
  tags: string[];
  wordCount: number;
  chapterCount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  importedAt: string;
  updatedAt: string;
  hasGraph: boolean;
}
```

### Chapter (章节)

```typescript
interface Chapter {
  id: string;
  novelId: string;
  chapterNumber: number;
  title: string;
  startPosition: number;
  endPosition: number;
  wordCount: number;
}
```

### CharacterGraph (人物关系图)

```typescript
interface CharacterGraph {
  id: string;
  novelId: string;
  characters: Character[];
  relationships: Relationship[];
  generatedAt: string;
  version: string;
}
```

## 状态管理

使用 Zustand 管理全局状态:

```typescript
interface AppState {
  novels: Novel[];
  selectedNovelIds: string[];
  currentSearchResult: SearchResult | null;
  recentQueries: string[];
  processingStatuses: Record<string, NovelProcessingStatus>;
  
  // 搜索历史 (完整记录)
  searchHistory: SearchHistory[];
  
  // Actions
  setNovels: (novels: Novel[]) => void;
  setSelectedNovelIds: (ids: string[]) => void;
  setCurrentSearchResult: (result: SearchResult | null) => void;
  addRecentQuery: (query: string) => void;
  addSearchHistory: (history: SearchHistory) => void;
  removeSearchHistory: (id: string) => void;
  clearSearchHistory: () => void;
  loadSearchHistoryItem: (history: SearchHistory) => void;
  setProcessingStatus: (novelId: string, status: NovelProcessingStatus) => void;
}

// 搜索历史记录类型
interface SearchHistory {
  id: string;                    // 唯一标识
  query: string;                 // 搜索问题
  answer: string;                // AI回答
  selectedNovelIds: string[];    // 选中的小说ID列表
  selectedNovelTitles: string[]; // 选中的小说标题列表
  searchMode: 'keyword' | 'semantic'; // 搜索模式
  references: Reference[];       // 参考段落
  tokenStats?: TokenStats;       // Token统计
  timestamp: string;             // 搜索时间 (ISO 8601)
  elapsed?: number;              // 耗时（秒）
}
```

## 开发指南

### 代码风格

- 遵循 ESLint 规则
- 使用函数式组件和 Hooks
- 优先使用 TypeScript 类型注解
- 组件和函数使用清晰的命名

### 组件开发规范

```typescript
// ✅ 推荐: 函数式组件 + TypeScript + 解构 props
interface MyComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onSubmit }) => {
  // 组件逻辑
  return <div>{title}</div>;
};
```

### 性能优化建议

- 使用 `React.memo` 避免不必要的重渲染
- 使用 `useMemo` 和 `useCallback` 缓存计算结果和回调函数
- 大列表使用虚拟滚动
- 图片和资源使用懒加载

## 部署

### 使用 Vercel 部署 (推荐)

1. 在 [Vercel](https://vercel.com) 注册账号
2. 连接 GitHub 仓库
3. 配置构建设置:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. 点击 Deploy

### 使用 Nginx 部署

```bash
# 构建
npm run build

# 上传 dist/ 到服务器
scp -r dist/* user@server:/var/www/html/
```

Nginx 配置:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### 使用 Docker 部署

Dockerfile:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 浏览器兼容性

| 浏览器 | 最低版本 | 推荐版本 |
|--------|---------|---------|
| Chrome | 90+ | 最新版 |
| Firefox | 88+ | 最新版 |
| Safari | 14+ | 最新版 |
| Edge | 90+ | 最新版 |

**核心功能依赖**:
- Fetch API
- File API
- ES2020
- CSS Grid & Flexbox

## 常见问题

### Q: 导入的小说显示乱码？
A: 项目支持自动检测编码 (UTF-8, GBK, GB2312)，如果仍然乱码请使用文本编辑器转换为 UTF-8 编码。

### Q: 小说上传失败或处理卡住？
A: 检查后端服务是否运行 (`http://localhost:8000`)，网络连接是否稳定，文件大小是否超过限制 (50MB)。

### Q: 搜索功能无结果?
A: 确保至少选择一部小说且小说已完成处理 (状态为 `completed`)。

### Q: 人物关系图谱无法生成？
A: 图谱生成需要较长时间，请等待小说完成向量化处理后再尝试。

### Q: 如何配置后端地址？
A: 在 `.env` 文件中设置 `VITE_API_BASE_URL=http://your-backend-url:8000/api/v1`

### Q: 为什么环境变量不生效？
A: 确保变量名以 `VITE_` 开头，修改环境变量后需要重启开发服务器。

## 主题定制

### 修改主题色

编辑 `src/App.tsx` 中的 `ConfigProvider` 配置:

```typescript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#8B7355',      // 主色调
      colorBgBase: '#F5E6D3',        // 背景色
      fontFamily: "'Noto Serif SC', 'Source Han Serif SC', serif",
    },
  }}
>
```

### 修改阅读器主题

编辑 `src/pages/ReaderPage.tsx` 中的 `THEME_STYLES`:

```typescript
const THEME_STYLES = {
  cream: { background: '#F5E6D3', color: '#2C2416' },
  green: { background: '#E8F5E9', color: '#1B5E20' },
  // ...
};
```

## 相关文档

- [项目主 README](../README.md) - 项目概览和快速开始
- [需求文档](../小说RAG系统需求文档.md) - 完整功能需求
- [API 规范](../backend_api_specification.yaml) - OpenAPI 接口文档
- [后端文档](../backend/README.md) - 后端开发指南

## 许可证

MIT License
