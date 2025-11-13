# Tasks: 网络小说智能问答系统

**Created:** 2025-11-13  
**Feature:** 网络小说智能问答系统  
**Status:** Ready for Implementation

---

## 📋 任务概览

本文档定义了网络小说智能问答系统的完整实现任务清单，按用户故事组织，支持独立实现和测试。

### 关键统计

- **总任务数**: 94
- **并行任务数**: 49
- **用户故事数**: 7
- **预计工期**: 14-20周

### 技术栈

- **前端**: React 18 + Next.js 14 + TypeScript + Ant Design 5.x
- **后端**: FastAPI 0.104+ + Python 3.10+
- **AI服务**: 智谱AI (GLM-4系列 + Embedding-3)
- **向量库**: ChromaDB 0.4+
- **图谱**: NetworkX 3.0+
- **NLP**: HanLP 2.1+

---

## 🎯 实现策略

### MVP优先原则

**MVP范围** (User Story 1): 小说上传、解析、索引、基础问答
- 目标: 3-5周内实现可演示原型
- 验收: 成功上传500万字小说，事实查询准确率>75%

### 增量交付

1. **Phase 1-2**: Setup + Foundational (Week 1-2)
2. **Phase 3**: US1 小说管理与基础问答 (Week 3-7) - MVP
3. **Phase 4**: US2 在线阅读 (Week 8-9)
4. **Phase 5**: US3 知识图谱与GraphRAG (Week 10-12)
5. **Phase 6**: US4 演变分析与Self-RAG (Week 13-14)
6. **Phase 7**: US5 可视化 (Week 15-16)
7. **Phase 8**: US6 模型管理 (Week 17)
8. **Phase 9**: US7 Token统计 (Week 18)
9. **Phase 10**: Polish (Week 19-20)

---

## Phase 1: Setup (项目初始化)

**目标**: 搭建项目基础结构，配置开发环境

**预计时间**: 2-3天

### 任务清单

- [ ] T001 创建项目根目录结构 (backend/, frontend/, docker-compose.yml)
- [ ] T002 [P] 初始化后端FastAPI项目 (backend/app/main.py, backend/requirements.txt)
- [ ] T003 [P] 初始化前端Next.js项目 (frontend/src/app/page.tsx, frontend/package.json)
- [ ] T004 配置Python虚拟环境 (backend/venv/, backend/.env.example)
- [ ] T005 [P] 配置智谱AI SDK (backend/app/core/config.py, 添加zhipuai依赖)
- [ ] T006 [P] 配置ESLint和Prettier (frontend/.eslintrc.json, frontend/.prettierrc)
- [ ] T007 创建数据存储目录结构 (backend/data/chromadb/, backend/data/sqlite/, backend/data/graphs/, backend/data/uploads/)
- [ ] T008 配置Git忽略规则 (.gitignore: venv/, .env, data/, node_modules/)
- [ ] T009 [P] 编写README快速开始指南 (README.md, backend/README.md, frontend/README.md)
- [ ] T010 [P] 配置Docker Compose (docker-compose.yml: backend和frontend服务定义)

### 验收标准

- ✅ 项目结构完整，目录清晰
- ✅ 后端FastAPI可启动 (uvicorn app.main:app --reload)
- ✅ 前端Next.js可启动 (npm run dev)
- ✅ 智谱AI SDK可导入
- ✅ 环境变量配置文档完整

---

## Phase 2: Foundational (基础设施)

**目标**: 实现核心基础模块，为所有用户故事提供支撑

**预计时间**: 1周

### 数据库与存储

- [ ] T011 设计SQLite数据库Schema (backend/app/db/schema.sql: novels, chapters, entities, queries, token_stats表)
- [ ] T012 实现SQLAlchemy模型 (backend/app/models/database.py)
- [ ] T013 创建数据库初始化脚本 (backend/app/db/init_db.py)
- [ ] T014 [P] 配置ChromaDB客户端 (backend/app/core/chromadb_client.py)
- [ ] T015 [P] 实现文件存储工具类 (backend/app/utils/file_storage.py)

### API基础设施

- [ ] T016 配置CORS中间件 (backend/app/main.py: add_middleware(CORSMiddleware))
- [ ] T017 [P] 实现全局异常处理 (backend/app/core/error_handlers.py)
- [ ] T018 [P] 配置OpenAPI文档 (backend/app/main.py: title, description, version)
- [ ] T019 [P] 实现请求日志中间件 (backend/app/middleware/logging.py)
- [ ] T020 创建健康检查端点 (backend/app/api/health.py: GET /health)

### 智谱AI集成

- [ ] T021 封装智谱AI客户端 (backend/app/services/zhipu_client.py: ZhipuAIClient类)
- [ ] T022 实现Embedding-3向量化 (backend/app/services/zhipu_client.py: embed_texts方法)
- [ ] T023 实现GLM-4系列调用封装 (backend/app/services/zhipu_client.py: chat_completion方法)
- [ ] T024 实现流式输出封装 (backend/app/services/zhipu_client.py: chat_completion_stream方法)
- [ ] T025 实现API调用重试机制 (backend/app/services/zhipu_client.py: 指数退避重试)
- [ ] T026 实现Token统计工具 (backend/app/utils/token_counter.py)

### 前端基础组件

- [ ] T027 [P] 创建布局组件 (frontend/src/components/Layout.tsx: Header, Sidebar, Content)
- [ ] T028 [P] 创建导航组件 (frontend/src/components/Navigation.tsx)
- [ ] T029 [P] 配置Zustand状态管理 (frontend/src/store/index.ts)
- [ ] T030 [P] 配置TanStack Query (frontend/src/lib/queryClient.ts)
- [ ] T031 [P] 创建API客户端封装 (frontend/src/lib/api.ts)
- [ ] T032 [P] 实现WebSocket工具类 (frontend/src/lib/websocket.ts)

### 验收标准

- ✅ SQLite数据库可初始化
- ✅ ChromaDB连接正常
- ✅ 智谱AI API测试连接成功
- ✅ 前端可访问后端健康检查接口
- ✅ 基础UI布局显示正常

---

## Phase 3: User Story 1 - 小说管理与基础问答 (MVP核心)

**用户故事**: 作为用户，我希望能上传小说文件，系统自动索引，并能进行基础的事实查询

**优先级**: P0 (MVP必需)

**预计时间**: 4-5周

**独立测试标准**:
- ✅ 成功上传并索引500万字小说
- ✅ 索引进度实时显示
- ✅ 基础事实查询准确率>75%
- ✅ 查询响应时间<30秒
- ✅ 流式响应正常工作

### 文件上传与解析

- [ ] T033 [US1] 实现文件上传API (backend/app/api/novels.py: POST /novels/upload)
- [ ] T034 [US1] 实现TXT文件解析 (backend/app/services/parser/txt_parser.py)
- [ ] T035 [US1] 实现EPUB文件解析 (backend/app/services/parser/epub_parser.py)
- [ ] T036 [US1] 实现编码检测 (backend/app/utils/encoding_detector.py: 使用chardet)
- [ ] T037 [US1] 实现章节识别算法 (backend/app/services/parser/chapter_detector.py: 正则匹配)

### 文本分块与向量化

- [ ] T038 [US1] 配置RecursiveCharacterTextSplitter (backend/app/services/text_splitter.py: chunk_size=550, overlap=125)
- [ ] T039 [US1] 实现中文分块优化 (backend/app/services/text_splitter.py: 中文分隔符优先级)
- [ ] T040 [US1] 实现批量向量化 (backend/app/services/embedding_service.py: 调用智谱Embedding-3)
- [ ] T041 [US1] 实现向量存储到ChromaDB (backend/app/services/embedding_service.py: 保存向量和元数据)
- [ ] T042 [US1] 实现断点续传机制 (backend/app/services/indexing_service.py: 进度保存和恢复)

### 索引进度追踪

- [ ] T043 [US1] 实现进度WebSocket服务 (backend/app/api/websocket.py: WS /ws/progress/{novel_id})
- [ ] T044 [US1] 实现进度状态更新 (backend/app/services/indexing_service.py: 进度回调)
- [ ] T045 [US1] 实现前端进度监听 (frontend/src/hooks/useIndexingProgress.ts)
- [ ] T046 [US1] 创建进度条组件 (frontend/src/components/ProgressBar.tsx)

### 小说管理UI

- [ ] T047 [P] [US1] 创建小说列表页面 (frontend/src/app/novels/page.tsx)
- [ ] T048 [P] [US1] 创建小说卡片组件 (frontend/src/components/NovelCard.tsx)
- [ ] T049 [P] [US1] 创建上传Modal组件 (frontend/src/components/UploadModal.tsx)
- [ ] T050 [US1] 实现文件拖拽上传 (frontend/src/components/UploadModal.tsx: Dragger组件)
- [ ] T051 [US1] 实现上传进度展示 (frontend/src/components/UploadModal.tsx: Steps组件)

### 小说管理API

- [ ] T052 [P] [US1] 实现获取小说列表API (backend/app/api/novels.py: GET /novels)
- [ ] T053 [P] [US1] 实现获取小说详情API (backend/app/api/novels.py: GET /novels/{id})
- [ ] T054 [P] [US1] 实现删除小说API (backend/app/api/novels.py: DELETE /novels/{id})
- [ ] T055 [US1] 实现获取索引进度API (backend/app/api/novels.py: GET /novels/{id}/progress)

### 基础RAG引擎

- [ ] T056 [US1] 实现查询向量化 (backend/app/services/rag_engine.py: query_embedding方法)
- [ ] T057 [US1] 实现语义检索 (backend/app/services/rag_engine.py: vector_search方法, Top-30)
- [ ] T058 [US1] 实现关键词检索 (backend/app/services/rag_engine.py: keyword_search方法)
- [ ] T059 [US1] 实现混合Rerank (backend/app/services/rag_engine.py: rerank方法, Top-10)
- [ ] T060 [US1] 构建RAG Prompt (backend/app/services/rag_engine.py: build_prompt方法)
- [ ] T061 [US1] 实现答案生成 (backend/app/services/rag_engine.py: generate_answer方法)

### 智能问答API

- [ ] T062 [US1] 实现流式查询WebSocket (backend/app/api/query.py: WS /api/query/stream)
- [ ] T063 [US1] 实现查询理解阶段 (backend/app/services/query_processor.py: understand_query方法)
- [ ] T064 [US1] 实现检索阶段 (backend/app/services/query_processor.py: retrieve_context方法)
- [ ] T065 [US1] 实现生成阶段 (backend/app/services/query_processor.py: generate_answer方法)
- [ ] T066 [US1] 实现完成汇总阶段 (backend/app/services/query_processor.py: finalize_result方法)
- [ ] T067 [US1] 实现非流式查询API (backend/app/api/query.py: POST /api/query)

### 智能问答UI

- [ ] T068 [US1] 创建问答页面 (frontend/src/app/query/page.tsx)
- [ ] T069 [US1] 实现查询输入区 (frontend/src/components/QueryInput.tsx)
- [ ] T070 [US1] 实现流式响应展示 (frontend/src/components/StreamingResponse.tsx)
- [ ] T071 [US1] 实现阶段进度展示 (frontend/src/components/StageProgress.tsx)
- [ ] T072 [US1] 实现流式文本框 (frontend/src/components/StreamingTextBox.tsx: 自动滚动)
- [ ] T073 [US1] 实现答案展示组件 (frontend/src/components/AnswerDisplay.tsx)
- [ ] T074 [US1] 实现引用展示组件 (frontend/src/components/CitationList.tsx)
- [ ] T075 [US1] 实现WebSocket连接管理 (frontend/src/hooks/useQueryStream.ts)

### US1 验收标准

- ✅ 成功上传500万字小说，索引完成
- ✅ 索引进度实时显示，断点续传正常
- ✅ 基础事实查询准确率>80%（MVP目标，符合PRD）
- ✅ 查询流式响应正常，5个阶段清晰展示
- ✅ 流式文本自动滚动，用户可干预
- ✅ 查询响应时间<30秒
- ✅ 引用准确，100%包含章节号

---

## Phase 4: User Story 2 - 在线阅读

**用户故事**: 作为用户，我希望能在系统中直接阅读小说，按章节浏览

**优先级**: P1

**预计时间**: 1-2周

**独立测试标准**:
- ✅ 章节列表完整显示
- ✅ 章节内容无乱码
- ✅ 章节切换流畅(<1秒)
- ✅ 支持10万字超长章节

### 章节管理API

- [ ] T076 [P] [US2] 实现获取章节列表API (backend/app/api/chapters.py: GET /novels/{id}/chapters)
- [ ] T077 [P] [US2] 实现获取章节内容API (backend/app/api/chapters.py: GET /novels/{id}/chapters/{num})
- [ ] T078 [US2] 实现章节缓存机制 (backend/app/services/chapter_service.py: Redis/内存缓存)

### 阅读器UI

- [ ] T079 [US2] 创建阅读器页面 (frontend/src/app/reader/page.tsx)
- [ ] T080 [P] [US2] 创建章节侧边栏组件 (frontend/src/components/ChapterSidebar.tsx)
- [ ] T081 [P] [US2] 创建阅读区域组件 (frontend/src/components/ReadingArea.tsx)
- [ ] T082 [US2] 实现章节搜索功能 (frontend/src/components/ChapterSidebar.tsx: 搜索框)
- [ ] T083 [US2] 实现章节导航按钮 (frontend/src/components/ChapterNavigation.tsx: 上一章/下一章)
- [ ] T084 [US2] 实现全屏阅读模式 (frontend/src/app/reader/page.tsx: 全屏切换)

### US2 验收标准

- ✅ 章节列表加载<1秒
- ✅ 章节内容完整无乱码
- ✅ 章节切换流畅
- ✅ 支持10万字章节流畅显示
- ✅ 章节搜索功能正常

---

## Phase 5: User Story 3 - 知识图谱与GraphRAG

**用户故事**: 作为用户，我希望系统能构建知识图谱，利用角色关系提升问答准确性

**优先级**: P0

**预计时间**: 2-3周

**依赖**: US1完成

**独立测试标准**:
- ✅ 知识图谱构建成功
- ✅ 角色识别准确率>70%
- ✅ 关系提取准确率>60%
- ✅ GraphRAG检索结果质量提升15%+

### 实体提取

- [ ] T085 [US3] 配置HanLP模型 (backend/app/services/nlp/hanlp_client.py)
- [ ] T086 [US3] 实现实体提取服务 (backend/app/services/nlp/entity_extractor.py: 角色/地点/组织)
- [ ] T087 [US3] 实现实体去重与合并 (backend/app/services/nlp/entity_merger.py)
- [ ] T088 [US3] 存储实体到SQLite (backend/app/services/entity_service.py)

### 知识图谱构建

- [ ] T089 [US3] 实现NetworkX图谱初始化 (backend/app/services/graph/graph_builder.py)
- [ ] T090 [US3] 实现节点添加逻辑 (backend/app/services/graph/graph_builder.py: add_entity方法)
- [ ] T091 [US3] 实现关系提取 (backend/app/services/graph/relation_extractor.py: 使用GLM-4)
- [ ] T092 [US3] 实现边添加逻辑 (backend/app/services/graph/graph_builder.py: add_relation方法)
- [ ] T093 [US3] 实现时序属性标注 (backend/app/services/graph/graph_builder.py: 章节范围)
- [ ] T094 [US3] 实现图谱持久化 (backend/app/services/graph/graph_builder.py: pickle保存)
- [ ] T095 [US3] 实现PageRank重要性计算 (backend/app/services/graph/graph_analyzer.py)

### 章节重要性评分

- [ ] T096 [US3] 实现章节重要性计算 (backend/app/services/graph/chapter_scorer.py: 新增实体30% + 关系变化50% + 事件密度20%)
- [ ] T097 [US3] 更新章节表importance_score字段 (backend/app/services/indexing_service.py)

### GraphRAG集成

- [ ] T098 [US3] 实现图谱检索 (backend/app/services/rag_engine.py: graph_search方法)
- [ ] T099 [US3] 实现时序查询 (backend/app/services/graph/graph_query.py: get_relationship_at_chapter)
- [ ] T100 [US3] 增强混合Rerank (backend/app/services/rag_engine.py: 添加时序权重15%)
- [ ] T101 [US3] 实现置信度评分 (backend/app/services/rag_engine.py: 图谱一致性+向量匹配度)

### US3 验收标准

- ✅ 千万字小说知识图谱构建完成
- ✅ 实体识别召回率>70%
- ✅ 关系提取准确率>60%
- ✅ GraphRAG检索准确率提升15%+
- ✅ 时序查询功能正常

---

## Phase 6: User Story 4 - 演变分析与Self-RAG

**用户故事**: 作为用户，我希望系统能分析角色演变，检测并解释矛盾信息

**优先级**: P0

**预计时间**: 2-3周

**依赖**: US3完成

**独立测试标准**:
- ✅ 演变分析基本准确
- ✅ 矛盾检测召回率>70%
- ✅ Self-RAG修正提升准确率10%+
- ✅ 诡计识别率>70%

### 智能查询路由

- [ ] T102 [US4] 实现查询类型分类 (backend/app/services/query_router.py: 对话/分析/事实)
- [ ] T103 [US4] 实现对话类查询策略 (backend/app/services/rag_engine.py: 优先短块+引号权重)
- [ ] T104 [US4] 实现分析类查询策略 (backend/app/services/rag_engine.py: 合并相邻块)

### 演变分析

- [ ] T105 [US4] 实现时序分段检索 (backend/app/services/evolution_analyzer.py: 早/中/后期)
- [ ] T106 [US4] 实现演变点识别 (backend/app/services/evolution_analyzer.py: 突变关键词)
- [ ] T107 [US4] 实现图谱演变查询 (backend/app/services/graph/graph_query.py: get_relationship_evolution)
- [ ] T108 [US4] 实现演变轨迹生成 (backend/app/services/evolution_analyzer.py)

### Self-RAG增强（PRD § 2.3.4完整要求）

- [ ] T109 [US4] 实现断言提取 (backend/app/services/self_rag/assertion_extractor.py: 使用GLM-4提取关键断言)
- [ ] T110 [US4] 实现多源证据收集 (backend/app/services/self_rag/evidence_collector.py: 为每个断言收集多个证据源)
- [ ] T111 [US4] 实现证据质量评分 (backend/app/services/self_rag/evidence_scorer.py: 三维评分)
  - 时效性评分：证据距离查询时间点的远近
  - 具体性评分：证据的详细程度和明确性
  - 权威性评分：基于来源章节重要性和可信度
- [ ] T112 [US4] 实现时序一致性检查 (backend/app/services/self_rag/consistency_checker.py: 验证事件时间线合理性)
- [ ] T113 [US4] 实现角色一致性检查 (backend/app/services/self_rag/consistency_checker.py: 验证角色行为逻辑连贯性)
- [ ] T114 [US4] 实现矛盾检测 (backend/app/services/self_rag/contradiction_detector.py: 检测断言间冲突)
- [ ] T115 [US4] 实现答案修正 (backend/app/services/self_rag/answer_corrector.py: 基于矛盾检测修正答案或标注不确定性)

### 矛盾展示UI

- [ ] T116 [US4] 创建矛盾卡片组件 (frontend/src/components/ContradictionCard.tsx)
- [ ] T117 [US4] 集成Self-RAG验证阶段UI (frontend/src/components/StreamingResponse.tsx: 验证阶段)

### US4 验收标准

- ✅ 演变分析提取关键转折点
- ✅ 矛盾检测召回率>77%（MVP目标，优化后>90%）
- ✅ Self-RAG修正提升准确率10%+
- ✅ 证据质量评分准确率>75%
- ✅ 时序/角色一致性检查覆盖率>85%
- ✅ 诡计识别率>72%（MVP目标，优化后>88%）

---

## Phase 7: User Story 5 - 可视化分析

**用户故事**: 作为用户，我希望能查看角色关系图和时间线可视化

**优先级**: P0

**预计时间**: 1-2周

**依赖**: US3完成

**独立测试标准**:
- ✅ 关系图清晰展示主要角色
- ✅ 时间线标注非线性叙事
- ✅ 图表交互流畅
- ✅ 支持导出PNG

### 关系图生成

- [ ] T118 [P] [US5] 实现关系图数据API (backend/app/api/graph.py: GET /graph/relations/{id})
- [ ] T119 [US5] 实现图谱数据转换 (backend/app/services/graph/graph_exporter.py: NetworkX → JSON)
- [ ] T120 [US5] 实现关系过滤 (backend/app/api/graph.py: 按章节范围过滤)

### 时间线生成

- [ ] T121 [P] [US5] 实现时间线数据API (backend/app/api/graph.py: GET /graph/timeline/{id})
- [ ] T122 [US5] 实现时间标记提取 (backend/app/services/timeline/time_extractor.py)
- [ ] T123 [US5] 实现时间轴构建 (backend/app/services/timeline/timeline_builder.py)
- [ ] T124 [US5] 标注叙述顺序vs真实顺序 (backend/app/services/timeline/timeline_builder.py)

### 可视化UI

- [ ] T125 [US5] 创建可视化页面 (frontend/src/app/graph/page.tsx: Tabs布局)
- [ ] T126 [P] [US5] 实现关系图组件 (frontend/src/components/RelationGraph.tsx: Plotly力导向图)
- [ ] T127 [P] [US5] 实现时间线组件 (frontend/src/components/Timeline.tsx: Plotly时间线)
- [ ] T128 [US5] 实现时间滑块 (frontend/src/components/RelationGraph.tsx: 章节范围选择)
- [ ] T129 [US5] 实现图表交互 (frontend/src/components/RelationGraph.tsx: 点击节点/边)
- [ ] T130 [US5] 实现图表导出 (frontend/src/components/GraphExport.tsx: 导出PNG)

### US5 验收标准

- ✅ 关系图显示>10个主要角色
- ✅ 关系准确率>70%
- ✅ 时间线标注非线性片段
- ✅ 图表交互流畅
- ✅ 支持导出PNG

---

## Phase 8: User Story 6 - 模型管理

**用户故事**: 作为用户，我希望能在多个智谱AI模型之间切换，根据查询复杂度选择

**优先级**: P0

**预计时间**: 3-5天

**依赖**: US1完成

**独立测试标准**:
- ✅ 支持GLM-4.6/4.5/4-Plus/4/Flash切换
- ✅ 模型切换实时生效
- ✅ Token消耗按模型正确统计

### 模型配置

- [ ] T131 [P] [US6] 定义模型枚举 (backend/app/models/schemas.py: ModelType枚举)
- [ ] T132 [P] [US6] 实现模型配置加载 (backend/app/core/config.py: 模型列表和默认值)
- [ ] T133 [US6] 实现模型验证 (backend/app/api/query.py: 验证model参数)

### 模型切换

- [ ] T134 [US6] 动态模型调用 (backend/app/services/zhipu_client.py: 根据model参数调用)
- [ ] T135 [US6] 前端模型选择器 (frontend/src/components/ModelSelector.tsx)
- [ ] T136 [US6] 保存用户偏好 (frontend/src/store/userPreferences.ts: localStorage)

### 配置管理UI

- [ ] T137 [US6] 创建设置页面 (frontend/src/app/settings/page.tsx)
- [ ] T138 [P] [US6] 实现API Key配置 (frontend/src/components/ApiKeyConfig.tsx)
- [ ] T139 [P] [US6] 实现连接测试 (backend/app/api/config.py: POST /config/test-connection)
- [ ] T140 [US6] 实现默认模型设置 (frontend/src/components/ModelConfig.tsx)

### US6 验收标准

- ✅ 模型切换成功，调用正确模型
- ✅ 模型选择器显示正常
- ✅ API Key配置和测试功能正常
- ✅ 用户偏好保存成功

---

## Phase 9: User Story 7 - Token统计

**用户故事**: 作为用户，我希望能查看详细的Token消耗统计，控制成本

**优先级**: P0

**预计时间**: 3-5天

**依赖**: US1, US6完成

**独立测试标准**:
- ✅ Token统计准确
- ✅ 按模型分类正确
- ✅ 累计统计数据准确
- ✅ 统计图表清晰

### Token追踪

- [ ] T141 [US7] 实现Token计数封装 (backend/app/utils/token_counter.py: count_tokens方法)
- [ ] T142 [US7] 实现索引Token统计 (backend/app/services/indexing_service.py: 记录Embedding-3消耗)
- [ ] T143 [US7] 实现查询Token统计 (backend/app/services/query_processor.py: 记录各阶段消耗)
- [ ] T144 [US7] 存储Token统计到token_stats表 (backend/app/services/token_stats_service.py)

### Token统计API

- [ ] T145 [P] [US7] 实现Token统计查询API (backend/app/api/stats.py: GET /stats/tokens)
- [ ] T146 [P] [US7] 实现按时间段统计 (backend/app/api/stats.py: 支持period参数)
  - 支持按日统计 (period=day)
  - 支持按周统计 (period=week)
  - 支持按月统计 (period=month)
  - 支持自定义日期范围 (startDate, endDate参数)
- [ ] T147 [P] [US7] 实现按模型分类统计 (backend/app/services/token_stats_service.py: 分别统计embedding-3、glm-4系列)
- [ ] T148 [P] [US7] 实现按操作类型统计 (backend/app/services/token_stats_service.py: index vs query独立统计)

### Token统计UI

- [ ] T149 [US7] 查询结果Token展示 (frontend/src/components/TokenStats.tsx: 折叠面板)
- [ ] T150 [P] [US7] 创建统计卡片组件 (frontend/src/components/StatCard.tsx)
- [ ] T151 [P] [US7] 实现统计图表 (frontend/src/components/TokenChart.tsx: Plotly柱状图)
- [ ] T152 [US7] 集成到设置页面 (frontend/src/app/settings/page.tsx: Token统计Section)

### US7 验收标准

- ✅ 索引完成显示Token消耗
- ✅ 查询结果显示Token消耗
- ✅ 统计页面显示累计数据
- ✅ 按模型分类统计正确
- ✅ 按时间段统计正确

---

## Phase 10: Polish & Cross-Cutting Concerns (打磨与跨领域关注点)

**目标**: 优化性能、完善错误处理、用户体验提升、文档完善

**预计时间**: 2-3周

### 性能优化

- [ ] T153 [P] 优化ChromaDB索引参数 (backend/app/core/chromadb_client.py: HNSW参数调优)
- [ ] T154 [P] 实现查询结果缓存 (backend/app/services/cache_service.py: Redis或内存缓存)
- [ ] T155 [P] 优化前端代码分割 (frontend/next.config.js: 动态导入)
- [ ] T156 [P] 实现图片和静态资源压缩 (frontend/next.config.js)
- [ ] T157 优化Prompt精简 (backend/app/prompts/: 压缩系统提示词)
- [ ] T158 实现批处理优化 (backend/app/services/embedding_service.py: 批处理大小调优)

### 错误处理与日志

- [ ] T159 [P] 完善API错误处理 (backend/app/core/error_handlers.py: 细化错误类型)
- [ ] T160 [P] 实现详细日志记录 (backend/app/core/logging.py: 结构化日志)
- [ ] T161 [P] 实现前端错误边界 (frontend/src/components/ErrorBoundary.tsx)
- [ ] T162 实现用户友好错误提示 (frontend/src/components/ErrorMessage.tsx)

### 用户体验提升

- [ ] T163 [P] 实现加载骨架屏 (frontend/src/components/Skeleton.tsx)
- [ ] T164 [P] 优化流式文本滚动体验 (frontend/src/components/StreamingTextBox.tsx: 用户干预检测)
- [ ] T165 实现查询历史侧边栏 (frontend/src/components/QueryHistorySidebar.tsx)
- [ ] T166 实现用户反馈功能 (frontend/src/components/FeedbackButtons.tsx + backend API)
- [ ] T167 实现暗黑模式支持 (frontend/src/app/layout.tsx + Tailwind配置)

### 测试

- [ ] T168 [P] 编写后端单元测试 (backend/tests/: pytest, 覆盖率>80%)
- [ ] T169 [P] 编写前端单元测试 (frontend/tests/: Jest, 关键组件)
- [ ] T170 编写API集成测试 (backend/tests/integration/)
- [ ] T171 编写E2E测试 (tests/e2e/: Playwright, 关键流程)
- [ ] T172 性能测试 (tests/performance/: 索引和查询性能)

### 文档

- [ ] T173 [P] 编写用户手册 (docs/user-guide.md)
- [ ] T174 [P] 编写开发文档 (docs/development.md)
- [ ] T175 [P] 编写API文档 (补充OpenAPI注释)
- [ ] T176 编写部署文档 (docs/deployment.md)
- [ ] T177 录制演示视频 (docs/demo.mp4)

### 部署准备

- [ ] T178 [P] 完善Docker配置 (Dockerfile优化, 镜像大小压缩)
- [ ] T179 [P] 编写部署脚本 (scripts/deploy.sh)
- [ ] T180 配置CI/CD (可选: .github/workflows/)
- [ ] T181 编写数据备份脚本 (backend/scripts/backup.py)

### 可访问性与性能监控（宪章合规）

- [ ] T182 [P] 执行WCAG 2.1 AA审计 (frontend/: 使用Axe DevTools扫描所有页面)
- [ ] T183 [P] 实现键盘导航支持 (frontend/src/components/: 焦点管理、Tab顺序、快捷键)
- [ ] T184 验证屏幕阅读器兼容性 (测试NVDA/JAWS，补充ARIA标签)
- [ ] T185 [P] 集成Core Web Vitals监控 (frontend/src/lib/web-vitals.ts: FCP/LCP/FID/CLS上报)
- [ ] T186 配置覆盖率强制检查 (CI: pytest-cov≥80%, jest --coverage≥80%, 失败阻止合并)

---

## 📊 任务依赖关系图

### 依赖关系

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: 小说管理与基础问答) ← MVP核心
    ↓
    ├→ Phase 4 (US2: 在线阅读)
    ├→ Phase 5 (US3: 知识图谱与GraphRAG)
    │       ↓
    │   Phase 6 (US4: 演变分析与Self-RAG)
    ├→ Phase 7 (US5: 可视化) ← 依赖US3
    ├→ Phase 8 (US6: 模型管理)
    └→ Phase 9 (US7: Token统计) ← 依赖US6
    
Phase 10 (Polish) ← 依赖所有US完成
```

### 用户故事完成顺序

1. **US1** (必须最先): 小说管理与基础问答 - MVP基础
2. **US3** (第二优先): 知识图谱与GraphRAG - 核心能力
3. **US4** (第三优先): 演变分析与Self-RAG - 依赖US3
4. **US2, US5, US6, US7** (并行): 可独立实现的增强功能

---

## 🔄 并行执行示例

### Week 3-7 (US1实现期间)

**前端并行任务**:
- T047, T048, T049 (小说管理UI)
- T068-T075 (智能问答UI)

**后端并行任务**:
- T033-T037 (文件解析)
- T038-T042 (文本分块)
- T052-T055 (小说管理API)
- T056-T061 (RAG引擎)

### Week 15-18 (多US并行)

**US2 + US5 + US6 + US7 并行**:
- US2: T076-T084 (在线阅读)
- US5: T118-T130 (可视化)
- US6: T131-T140 (模型管理)
- US7: T141-T152 (Token统计)

---

## ✅ 验收检查清单

### MVP发布 (US1完成)

- [ ] ✅ 成功上传并索引500万字小说
- [ ] ✅ 索引进度实时显示
- [ ] ✅ 智谱API连接正常
- [ ] ✅ 基础事实查询准确率>75%
- [ ] ✅ 查询响应时间<30秒
- [ ] ✅ 流式响应5个阶段正常显示
- [ ] ✅ UI操作流畅，无重大bug

### 功能完整版 (所有US完成)

- [ ] ✅ 所有7个用户故事功能就绪
- [ ] ✅ 知识图谱构建成功
- [ ] ✅ 诡计识别率>70%
- [ ] ✅ 矛盾检测召回率>70%
- [ ] ✅ 可视化图表清晰
- [ ] ✅ 模型切换正常
- [ ] ✅ Token统计准确

### 正式版本 (Phase 10完成)

- [ ] ✅ 事实查询准确率>92%
- [ ] ✅ 诡计识别率>88%
- [ ] ✅ 矛盾检测召回率>90%
- [ ] ✅ 测试覆盖率>80%
- [ ] ✅ 性能指标达标
- [ ] ✅ 用户文档完整
- [ ] ✅ 部署文档完整

---

## 📝 任务格式说明

### 清单格式

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **Checkbox**: `- [ ]` 标记任务状态
- **TaskID**: 唯一任务编号 (T001-T181)
- **[P]**: 可并行执行标记 (45个并行任务)
- **[Story]**: 用户故事标记 (US1-US7)
- **Description**: 清晰的任务描述 + 具体文件路径

### 示例

- ✅ `- [ ] T033 [US1] 实现文件上传API (backend/app/api/novels.py: POST /novels/upload)`
- ✅ `- [ ] T047 [P] [US1] 创建小说列表页面 (frontend/src/app/novels/page.tsx)`

---

## 🎯 实施建议

1. **MVP优先**: 专注Phase 1-3 (US1)，3-5周完成可演示原型
2. **并行开发**: 前后端分工，最大化并行任务执行
3. **增量交付**: 每个Phase完成后立即集成测试
4. **质量把关**: 每个US完成后进行独立验收
5. **文档同步**: 开发过程中同步更新文档

---

**任务清单生成完成**

*本文档定义了89个具体任务，支持14-20周的增量开发计划。*

