# 小说RAG分析系统 - 前端

这是一个基于RAG（检索增强生成）技术的中文小说智能分析平台的Web前端应用。

## 功能特性

### 核心功能
- ✅ **小说管理**：导入、编辑、删除TXT格式的中文小说
- ✅ **智能搜索**：支持关键词搜索和语义问答
- ✅ **原文引用**：精准定位并展示相关原文段落
- ✅ **人物关系图谱**：自动生成可交互的人物关系网络图
- ✅ **章节阅读**：支持多种阅读主题和个性化设置

### 技术栈

- **框架**：React 18 + TypeScript + Vite
- **UI组件**：Ant Design 5
- **状态管理**：Zustand
- **路由**：React Router v6
- **数据存储**：IndexedDB (Dexie.js)
- **可视化**：React Force Graph 2D
- **工具库**：dayjs、uuid

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── ImportNovelModal.tsx    # 导入小说弹窗
│   │   └── EditNovelModal.tsx      # 编辑小说弹窗
│   ├── pages/              # 页面组件
│   │   ├── HomePage.tsx            # 首页/小说管理
│   │   ├── SearchPage.tsx          # 搜索与问答
│   │   ├── GraphPage.tsx           # 人物关系图谱
│   │   └── ReaderPage.tsx          # 章节阅读
│   ├── store/              # 状态管理
│   │   └── useStore.ts             # Zustand store
│   ├── utils/              # 工具函数
│   │   ├── db.ts                   # IndexedDB操作
│   │   ├── textProcessing.ts      # 文本处理工具
│   │   └── mockData.ts            # Mock数据生成
│   ├── types/              # TypeScript类型定义
│   │   └── index.ts
│   ├── App.tsx             # 应用根组件
│   ├── App.css             # 全局样式
│   └── main.tsx            # 应用入口
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 主要功能使用说明

### 1. 导入小说

1. 点击首页的"导入新小说"按钮
2. 拖拽或选择TXT文件（支持UTF-8、GBK、GB2312编码）
3. 系统自动识别章节结构
4. 填写小说信息（书名、作者、简介等）
5. 确认导入

### 2. 智能搜索

1. 进入搜索页面
2. 选择要搜索的小说
3. 输入问题或关键词
4. 查看AI生成的回答和原文引用
5. 可以展开上下文或跳转到原文阅读

### 3. 人物关系图谱

1. 在小说卡片点击"关系图"按钮
2. 系统自动分析人物关系（首次需要一些时间）
3. 交互式浏览人物关系网络
4. 点击节点查看人物详情
5. 点击关系线查看关系详情
6. 可以筛选、搜索和导出图谱

### 4. 章节阅读

1. 在小说卡片点击"阅读"按钮
2. 左侧显示章节目录
3. 点击章节切换内容
4. 可以自定义字体、主题、行高等阅读设置
5. 支持从搜索结果直接跳转到指定段落

## 数据存储

所有数据（小说内容、搜索历史、人物关系图谱等）都存储在浏览器的IndexedDB中，不会上传到服务器。

### 存储限制

不同浏览器的IndexedDB存储限制不同：
- Chrome/Edge: 约可用磁盘空间的60%
- Firefox: 约2GB（可请求更多）
- Safari: 约1GB

建议定期清理不需要的小说以释放空间。

## Mock数据说明

当前版本使用模拟数据来演示功能：

- **搜索结果**：使用`generateMockSearchResult`生成模拟的AI回答和引用
- **人物关系**：使用`generateMockCharacterGraph`生成示例人物关系图谱

实际应用中，这些功能需要接入后端API来实现真实的RAG检索和分析。

## 性能优化建议

### 大文件处理
- 导入300万字以上的小说时会分块处理
- 使用虚拟滚动渲染长列表
- 章节内容按需加载

### 浏览器兼容性
- 推荐使用Chrome、Edge、Firefox最新版
- 需要支持ES6+、IndexedDB、WebAssembly

## 开发说明

### 添加新功能

1. 在`types/index.ts`中定义数据类型
2. 在`utils/`中添加相关工具函数
3. 在`components/`或`pages/`中创建UI组件
4. 在`store/useStore.ts`中添加状态管理（如需要）

### 调试技巧

- 使用浏览器开发工具的Application标签查看IndexedDB数据
- 使用React DevTools查看组件状态
- 检查Console日志获取错误信息

## 未来扩展

- [ ] 接入后端RAG API
- [ ] 真实的文本分析和NLP处理
- [ ] 更多可视化图表
- [ ] 笔记和标注功能
- [ ] 云端同步
- [ ] 移动端优化

## 许可证

MIT

## 联系方式

如有问题或建议，请提交Issue。
