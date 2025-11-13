# 网络小说智能问答系统 - 前端

Next.js 14前端应用，提供现代化的用户界面和流畅的交互体验。

## 技术栈

- **框架**: React 18 + Next.js 14 + TypeScript
- **UI组件库**: Ant Design 5.x
- **状态管理**: Zustand + TanStack Query
- **可视化**: Plotly.js
- **样式**: Tailwind CSS
- **构建工具**: Turbopack (Next.js 14内置)

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
npm run build
npm run start
```

## 项目结构

```
frontend/
├── app/                  # Next.js App Router
│   ├── page.tsx         # 首页
│   ├── layout.tsx       # 根布局
│   ├── globals.css      # 全局样式
│   ├── novels/          # 小说管理页面
│   ├── query/           # 智能问答页面
│   ├── reader/          # 在线阅读页面
│   ├── graph/           # 知识图谱页面
│   └── settings/        # 设置页面
├── components/          # UI组件
│   ├── Layout.tsx       # 布局组件
│   ├── Navigation.tsx   # 导航组件
│   ├── NovelCard.tsx    # 小说卡片
│   ├── QueryInput.tsx   # 查询输入
│   ├── StreamingResponse.tsx  # 流式响应
│   ├── RelationGraph.tsx      # 关系图
│   └── Timeline.tsx     # 时间线
├── lib/                 # 工具库
│   ├── api.ts          # API客户端
│   ├── queryClient.ts  # TanStack Query配置
│   └── websocket.ts    # WebSocket工具
├── store/              # Zustand状态管理
│   ├── index.ts        # Store入口
│   └── userPreferences.ts  # 用户偏好
├── types/              # TypeScript类型定义
│   ├── novel.ts        # 小说类型
│   ├── query.ts        # 查询类型
│   └── chapter.ts      # 章节类型
├── hooks/              # 自定义Hooks
│   ├── useIndexingProgress.ts
│   └── useQueryStream.ts
├── styles/             # 样式文件
├── public/             # 静态资源
├── package.json        # 依赖配置
├── tsconfig.json       # TypeScript配置
├── next.config.js      # Next.js配置
└── tailwind.config.ts  # Tailwind配置
```

## 功能模块

### 小说管理
- 文件上传（拖拽支持）
- 小说列表展示
- 索引进度实时监控
- 小说详情查看
- 删除操作

### 智能问答
- 实时流式响应
- 5阶段进度展示（理解、检索、生成、验证、汇总）
- 引用来源展示（带章节链接）
- 矛盾检测结果
- Token消耗统计
- 模型切换

### 在线阅读
- 章节列表侧边栏
- 章节搜索
- 上一章/下一章导航
- 全屏阅读模式
- 阅读进度记忆

### 知识图谱
- 关系图可视化（力导向图）
- 时间线可视化
- 时间滑块（章节范围选择）
- 图表交互（点击节点/边）
- 图表导出（PNG）

### 设置
- API Key配置
- 模型管理
- 默认模型设置
- Token统计查看

## 开发指南

### 添加新页面

```bash
# 在 app/ 目录下创建新路由
mkdir app/my-page
touch app/my-page/page.tsx
```

```tsx
// app/my-page/page.tsx
export default function MyPage() {
  return <div>My Page</div>;
}
```

### 创建新组件

```tsx
// components/MyComponent.tsx
export interface MyComponentProps {
  title: string;
}

export function MyComponent({ title }: MyComponentProps) {
  return <div>{title}</div>;
}
```

### 使用API

```tsx
// 使用 TanStack Query
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['novels'],
    queryFn: () => api.get('/api/novels'),
  });

  if (isLoading) return <div>Loading...</div>;
  return <div>{data.length} novels</div>;
}
```

### 使用WebSocket

```tsx
import { useQueryStream } from '@/hooks/useQueryStream';

function QueryPage() {
  const { connect, answer, stage } = useQueryStream();

  const handleQuery = (query: string) => {
    connect(novelId, query, 'glm-4');
  };

  return (
    <div>
      <QueryInput onSubmit={handleQuery} />
      <StreamingResponse answer={answer} stage={stage} />
    </div>
  );
}
```

## 测试

```bash
# 运行测试
npm run test

# 生成覆盖率报告
npm run test:coverage
```

## 代码规范

```bash
# ESLint检查
npm run lint

# 格式化代码
npm run format

# 类型检查
npm run type-check
```

## 构建优化

### 代码分割

Next.js自动进行代码分割，也可以手动指定：

```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false,
});
```

### 图片优化

使用Next.js Image组件：

```tsx
import Image from 'next/image';

<Image
  src="/cover.jpg"
  alt="Novel Cover"
  width={300}
  height={400}
  priority
/>
```

### 性能监控

```bash
# 分析打包大小
npm run build
npm run analyze
```

## 环境变量

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 故障排除

### 热重载不工作

```bash
# 清除缓存
rm -rf .next
npm run dev
```

### 样式不生效

```bash
# 重新生成Tailwind样式
npm run dev
```

### TypeScript错误

```bash
# 重新生成类型定义
npm run type-check
```

## 部署

### Vercel (推荐)

```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
vercel
```

### Docker

```bash
# 构建镜像
docker build -t novel-rag-frontend .

# 运行容器
docker run -p 3000:3000 novel-rag-frontend
```

## 性能目标

- **FCP (First Contentful Paint)**: < 1.5s
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

## 可访问性

- 遵循WCAG 2.1 AA标准
- 支持键盘导航
- 屏幕阅读器兼容
- 合理的颜色对比度

## 许可证

MIT License

