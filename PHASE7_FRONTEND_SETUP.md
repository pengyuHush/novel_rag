# Phase 7 前端依赖安装指南

## 📦 新增依赖

Phase 7 可视化功能需要以下前端依赖：

### 1. ReactFlow - 关系图可视化
- **用途**: 力导向图、节点交互
- **版本**: ^11.10.0
- **官网**: https://reactflow.dev/

### 2. html2canvas - 图表导出
- **用途**: 将DOM元素转换为PNG图片
- **版本**: ^1.4.1
- **官网**: https://html2canvas.hertzen.com/

---

## 🚀 安装步骤

### 方法 1: 使用 npm

```bash
cd frontend
npm install reactflow html2canvas
```

### 方法 2: 使用 yarn

```bash
cd frontend
yarn add reactflow html2canvas
```

### 方法 3: 使用 pnpm

```bash
cd frontend
pnpm add reactflow html2canvas
```

---

## 📝 package.json 更新

安装后，`frontend/package.json` 应包含以下依赖：

```json
{
  "dependencies": {
    "react": "^18.x.x",
    "react-dom": "^18.x.x",
    "antd": "^5.x.x",
    "next": "^14.x.x",
    "reactflow": "^11.10.0",
    "html2canvas": "^1.4.1",
    ...
  }
}
```

---

## ✅ 验证安装

安装完成后，运行以下命令验证：

```bash
cd frontend
npm list reactflow html2canvas
```

**预期输出**:
```
frontend@0.1.0 D:\code\vibe_coding\novel_rag_spec_kit\frontend
├── html2canvas@1.4.1
└── reactflow@11.10.4
```

---

## 🔧 TypeScript类型定义

如果使用TypeScript，这些库已自带类型定义，无需额外安装 `@types/*` 包。

---

## 🎨 CSS导入

ReactFlow需要导入CSS样式，已在组件中包含：

```typescript
// RelationGraph.tsx
import 'reactflow/dist/style.css';
```

确保Next.js配置允许导入CSS文件（默认已支持）。

---

## 🐛 常见问题

### 问题 1: 安装失败
```bash
npm ERR! ERESOLVE unable to resolve dependency tree
```

**解决方案**:
```bash
npm install reactflow html2canvas --legacy-peer-deps
```

### 问题 2: ReactFlow样式未加载

**解决方案**:
确保在组件顶部导入CSS：
```typescript
import 'reactflow/dist/style.css';
```

### 问题 3: html2canvas导出空白

**解决方案**:
1. 确保目标元素已完全渲染
2. 检查跨域图片（如有）

---

## 🚀 启动开发服务器

安装依赖后，启动前端：

```bash
cd frontend
npm run dev
```

访问：`http://localhost:3000/graph`

---

## 📖 相关文档

- **ReactFlow文档**: https://reactflow.dev/learn
- **html2canvas文档**: https://html2canvas.hertzen.com/documentation
- **Phase 7报告**: PHASE7_COMPLETION_REPORT.md

---

**最后更新**: 2025-11-13

