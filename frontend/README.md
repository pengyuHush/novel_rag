# 志异全考 - 网络小说智能问答系统前端

基于 Next.js 14 + React 18 + TypeScript + shadcn/ui 的现代化前端应用。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **UI库**: shadcn/ui + TailwindCSS
- **状态管理**: Zustand
- **数据获取**: TanStack Query + Axios
- **实时通信**: WebSocket
- **图表可视化**: Plotly.js
- **Markdown渲染**: react-markdown + remark-gfm

## 功能特性

### 1. 智能问答主界面
- 左侧：小说列表侧边栏
  - 小说上传和管理
  - 勾选小说进行查询
  - 阅读、查看图谱、删除等操作
- 中间：查询区域
  - 查询输入框和模型选择器
  - 预设查询按钮（常用查询短语）
  - 5阶段查询状态展示（查询理解→检索内容→生成答案→Self-RAG验证→完成汇总）
  - Token消耗统计（实时展示）
  - 思考过程和最终答案面板（支持流式输出和Markdown渲染）
- 右侧：引用列表（固定展示）

### 2. 在线阅读器
- 左侧章节列表，支持搜索
- 流畅的章节内容展示
- 上一章/下一章快速切换

### 3. 图谱可视化
- 角色关系图谱（Plotly网络图）
- 事件时间线

### 4. 设置页面
- 智谱AI API Key配置
- 默认模型选择
- Token消耗统计查看

## 环境要求

- Node.js 18+
- npm 或 yarn

## 安装依赖

```bash
cd frontend
npm install
```

## 配置

### 1. 后端API地址

在 `next.config.ts` 中已配置好API代理：

```typescript
{
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}
```

如需修改后端地址，请编辑此文件。

### 2. WebSocket配置

WebSocket地址在 `lib/websocket.ts` 中配置：

```typescript
const WS_BASE_URL = 'ws://localhost:8000';
```

## 运行开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 构建生产版本

```bash
npm run build
npm run start
```

## 项目结构

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx            # 根布局（Header + Providers）
│   ├── page.tsx              # 主页（智能问答界面）
│   ├── providers.tsx         # TanStack Query Provider
│   ├── reader/[novelId]/     # 阅读器页面
│   ├── settings/             # 设置页面
│   └── globals.css           # 全局样式
├── components/               # React组件
│   ├── ui/                   # shadcn/ui基础组件
│   ├── layout/               # 布局组件
│   │   ├── Header.tsx
│   │   └── NovelSidebar.tsx
│   ├── query/                # 查询相关组件
│   │   ├── QueryInput.tsx
│   │   ├── PresetQueries.tsx
│   │   ├── QueryStages.tsx
│   │   ├── TokenStats.tsx
│   │   ├── ThinkingPanel.tsx
│   │   └── CitationList.tsx
│   ├── novel/                # 小说管理组件
│   │   └── UploadModal.tsx
│   └── graph/                # 可视化组件
│       ├── GraphModal.tsx
│       ├── RelationGraph.tsx
│       └── Timeline.tsx
├── lib/                      # 工具库
│   ├── api.ts                # REST API客户端
│   ├── websocket.ts          # WebSocket客户端
│   └── utils.ts              # 工具函数
├── hooks/                    # 自定义Hooks
│   └── useQuery.ts           # 查询Hook
├── store/                    # Zustand状态管理
│   ├── novelStore.ts
│   └── queryStore.ts
├── types/                    # TypeScript类型定义
│   └── api.ts
└── package.json
```

## 核心功能实现

### WebSocket流式查询

通过 `useQueryWebSocket` hook管理WebSocket连接：

```typescript
import { useQueryWebSocket } from '@/hooks/useQuery';

const { executeQuery } = useQueryWebSocket();

// 执行查询
executeQuery(novelId, query, model);
```

WebSocket消息格式：
- `stage`: 当前阶段（understanding/retrieving/generating/validating/finalizing）
- `thinking`: 思考过程（增量）
- `content`: 答案内容（增量）
- `is_delta`: 是否为增量消息
- `citations`: 引用列表
- `metadata.token_stats`: Token统计

### 状态管理

使用Zustand管理全局状态：

```typescript
// 小说状态
import { useNovelStore } from '@/store/novelStore';
const { novels, selectedNovelId, setSelectedNovel } = useNovelStore();

// 查询状态
import { useQueryStore } from '@/store/queryStore';
const { isQuerying, thinking, answer, citations } = useQueryStore();
```

### Markdown渲染

使用 `react-markdown` 和 `remark-gfm` 渲染Markdown内容：

```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {content}
</ReactMarkdown>
```

## 样式和主题

- 使用 TailwindCSS 进行样式管理
- shadcn/ui 提供一致的UI组件
- 支持亮色/暗色主题（通过CSS变量）
- 自定义滚动条样式

## 注意事项

1. **后端依赖**: 前端依赖后端API，请确保后端服务（FastAPI）已启动
2. **WebSocket连接**: 查询功能依赖WebSocket，请确保后端WebSocket服务正常
3. **API Key**: 使用前需要在设置页面配置智谱AI API Key
4. **浏览器兼容性**: 推荐使用Chrome 90+或Edge 90+

## 常见问题

### 1. WebSocket连接失败
- 检查后端是否正常运行
- 检查 `lib/websocket.ts` 中的WebSocket地址配置
- 确认浏览器支持WebSocket

### 2. API请求失败
- 检查 `next.config.ts` 中的API代理配置
- 确认后端运行在 http://localhost:8000

### 3. 图表不显示
- Plotly.js 使用动态导入避免SSR问题
- 检查浏览器控制台是否有错误

## 开发建议

1. 使用TypeScript严格模式进行开发
2. 遵循React Hooks最佳实践
3. 组件尽量保持单一职责
4. 使用Zustand进行全局状态管理，避免prop drilling
5. API调用统一通过 `lib/api.ts` 进行

## License

MIT
