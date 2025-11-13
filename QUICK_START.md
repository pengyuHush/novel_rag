# 🚀 快速启动指南

**网络小说智能问答系统 - MVP版本**

---

## ⚡ 5分钟快速启动

### 前提条件

- ✅ Python 3.12
- ✅ Poetry 2.2.1
- ✅ Node.js 18+
- ✅ 智谱AI API Key

---

## 第一步：启动后端

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖（首次运行）
poetry install

# 3. 配置环境变量
echo "ZHIPU_API_KEY=your_api_key_here" > .env

# 4. 启动服务
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端**:
- 访问 http://localhost:8000/docs - API文档
- 访问 http://localhost:8000/health - 健康检查

---

## 第二步：启动前端

**新开一个终端窗口**:

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（首次运行）
npm install

# 3. 启动开发服务器
npm run dev
```

**验证前端**:
- 访问 http://localhost:3000 - 主页

---

## 第三步：测试完整流程

### 1. 上传小说

1. 访问 http://localhost:3000/novels
2. 点击"上传小说"
3. 拖拽或选择 TXT/EPUB 文件
4. 填写标题和作者
5. 点击"开始上传"

### 2. 等待索引

- 在小说列表中查看进度
- 等待状态变为"索引完成"（可能需要数分钟）

### 3. 智能问答

1. 点击小说卡片的"问答"按钮
2. 输入问题，例如：
   - "主角叫什么名字？"
   - "故事发生在哪里？"
   - "主角的性格特点是什么？"
3. 观察流式响应和引用来源

---

## 🎯 功能演示

### 小说管理

| 功能 | 地址 | 说明 |
|------|------|------|
| 主页 | http://localhost:3000 | 系统介绍 |
| 小说列表 | http://localhost:3000/novels | 管理小说 |
| 上传小说 | 点击"上传小说"按钮 | 支持TXT/EPUB |
| 搜索过滤 | 列表页面 | 按标题和状态 |

### 智能问答

| 功能 | 地址 | 说明 |
|------|------|------|
| 问答页面 | http://localhost:3000/query | 智能问答 |
| 流式响应 | 自动 | 实时生成 |
| 引用来源 | 右侧栏 | 章节引用 |
| 模型选择 | 下拉框 | GLM-4系列 |

---

## 🧪 API测试

### 使用curl测试

```bash
# 1. 上传小说
curl -X POST "http://localhost:8000/api/novels/upload" \
  -F "file=@your_novel.txt" \
  -F "title=测试小说" \
  -F "author=作者名"

# 2. 获取列表
curl "http://localhost:8000/api/novels"

# 3. 智能问答
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": 1,
    "query": "主角叫什么名字？",
    "model": "glm-4"
  }'
```

### 使用Swagger UI

访问 http://localhost:8000/docs 使用交互式API文档

---

## ⚠️ 常见问题

### Q1: 后端启动失败

**检查项**:
- Python版本是否为3.12？
- Poetry是否正确安装？
- `.env` 文件是否配置了 `ZHIPU_API_KEY`？

**解决方案**:
```bash
# 查看Poetry环境
poetry env info

# 重新安装依赖
poetry install --no-cache
```

### Q2: 前端启动失败

**检查项**:
- Node.js版本是否 >= 18？
- 依赖是否正确安装？

**解决方案**:
```bash
# 清除缓存并重装
rm -rf node_modules package-lock.json
npm install
```

### Q3: 上传文件后没有反应

**可能原因**:
- 后端服务未启动
- API地址配置错误

**解决方案**:
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查前端环境变量
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Q4: 索引很慢或失败

**可能原因**:
- 文件太大（>100MB）
- 网络不稳定（调用智谱AI）
- API配额不足

**解决方案**:
- 先测试小文件（<1MB）
- 检查网络连接
- 确认智谱AI账户余额

---

## 📚 目录结构

```
novel_rag_spec_kit/
├── backend/                 # 后端服务
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── core/          # 核心配置
│   ├── data/              # 数据存储（自动创建）
│   ├── pyproject.toml     # Poetry配置
│   └── .env               # 环境变量（需创建）
├── frontend/               # 前端应用
│   ├── src/               # 源代码
│   │   ├── app/          # 页面
│   │   ├── components/   # 组件
│   │   ├── hooks/        # Hooks
│   │   ├── lib/          # 工具
│   │   └── types/        # 类型定义
│   ├── package.json       # npm配置
│   └── .env.local         # 环境变量（需创建）
└── specs/                  # 规格文档
```

---

## 🔧 开发配置

### 后端开发

```bash
# 代码格式化
poetry run black app/

# 类型检查
poetry run mypy app/

# 运行测试
poetry run pytest
```

### 前端开发

```bash
# 代码格式化
npm run lint

# 类型检查
npm run type-check

# 构建生产版本
npm run build
```

---

## 📊 性能参考

| 操作 | 预期时间 | 说明 |
|------|----------|------|
| 上传小说（1MB） | 1-2秒 | 文件传输 |
| 索引小说（10万字） | 2-5分钟 | 依赖API速度 |
| 索引小说（100万字） | 10-20分钟 | 依赖API速度 |
| 查询响应 | 5-15秒 | 检索+生成 |
| 流式输出延迟 | <1秒 | 首字延迟 |

---

## 🎓 示例数据

### 测试用小说示例

```
第一章 开始

很久很久以前，有一个年轻人叫李明。他住在一个小村庄里，梦想着去外面的世界冒险。

一天，村子里来了一位神秘的老人...

第二章 启程

李明收拾好行李，告别了家人，踏上了冒险的旅程...
```

保存为 `test_novel.txt` 并上传测试。

---

## 💡 使用技巧

### 1. 提问技巧

**好的问题**:
- "主角叫什么名字？"
- "第一章发生了什么？"
- "主角和配角是什么关系？"

**不好的问题**:
- "这本书好看吗？"（主观问题）
- "作者是谁？"（元数据问题，不在内容中）

### 2. 上传建议

- 首次测试建议使用小文件（<1MB）
- 确保文件编码为UTF-8或GBK
- TXT文件章节格式清晰（如"第一章"）

### 3. 模型选择

| 模型 | 速度 | 质量 | 适用场景 |
|------|------|------|----------|
| GLM-4-Flash | ⚡⚡⚡ | ⭐⭐ | 快速测试 |
| GLM-4 | ⚡⚡ | ⭐⭐⭐ | 日常使用 |
| GLM-4-Plus | ⚡ | ⭐⭐⭐⭐ | 复杂问题 |

---

## 📖 相关文档

- [Phase 3 完成报告](./PHASE3_COMPLETION_REPORT.md) - 详细功能说明
- [后端README](./backend/README.md) - 后端开发指南
- [前端README](./frontend/README.md) - 前端开发指南
- [API文档](http://localhost:8000/docs) - Swagger UI

---

## 🎉 开始体验

现在您已经准备好开始使用系统了！

1. ✅ 启动后端和前端
2. ✅ 上传一本小说
3. ✅ 等待索引完成
4. ✅ 开始智能问答

**祝您使用愉快！** 🚀

---

**最后更新**: 2025-11-13  
**系统版本**: MVP v1.0  
**支持**: 查看项目README获取帮助

