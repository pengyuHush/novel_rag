# API文档使用指南

本指南帮助你快速上手使用网络小说智能问答系统的API文档。

---

## 📚 文档列表

我们提供了3种格式的API文档，满足不同使用场景：

### 1. **openapi.yaml** - OpenAPI 3.0规范文档
- **用途**: 标准化API规范，可用于自动生成客户端SDK
- **特点**: 机器可读，符合OpenAPI 3.0标准
- **适用于**: 开发团队、API网关、自动化工具

**使用方式**:
```bash
# 使用Swagger UI可视化
npx swagger-ui-watcher docs/openapi.yaml

# 生成客户端SDK（Python）
openapi-generator-cli generate -i docs/openapi.yaml -g python -o ./sdk/python

# 生成客户端SDK（TypeScript）
openapi-generator-cli generate -i docs/openapi.yaml -g typescript-axios -o ./sdk/typescript
```

---

### 2. **api-reference.md** - Markdown格式API参考
- **用途**: 人类可读的详细API文档
- **特点**: 包含完整的说明、示例、最佳实践
- **适用于**: 开发者阅读、文档网站

**特色内容**:
- ✅ 详细的接口说明和参数解释
- ✅ 完整的请求/响应示例
- ✅ Python、JavaScript、cURL代码示例
- ✅ WebSocket连接流程说明
- ✅ 错误处理和常见问题
- ✅ 性能指标和并发限制

**在线阅读**:
- 直接在GitHub上查看
- 使用Markdown编辑器（如Typora、VS Code）
- 部署到文档网站（如Docusaurus、VuePress）

---

### 3. **postman-collection.json** - Postman集合
- **用途**: 快速测试和调试API
- **特点**: 预配置的请求集合，开箱即用
- **适用于**: API测试、接口调试

**导入步骤**:
1. 打开Postman
2. 点击左上角 **Import**
3. 选择 `docs/postman-collection.json`
4. 导入成功后，在Collections中找到 **"网络小说智能问答系统 API"**

**环境变量配置**:
导入后，配置以下变量：
- `base_url`: API基础URL（默认 `http://localhost:8000`）
- `novel_id`: 测试用的小说ID
- `chapter_num`: 测试用的章节号
- `query_id`: 测试用的查询ID
- `node_id`: 测试用的节点ID（如"萧炎"）

---

## 🚀 快速开始

### 场景1: 我想快速测试API

**推荐**: 使用 **Postman集合**

1. 导入 `postman-collection.json` 到Postman
2. 启动后端服务: `cd backend && uvicorn app.main:app --reload`
3. 在Postman中执行 **健康检查 > 基础健康检查**
4. 如果返回 `{"status": "ok"}`，说明服务正常
5. 依次测试其他接口

---

### 场景2: 我想了解完整的API功能

**推荐**: 阅读 **api-reference.md**

直接在GitHub或Markdown编辑器中打开 `docs/api-reference.md`，内容包括：
- 所有33个API端点的详细说明
- 请求/响应示例
- 数据模型定义
- WebSocket协议说明
- 错误处理指南

---

### 场景3: 我想生成客户端SDK

**推荐**: 使用 **openapi.yaml**

安装OpenAPI Generator:
```bash
npm install -g @openapitools/openapi-generator-cli
```

生成Python客户端:
```bash
openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g python \
  -o ./sdk/python \
  --additional-properties=packageName=novel_rag_client
```

生成TypeScript客户端:
```bash
openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g typescript-axios \
  -o ./sdk/typescript
```

---

### 场景4: 我想部署API文档网站

**推荐**: 使用 **openapi.yaml** + Swagger UI

方法1: 使用Docker
```bash
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/docs/openapi.yaml \
  -v $(pwd)/docs:/docs \
  swaggerapi/swagger-ui
```

方法2: 使用Redoc
```bash
npx redoc-cli serve docs/openapi.yaml --watch
```

方法3: 集成到FastAPI（已内置）
访问 `http://localhost:8000/docs` 即可看到Swagger UI界面

---

## 📖 接口分类速览

### 🏥 健康检查（4个接口）
检查各个组件的服务状态。

```bash
# 快速检查
curl http://localhost:8000/api/health
```

---

### 📚 小说管理（6个接口）
上传、查询、删除小说，监控索引进度。

**核心流程**:
1. `POST /api/novels/upload` - 上传小说文件
2. `GET /api/novels/{novel_id}/progress` - 监控索引进度
3. `GET /api/novels/{novel_id}` - 查看小说详情

---

### 📄 章节管理（4个接口）
获取章节列表、内容、搜索章节。

**典型用法**:
```bash
# 获取第1章内容
curl http://localhost:8000/api/chapters/1/1
```

---

### 💬 智能问答（5个接口）
核心功能：查询、历史记录、用户反馈。

**两种查询方式**:
1. **非流式**: `POST /api/query` - 等待完整结果
2. **流式**: `WebSocket /api/query/stream` - 实时返回思考过程

---

### 🕸️ 知识图谱（4个接口）
可视化角色关系、时间线、统计信息。

**数据格式**:
- 关系图谱: Plotly.js兼容格式
- 时间线: 按叙事顺序和时序排列

---

### 📊 统计信息（3个接口）
Token消耗、系统使用统计。

---

### ⚙️ 系统配置（5个接口）
获取/更新配置、模型列表、连接测试。

---

## 🔍 常见问题

### Q1: 如何找到某个功能对应的API？

**方法1**: 在 `api-reference.md` 中按Ctrl+F搜索关键词

**方法2**: 查看目录，按功能分类导航

**方法3**: 在Postman集合中按文件夹浏览

---

### Q2: 如何测试WebSocket流式查询？

**方法1**: 使用前端应用（推荐）

**方法2**: 使用WebSocket客户端工具
```javascript
// 浏览器Console
const ws = new WebSocket('ws://localhost:8000/api/query/stream');
ws.onopen = () => {
  ws.send(JSON.stringify({
    novel_id: 1,
    query: "测试问题",
    model: "GLM-4.5-Air"
  }));
};
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

**方法3**: 使用Postman的WebSocket功能（New > WebSocket Request）

---

### Q3: 响应中的字段含义不清楚？

查看 `api-reference.md` 的 **数据模型** 章节，包含所有字段的详细说明。

---

### Q4: 如何处理错误响应？

参考 `api-reference.md` 的 **错误处理** 章节，包含：
- HTTP状态码说明
- 错误响应格式
- 常见错误码和解决方案

---

## 🛠️ 工具推荐

### API测试
- **Postman** - 功能强大，支持环境变量、脚本
- **Insomnia** - 简洁轻量，支持GraphQL
- **HTTPie** - 命令行工具，语法简洁

### 文档浏览
- **Swagger UI** - 在线交互式文档
- **Redoc** - 美观的静态文档
- **Stoplight Studio** - 可视化编辑OpenAPI

### SDK生成
- **OpenAPI Generator** - 支持50+语言
- **Swagger Codegen** - 老牌工具

---

## 📝 最佳实践

### 1. 使用环境变量
在Postman中配置多个环境（开发/测试/生产）：
```json
{
  "dev": {
    "base_url": "http://localhost:8000"
  },
  "prod": {
    "base_url": "https://api.example.com"
  }
}
```

---

### 2. 处理分页
对于列表接口，始终使用分页参数：
```bash
GET /api/novels?skip=0&limit=20
GET /api/novels?skip=20&limit=20
```

---

### 3. 监控索引进度
上传小说后，使用轮询监控进度：
```python
import time
while True:
    progress = get_progress(novel_id)
    if progress['status'] == 'completed':
        break
    time.sleep(5)
```

---

### 4. 错误重试
网络请求失败时，实现指数退避重试：
```python
import time
for retry in range(3):
    try:
        response = api_call()
        break
    except Exception:
        time.sleep(2 ** retry)
```

---

## 🔗 相关资源

### 项目文档
- [用户指南](./user-guide.md) - 如何使用系统
- [开发文档](./development.md) - 如何参与开发
- [部署文档](./deployment.md) - 如何部署到生产
- [查询参数配置](./查询阶段可配置参数说明.md) - 调优指南

### 外部文档
- [OpenAPI规范](https://spec.openapis.org/oas/v3.0.3) - 官方标准
- [智谱AI文档](https://open.bigmodel.cn/dev/api) - AI模型API
- [FastAPI文档](https://fastapi.tiangolo.com/) - 后端框架

---

## 📧 反馈与支持

如果你发现文档中的错误或有改进建议：

1. 提交Issue到GitHub仓库
2. 发送邮件至开发团队
3. 在项目讨论区留言

---

**文档维护**: AI Assistant  
**最后更新**: 2025-11-17  
**版本**: v0.1.0

