# 文档中心

欢迎来到网络小说智能问答系统文档中心！本目录包含了系统的所有文档。

---

## 📖 快速导航

### 🚀 新手入门
如果你是第一次使用本系统，建议按照以下顺序阅读：

1. **[用户指南](./user-guide.md)** ⭐ 必读
   - 系统安装和启动
   - 基本使用流程
   - 常见问题解答

2. **[API文档使用指南](./API文档使用指南.md)**
   - 如何选择合适的API文档格式
   - Postman快速测试
   - 常见使用场景

---

## 📚 完整文档列表

### 用户文档

#### [用户指南](./user-guide.md)
- **适合**: 所有用户
- **内容**: 
  - 环境准备和安装
  - 小说上传和管理
  - 智能问答使用
  - 知识图谱可视化
  - 在线阅读功能
  - 系统配置和优化

---

### API文档

#### [API接口文档](./api-reference.md) 📄
- **格式**: Markdown
- **适合**: 开发者阅读
- **内容**:
  - 33个API端点的详细说明
  - 请求/响应示例
  - Python、JavaScript、cURL代码示例
  - WebSocket协议说明
  - 错误处理指南
  - 性能指标

#### [OpenAPI规范](./openapi.yaml) 🤖
- **格式**: YAML（OpenAPI 3.0）
- **适合**: 自动化工具、SDK生成
- **用途**:
  - 生成客户端SDK
  - 集成到API网关
  - 自动化测试
  - Swagger UI可视化

#### [Postman集合](./postman-collection.json) 🧪
- **格式**: JSON
- **适合**: API测试和调试
- **用途**:
  - 导入到Postman快速测试
  - 包含所有接口的示例请求
  - 预配置环境变量

#### [API文档使用指南](./API文档使用指南.md) 📖
- **适合**: 不知道选哪个文档的人
- **内容**:
  - 3种API文档的对比
  - 不同场景下的文档选择
  - 快速开始指南
  - 工具推荐

---

### 开发者文档

#### [开发文档](./development.md)
- **适合**: 开发者、贡献者
- **内容**:
  - 开发环境搭建
  - 项目结构说明
  - 编码规范
  - 贡献流程
  - 测试指南

#### [查询参数配置](./查询阶段可配置参数说明.md)
- **适合**: 需要优化查询效果的用户
- **内容**:
  - 检索参数（Top-K、Rerank）
  - LLM生成参数（Temperature、Top-P）
  - Rerank权重调优
  - Self-RAG参数
  - GraphRAG参数
  - 完整配置示例

---

### 运维文档

#### [部署文档](./deployment.md)
- **适合**: 运维人员、部署人员
- **内容**:
  - Docker部署
  - 生产环境配置
  - 性能优化
  - 监控和日志
  - 故障排除

---

## 🎯 按场景查找文档

### 场景1: 我想快速体验系统
👉 阅读: [用户指南](./user-guide.md) 的"快速开始"章节

### 场景2: 我想测试API接口
👉 使用: [Postman集合](./postman-collection.json) + [API文档使用指南](./API文档使用指南.md)

### 场景3: 我想集成到我的应用
👉 阅读: [API接口文档](./api-reference.md)  
👉 使用: [OpenAPI规范](./openapi.yaml) 生成SDK

### 场景4: 我想优化查询效果
👉 阅读: [查询参数配置](./查询阶段可配置参数说明.md)

### 场景5: 我想参与开发
👉 阅读: [开发文档](./development.md)

### 场景6: 我想部署到生产环境
👉 阅读: [部署文档](./deployment.md)

---

## 📊 文档结构图

```
docs/
├── README.md                           # 本文件 - 文档导航
├── user-guide.md                       # 用户指南
├── api-reference.md                    # API参考（Markdown）
├── openapi.yaml                        # OpenAPI 3.0规范
├── postman-collection.json            # Postman集合
├── API文档使用指南.md                  # API文档使用指南
├── development.md                      # 开发文档
├── deployment.md                       # 部署文档
└── 查询阶段可配置参数说明.md           # 查询参数配置
```

---

## 🔍 快速搜索

### API相关
- 如何上传小说？ → [API接口文档 - 小说管理](./api-reference.md#小说管理-api)
- 如何查询问答？ → [API接口文档 - 智能问答](./api-reference.md#智能问答-api)
- WebSocket怎么用？ → [API接口文档 - WebSocket](./api-reference.md#websocket-api)

### 配置相关
- 如何修改模型？ → [查询参数配置 - LLM生成参数](./查询阶段可配置参数说明.md#二llm生成参数llm-generation-parameters)
- 如何提高准确率？ → [查询参数配置 - 参数调优建议](./查询阶段可配置参数说明.md#七参数调优建议)
- 如何降低成本？ → [查询参数配置 - 按成本优化](./查询阶段可配置参数说明.md#73-按成本优化)

### 部署相关
- Docker部署？ → [部署文档 - Docker部署](./deployment.md)
- 性能优化？ → [部署文档 - 性能优化](./deployment.md)
- 日志查看？ → [部署文档 - 监控日志](./deployment.md)

---

## 📝 文档版本

| 文档 | 版本 | 最后更新 |
|------|------|----------|
| 用户指南 | v1.0 | 2025-11-17 |
| API接口文档 | v0.1.0 | 2025-11-17 |
| OpenAPI规范 | v0.1.0 | 2025-11-17 |
| 查询参数配置 | v1.0 | 2025-11-17 |
| API文档使用指南 | v1.0 | 2025-11-17 |

---

## 🔗 外部资源

### 官方文档
- [FastAPI文档](https://fastapi.tiangolo.com/) - 后端框架
- [Next.js文档](https://nextjs.org/docs) - 前端框架
- [智谱AI文档](https://open.bigmodel.cn/dev/api) - AI模型API

### 标准规范
- [OpenAPI规范](https://spec.openapis.org/oas/v3.0.3) - API标准
- [WebSocket协议](https://datatracker.ietf.org/doc/html/rfc6455) - WebSocket标准

### 技术博客
- [RAG技术解析](https://www.langchain.com/rag)
- [向量数据库最佳实践](https://www.trychroma.com/docs)

---

## 💡 文档贡献

发现文档错误或有改进建议？

1. 提交Issue到GitHub
2. 发起Pull Request
3. 联系维护团队

---

## 📧 获取帮助

- **GitHub Issues**: 提交问题和Bug报告
- **讨论区**: 技术讨论和经验分享
- **邮件**: 联系开发团队

---

**文档维护**: AI Assistant  
**最后更新**: 2025-11-17  
**项目版本**: v0.1.0

