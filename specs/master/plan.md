# Plan: 网络小说智能问答系统

**Created:** 2025-11-13  
**Status:** Draft  
**Owner:** Development Team

## Overview

本项目旨在构建一个**个人级网络小说智能问答系统**，核心价值在于**准确理解复杂叙事结构**，特别是识别和处理**叙述诡计**（如时间线倒叙、角色立场演变、关键信息延迟揭示等）。系统基于**RAG（Retrieval-Augmented Generation）**架构，结合**GraphRAG**和**Self-RAG**技术，使用**智谱AI开放平台**的GLM-4系列大模型和Embedding-3向量模型，支持处理单本**千万字级**长篇小说。

**核心设计原则**: 准确性 > 成本 > 效率

**技术架构**: 前后端分离（React + Next.js前端 + FastAPI后端），无需本地GPU，纯API调用方案。

## Constitution Compliance Check

本计划已根据项目宪章（v1.0.0）进行审查：

- [x] **Code Quality Excellence:** 
  - Python后端遵循PEP 8标准
  - TypeScript前端使用ESLint + Prettier
  - 强制代码审查（所有代码合并前必须审查）
  - 公共API必须包含完整的类型注解和文档字符串
  
- [x] **Comprehensive Testing Standards:** 
  - 单元测试覆盖率目标: ≥ 80%
  - 关键RAG流程覆盖率: 100%
  - API端点集成测试全覆盖
  - 使用pytest（后端）和Jest（前端）
  
- [x] **User Experience Consistency:** 
  - 使用Ant Design 5.x组件库保证UI一致性
  - 响应式设计支持桌面/平板/移动端
  - 流式响应提供即时反馈
  - 清晰的进度指示和错误提示
  
- [x] **Performance Requirements:** 
  - 简单查询响应 < 30秒
  - 复杂查询响应 < 3分钟
  - 知识库加载 < 10秒
  - 前端首屏加载 < 1.5秒（FCP，符合宪章要求）
  - API响应时间目标（智谱API除外）: p95 < 500ms

## Goals & Success Metrics

### Primary Goals
1. 实现千万字级网络小说的准确索引和检索
2. 构建能够识别叙述诡计的智能问答系统
3. 提供流畅的用户体验（包括阅读、问答、可视化）
4. 保持成本可控（单次查询 < ¥0.5）

### Success Metrics
- **事实查询准确率:** MVP 80% → 优化后 92%+
- **诡计识别率:** MVP 72% → 优化后 88%+
- **矛盾检测召回率:** MVP 77% → 优化后 90%+
- **简单查询响应时间:** < 30秒
- **复杂查询响应时间:** < 3分钟
- **用户满意度:** 4.5/5.0+
- **性能基线:** FCP < 2.0s, LCP < 2.5s, FID < 100ms, CLS < 0.1

## Scope

### In Scope
- 小说上传、解析和索引（TXT、EPUB格式）
- 智能问答（事实查询、演变分析、矛盾检测、时间线重建）
- 在线阅读功能（分章节浏览）
- 知识图谱构建和可视化
- 角色关系图和时间线可视化
- 模型管理（智谱AI GLM-4系列切换）
- Token消耗统计和成本控制
- 用户反馈收集
- 流式响应（WebSocket）

### Out of Scope
- 商业化功能（多用户管理、权限控制）
- 在线爬虫抓取小说（版权风险）
- 自动翻译功能
- 社交分享功能
- 移动端原生APP（仅Web响应式）
- 本地LLM部署（仅API调用）
- 实时协作功能

## Architecture & Design

### High-Level Architecture

```
前端层（React + Next.js）
  ├─ 小说管理（上传/列表）
  ├─ 在线阅读（分章阅读）
  ├─ 智能问答（RAG问答）
  ├─ 可视化分析（图谱/时间线）
  └─ 系统设置（配置）
       ↓ RESTful API / WebSocket
后端层（FastAPI）
  ├─ API路由层
  ├─ 业务逻辑层
  │   ├─ 文档处理服务
  │   ├─ RAG引擎服务
  │   ├─ 诡计检测服务
  │   └─ 模型管理服务
  └─ AI模型层（智谱AI）
       ├─ GLM-4系列（生成）
       └─ Embedding-3（向量化）
       ↓
数据持久层
  ├─ ChromaDB（向量）
  ├─ SQLite（元数据）
  ├─ NetworkX（图谱）
  └─ 本地文件系统
```

### Key Components

1. **文档处理模块:** 小说解析、章节识别、文本分块（RecursiveCharacterTextSplitter）
2. **RAG引擎:** 混合检索（语义+关键词+图谱）、智能查询路由、Rerank
3. **GraphRAG模块:** 知识图谱构建（NetworkX）、时序关系分析、章节重要性评分
4. **Self-RAG模块:** 断言提取、证据质量评分、矛盾检测、答案修正
5. **智谱AI集成:** API调用封装、流式输出、Token统计、错误重试
6. **可视化模块:** Plotly图表生成（关系图、时间线）
7. **阅读器模块:** 章节管理、内容渲染、导航
8. **WebSocket服务:** 实时进度推送、流式响应传输

### Technology Stack

- **前端:** React 18 + Next.js 14 + TypeScript
- **UI组件库:** Ant Design 5.x
- **状态管理:** Zustand + TanStack Query
- **后端:** FastAPI 0.104+ + Python 3.10+
- **LLM框架:** LangChain（文本分块、RAG编排）
- **AI服务:** 智谱AI（GLM-4系列 + Embedding-3）
- **向量数据库:** ChromaDB 0.4+
- **关系数据库:** SQLite 3.40+
- **NLP工具:** HanLP 2.1+（中文NER）
- **图谱库:** NetworkX 3.0+
- **可视化:** Plotly 5.17+
- **文件解析:** ebooklib（EPUB）、chardet（编码检测）
- **基础设施:** 本地部署（无需云服务），可选Docker容器化

### Design System Compliance

- [x] 使用统一的设计系统组件（Ant Design 5.x）
- [x] 遵循现有的交互模式（标准表单、按钮、导航）
- [x] 满足WCAG 2.1 AA标准（颜色对比度、键盘导航、语义化HTML）

## Implementation Strategy

**总体时间线:** 14-20周，分10个Phase增量交付

### Phase 1: Setup (项目初始化，2-3天)
- 搭建项目基础结构，配置开发环境
- 初始化前后端项目，配置智谱AI SDK

### Phase 2: Foundational (基础设施，1周)
- 数据库与存储（SQLite + ChromaDB + NetworkX）
- API基础设施（CORS、异常处理、日志）
- 智谱AI集成（Embedding-3 + GLM-4封装）
- 前端基础组件（Layout、Navigation、状态管理）

**关键里程碑:** 基础架构完成，可进行功能开发

### Phase 3: User Story 1 - 小说管理与基础问答 (4-5周，MVP核心)
- 文件上传与解析、文本分块与向量化
- 索引进度追踪、小说管理UI
- 基础RAG引擎、智能问答API
- 智能问答UI（流式响应、5阶段展示）

**关键里程碑:** MVP版本发布，事实查询准确率 > 80%

### Phase 4: User Story 2 - 在线阅读 (1-2周)
- 章节管理API、阅读器UI
- 章节搜索、全屏阅读模式

### Phase 5: User Story 3 - 知识图谱与GraphRAG (2-3周)
- 实体提取（HanLP）、知识图谱构建（NetworkX）
- 章节重要性评分、GraphRAG集成

**关键里程碑:** GraphRAG功能上线，检索质量提升15%+

### Phase 6: User Story 4 - 演变分析与Self-RAG (2-3周)
- 智能查询路由、演变分析
- Self-RAG增强（证据质量评分、一致性检查）
- 矛盾检测与展示UI

**关键里程碑:** 诡计检测功能上线，识别率 > 72%

### Phase 7: User Story 5 - 可视化分析 (1-2周)
- 关系图生成（Plotly力导向图）
- 时间线生成与可视化UI

### Phase 8: User Story 6 - 模型管理 (3-5天)
- 模型配置（GLM-4.6/4.5/4-Plus/4/Flash）
- 模型切换、配置管理UI

### Phase 9: User Story 7 - Token统计 (3-5天)
- Token追踪、Token统计API
- Token统计UI（图表、累计数据）

### Phase 10: Polish & Cross-Cutting Concerns (2-3周)
- 性能优化、错误处理与日志
- 用户体验提升、测试（单元+集成+E2E）
- 文档、部署准备
- **可访问性与性能监控**（宪章合规）

**关键里程碑:** 正式版本发布，稳定可用

## Testing Strategy

符合宪章的测试标准：

### Unit Testing
- **覆盖率目标:** ≥ 80%（强制，低于80%阻止PR合并）
- **关键逻辑覆盖率:** 100%（RAG流程、GraphRAG、Self-RAG）
- **工具:** pytest（后端）、Jest（前端）
- **覆盖率强制机制:**
  - CI流程中配置覆盖率检查（pytest-cov / jest --coverage）
  - 覆盖率低于80%自动标记PR为不可合并
  - 每周生成覆盖率趋势报告
- **重点测试模块:**
  - 文本分块算法（RecursiveCharacterTextSplitter）
  - 向量检索和Rerank逻辑
  - 知识图谱构建和查询
  - Token统计准确性
  - 智谱API调用封装

### Integration Testing
- [x] API端点测试（所有REST和WebSocket端点）
- [x] 智谱AI API集成测试（模拟和实际调用）
- [x] ChromaDB向量数据库集成测试
- [x] SQLite元数据库集成测试
- [x] 文件解析集成测试（TXT/EPUB）

### End-to-End Testing
- [x] 关键用户流程
  - 小说上传 → 索引构建 → 查询 → 结果展示
  - 阅读器使用流程
  - 可视化图表生成
- [x] 跨浏览器测试（Chrome、Edge、Firefox）
- [x] 响应式测试（桌面、平板、移动端）

### Performance Testing
- [x] 索引构建性能测试（千万字小说）
- [x] 查询响应时间验证
  - 简单查询 < 30秒
  - 复杂查询 < 3分钟
- [x] 前端性能指标（Core Web Vitals）
  - FCP < 2.0s
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- [x] 内存占用测试（峰值 < 8GB）
- [x] 并发测试（个人应用，单用户）

## Performance Considerations

### Target Metrics
- **前端性能:**
  - FCP（首次内容绘制）: < 1.5s（宪章要求）
  - LCP（最大内容绘制）: < 2.5s
  - FID（首次输入延迟）: < 100ms
  - CLS（累积布局偏移）: < 0.1
- **后端性能:**
  - API响应时间（智谱API除外）p95: < 500ms
  - 索引构建速度: 取决于网络和智谱API（千万字预计3-5小时）
  - 简单查询响应: < 30秒
  - 复杂查询响应: < 3分钟
  - 知识库加载: < 10秒
- **资源占用:**
  - 内存峰值: < 8GB（无需GPU）
  - 存储空间: 50GB+（索引数据）

### Optimization Plan
- **检索优化:**
  - 使用ChromaDB的HNSW索引（近似最近邻）
  - 智能查询路由，根据查询类型动态调整策略
  - 候选块数优化（Top-30 → Rerank → Top-10）
  - 结果缓存，常见查询直接返回
- **前端优化:**
  - 代码分割和懒加载（Next.js动态导入）
  - 图片和静态资源压缩
  - 使用React.memo减少不必要的重新渲染
  - 流式响应提升用户感知速度
- **API调用优化:**
  - 智谱API批处理（Embedding-3批量向量化）
  - 指数退避重试机制
  - 超时控制和错误降级
  - 优先使用GLM-4-Flash降低成本和延迟
- **成本优化:**
  - 简单查询使用GLM-4-Flash
  - 复杂查询使用GLM-4
  - 仅最复杂推理使用GLM-4-Plus
  - 限制检索块数（Top-10），避免上下文过长
  - Prompt优化，精简系统提示词

## Risks & Mitigations
### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 智谱API调用失败或限流 | 高 | 低 | ①实现指数退避重试机制 ②错误提示和降级方案 ③监控API状态 |
| 准确率不达标(MVP<80%) | 高 | 中 | ①优化Prompt工程 ②增强Self-RAG深度 ③必要时切换GLM-4-Plus ④迭代优化检索策略 |
| API成本超预期 | 中 | 中 | ①优先使用GLM-4-Flash ②实现查询结果缓存 ③设置成本上限告警 ④优化Prompt长度 |
| ChromaDB性能瓶颈 | 中 | 低 | ①优化HNSW索引参数 ②考虑升级到Milvus/Weaviate ③实现分块索引 |
| 诡计识别效果差(MVP<72%) | 高 | 中 | ①丰富知识图谱属性 ②优化Self-RAG机制 ③使用GLM-4-Plus增强推理 |

### 数据风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 文件编码识别错误 | 中 | 中 | ①使用chardet自动检测 ②提供手动指定编码选项 ③UTF-8优先策略 |
| 章节识别失败 | 中 | 中 | ①多种正则规则兼容 ②提供手动标注接口 ③允许用户自定义章节标记 |
| 索引数据损坏 | 中 | 低 | ①定期自动备份 ②校验机制检测损坏 ③提供重建索引功能 |

### 合规风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 宪章合规性不足 | 高 | 低 | ①定期合规审查 ②CI强制覆盖率检查 ③可访问性审计(T182-T184) |
| 性能指标未达标(FCP>1.5s) | 中 | 中 | ①前端性能优化(代码分割、懒加载) ②Core Web Vitals监控(T185) ③定期性能测试 |
```

## Dependencies

### Internal
- 前端与后端通过RESTful API和WebSocket通信
- 所有模块共享ChromaDB向量数据库和SQLite元数据库
- GraphRAG模块依赖基础RAG引擎
- Self-RAG模块依赖GraphRAG检索结果
- 可视化模块依赖知识图谱数据

### External

**必需依赖:**
- **智谱AI开放平台:** GLM-4系列模型、Embedding-3向量模型（需要API Key和充值）
- **Python 3.10+:** 后端运行环境
- **Node.js 18+:** 前端构建和运行环境
- **网络连接:** 调用智谱AI API，上传下载依赖包

**Python库依赖:**
- FastAPI 0.104+ : Web框架
- LangChain 0.1+ : RAG编排和文本分块
- ChromaDB 0.4+ : 向量数据库
- HanLP 2.1+ : 中文NLP
- NetworkX 3.0+ : 知识图谱
- Plotly 5.17+ : 可视化
- SQLAlchemy : 数据库ORM
- Pydantic : 数据验证
- zhipuai : 智谱AI SDK
- ebooklib : EPUB解析
- chardet : 编码检测

**前端库依赖:**
- React 18 : UI框架
- Next.js 14 : React框架
- TypeScript : 类型检查
- Ant Design 5.x : UI组件库
- Zustand : 状态管理
- TanStack Query : 数据获取
- Plotly.js : 图表渲染

## Timeline

| 里程碑 | 日期 | 状态 |
|--------|------|------|
| [里程碑1] | [YYYY-MM-DD] | [计划中/进行中/完成] |
| [里程碑2] | [YYYY-MM-DD] | [计划中/进行中/完成] |

## Review & Approvals

| 角色 | 姓名 | 批准日期 | 签名 |
|------|------|----------|------|
| 技术负责人 | | | |
| 产品负责人 | | | |
| 设计负责人 | | | |

## Notes & Updates

[记录重要的讨论、决策和变更]
