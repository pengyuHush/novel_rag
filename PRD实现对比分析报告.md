# PRD与实现对比分析报告

## 文档版本
- **PRD文档**: 网络小说智能问答系统PRD-最终版.md (版本 3.0, 2025-11-11)
- **代码版本**: 当前代码库 (2025-11-13)
- **审查日期**: 2025-11-13

---

## 📊 总体评估

**符合度**: ⭐⭐⭐⭐☆ (85%)

**核心功能完成度**: ✅ 高
**技术架构一致性**: ✅ 高
**细节实现差异**: ⚠️ 存在部分差异

---

## ✅ 完全符合PRD的部分

### 1. 技术架构 (100%符合)

#### 前端技术栈
- ✅ React 18
- ✅ Next.js 14
- ✅ Ant Design UI组件库
- ✅ Zustand 状态管理
- ✅ TypeScript

#### 后端技术栈
- ✅ FastAPI 0.104+
- ✅ Python 3.10+
- ✅ SQLite数据库
- ✅ ChromaDB向量数据库
- ✅ NetworkX知识图谱
- ✅ HanLP中文NLP
- ✅ 智谱AI API集成

### 2. 核心模块实现

#### ✅ 小说管理模块 (2.1节)
- **上传功能**: 完整实现,支持TXT/EPUB
- **多本管理**: 完整实现列表、删除、切换功能
- **在线阅读**: 完整实现(2.1.3节)
  - 章节列表侧边栏 ✅
  - 阅读区域展示 ✅
  - 上一章/下一章导航 ✅
  - 全屏阅读模式 ✅
  - API: `GET /api/novels/{novel_id}/chapters` ✅
  - API: `GET /api/novels/{novel_id}/chapters/{num}` ✅

#### ✅ 智能问答模块 (2.2节)
- **基础问答**: 完整实现
  - Hybrid Search ✅
  - 语义检索 ✅
  - 智能查询路由 ✅
- **WebSocket流式响应**: 完整实现
  - 5阶段展示(理解/检索/生成/验证/汇总) ✅
  - 流式token输出 ✅
  - 实时进度展示 ✅

#### ✅ 知识图谱模块
- **GraphBuilder**: 完整实现
- **NetworkX图谱**: 完整实现
- **时序属性标注**: 完整实现

### 3. 数据库设计 (4.3节)

完全符合PRD设计:
- ✅ novels表: 所有字段齐全
- ✅ chapters表: 所有字段齐全
- ✅ entities表: 所有字段齐全
- ✅ queries表: 所有字段齐全

---

## ⚠️ 部分差异 (需要注意)

### 1. 模型支持差异 ⚠️

**PRD文档 (2.5节)要求:**
```
- GLM-4.6 (旗舰)
- GLM-4.5 (高级)
- GLM-4-Plus (高端)
- GLM-4 (标准)
- GLM-4-Flash (快速)
- Embedding-3 (向量模型)
```

**实际实现 (backend/app/core/config.py):**
```python
supported_models = [
    # 免费模型
    "GLM-4.5-Flash",        # ✅ 新增
    "GLM-4-Flash-250414",   # ✅ PRD中的GLM-4-Flash对应版本
    
    # 高性价比
    "GLM-4.5-Air",          # ✅ 新增(默认模型)
    "GLM-4.5-AirX",         # ✅ 新增
    "GLM-4-Air-250414",     # ✅ 新增
    
    # 极速模型
    "GLM-4.5-X",            # ✅ 新增
    "GLM-4-AirX",           # ✅ 新增
    "GLM-4-FlashX-250414",  # ✅ 新增
    
    # 高性能模型
    "GLM-4.5",              # ✅ PRD中的GLM-4.5
    "GLM-4-Plus",           # ✅ PRD中的GLM-4-Plus
    "GLM-4.6",              # ✅ PRD中的GLM-4.6
    
    # 超长上下文
    "GLM-4-Long",           # ✅ 新增
]
```

**默认模型差异:**
- **PRD文档**: 推荐`GLM-4`作为标准模型
- **实际实现**: 默认`GLM-4.5-Air`(更新更优)

**分析**: 
- ✅ **正向改进**: 实现包含了更多智谱AI新模型(符合官方文档更新)
- ✅ 默认模型选择`GLM-4.5-Air`更优(性价比高)
- ⚠️ PRD中的`GLM-4`标准模型未在列表中,但有更新的`GLM-4.5-Air`替代

**建议**: 更新PRD文档以反映最新的智谱AI模型列表

---

### 2. 分块策略参数 ✅

**PRD文档 (2.1.1节)要求:**
```
- 块大小: 500-600字符
- 块重叠: 100-150字符
```

**实际实现 (backend/app/core/config.py):**
```python
chunk_size: int = 550       # ✅ 在500-600范围内
chunk_overlap: int = 125    # ✅ 在100-150范围内
```

**分析**: ✅ **完全符合PRD规范**,选择了推荐范围的中间值

---

### 3. 检索参数差异 ⚠️

**PRD文档 (2.2.1节)要求:**
```
- 语义检索: Top-30候选块
- Rerank后: Top-10块
- 混合权重: 语义60% + 实体25% + 时序15%
```

**实际实现 (backend/app/core/config.py + rag_engine.py):**
```python
# config.py
top_k_retrieval: int = 30   # ✅ 符合
top_k_rerank: int = 10      # ✅ 符合

# rag_engine.py中的rerank方法
# ✅ 实现了查询路由(对话/分析/事实)
# ⚠️ 混合权重未明确体现"语义60% + 实体25% + 时序15%"
```

**分析**: 
- ✅ Top-K参数完全符合
- ⚠️ 混合权重公式未完全显式实现(但有类似逻辑)

**建议**: 在`rag_engine.py`的`rerank`方法中明确注释或实现混合权重公式

---

### 4. Self-RAG实现状态 ⚠️

**PRD文档 (2.3.4节)要求:**
```
Self-RAG增强流程:
1. ✅ 初次生成
2. ⚠️ 多源证据收集 + 证据质量评分
3. ⚠️ 增强矛盾检测(时序一致性 + 角色一致性)
4. ⚠️ 自反思修正
5. ⚠️ 置信度评分
```

**实际实现 (backend/app/api/query.py):**
```python
# 阶段4: Self-RAG验证（TODO: 完整实现）
await websocket.send_json(StreamMessage(
    stage=QueryStage.VALIDATING,
    content="正在验证答案准确性...",
    progress=0.8
).model_dump())

# TODO: 实现Self-RAG验证逻辑
# - 从答案中提取断言
# - 检索多源证据
# - 检测矛盾信息
# - 计算置信度
# 当前版本跳过此步骤，直接进入完成阶段
```

**后端代码存在但未完整集成:**
- ✅ `self_rag/assertion_extractor.py` - 断言提取器(已实现)
- ✅ `self_rag/evidence_collector.py` - 证据收集器(已实现)
- ✅ `self_rag/evidence_scorer.py` - 证据评分器(已实现)
- ✅ `self_rag/consistency_checker.py` - 一致性检查器(已实现)
- ✅ `self_rag/contradiction_detector.py` - 矛盾检测器(已实现)
- ✅ `self_rag/answer_corrector.py` - 答案修正器(已实现)
- ⚠️ **但未在`query.py`的WebSocket流中调用**

**分析**: 
- ✅ Self-RAG所有子模块已完整实现
- ⚠️ **关键问题**: 未在查询流程中真正使用
- ⚠️ WebSocket查询中跳过了Self-RAG验证阶段

**影响**: 
- 无法实现PRD承诺的"矛盾检测率>70%"和"自反思修正提升准确率12%+"
- 前端展示的矛盾检测结果为空

**建议**: 
1. 在`query.py`的`query_stream`函数中集成Self-RAG验证逻辑
2. 调用已实现的6个Self-RAG子模块
3. 返回矛盾检测结果和修正后的答案

---

### 5. GraphRAG集成状态 ⚠️

**PRD文档 (2.3.3节)要求:**
```
GraphRAG实现:
1. ✅ 图谱检索
2. ✅ 向量检索
3. ⚠️ 章节重要性动态评分(基于图谱)
4. ⚠️ 双路融合(图谱+向量)
5. ⚠️ 置信度评分(图谱一致性+向量匹配度)
```

**实际实现分析:**

**已实现部分:**
- ✅ `graph/graph_builder.py` - 图谱构建完整
- ✅ `graph/graph_query.py` - 图谱查询完整
- ✅ `graph/graph_analyzer.py` - 图谱分析完整

**未完全集成部分:**
- ⚠️ `rag_engine.py`中未显式调用图谱查询
- ⚠️ 未实现"章节重要性动态评分"
- ⚠️ 未实现"双路融合"逻辑
- ⚠️ 未实现"置信度评分(图谱+向量)"

**建议**: 
1. 在`rag_engine.py`的`rerank`方法中集成图谱查询
2. 实现章节重要性评分逻辑
3. 融合图谱信息到检索结果中

---

### 6. Token统计实现 ⚠️

**PRD文档 (2.6节)要求:**
```json
{
  "totalTokens": 12500,
  "byModel": {
    "embedding-3": {
      "inputTokens": 2000
    },
    "glm-4": {
      "promptTokens": 8500,
      "completionTokens": 2000,
      "totalTokens": 10500
    }
  }
}
```

**实际实现 (backend/app/api/query.py):**
```python
# 非流式查询
token_stats=TokenStats(
    total_tokens=0,  # TODO: 实际统计
    prompt_tokens=0,
    completion_tokens=0
)

# WebSocket流式查询
# ⚠️ 未返回Token统计信息
```

**分析**: 
- ⚠️ Token统计功能未完整实现
- ⚠️ 前端`TokenStats.tsx`组件已实现,但后端未提供数据
- ✅ `token_stats_service.py`服务已实现,但未被调用

**建议**: 
1. 在查询流程中调用`token_stats_service.py`
2. 统计Embedding-3和GLM模型的Token消耗
3. 在WebSocket最终结果中返回完整的Token统计

---

### 7. 演变分析功能 ⚠️

**PRD文档 (2.2.2节)要求:**
```
演变分析功能:
- ✅ 时序分段检索
- ⚠️ 演变点识别
- ⚠️ 知识图谱辅助
- ⚠️ 时间线展示
```

**实际实现:**
- ✅ `evolution_analyzer.py`已实现
- ⚠️ 未在前端提供独立的"演变分析"入口
- ⚠️ 未在查询类型路由中明确处理演变类查询

**建议**: 
1. 在前端查询界面添加"查询类型"选择(事实/关系/演变/矛盾)
2. 根据查询类型调用不同的分析逻辑
3. 为演变分析提供专门的可视化展示

---

### 8. 时间线重建功能 ⚠️

**PRD文档 (2.2.4节)要求:**
```
时间线重建:
- ⚠️ 时间标记提取
- ⚠️ 时间轴构建
- ⚠️ 叙述顺序对比
- ⚠️ Plotly可视化
```

**实际实现:**
- ✅ `timeline/time_extractor.py`已实现
- ✅ `timeline/timeline_builder.py`已实现
- ⚠️ 前端`Timeline.tsx`组件已实现,但API未完整对接
- ⚠️ `/api/graph/timeline/{novel_id}`端点未在`graph.py`中实现

**建议**: 
1. 在`backend/app/api/graph.py`中实现时间线API
2. 对接前端`Timeline.tsx`组件
3. 提供时间线可视化页面

---

### 9. 可视化模块差异 ⚠️

**PRD文档 (2.4节)要求:**
```
可视化模块:
- ✅ 角色关系图(Plotly)
- ⚠️ 时间线可视化(Plotly)
- ⚠️ 统计数据面板
```

**实际实现 (frontend/app/graph/page.tsx):**
```tsx
<Tabs>
  <TabPane tab="角色关系图" key="relations">  {/* ✅ 已实现 */}
    <RelationGraph novelId={selectedNovelId} />
  </TabPane>
  <TabPane tab="时间线分析" key="timeline">  {/* ⚠️ 组件已实现,API未对接 */}
    <TimelineVisualization novelId={selectedNovelId} />
  </TabPane>
  <TabPane tab="统计数据" key="stats">  {/* ⚠️ 未实现 */}
    <StatisticsDashboard novelId={selectedNovelId} />
  </TabPane>
</Tabs>
```

**API实现状态:**
- ✅ `GET /api/graph/relations/{novel_id}` - 已实现
- ⚠️ `GET /api/graph/timeline/{novel_id}` - **未实现**
- ⚠️ `GET /api/graph/statistics/{novel_id}` - **未实现**

**建议**: 
1. 实现`/api/graph/timeline/{novel_id}`端点
2. 实现`/api/graph/statistics/{novel_id}`端点
3. 完善前端`StatisticsDashboard`组件

---

### 10. 用户反馈功能 ⚠️

**PRD文档 (2.7.1节)要求:**
```
用户反馈:
- ✅ 👍准确 / 👎不准确按钮
- ✅ 反馈输入框
- ✅ 数据记录
```

**实际实现:**
- ✅ 后端API: `POST /api/query/{query_id}/feedback` 已实现
- ⚠️ 前端未实现反馈UI组件
- ⚠️ 查询结果页面未显示反馈按钮

**建议**: 
1. 在前端`StreamingTextBox`或查询结果区域添加反馈按钮
2. 实现反馈提交逻辑
3. 保存反馈到数据库

---

### 11. 查询历史功能 ⚠️

**PRD文档 (2.7.2节)标注为P2:**
```
查询历史(P2,后续版本):
- 历史查询列表
- 搜索历史查询
- 重新执行历史查询
- 导出查询记录
```

**实际实现:**
- ✅ 后端API: `GET /api/query/history` 已实现
- ⚠️ 前端未实现历史查询页面/组件
- ⚠️ PRD标注为P2(后续版本),当前未实现**符合预期**

**建议**: 保持现状,后续版本再实现

---

## 🎯 PRD文档需要更新的部分

### 1. 模型列表更新

**当前PRD (2.5.1节):**
```
- GLM-4.6 (旗舰)
- GLM-4.5 (高级)
- GLM-4-Plus (高端)
- GLM-4 (标准)
- GLM-4-Flash (快速)
```

**建议更新为(基于智谱AI官方最新文档):**
```
免费模型:
- GLM-4.5-Flash (免费,推荐测试)
- GLM-4-Flash-250414 (免费,超长上下文)

高性价比模型:
- GLM-4.5-Air (推荐,默认)
- GLM-4.5-AirX
- GLM-4-Air-250414

极速模型:
- GLM-4.5-X
- GLM-4-AirX
- GLM-4-FlashX-250414

高性能模型:
- GLM-4.5
- GLM-4-Plus (超长上下文)
- GLM-4.6 (旗舰)

超长上下文:
- GLM-4-Long (百万tokens)
```

---

### 2. 默认模型更新

**当前PRD:**
```
默认模型: GLM-4 (标准，推荐)
```

**建议更新为:**
```
默认模型: GLM-4.5-Air (高性价比，推荐)
理由: 更新的模型,性能更好,价格更低(¥0.001/千tokens)
```

---

### 3. 技术依赖版本更新

**当前PRD (1.6节):**
```
依赖:
- LangChain
- ChromaDB
- HanLP
- NetworkX
- Plotly
- Streamlit  ⚠️ 错误
```

**实际实现:**
```
前端:
- React 18 + Next.js 14 (不是Streamlit!)
- Ant Design
- Zustand
- TanStack Query
- Plotly.js

后端:
- FastAPI
- LangChain
- ChromaDB
- HanLP
- NetworkX
- Plotly (后端图表生成,可选)
```

**PRD错误**: 文档提到使用`Streamlit`作为前端,但实际采用了更现代的`React + Next.js`架构

**建议**: 更新PRD第1.6节和4.2节,删除Streamlit相关描述,更新为React + Next.js

---

### 4. API端点文档更新

**PRD遗漏的已实现端点:**
```
✅ GET  /config/models - 获取模型列表
✅ POST /config/test-connection - 测试API连接
✅ GET  /config/current - 获取当前配置
✅ GET  /health - 健康检查
```

**建议**: 在PRD第5.3节中添加这些端点

---

## 📋 功能完成度总结表

| 功能模块 | PRD要求 | 实现状态 | 完成度 | 备注 |
|---------|--------|---------|-------|------|
| **小说管理** | P0 | ✅ | 100% | 完全符合 |
| **在线阅读** | P1 | ✅ | 100% | 完全符合 |
| **基础问答** | P0 | ✅ | 95% | Token统计未完整 |
| **流式响应** | P0 | ✅ | 100% | 完全符合 |
| **智能查询路由** | P0 | ✅ | 90% | 已实现3种类型路由 |
| **演变分析** | P0 | ⚠️ | 60% | 代码已实现,未集成到UI |
| **矛盾检测** | P0 | ⚠️ | 70% | 代码已实现,未在查询流程中调用 |
| **时间线重建** | P0 | ⚠️ | 60% | 代码已实现,API未对接 |
| **Self-RAG** | P0 | ⚠️ | 80% | 所有子模块已实现,但未在查询中调用 |
| **GraphRAG** | P0 | ⚠️ | 70% | 图谱已构建,但未融合到检索 |
| **知识图谱** | P0 | ✅ | 90% | 构建完整,查询部分未完全集成 |
| **角色关系图** | P0 | ✅ | 100% | 完全符合 |
| **时间线可视化** | P0 | ⚠️ | 50% | 组件已实现,后端API未对接 |
| **Token统计** | P0 | ⚠️ | 50% | 服务已实现,未在查询中调用 |
| **模型切换** | P0 | ✅ | 100% | 完全符合,支持更多模型 |
| **用户反馈** | P0 | ⚠️ | 50% | 后端已实现,前端UI未实现 |
| **查询历史** | P2 | ⚠️ | 50% | 后端已实现,前端未实现(符合P2优先级) |

---

## 🔧 优先级修复建议

### 🔴 高优先级 (影响核心功能)

1. **集成Self-RAG到查询流程** ⭐⭐⭐⭐⭐
   - **影响**: 无法实现PRD承诺的矛盾检测和自反思修正
   - **修复**: 在`query.py`的`query_stream`中调用Self-RAG模块
   - **预计工作量**: 4-6小时

2. **实现Token统计** ⭐⭐⭐⭐⭐
   - **影响**: 用户无法看到API消耗,成本不透明
   - **修复**: 在查询流程中调用`token_stats_service.py`
   - **预计工作量**: 2-3小时

3. **集成GraphRAG到检索流程** ⭐⭐⭐⭐
   - **影响**: 图谱增强检索未生效,准确率受影响
   - **修复**: 在`rag_engine.py`中融合图谱查询
   - **预计工作量**: 6-8小时

### 🟡 中优先级 (完善功能体验)

4. **实现时间线API对接** ⭐⭐⭐
   - **影响**: 时间线可视化功能不可用
   - **修复**: 实现`/api/graph/timeline/{novel_id}`端点
   - **预计工作量**: 3-4小时

5. **实现用户反馈UI** ⭐⭐⭐
   - **影响**: 无法收集用户反馈优化系统
   - **修复**: 在查询结果页面添加反馈按钮
   - **预计工作量**: 2-3小时

6. **实现统计数据API** ⭐⭐
   - **影响**: 统计数据面板无数据展示
   - **修复**: 实现`/api/graph/statistics/{novel_id}`端点
   - **预计工作量**: 2-3小时

### 🟢 低优先级 (优化改进)

7. **更新PRD文档** ⭐⭐
   - 更新模型列表
   - 修正Streamlit→React的描述
   - 添加新增API端点文档
   - **预计工作量**: 2-3小时

8. **实现查询历史前端** ⭐
   - **影响**: P2功能,后续版本再实现
   - **预计工作量**: 4-6小时

---

## 💡 代码质量评估

### ✅ 优点

1. **架构清晰**: 前后端分离,模块化设计良好
2. **代码规范**: TypeScript + Python类型注解完善
3. **组件复用**: 前端组件封装合理,可复用性强
4. **服务分层**: 后端服务层、API层、数据层分离清晰
5. **错误处理**: 完善的异常处理和错误提示
6. **日志记录**: 详细的日志输出,便于调试
7. **文档注释**: 代码注释清晰,便于维护

### ⚠️ 改进点

1. **TODO标记过多**: 多个关键功能标记为TODO但未实现
   - `query.py`中Self-RAG验证逻辑
   - Token统计调用
   - 置信度计算

2. **功能完整性**: 部分模块实现了但未集成
   - Self-RAG 6个子模块已实现但未使用
   - GraphRAG图谱查询未融合到检索
   - Token统计服务未调用

3. **API一致性**: 部分API端点定义在PRD中但未实现
   - `/api/graph/timeline/{novel_id}`
   - `/api/graph/statistics/{novel_id}`

4. **前端组件**: 部分组件已实现但未对接数据
   - `TokenStats.tsx`组件无数据
   - `Timeline.tsx`组件无API对接

---

## 📌 总结与建议

### 核心结论

1. **整体架构**: ✅ 完全符合PRD设计,技术选型正确
2. **基础功能**: ✅ 小说管理、在线阅读、基础问答完整实现
3. **高级功能**: ⚠️ Self-RAG、GraphRAG、演变分析等已实现代码但未集成
4. **可视化**: ⚠️ 关系图完整,时间线和统计数据需补充
5. **成本控制**: ⚠️ Token统计功能未完整,影响成本透明度

### 下一步行动建议

#### 立即修复 (本周内)
1. ✅ 集成Self-RAG到查询流程
2. ✅ 实现Token统计并返回给前端
3. ✅ 实现用户反馈UI

#### 短期优化 (2周内)
4. ✅ 集成GraphRAG到检索流程
5. ✅ 实现时间线API对接
6. ✅ 实现统计数据API

#### 长期完善 (1个月内)
7. ✅ 完善演变分析UI
8. ✅ 实现查询历史前端
9. ✅ 更新PRD文档

### 优先级排序

```
P0 (必须修复): Self-RAG集成、Token统计、GraphRAG集成
P1 (重要): 用户反馈UI、时间线API、统计API
P2 (优化): PRD文档更新、查询历史前端
```

---

## 附录: 快速定位指南

### 需要修复的关键文件

1. **后端**:
   - `backend/app/api/query.py` (集成Self-RAG + Token统计)
   - `backend/app/services/rag_engine.py` (集成GraphRAG)
   - `backend/app/api/graph.py` (实现时间线和统计API)

2. **前端**:
   - `frontend/app/query/page.tsx` (添加反馈按钮)
   - `frontend/components/TokenStats.tsx` (对接Token数据)
   - `frontend/components/Timeline.tsx` (对接时间线API)

3. **文档**:
   - `网络小说智能问答系统PRD-最终版.md` (更新模型列表和技术栈)

---

## 📞 联系信息

如有疑问或需要进一步讨论,请参考:
- 代码仓库: `D:\code\vibe_coding\novel_rag_spec_kit`
- PRD文档: `网络小说智能问答系统PRD-最终版.md`
- 任务清单: `specs/master/tasks.md`

---

**报告生成时间**: 2025-11-13  
**审查者**: AI Assistant  
**文档版本**: 1.0

