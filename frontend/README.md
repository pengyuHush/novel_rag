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
- 💾 **本地存储**：使用 IndexedDB 实现浏览器端数据持久化
- 🎯 **精准定位**：搜索结果直接定位到原文段落和章节

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
- ✅ 搜索历史记录
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
本地存储：Dexie.js 4.2.1 (IndexedDB)
文件处理：jschardet 3.1.4
时间处理：dayjs 1.11.19
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
│   │   ├── ImportNovelModal.tsx    # 导入小说弹窗
│   │   └── EditNovelModal.tsx      # 编辑小说信息弹窗
│   │
│   ├── store/                # 状态管理
│   │   └── useStore.ts       # Zustand 全局状态
│   │
│   ├── types/                # TypeScript 类型定义
│   │   └── index.ts          # 数据模型类型
│   │
│   └── utils/                # 工具函数
│       ├── db.ts             # IndexedDB 数据库配置
│       ├── textProcessing.ts # 文本处理（编码检测、章节识别）
│       └── mockData.ts       # 模拟数据生成
│
├── public/                   # 静态资源
├── index.html                # HTML 模板
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── package.json              # 项目依赖
└── README.md                 # 项目文档
```

### 数据模型

#### Novel（小说）
```typescript
interface Novel {
  id: string;              // 唯一标识符
  title: string;           // 书名
  author: string;          // 作者
  description: string;     // 简介
  tags: string[];          // 标签
  content: string;         // 全文内容
  chapters: Chapter[];     // 章节列表
  wordCount: number;       // 总字数
  importedAt: number;      // 导入时间戳
}
```

#### Chapter（章节）
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

#### CharacterGraph（人物关系图）
```typescript
interface CharacterGraph {
  id: string;              // 图谱标识符
  novelId: string;         // 所属小说ID
  characters: Character[]; // 人物列表
  relationships: Relationship[]; // 关系列表
  generatedAt: number;     // 生成时间戳
}

interface Character {
  id: string;              // 人物标识符
  name: string;            // 姓名
  role: string;            // 角色类型
  description: string;     // 描述
  appearances: number;     // 出场次数
}

interface Relationship {
  source: string;          // 源人物ID
  target: string;          // 目标人物ID
  type: string;            // 关系类型
  strength: number;        // 关系强度 (1-10)
  description: string;     // 关系描述
}
```

### 状态管理

使用 Zustand 管理全局状态：

```typescript
interface AppState {
  novels: Novel[];                    // 小说列表
  searchHistory: SearchHistory[];     // 搜索历史
  storageInfo: StorageInfo;           // 存储信息
  
  // Actions
  loadNovels: () => Promise<void>;
  addNovel: (novel: Novel) => Promise<void>;
  updateNovel: (novel: Novel) => Promise<void>;
  deleteNovel: (id: string) => Promise<void>;
  // ... 更多操作
}
```

### 本地存储方案

使用 **IndexedDB** 存储小说数据，通过 Dexie.js 封装：

```typescript
class NovelDatabase extends Dexie {
  novels!: Dexie.Table<Novel, string>;
  chapters!: Dexie.Table<Chapter, string>;
  characterGraphs!: Dexie.Table<CharacterGraph, string>;
  searchHistory!: Dexie.Table<SearchHistory, string>;
}
```

**优势：**
- 支持存储大容量数据（数百MB级别）
- 异步操作，不阻塞主线程
- 支持索引和高效查询
- 数据持久化，刷新页面不丢失

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

如果需要配置环境变量（如 API 地址），创建 `.env` 文件：

```env
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=小说RAG分析系统
```

在代码中使用：

```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
```

**注意：**
- Vite 环境变量必须以 `VITE_` 开头
- 构建时会被静态替换
- 不要在环境变量中存储敏感信息（前端代码是公开的）

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

- **IndexedDB**：所有现代浏览器均支持
- **File API**：用于文件上传
- **ES2020**：现代 JavaScript 特性
- **CSS Grid & Flexbox**：响应式布局

### 已知限制

- ❌ 不支持 IE 11 及更早版本
- ⚠️ Safari 旧版本可能在文件编码检测上有兼容问题
- ⚠️ 移动端浏览器建议使用 Chrome 或 Safari

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

### Q2：小说字数过大导致导入失败？

**A**：IndexedDB 理论上支持存储数百 MB 数据，但：
1. 注意浏览器的存储配额限制
2. Chrome/Edge 通常允许存储更大的数据
3. 可以在浏览器设置中增加存储配额

### Q3：章节识别不准确怎么办？

**A**：当前版本章节识别基于正则表达式匹配：
- 支持的格式：第X章、第X回、Chapter X 等
- 如识别错误，未来版本将支持手动调整

### Q4：搜索功能如何工作？

**A**：当前版本使用**模拟数据**演示功能：
- 搜索仅为前端演示，会返回预设的模拟结果
- 真实的语义搜索需要后端 RAG 系统支持
- 计划在未来版本接入后端 API

### Q5：人物关系图如何生成？

**A**：当前版本使用**模拟数据**：
- 关系图为随机生成的演示数据
- 真实的关系提取需要 NLP 模型支持
- 未来将接入后端人物关系抽取服务

### Q6：数据存储在哪里？

**A**：所有数据存储在浏览器的 **IndexedDB** 中：
- 数据仅保存在本地，不会上传到服务器
- 清除浏览器数据会导致数据丢失
- 建议定期备份重要小说文件

### Q7：如何清除所有数据？

**A**：
```javascript
// 打开浏览器控制台，执行：
indexedDB.deleteDatabase('NovelDatabase');
// 然后刷新页面
```

或在浏览器设置中清除站点数据。

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

### 当前版本（v1.0）- MVP

- ✅ 小说导入和管理
- ✅ 章节识别和阅读器
- ✅ 模拟搜索和问答
- ✅ 模拟人物关系图谱
- ✅ 响应式设计

### 未来版本

#### v1.1 - 后端集成

- [ ] 接入后端 RAG API
- [ ] 真实的语义搜索
- [ ] 人物关系抽取服务
- [ ] 用户认证和权限管理

#### v1.2 - 功能增强

- [ ] 多小说关联分析
- [ ] 情节时间线可视化
- [ ] 阅读笔记和标注
- [ ] 导出和分享功能

#### v1.3 - 性能优化

- [ ] 虚拟滚动优化大列表
- [ ] Service Worker 离线支持
- [ ] Web Worker 后台处理
- [ ] 增量式章节加载

#### v2.0 - 高级特性

- [ ] AI 辅助创作
- [ ] 小说对比分析
- [ ] 社区分享和讨论
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
- [Dexie.js](https://dexie.org/) - IndexedDB 封装库
- [React Force Graph](https://github.com/vasturiano/react-force-graph) - 力导向图可视化
- [jschardet](https://github.com/aadsm/jschardet) - 字符编码检测

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
