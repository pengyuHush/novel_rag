# 网络小说智能问答系统产品需求文档（最终版）

## 文档版本控制
| 版本 | 日期 | 作者 | 修订说明 |
|------|------|------|----------|
| 3.0 | 2025-11-11 | AI Assistant | 融合版本，基于用户确认需求 |
| 2.0 | 2024-12-19 | AI Assistant | 详细版本 |
| 1.0 | 2024-11-11 | Grok 4 | 初始版本 |

---

## 执行摘要

本文档定义了一个**个人级网络小说智能问答系统**的完整产品需求。系统核心价值在于**准确理解复杂叙事结构**，特别是识别和处理**叙述诡计**（如时间线倒叙、角色立场演变、关键信息延迟揭示等），为用户提供可靠的剧情、角色查询服务。

**核心设计原则**：
```
准确性 > 成本 > 效率
```

系统基于**Retrieval-Augmented Generation (RAG)** 架构，结合**GraphRAG**和**Self-RAG**技术，使用**智谱AI开放平台**提供的API服务（GLM-4系列大模型 + Embedding向量模型），无需本地GPU，可处理单本**千万字级**长篇小说。

---

## 1. 产品概述

### 1.1 产品愿景

开发一个能够**深度理解**网络小说叙事结构的智能问答系统，通过增强的RAG技术和知识图谱，抵抗叙述诡计误导，为读者提供**高准确率**的剧情分析、角色关系梳理和时间线重建服务。

### 1.2 产品定位

- **目标用户**：网络小说深度爱好者（个人使用）
- **核心场景**：阅读辅助、情节回顾、角色关系梳理、矛盾检测
- **差异化价值**：
  1. 支持**千万字级**超长文本处理
  2. **叙述诡计识别**（时间线欺骗、角色演变、信息隐藏、身份伪装）
  3. 准确性优先，基于**智谱AI GLM-4系列**高质量大模型
  4. 知识图谱增强的时序关系分析
  5. **零硬件门槛**，无需本地GPU部署

### 1.3 成功标准

| 指标类型 | 目标值 | 说明 |
|---------|--------|------|
| **准确率** | MVP: 80%，迭代后: 92%+ | 事实查询准确率（优化检索+智谱GLM-4） |
| **诡计识别率** | MVP: 72%，迭代后: 88%+ | 中级叙述诡计识别（增强Self-RAG） |
| **响应时间** | 简单<30秒，复杂<3分钟 | 基于智谱API，速度大幅提升 |
| **文本处理能力** | 单本≤1000万字 | 硬性要求 |
| **成本控制** | 单次查询<¥0.5 | 基于智谱API定价 |
| **用户满意度** | 4.5/5.0+ | 手动评估 |

### 1.4 目标用户画像

| 用户类型 | 核心需求 | 典型行为 |
|---------|----------|----------|
| **深度读者** | 理解复杂剧情、角色关系 | 阅读千万字长篇，需回顾前期伏笔 |
| **分析爱好者** | 时间线梳理、矛盾检测 | 关注叙事结构，发现作者埋伏 |
| **效率阅读者** | 快速查询遗忘内容 | 长期追更，需要快速定位剧情 |

### 1.5 核心使用场景

#### 场景1：事实查询
**用例**："主角在第几章获得金手指？获得时的具体情况是什么？"  
**系统行为**：检索相关章节，提供章节号+原文引用+简要描述

#### 场景2：角色关系查询（抗诡计）
**用例**："A角色和B角色是什么关系？我记得前期是敌人，后期好像变了？"  
**系统行为**：
- 检测关系演变节点
- 展示时间线上的关系变化
- 标注关键转折章节
- 提供演变原因分析

#### 场景3：矛盾检测
**用例**："主角的能力设定是不是前后矛盾了？"  
**系统行为**：
- 检索能力相关描述
- 按时间线排列
- 标注可能矛盾点
- 分析是否为叙述诡计（如能力隐藏）

#### 场景4：时间线重建
**用例**："这本书有很多倒叙，帮我按实际时间顺序梳理事件"  
**系统行为**：
- 提取事件时间标记
- 重建真实时间线
- 生成时间线可视化图
- 标注叙述顺序与真实顺序的差异

### 1.6 假设与依赖

**假设**：
- 用户拥有小说文本合法使用权
- 硬件环境：普通PC（8GB+内存，50GB存储空间）+ 稳定网络连接
- 小说为中文，章节标记明显（如"第X章"或章节名）
- 用户可接受长时间索引构建（数小时）
- 用户拥有智谱AI开放平台账号和API Key

**依赖**：
- 开源库：LangChain、ChromaDB、HanLP、NetworkX、Plotly、React、Next.js
- **智谱AI服务**：
  - GLM-4系列模型（glm-4-plus / glm-4 / glm-4-flash）
  - Embedding-3向量模型
- Python 3.10+运行环境
- 智谱AI Python SDK (zhipuai)

---

## 2. 核心功能需求

### 2.1 小说管理模块

#### 2.1.1 小说上传与处理（P0）

**功能描述**：支持上传超长篇网络小说文件，自动解析并构建知识库

**输入规格**：
- 文件格式：TXT（UTF-8）、EPUB
- 文件大小：单本最大1000万字（约20-30MB TXT文件）
- 章节要求：需包含明显章节标记（如"第XXX章"、章节名等）

**处理流程**：
1. **文件解析**：自动识别编码（UTF-8）、提取章节结构
2. **文本分块**：
   - **分块技术**：RecursiveCharacterTextSplitter（LangChain）
   - **分块策略**：递归分割，针对中文网络小说优化
     - 按段落边界（\n\n）
     - 按句子边界（。！？）
     - 按中文特殊标点（……、——）
     - 按短句边界（，、；）
     - 最后按字符强制分割
   - **块大小**：**500-600字符**（针对中文优化，信息密度更高）
   - **块重叠**：**100-150字符**（减少冗余，保持连贯）
   - **优势**：避免在句子中间截断，小块检索更精准，适合中文小说场景
3. **实体提取**：
   - 角色识别（HanLP NER）
   - 地点、组织、关键物品提取
   - 时间标记提取（如"三年前"、"XX年"）
4. **嵌入向量化**：
   - 使用智谱AI Embedding-3模型
   - 批处理大小：100个文本块/批（API限制）
   - 向量维度：1024维
   - API调用方式：通过智谱AI Python SDK
5. **知识图谱构建**：
   - 角色关系网（NetworkX）
   - 时序属性标注（早期/中期/后期）
   - 关系演变记录（敌对→中立→盟友等）
6. **索引存储**：
   - 向量存储：ChromaDB持久化
   - 元数据存储：SQLite（章节、角色、事件表）
   - 图谱存储：NetworkX pickle格式

**性能要求**：
- 处理速度：取决于网络和智谱API QPS限制
- 千万字小说预计：3-5小时（含API调用延迟）
- **断点续传**：每处理100章保存进度，支持失败恢复
- **Token统计**：实时统计并在完成后展示总token消耗（详见2.6节）

**验收标准**：
- ✅ 成功处理1000万字小说
- ✅ 章节识别准确率>95%
- ✅ 实体提取召回率>70%
- ✅ 支持进度保存和断点续传
- ✅ 显示实时处理进度条
- ✅ 准确统计并展示Token消耗

#### 2.1.2 多本小说管理（P0）

**功能描述**：支持同时管理多本小说，切换查询对象

**功能清单**：
- 小说列表展示（书名、字数、章节数、处理状态）
- 选择当前查询小说（单选）
- 删除小说及其所有索引数据
- 查看小说基本信息（角色数量、关系图规模、索引完成度）

**验收标准**：
- ✅ 支持至少5本小说同时存储
- ✅ 小说切换响应时间<3秒
- ✅ 删除操作安全确认机制

#### 2.1.3 小说阅读功能（P1）

**功能描述**：提供简洁的分章节在线阅读界面，用户可直接阅读已上传的小说原文

**核心功能**：

1. **章节列表**：
   - 显示完整章节目录（章节号 + 章节标题）
   - 支持快速跳转到指定章节
   - 支持章节搜索（按标题或章节号）

2. **阅读界面**：
   - 清晰的文本排版展示
   - 上一章/下一章快速切换
   - 支持全屏阅读模式

3. **入口设计**：
   - 在小说列表的每个小说卡片中提供"阅读"按钮
   - 与"查看信息"、"查看图谱"、"问答"等按钮并列
   - 点击后直接进入该小说的阅读页面

**前端实现**（React + Next.js）：
```typescript
// 简化的组件结构
<NovelReader>
  <ChapterList />        // 左侧章节列表
  <ReadingArea>          // 阅读区域
    <ChapterContent />   // 章节正文
    <ChapterNav />       // 上一章/下一章按钮
  </ReadingArea>
</NovelReader>
```

**后端API（FastAPI）**：
```python
# 章节相关API
GET  /api/novels/{novel_id}/chapters        # 获取章节列表
GET  /api/novels/{novel_id}/chapters/{num}  # 获取指定章节内容
```

**验收标准**：
- ✅ 章节列表加载流畅（<1秒）
- ✅ 章节内容显示完整无乱码
- ✅ 支持至少10万字章节的流畅阅读
- ✅ 章节切换响应快速

#### 2.1.4 增量更新（P2，后续版本）

**功能描述**：支持为已索引小说添加新章节（追更场景）

**实现要点**：
- 检测新增章节（章节号连续性）
- 仅对新章节进行索引
- 更新知识图谱（新增角色/关系）
- 保持已有索引完整性

---

### 2.2 智能问答模块

#### 2.2.1 基础问答（P0）

**功能描述**：回答关于小说内容的事实性问题

**查询类型**：
1. **事实查询**："X角色在第几章出现？"
2. **关系查询**："A和B是什么关系？"
3. **描述查询**："主角的外貌特征是什么？"
4. **定位查询**："某个关键情节发生在哪一章？"

**检索机制**（Hybrid Search + 智能路由）：

1. **语义检索**：
   - 查询向量化（智谱AI Embedding-3）
   - 向量相似度搜索（ChromaDB）
   - Top-K: 30个候选块（增加召回）
2. **关键词检索**：
   - 提取查询中的实体/关键词
   - 元数据精确匹配
   - 章节范围过滤
3. **智能查询路由**：
   - LLM分类查询类型（对话/分析/事实）
   - 对话类查询：优先短块，增强引号内容权重
   - 分析类查询：合并相邻块，扩展上下文
   - 事实查询：保持标准检索策略
4. **增强混合排序**：
   - 语义相似度 × 0.60
   - 实体匹配 × 0.25
   - **时序权重 × 0.15**（基于章节重要性和位置）
   - 块质量权重：长度接近550字符最优
   - 最终返回Top-10块

**生成机制**：
- 将Top-10块+查询组成Prompt
- 调用智谱AI GLM-4系列模型生成答案
- 答案格式：结论 + 原文引用（章节号）
- Token限制：输入<8K，输出<2K（GLM-4支持128K上下文）

**验收标准**：
- ✅ 简单事实查询准确率>80%（MVP）
- ✅ 响应时间<30秒（智谱API加速）
- ✅ 100%提供原文引用

#### 2.2.2 演变分析（P0）

**功能描述**：分析角色性格、立场、能力的演变过程

**查询示例**："分析主角的性格发展轨迹"

**实现策略**：

1. **时序分段检索**：
   - 将小说分为早期/中期/后期
   - 每个时期检索相关描述
2. **演变点识别**：
   - 检测突变关键词（"从此"、"改变"、"觉醒"等）
   - 对比不同时期的描述差异
3. **知识图谱辅助**：
   - 查询图谱中的属性演变记录
   - 提取关系变化节点
4. **时间线展示**：
   - 生成演变时间轴
   - 标注关键转折点

**验收标准**：
- ✅ 识别出主要演变节点
- ✅ 提供演变原因分析
- ✅ 时间线可视化展示

#### 2.2.3 矛盾检测（P0）

**功能描述**：识别并解释小说中的前后矛盾信息

**检测类型**：
1. **角色属性矛盾**：性格、能力、背景设定不一致
2. **事件矛盾**：事件发生时间、地点、过程冲突
3. **关系矛盾**：角色关系前后描述不符

**检测流程**：
1. **多时期检索**：检索同一对象在不同章节的描述
2. **语义对比**：使用LLM判断描述是否矛盾
3. **分类判断**：
   - **真矛盾**：作者笔误或设定疏漏
   - **伪矛盾（叙述诡计）**：有意隐藏信息、后期反转
4. **证据收集**：提取矛盾来源章节

**输出格式**：
```
矛盾类型：角色能力矛盾
早期描述：第X章，"角色A不会使用火系魔法"
后期描述：第Y章，"角色A释放了强大的火球术"
分析：可能的叙述诡计，角色A一直隐藏实力
置信度：中等
```

**验收标准**：
- ✅ 检测出明显矛盾（召回率>70%）
- ✅ 区分真矛盾和诡计（准确率>60%）
- ✅ 提供证据引用

#### 2.2.4 时间线重建（P0）

**功能描述**：处理倒叙、插叙等非线性叙事，重建真实时间线

**实现策略**：
1. **时间标记提取**：
   - 绝对时间："XX年X月"
   - 相对时间："三年前"、"半个月后"
   - 事件顺序词："之前"、"后来"
2. **时间轴构建**：
   - 将事件映射到时间轴
   - 处理时间冲突（选择更可靠的描述）
3. **叙述顺序对比**：
   - 叙述顺序：章节顺序
   - 真实顺序：重建后时间线
   - 标注倒叙/插叙片段

**可视化**：
- 使用Plotly生成交互式时间线图
- 双轨展示：叙述顺序 vs 真实顺序
- 点击事件显示详情

**验收标准**：
- ✅ 识别70%+时间标记
- ✅ 时间线基本准确
- ✅ 可视化清晰易懂

---

### 2.3 叙述诡计处理（核心模块）

#### 2.3.1 诡计类型定义

基于用户需求，重点处理**中级叙述诡计**：

| 诡计类型 | 定义 | 检测策略 | 优先级 |
|---------|------|----------|--------|
| **角色立场演变** | 角色从敌人变盟友，或反之 | 时序关系图+情感分析 | P0 |
| **关键信息延迟揭示** | 重要信息前期隐藏，后期揭示 | 信息出现时间分析 | P0 |
| **时间线欺骗** | 倒叙/插叙导致时间误解 | 时间标记提取+对齐 | P0 |
| **身份/关系隐藏** | 角色真实身份/关系被隐藏 | 线索关联+图谱推理 | P0 |

#### 2.3.2 知识图谱增强

**图谱结构**：
- **节点**：角色、组织、地点
- **边**：关系类型（盟友、敌对、师徒、亲属等）
- **时序属性**：
  - 关系生效章节
  - 关系失效章节
  - 演变轨迹（敌→中立→友）

**图谱查询**：
- 查询两角色在特定章节的关系
- 追踪关系演变路径
- 检测关系突变点

**示例**：
```python
# 图谱节点
Node: "角色A"
  - 属性: {姓名, 性别, 初登场章节}

# 图谱边（时序）
Edge: "角色A" -[敌对]-> "角色B"
  - 章节范围: [5, 120]
  - 转折事件: "第120章，真相揭示"
  
Edge: "角色A" -[盟友]-> "角色B"
  - 章节范围: [121, 500]
```

#### 2.3.3 GraphRAG集成

**GraphRAG原理**：结合知识图谱的检索增强生成

**实现步骤**：
1. **图谱检索**：根据查询实体，检索相关子图
2. **向量检索**：并行进行语义检索
3. **章节重要性计算**：
   - 基于知识图谱动态评分章节重要性
   - 因子：新增实体数量（30%）、关系变化数量（50%）、事件密度（20%）
   - 影响检索时序权重分配
4. **双路融合**：
   - 图谱提供结构化关系 + 时序信息
   - 向量提供原文细节
   - **置信度评分**：根据图谱一致性和向量匹配度综合打分
5. **生成答案**：LLM综合两路信息

**优势**：
- 图谱明确记录时序关系，防止被早期描述误导
- 向量检索补充细节，保证答案完整性
- 章节重要性动态调整，优先检索关键转折点

#### 2.3.4 Self-RAG自反思

**Self-RAG机制**：生成答案后自我验证，检测矛盾

**增强流程**：
1. **初次生成**：标准RAG流程生成答案
2. **多源证据收集**：
   - 提取答案中的关键断言
   - 为每个断言收集多源证据
   - **证据质量评分**：时效性、具体性、权威性
3. **增强矛盾检测**：
   - 重新检索验证每个断言
   - **时序一致性检查**：验证事件时间线
   - **角色一致性检查**：验证角色行为逻辑
   - 检测断言间的冲突
4. **自反思修正**：
   - 如检测到矛盾，重新检索更多证据
   - 修正答案或标注不确定性
   - 提供矛盾分析（真矛盾 vs 叙述诡计）
5. **置信度评分**：
   - 高置信度：多个高质量证据一致
   - 中置信度：证据部分冲突，可能为叙述诡计
   - 低置信度：证据严重冲突或不足

**示例**：
```
查询："角色A是反派吗？"

初次答案："是，第10章角色A杀害无辜"
自反思检测："但第200章揭示，角色A当时被控制"
修正答案："角色A早期行为邪恶，但第200章揭示其被反派控制，
         后期成为正面角色。这是典型的叙述诡计。"
```

**验收标准**：
- ✅ 矛盾检测率>70%（MVP）
- ✅ 自反思修正提升准确率12%+（增强机制效果）
- ✅ 明确标注不确定性
- ✅ 证据质量评分准确率>75%
- ✅ 时序/角色一致性检查覆盖率>85%

---

### 2.4 可视化模块

#### 2.4.1 角色关系图（P0）

**功能描述**：生成交互式角色关系网络图

**技术实现**：
- NetworkX生成图谱
- Plotly可视化
- 力导向布局（Force-directed layout）

**图形元素**：
- **节点**：角色（大小表示重要性）
- **边**：关系（颜色表示关系类型）
- **标签**：角色名、关系类型

**交互功能**：

- 点击节点：显示角色详细信息
- 点击边：显示关系演变历史
- 时间滑块：查看特定章节范围的关系网

**验收标准**：
- ✅ 显示主要角色关系（>10个角色）
- ✅ 关系准确率>70%
- ✅ 支持交互操作

#### 2.4.2 时间线可视化（P0）

**功能描述**：生成事件时间轴，展示叙述顺序与真实顺序

**可视化形式**：
- Plotly时间线图（Timeline）
- 双轨道：上轨为叙述顺序，下轨为真实顺序
- 连线标注倒叙/插叙片段

**验收标准**：
- ✅ 清晰展示主要事件
- ✅ 标注非线性叙事片段
- ✅ 支持导出图片

---

### 2.5 模型管理与切换（P0）

#### 2.5.1 模型配置

**支持模型列表（智谱AI系列）**：

| 模型类型 | 模型名称 | 特点 | 适用场景 | 价格（元/千tokens） |
|---------|---------|------|----------|---------------------|
| **免费模型** | GLM-4.5-Flash | 免费，日常查询 | 简单事实查询、开发测试 | 免费 |
| **免费模型** | GLM-4-Flash | 免费，128K上下文 | 长文本查询 | 免费 |
| **高性价比** | GLM-4.5-Air | 推荐，性价比最高 | 常规问答、关系查询 | 输入/输出: ¥0.001 |
| **高性价比** | GLM-4.5-AirX | 增强版，高性价比 | 复杂查询、推理 | 输入/输出: ¥0.001 |
| **极速模型** | GLM-4.5-X | 极速响应 | 需要快速响应的场景 | 输入/输出: ¥0.01 |
| **高性能** | GLM-4.5 | 高性能 | 复杂诡计识别、深度分析 | 输入/输出: ¥0.05 |
| **高性能** | GLM-4-Plus | 顶级性能，128K上下文 | 演变分析、矛盾检测 | 输入/输出: ¥0.05 |
| **旗舰模型** | GLM-4.6 | 最新旗舰 | 超复杂推理、关键查询 | 输入/输出: ¥0.1 |
| **超长上下文** | GLM-4-Long | 100万tokens上下文 | 极长文本分析 | 输入/输出: ¥0.001 |
| **向量模型** | Embedding-3 | 1024维向量 | 文本向量化 | 输入: ¥0.001 |

**说明**：
- 系统支持9个智谱AI大语言模型，涵盖免费、高性价比、高性能等多个级别
- 推荐日常使用**GLM-4.5-Air**（性价比最高）或免费模型**GLM-4.5-Flash**
- GLM-4-Long支持百万tokens上下文，适合极长文本场景
- 价格为2025年11月数据，最新价格请参考[智谱AI定价页面](https://open.bigmodel.cn/pricing)

#### 2.5.2 手动切换机制

**前端UI设计**：

- 查询界面顶部：模型选择下拉框（React Select组件）
- 显示当前模型：名称 + 标签（如"GLM-4.6（旗舰）"）+ 预计成本
- 实时切换，无需刷新页面
- 模型选项分组显示（旗舰/高端/标准/快速）

**切换逻辑（前后端交互）**：
- **前端**：
  - 用户选择模型 → 更新本地状态（Zustand）
  - 发送查询请求时携带`model`参数
  - 保存用户偏好到localStorage
- **后端**：
  - FastAPI接收查询请求（含`model`参数）
  - 验证模型名称合法性
  - 动态调用智谱AI对应模型API
  - 返回结果及Token统计

#### 2.5.3 智谱AI API配置

**配置要求**：
- 智谱AI开放平台账号
- API Key（在[智谱AI控制台](https://open.bigmodel.cn/usercenter/apikeys)获取）
- 账户余额充足（建议预存¥50起）

**SDK安装**：
```bash
pip install zhipuai
```

**初始化客户端**：
```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your_api_key_here")
```

**验收标准**：
- ✅ API连接测试成功
- ✅ 模型调用响应正常
- ✅ Token消耗统计准确

---

### 2.6 Token消耗统计（P0）

#### 2.6.1 统计维度

**小说上传流程**：
- Embedding-3向量化消耗：
  - 文本块数量
  - Input tokens总量
  - API调用次数

**智能问答流程**：
- Embedding-3（查询向量化）：
  - Input tokens
- GLM-4系列（答案生成）：
  - Prompt tokens
  - Completion tokens
  - Total tokens
- GLM-4系列（Self-RAG验证，如启用）：
  - Prompt tokens
  - Completion tokens
  - Total tokens

#### 2.6.2 统计汇总

**单次操作统计**：
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

**累计统计**：
- 按模型分类的总消耗
- 操作类型分类（索引/查询）
- 时间段统计（日/周/月）

**显示位置**：
- 上传完成页面：显示本次索引的token消耗
- 查询结果下方：显示本次查询的token消耗（折叠面板）
- 统计页面：显示累计消耗和图表

**验收标准**：
- ✅ 准确记录各模型token消耗
- ✅ 按模型正确分类统计
- ✅ 累计统计数据准确

---

### 2.7 辅助功能

#### 2.7.1 用户反馈（P0）

**功能描述**：用户标记答案是否准确，供后续优化

**UI元素**：
- 答案下方："👍 准确" / "👎 不准确"按钮
- 点击"不准确"：弹出输入框，记录问题

**数据记录**：
- 查询内容
- 答案内容
- 用户反馈
- 时间戳

#### 2.7.2 查询历史（P2，后续版本）

**功能描述**：查看和管理历史查询记录

**功能清单**：
- 历史查询列表
- 搜索历史查询
- 重新执行历史查询
- 导出查询记录

---

## 3. 非功能需求

### 3.1 性能需求

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **索引构建速度** | 取决于网络和API | 千万字需3-5小时（含API调用） |
| **简单查询响应** | <30秒 | 事实查询、GLM-4-Flash |
| **复杂查询响应** | <3分钟 | 演变分析、矛盾检测、GLM-4 |
| **超复杂查询** | <10分钟 | GLM-4-Plus深度推理 |
| **知识库加载** | <10秒 | 切换小说时 |
| **模型切换** | <1秒 | 仅改变API参数 |
| **并发支持** | 1用户 | 个人应用，无需并发 |

**性能优化策略**：

- 向量检索：使用ChromaDB的HNSW索引（近似最近邻）
- 结果缓存：常见查询缓存结果
- 分批处理：大文本分批嵌入

### 3.2 准确性需求

| 指标 | MVP目标 | 优化后目标 | 验证方式 |
|------|---------|-----------|----------|
| **事实查询准确率** | 80% | 92%+ | 手动评估（优化检索+智谱GLM-4） |
| **诡计识别率** | 72% | 88%+ | 手动评估（增强Self-RAG） |
| **引用准确性** | 100% | 100% | 自动验证 |
| **矛盾检测召回率** | 77% | 90%+ | 手动评估（增强验证机制） |

**准确性保证机制**：
1. **智能查询路由**：根据查询类型动态调整检索策略
2. **多证据融合**：综合多个检索块，避免单一来源
3. **时序验证**：通过知识图谱验证时序关系 + 章节重要性动态评分
4. **增强Self-RAG**：证据质量评分 + 时序/角色一致性检查
5. **置信度评分**：基于图谱一致性和证据质量综合打分

### 3.3 成本控制需求

**成本目标（基于智谱AI定价）**：
- **索引构建（一次性）**：
  - 500万字小说：约¥1.5-2.5（Embedding-3）
  - 1000万字小说：约¥3-5（Embedding-3）
- **单次查询**：<¥0.5
- **典型查询成本**：
  - 简单查询（GLM-4-Flash）：¥0.004-0.01/次
  - 标准查询（GLM-4）：¥0.04-0.08/次
  - 复杂查询（GLM-4-Plus）：¥0.2-0.3/次
- **月度预算**（假设每天10次查询）：
  - 轻度使用（主要用Flash）：¥3-5/月
  - 中度使用（混合）：¥15-25/月
  - 重度使用（主要用Plus）：¥60-100/月

**成本优化策略**：
- 简单查询优先使用GLM-4-Flash（仅¥1/百万tokens）
- 复杂查询使用GLM-4（性价比最高）
- 仅最复杂的诡计识别使用GLM-4-Plus
- 检索块数限制：Top-10（避免上下文过长）
- Prompt优化：精简系统提示词
- 结果缓存：相同查询直接返回缓存

### 3.4 可用性需求

**易用性目标**：
- **学习成本**：15分钟内掌握基本操作
- **操作步骤**：核心流程不超过3步
- **错误提示**：清晰的错误消息和解决建议

**界面设计原则**：

- 简洁直观，避免复杂配置
- 实时状态反馈（进度条、加载动画）
- 渐进式功能展示（高级功能折叠）

### 3.5 可靠性需求

**稳定性目标**：
- **系统可用性**：>95%（本地运行）
- **错误恢复**：索引失败自动断点续传
- **数据安全**：本地存储，定期备份提示

**异常处理**：
- API调用失败：自动重试3次，失败后提示切换本地模型
- 本地模型崩溃：记录日志，建议重启应用
- 索引损坏：检测并提示重建

### 3.6 兼容性需求

**平台支持**：
- **操作系统**：Windows 10/11（主要）、Linux（次要）
- **Python版本**：3.10+
- **浏览器**：Chrome 90+、Edge 90+（React + Next.js Web UI）

**文件格式**：

- TXT（UTF-8编码）
- EPUB（需epub库解析）

---

## 4. 技术架构

### 4.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                   前端层（React + Next.js）                  │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐   │
│  │小说管理   │在线阅读   │智能问答   │可视化分析 │系统设置│   │
│  │(上传/列表)│(分章阅读) │(RAG问答)  │(图谱/时间线)│(配置)│   │
│  └──────────┴──────────┴──────────┴──────────┴────────┘   │
│  React 18 + Next.js 14 + Ant Design / shadcn/ui          │
│  Zustand (状态) + TanStack Query (数据获取)               │
└──────────────────────────┬──────────────────────────────────┘
                           │ RESTful API (HTTP/JSON)
                           │ WebSocket (实时通信)
┌──────────────────────────▼──────────────────────────────────┐
│                   后端层（FastAPI）                          │
│  ┌────────────────────────────────────────────────────┐   │
│  │              API路由层                              │   │
│  │  /api/novels/*    /api/query/*    /api/graph/*     │   │
│  │  /api/chapters/*  /api/progress/*  /api/config/*   │   │
│  └───────────────────────┬────────────────────────────┘   │
│                          │                                 │
│  ┌───────────────────────▼────────────────────────────┐   │
│  │              业务逻辑层                              │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┐    │   │
│  │  │文档处理   │RAG引擎   │诡计检测   │模型管理  │    │   │
│  │  │服务      │服务      │服务      │服务      │    │   │
│  │  └──────────┴──────────┴──────────┴──────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│  FastAPI 0.104+ + Pydantic + Uvicorn                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   AI模型层（智谱AI）                         │
│  ┌────────────────────────────────────────────────────┐   │
│  │  GLM系列大语言模型 (API调用)                        │   │
│  │  • GLM-4.6 (旗舰)  • GLM-4.5 (高级)                │   │
│  │  • GLM-4-Plus      • GLM-4 (标准)                  │   │
│  │  • GLM-4-Flash (快速)                              │   │
│  └────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Embedding-3向量模型 (API调用)                      │   │
│  │  • 1024维向量化    • 批量处理                       │   │
│  └────────────────────────────────────────────────────┘   │
│  智谱AI Python SDK (zhipuai)                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   数据持久层                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │向量数据库 │元数据库   │知识图谱  │文件存储  │            │
│  │ChromaDB  │SQLite    │NetworkX  │本地FS    │            │
│  │(向量检索)│(结构数据) │(关系图谱) │(原文件)  │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 技术栈清单

| 技术类别 | 选型 | 版本 | 用途 |
|---------|------|------|------|
| **编程语言** | Python | 3.10+ | 后端主语言 |
| **后端框架** | FastAPI | 0.104+ | RESTful API + WebSocket服务 |
| **前端框架** | React 18 + Next.js 14 | 最新 | 现代化SPA/SSR |
| **UI组件库** | Ant Design / shadcn/ui | 最新 | UI组件 |
| **状态管理** | Zustand / TanStack Query | 最新 | 前端状态管理 |
| **实时通信** | WebSocket | 原生 | 流式响应传输 |
| **LLM框架** | LangChain | 0.1+ | RAG流程编排、文本分块（RecursiveCharacterTextSplitter） |
| **智谱AI SDK** | zhipuai | 最新 | 调用智谱AI服务 |
| **大语言模型** | GLM-4.6 / GLM-4系列 | API | 智能问答、推理 |
| **向量模型** | Embedding-3 | API | 文本向量化（1024维） |
| **向量数据库** | ChromaDB | 0.4+ | 向量存储检索 |
| **关系数据库** | SQLite | 3.40+ | 元数据存储 |
| **NLP工具** | HanLP | 2.1+ | 中文NER、实体提取 |
| **图谱库** | NetworkX | 3.0+ | 知识图谱 |
| **可视化** | Plotly | 5.17+ | 交互式图表 |
| **文件解析** | ebooklib | 0.18+ | EPUB解析 |
| **编码检测** | chardet | 5.0+ | 文件编码识别 |

### 4.3 数据库设计

#### 4.3.1 SQLite元数据库

**表1：novels（小说表）**
```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    total_chars INTEGER,
    total_chapters INTEGER,
    upload_date TIMESTAMP,
    index_status TEXT,  -- 'pending', 'processing', 'completed', 'failed'
    index_progress REAL,
    file_path TEXT
);
```

**表2：chapters（章节表）**
```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    chapter_num INTEGER,
    chapter_title TEXT,
    char_count INTEGER,
    start_pos INTEGER,
    end_pos INTEGER,
    FOREIGN KEY (novel_id) REFERENCES novels(id)
);
```

**表3：entities（实体表）**
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    entity_name TEXT,
    entity_type TEXT,  -- 'character', 'location', 'organization'
    first_chapter INTEGER,
    mention_count INTEGER,
    FOREIGN KEY (novel_id) REFERENCES novels(id)
);
```

**表4：queries（查询记录表）**
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    query_text TEXT,
    answer_text TEXT,
    model_used TEXT,
    token_consumed INTEGER,
    response_time REAL,
    user_feedback INTEGER,  -- 1: 准确, -1: 不准确, 0: 未反馈
    created_at TIMESTAMP,
    FOREIGN KEY (novel_id) REFERENCES novels(id)
);
```

#### 4.3.2 ChromaDB向量库

**Collection结构**：
- Collection名称：`novel_{novel_id}`（每本小说独立Collection）
- 文档ID：`chapter_{chapter_num}_block_{block_num}`
- 元数据：
  ```json
  {
    "chapter_num": 100,
    "block_num": 5,
    "char_start": 12000,
    "char_end": 13200,
    "entities": ["角色A", "角色B"]
  }
  ```

#### 4.3.3 知识图谱（NetworkX）

**图谱文件**：`novel_{id}_graph.pkl`

**节点属性**：
```python
{
    "name": "角色A",
    "type": "character",
    "first_chapter": 5,
    "importance": 0.95,  # PageRank分数
    "attributes": {
        "性别": "男",
        "阵营": "主角方"
    }
}
```

**边属性**：
```python
{
    "relation_type": "盟友",
    "start_chapter": 10,
    "end_chapter": None,  # None表示持续到最后
    "strength": 0.8,
    "evolution": [
        {"chapter": 10, "type": "陌生"},
        {"chapter": 50, "type": "朋友"},
        {"chapter": 120, "type": "盟友"}
    ]
}
```

### 4.4 核心算法流程

#### 4.4.1 文档索引流程

**核心步骤**：

1. **文件解析**：识别章节结构，分割章节
2. **分块处理**：
   - 使用RecursiveCharacterTextSplitter（LangChain）
   - 递归按分隔符优先级分割：段落（\n\n）→ 句子（。！？）→ 中文特殊标点（……、——）→ 短句（，、；）→ 字符
   - **块大小：500-600字符**（针对中文优化），**块重叠：100-150字符**
   - 保持语义完整性，避免在句子中间截断，小块检索更精准
3. **实体提取**：使用HanLP批量提取角色、地点、组织
4. **向量化**：调用智谱Embedding-3 API，批次大小100，生成1024维向量
5. **存储向量**：保存到ChromaDB，包含文本、向量、元数据
6. **构建知识图谱**：基于实体和关系构建NetworkX图谱
7. **断点续传**：每1000块保存进度，支持失败恢复

#### 4.4.2 查询处理流程（GraphRAG + Self-RAG）

**核心步骤**：

1. **查询理解**：使用HanLP提取查询中的实体 + LLM分类查询类型
2. **双路检索（GraphRAG）**：
   - 向量检索：智谱Embedding-3向量化查询，ChromaDB检索Top-30候选
   - 图谱检索：基于实体查询NetworkX图谱，获取关系信息 + 计算章节重要性
3. **智能查询路由**：
   - 根据查询类型调整检索策略（对话/分析/事实）
   - 对话类：优先短块 + 引号内容权重
   - 分析类：合并相邻块扩展上下文
4. **增强Rerank**：
   - 语义相似度（60%）+ 实体匹配（25%）+ 时序权重（15%）
   - 块质量权重调整
   - 选取Top-10块
5. **构建Prompt**：将检索结果和图谱信息组装为上下文
6. **初次生成**：调用智谱GLM-4系列API生成答案
7. **增强Self-RAG自反思**：
   - 提取答案中的关键断言
   - 多源证据收集 + 证据质量评分
   - 时序/角色一致性检查
   - 检测矛盾并修正答案
8. **返回结果**：包含答案、引用、置信度、Token消耗

#### 4.4.3 诡计检测流程

**核心步骤**：

1. **实体和断言提取**：从答案中提取核心实体和关键断言
2. **时序一致性检查**：
   - 检索实体在早期/中期/后期的描述
   - 对比不同时期描述的一致性
   - 查询知识图谱中的演变记录
   - 区分真矛盾和叙述诡计
3. **关键信息延迟揭示检测**：
   - 查找断言首次出现的章节
   - 判断是否为后期才揭示的重要信息
4. **诡计分类**：角色演变、信息延迟揭示、身份隐藏、时间线欺骗

### 4.5 部署架构

**本地部署方案（前后端分离，无需GPU）**：

```
项目根目录/
├── backend/（Python后端）
│   ├── app/
│   │   ├── main.py（FastAPI入口）
│   │   ├── api/（API路由）
│   │   │   ├── novels.py
│   │   │   ├── chapters.py
│   │   │   ├── query.py
│   │   │   ├── graph.py
│   │   │   └── config.py
│   │   ├── services/（业务逻辑）
│   │   │   ├── novel_service.py
│   │   │   ├── rag_engine.py
│   │   │   ├── graph_builder.py
│   │   │   └── zhipu_client.py
│   │   ├── models/（数据模型）
│   │   │   └── schemas.py
│   │   └── core/（核心配置）
│   │       ├── config.py
│   │       └── dependencies.py
│   ├── data/（数据存储）
│   │   ├── chromadb/（向量库）
│   │   ├── sqlite/（元数据库）
│   │   ├── graphs/（知识图谱）
│   │   └── uploads/（上传文件）
│   ├── requirements.txt
│   └── .env（API Key等敏感信息）
│
├── frontend/（React前端）
│   ├── src/
│   │   ├── app/（Next.js App Router）
│   │   │   ├── page.tsx（首页）
│   │   │   ├── novels/（小说管理）
│   │   │   ├── reader/（在线阅读）
│   │   │   ├── query/（智能问答）
│   │   │   └── graph/（可视化）
│   │   ├── components/（React组件）
│   │   ├── lib/（工具函数）
│   │   ├── hooks/（自定义Hooks）
│   │   └── store/（Zustand状态）
│   ├── public/
│   ├── package.json
│   └── next.config.js
│
└── docker-compose.yml（可选：容器化部署）
```

**启动命令**：

**后端（FastAPI）**：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端（Next.js）**：
```bash
cd frontend
npm install
npm run dev
```

**访问方式**：
- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs
- 后端健康检查：http://localhost:8000/health

**Docker部署（可选）**：
```bash
docker-compose up -d
```

---

## 5. 用户界面设计

### 5.1 页面结构（React + Next.js）

**技术方案**：
- **路由**：Next.js 14 App Router
- **布局**：响应式布局（支持桌面/平板/移动端）
- **组件库**：Ant Design 或 shadcn/ui
- **样式**：Tailwind CSS

**主导航**（顶部导航栏 + 侧边栏）：
```tsx
<Layout>
  <Header>
    <Logo />
    <NavMenu>
      <NavItem icon="📚" href="/novels">小说管理</NavItem>
      <NavItem icon="📖" href="/reader">在线阅读</NavItem>
      <NavItem icon="💬" href="/query">智能问答</NavItem>
      <NavItem icon="📊" href="/graph">可视化分析</NavItem>
      <NavItem icon="⚙️" href="/settings">系统设置</NavItem>
    </NavMenu>
    <UserInfo />
  </Header>
  <Content>{children}</Content>
</Layout>
```

### 5.2 核心页面设计

#### 5.2.1 小说管理页面（/novels）

**React组件结构**：
```tsx
<NovelsPage>
  <PageHeader
    title="📚 小说管理"
    extra={<UploadButton onClick={openUploadModal} />}
  />
  
  <NovelList>
    {novels.map(novel => (
      <NovelCard key={novel.id}>
        <CardHeader>
          <Title>{novel.title}</Title>
          <StatusBadge status={novel.indexStatus} />
        </CardHeader>
        <CardBody>
          <NovelInfo>
            <InfoItem icon="📝">字数：{formatNumber(novel.totalChars)}</InfoItem>
            <InfoItem icon="📄">章节：{novel.totalChapters}</InfoItem>
            <InfoItem icon="👥">角色：{novel.characterCount}</InfoItem>
          </NovelInfo>
          <ProgressBar 
            percent={novel.indexProgress} 
            status={novel.indexStatus}
          />
        </CardBody>
        <CardActions>
          <Button icon="📄" onClick={() => viewInfo(novel.id)}>
            查看信息
          </Button>
          <Button icon="📖" onClick={() => readNovel(novel.id)}>
            阅读
          </Button>
          <Button icon="💬" onClick={() => queryNovel(novel.id)}>
            问答
          </Button>
          <Button icon="📊" onClick={() => viewGraph(novel.id)}>
            查看图谱
          </Button>
          <Dropdown>
            <Menu>
              <MenuItem onClick={() => exportNovel(novel.id)}>
                导出数据
              </MenuItem>
              <MenuItem danger onClick={() => deleteNovel(novel.id)}>
                删除
              </MenuItem>
            </Menu>
          </Dropdown>
        </CardActions>
      </NovelCard>
    ))}
  </NovelList>
  
  <UploadModal 
    open={uploadModalOpen}
    onClose={closeUploadModal}
    onSuccess={refreshNovelList}
  />
</NovelsPage>
```

**上传流程**（Modal组件）：
```tsx
<UploadModal>
  <Steps current={currentStep}>
    <Step title="选择文件" />
    <Step title="填写信息" />
    <Step title="处理中" />
    <Step title="完成" />
  </Steps>
  
  {currentStep === 0 && (
    <Dragger
      accept=".txt,.epub"
      maxSize={100 * 1024 * 1024} // 100MB
      onChange={handleFileSelect}
    >
      拖拽文件到此处或点击上传
    </Dragger>
  )}
  
  {currentStep === 1 && (
    <Form>
      <FormItem label="书名" required>
        <Input value={novelTitle} onChange={setNovelTitle} />
      </FormItem>
      <FormItem label="作者">
        <Input value={author} onChange={setAuthor} />
      </FormItem>
    </Form>
  )}
  
  {currentStep === 2 && (
    <ProcessingStatus>
      <Progress percent={progress} />
      <StatusText>{currentTask}</StatusText>
      <Timeline>
        <TimelineItem status="finish">✅ 文件解析完成</TimelineItem>
        <TimelineItem status="process">🔄 向量化嵌入中...</TimelineItem>
        <TimelineItem status="wait">⏳ 知识图谱构建</TimelineItem>
      </Timeline>
    </ProcessingStatus>
  )}
  
  {currentStep === 3 && (
    <Result
      status="success"
      title="索引构建完成！"
      extra={[
        <Button type="primary" onClick={goToRead}>开始阅读</Button>,
        <Button onClick={goToQuery}>智能问答</Button>
      ]}
    />
  )}
</UploadModal>
```

**API调用**：
```typescript
// 上传小说
POST /api/novels/upload
Content-Type: multipart/form-data

// 获取小说列表
GET /api/novels?page=1&pageSize=10

// 获取处理进度（轮询或WebSocket）
GET /api/novels/{id}/progress
```

#### 5.2.2 在线阅读页面（/reader）

**React组件结构**：
```tsx
<ReaderPage>
  <ReaderLayout>
    {/* 左侧：章节列表 */}
    <ChapterSidebar width={280}>
      <SidebarHeader>
        <NovelTitle>{currentNovel.title}</NovelTitle>
        <BackButton onClick={backToList}>返回列表</BackButton>
      </SidebarHeader>
      <ChapterSearch placeholder="搜索章节..." />
      <ChapterList>
        {chapters.map(chapter => (
          <ChapterItem
            key={chapter.num}
            active={chapter.num === currentChapter}
            onClick={() => loadChapter(chapter.num)}
          >
            <ChapterNumber>第{chapter.num}章</ChapterNumber>
            <ChapterTitle>{chapter.title}</ChapterTitle>
          </ChapterItem>
        ))}
      </ChapterList>
    </ChapterSidebar>

    {/* 右侧：阅读区域 */}
    <ReadingArea>
      <ReadingHeader>
        <ChapterTitle>{currentChapterData.title}</ChapterTitle>
      </ReadingHeader>

      <ChapterContent>
        {currentChapterData.content}
      </ChapterContent>

      <ChapterNavigation>
        <Button 
          size="large" 
          disabled={!hasPrevChapter}
          onClick={prevChapter}
        >
          ← 上一章
        </Button>
        <ChapterInfo>
          第 {currentChapter} / {totalChapters} 章
        </ChapterInfo>
        <Button 
          size="large"
          disabled={!hasNextChapter}
          onClick={nextChapter}
        >
          下一章 →
        </Button>
      </ChapterNavigation>
    </ReadingArea>
  </ReaderLayout>
</ReaderPage>
```

**API调用**：
```typescript
// 获取章节列表
GET /api/novels/{novelId}/chapters
Response: {
  "chapters": [
    { "num": 1, "title": "第一章 标题", "charCount": 3500 },
    ...
  ]
}

// 获取章节内容
GET /api/novels/{novelId}/chapters/{chapterNum}
Response: {
  "chapterNum": 1,
  "title": "第一章 标题",
  "content": "章节正文内容...",
  "prevChapter": null,
  "nextChapter": 2
}
```

#### 5.2.3 智能问答页面（/query）

## 流式响应设计方案

### 查询流程阶段分析

智能问答流程分为以下5个阶段：

| 阶段 | 名称 | 耗时 | 是否流式 | 前端展示方式 |
|------|------|------|---------|-------------|
| 1 | 查询理解 | 1-2秒 | ❌ | 进度状态提示 |
| 2 | 双路检索 | 3-5秒 | ❌ | 进度状态 + 检索结果数量 |
| 3 | LLM生成答案 | 10-30秒 | ✅ **流式** | 流式文本输出（主要） |
| 4 | Self-RAG验证 | 5-10秒 | ❌ | 进度状态提示 |
| 5 | 完成汇总 | <1秒 | ❌ | 切换到最终展示 |

**详细说明**：

**阶段1：查询理解**
- 输入：用户查询文本
- 处理：HanLP提取实体 + 智谱Embedding-3向量化
- 输出：查询向量 + 实体列表 + 查询类型
- 前端展示：`🔍 正在理解查询...`

**阶段2：双路检索（GraphRAG）**
- 输入：查询向量 + 实体列表
- 处理：向量检索（ChromaDB）+ 图谱检索（NetworkX）
- 输出：Top-10文本块 + 图谱关系信息
- 前端展示：
  ```
  📚 正在检索相关内容...
  ├─ 向量检索：找到20个候选文本块
  └─ 图谱检索：找到3个相关角色关系
  ```

**阶段3：LLM生成答案（流式输出）** ⭐
- 输入：检索结果 + Prompt
- 处理：调用智谱GLM-4系列API（stream=True）
- 输出：逐字/逐词流式生成答案
- 前端展示：**流式文本输出框**（详见下方UI设计）

**阶段4：Self-RAG验证**
- 输入：初步答案
- 处理：提取断言 → 重新检索验证 → 检测矛盾
- 输出：修正后答案 + 矛盾列表 + 置信度
- 前端展示：
  ```
  🔄 正在验证答案一致性...
  ├─ 提取了3个关键断言
  ├─ 验证完成，发现1处潜在矛盾
  └─ 已修正答案
  ```

**阶段5：完成汇总**
- 输入：最终答案 + 所有元数据
- 处理：计算Token消耗、成本、耗时等
- 输出：完整查询结果
- 前端展示：切换到折叠视图（答案展开，其他折叠）

---

### 流式输出UI设计

```tsx
<QueryPage>
  <PageHeader title="💬 智能问答" />
  
  <QueryContainer>
    {/* 配置区 */}
    <ConfigBar>
      <Select
        label="当前小说"
        value={selectedNovelId}
        onChange={setSelectedNovelId}
        options={novels}
      />
      <Select
        label="使用模型"
        value={selectedModel}
        onChange={setSelectedModel}
        options={[
          { value: 'GLM-4.5-Flash', label: 'GLM-4.5-Flash（免费）' },
          { value: 'GLM-4-Flash-250414', label: 'GLM-4-Flash（免费，128K）' },
          { value: 'GLM-4.5-Air', label: 'GLM-4.5-Air（推荐）' },
          { value: 'GLM-4.5-AirX', label: 'GLM-4.5-AirX（增强）' },
          { value: 'GLM-4.5-X', label: 'GLM-4.5-X（极速）' },
          { value: 'GLM-4.5', label: 'GLM-4.5（高性能）' },
          { value: 'GLM-4-Plus', label: 'GLM-4-Plus（顶级）' },
          { value: 'GLM-4.6', label: 'GLM-4.6（旗舰）' },
          { value: 'GLM-4-Long', label: 'GLM-4-Long（百万上下文）' }
        ]}
      />
    </ConfigBar>

    {/* 输入区 */}
    <QueryInput>
      <TextArea
        placeholder="请输入您的问题，例如：萧炎和药老是什么时候相遇的？"
        value={queryText}
        onChange={setQueryText}
        autoSize={{ minRows: 3, maxRows: 6 }}
      />
      <ActionButtons>
        <Button
          type="primary"
          size="large"
          icon="🔍"
          loading={isQuerying}
          onClick={handleQuery}
        >
          查询
        </Button>
        <Button icon="🧹" onClick={clearQuery}>
          清空
        </Button>
      </ActionButtons>
    </QueryInput>

    {/* 流式响应区 - 查询进行中 */}
    {isQuerying && (
      <StreamingResponseContainer>
        {/* 阶段1: 查询理解 */}
        <StageSection status={stageStatus.understand}>
          <StageHeader>
            <StageIcon>🔍</StageIcon>
            <StageTitle>查询理解</StageTitle>
            <StageStatus>{stageStatus.understand}</StageStatus>
          </StageHeader>
          {understandResult && (
            <StageContent collapsed={currentStage > 1}>
              <InfoLine>提取实体：{understandResult.entities.join('、')}</InfoLine>
              <InfoLine>查询类型：{understandResult.queryType}</InfoLine>
            </StageContent>
          )}
        </StageSection>

        {/* 阶段2: 双路检索 */}
        <StageSection status={stageStatus.retrieve}>
          <StageHeader>
            <StageIcon>📚</StageIcon>
            <StageTitle>检索相关内容</StageTitle>
            <StageStatus>{stageStatus.retrieve}</StageStatus>
          </StageHeader>
          {retrieveResult && (
            <StageContent collapsed={currentStage > 2}>
              <InfoLine>
                ├─ 向量检索：找到 {retrieveResult.vectorCount} 个候选文本块
              </InfoLine>
              <InfoLine>
                └─ 图谱检索：找到 {retrieveResult.graphCount} 个相关角色关系
              </InfoLine>
            </StageContent>
          )}
        </StageSection>

        {/* 阶段3: LLM生成答案（流式输出） ⭐ */}
        <StageSection status={stageStatus.generate} highlight>
          <StageHeader>
            <StageIcon>💭</StageIcon>
            <StageTitle>生成答案</StageTitle>
            <StageStatus>{stageStatus.generate}</StageStatus>
          </StageHeader>
          {currentStage >= 3 && (
            <StreamingTextBox
              maxHeight={400}
              autoScroll={autoScroll}
              onUserScroll={handleUserScroll}
            >
              <MarkdownRenderer content={streamingAnswer} />
              {isGenerating && <Cursor>▋</Cursor>}
            </StreamingTextBox>
          )}
        </StageSection>

        {/* 阶段4: Self-RAG验证 */}
        <StageSection status={stageStatus.verify}>
          <StageHeader>
            <StageIcon>🔄</StageIcon>
            <StageTitle>验证答案一致性</StageTitle>
            <StageStatus>{stageStatus.verify}</StageStatus>
          </StageHeader>
          {verifyResult && (
            <StageContent collapsed={currentStage > 4}>
              <InfoLine>├─ 提取了 {verifyResult.assertionCount} 个关键断言</InfoLine>
              <InfoLine>├─ 验证完成，发现 {verifyResult.contradictionCount} 处潜在矛盾</InfoLine>
              {verifyResult.modified && (
                <InfoLine>└─ 已修正答案</InfoLine>
              )}
            </StageContent>
          )}
        </StageSection>

        {/* 实时统计 */}
        <RealtimeStats>
          <StatItem>⏱️ 已耗时：{elapsedTime}秒</StatItem>
          <StatItem>🔢 Token消耗：~{estimatedTokens}</StatItem>
        </RealtimeStats>
      </StreamingResponseContainer>
    )}

    {/* 最终结果展示 - 查询完成 */}
    {!isQuerying && queryResult && (
      <FinalResultContainer>
        {/* 主要元素：答案（始终展开） */}
        <AnswerSection expanded>
          <SectionTitle>📌 答案</SectionTitle>
          <AnswerContent markdown={queryResult.answer} />
        </AnswerSection>

        {/* 次要元素：折叠显示 */}
        <CollapsibleSections>
          {/* 原文引用 - 默认折叠 */}
          <Collapse defaultActiveKey={[]}>
            <Panel 
              header={`📖 原文引用 (${queryResult.citations.length})`}
              key="citations"
            >
              {queryResult.citations.map(citation => (
                <Citation key={citation.id}>
                  <CitationHeader>
                    <ChapterTag>第{citation.chapterNum}章</ChapterTag>
                    <ViewButton onClick={() => viewChapter(citation.chapterNum)}>
                      查看完整章节
                    </ViewButton>
                  </CitationHeader>
                  <CitationContent>{citation.text}</CitationContent>
                </Citation>
              ))}
            </Panel>

            {/* 知识图谱补充 - 默认折叠 */}
            {queryResult.graphInfo && (
              <Panel header="📊 知识图谱补充" key="graph">
                <GraphInfo data={queryResult.graphInfo} />
              </Panel>
            )}

            {/* 叙述诡计检测 - 默认折叠 */}
            {queryResult.contradictions?.length > 0 && (
              <Panel 
                header={`⚠️ 叙述诡计检测 (发现${queryResult.contradictions.length}处)`}
                key="contradictions"
              >
                <Alert type="warning">
                  检测到可能的叙述诡计或前后矛盾
                </Alert>
                {queryResult.contradictions.map(c => (
                  <ContradictionCard key={c.id}>
                    <CardTitle>{c.type}</CardTitle>
                    <Comparison>
                      <Column>
                        <Label>早期描述</Label>
                        <Content>{c.early}</Content>
                      </Column>
                      <Column>
                        <Label>后期描述</Label>
                        <Content>{c.late}</Content>
                      </Column>
                    </Comparison>
                    <Analysis>{c.analysis}</Analysis>
                  </ContradictionCard>
                ))}
              </Panel>
            )}

            {/* Token消耗统计 - 默认折叠 */}
            <Panel header="📊 Token消耗统计" key="tokens">
              <TokenStatsGrid>
                <SectionTitle>总计</SectionTitle>
                <StatRow>
                  <Label>🔢 总Token消耗</Label>
                  <Value>{queryResult.tokenStats.totalTokens.toLocaleString()}</Value>
                </StatRow>
                
                <Divider />
                
                <SectionTitle>按模型分类</SectionTitle>
                {Object.entries(queryResult.tokenStats.byModel).map(([model, stats]) => (
                  <ModelSection key={model}>
                    <ModelName>{model}</ModelName>
                    {stats.inputTokens && (
                      <StatRow>
                        <SubLabel>Input Tokens</SubLabel>
                        <Value>{stats.inputTokens.toLocaleString()}</Value>
                      </StatRow>
                    )}
                    {stats.promptTokens && (
                      <StatRow>
                        <SubLabel>Prompt Tokens</SubLabel>
                        <Value>{stats.promptTokens.toLocaleString()}</Value>
                      </StatRow>
                    )}
                    {stats.completionTokens && (
                      <StatRow>
                        <SubLabel>Completion Tokens</SubLabel>
                        <Value>{stats.completionTokens.toLocaleString()}</Value>
                      </StatRow>
                    )}
                    {stats.totalTokens && (
                      <StatRow>
                        <SubLabel>Total Tokens</SubLabel>
                        <Value>{stats.totalTokens.toLocaleString()}</Value>
                      </StatRow>
                    )}
                  </ModelSection>
                ))}
              </TokenStatsGrid>
            </Panel>
            
            {/* 查询详情 - 默认折叠 */}
            <Panel header="ℹ️ 查询详情" key="details">
              <DetailGrid>
                <DetailItem>
                  <Label>💡 置信度</Label>
                  <Value>
                    <ConfidenceBadge level={queryResult.confidence}>
                      {queryResult.confidence}
                    </ConfidenceBadge>
                  </Value>
                </DetailItem>
                <DetailItem>
                  <Label>⏱️ 响应时间</Label>
                  <Value>{queryResult.responseTime}秒</Value>
                </DetailItem>
                <DetailItem>
                  <Label>🤖 使用模型</Label>
                  <Value>{queryResult.model}</Value>
                </DetailItem>
                <DetailItem>
                  <Label>📅 查询时间</Label>
                  <Value>{formatTime(queryResult.timestamp)}</Value>
                </DetailItem>
              </DetailGrid>
            </Panel>
          </Collapse>
        </CollapsibleSections>

        {/* 用户反馈 */}
        <FeedbackSection>
          <FeedbackTitle>这个答案准确吗？</FeedbackTitle>
          <FeedbackButtons>
            <Button
              icon="👍"
              size="large"
              onClick={() => submitFeedback('positive')}
            >
              准确
            </Button>
            <Button
              icon="👎"
              size="large"
              onClick={() => submitFeedback('negative')}
            >
              不准确
            </Button>
          </FeedbackButtons>
        </FeedbackSection>
      </FinalResultContainer>
    )}

    {/* 历史查询侧边栏 */}
    <QueryHistorySidebar>
      <SidebarHeader>查询历史</SidebarHeader>
      <HistoryList>
        {queryHistory.map(item => (
          <HistoryItem key={item.id} onClick={() => loadQuery(item)}>
            <QueryText>{truncate(item.query, 50)}</QueryText>
            <MetaInfo>
              <ModelTag>{item.model}</ModelTag>
              <TimeTag>{formatTime(item.createdAt)}</TimeTag>
            </MetaInfo>
          </HistoryItem>
        ))}
      </HistoryList>
    </QueryHistorySidebar>
  </QueryContainer>
</QueryPage>
```

### 流式文本输出框关键特性

**核心功能**：
- **自动滚动**：流式输出时自动跟随最新内容
- **用户干预检测**：用户手动滚动时暂停自动滚动
- **快速返回底部**：提供"查看最新内容"按钮
- **流畅动画**：平滑滚动和光标闪烁效果

**前端WebSocket连接要点**：
- 建立连接：`ws://localhost:8000/api/query/stream`
- 消息类型：`stage_start`, `stage_complete`, `stream_token`, `query_complete`, `error`
- 状态管理：实时更新各阶段状态和流式文本内容

---

### 后端FastAPI流式响应实现

**核心流程**：

1. **接收请求**：通过WebSocket接收查询参数（novelId, query, model）
2. **5阶段处理**：
   - 阶段1：查询理解（HanLP提取实体 + 智谱Embedding-3向量化）
   - 阶段2：双路检索（向量检索 + 图谱检索）
   - 阶段3：LLM生成答案（智谱API流式输出，逐token推送）
   - 阶段4：Self-RAG验证（断言提取 + 矛盾检测 + 答案修正）
   - 阶段5：完成汇总（Token统计 + 结果封装）
3. **实时推送**：每阶段开始/完成时发送状态消息，LLM生成时实时推送token
4. **异常处理**：捕获WebSocketDisconnect和Exception，返回error消息

**非流式HTTP接口**：提供`POST /api/query`用于查询历史加载等场景

---

### 数据流转流程图

```
用户输入查询
    ↓
[阶段1] 查询理解 (1-2秒)
    ├─ HanLP提取实体
    └─ 智谱Embedding-3向量化
    ↓ 发送 stage_complete + 实体列表
    
[阶段2] 双路检索 (3-5秒)
    ├─ ChromaDB向量检索
    └─ NetworkX图谱检索
    ↓ 发送 stage_complete + 检索统计
    
[阶段3] LLM生成答案 (10-30秒) ⭐
    ├─ 构建Prompt
    ├─ 调用智谱GLM-4 (stream=True)
    └─ 逐token发送 stream_token
    ↓ 发送 stage_complete
    
[阶段4] Self-RAG验证 (5-10秒)
    ├─ 提取断言
    ├─ 检测矛盾
    └─ 修正答案
    ↓ 发送 stage_complete + 验证结果
    
[阶段5] 完成汇总 (<1秒)
    ├─ 汇总各阶段Token消耗
    ├─ 按模型分类统计
    └─ 组装完整结果
    ↓ 发送 query_complete
    
前端切换到折叠视图
```

---

### 用户体验要点

1. **渐进式展示**：每个阶段完成后立即展示结果，不等待全部完成
2. **流式输出**：LLM生成阶段实时显示token，给用户即时反馈
3. **自动滚动**：生成答案时自动跟随最新内容，但允许用户干预
4. **折叠收起**：完成后自动折叠中间过程，突出最终答案
5. **实时统计**：显示已耗时、Token消耗估算等实时信息
6. **Token透明**：完整展示各阶段、各模型的Token消耗明细
7. **错误恢复**：任何阶段出错都能优雅降级，不影响已展示的内容

#### 5.2.4 可视化分析页面（/graph）

**Tab布局**（React Tabs）：
```tsx
<GraphPage>
  <Tabs>
    <TabPane tab="角色关系图" key="relations">
      <RelationGraph novelId={selectedNovelId} />
    </TabPane>
    <TabPane tab="时间线分析" key="timeline">
      <TimelineVisualization novelId={selectedNovelId} />
    </TabPane>
    <TabPane tab="统计数据" key="stats">
      <StatisticsDashboard novelId={selectedNovelId} />
    </TabPane>
  </Tabs>
</GraphPage>
```

#### 5.2.5 系统设置页面（/settings）

**设置面板**：
```tsx
<SettingsPage>
  <SettingsSections>
    <Section title="🤖 模型配置">
      <FormItem label="智谱AI API Key">
        <Input.Password 
          value={apiKey} 
          onChange={setApiKey}
          placeholder="请输入API Key"
        />
        <Button onClick={testConnection}>测试连接</Button>
      </FormItem>
      <FormItem label="默认模型">
        <Radio.Group value={defaultModel}>
          <Radio value="GLM-4.5-Air">GLM-4.5-Air（推荐）</Radio>
          <Radio value="GLM-4.5-Flash">GLM-4.5-Flash（免费）</Radio>
          <Radio value="GLM-4.6">GLM-4.6（旗舰）</Radio>
        </Radio.Group>
      </FormItem>
    </Section>

    <Section title="📊 Token统计">
      <Statistics>
        <StatCard 
          title="本月Token总消耗" 
          value={monthTokens.toLocaleString()} 
        />
        <StatCard 
          title="查询次数" 
          value={queryCount} 
        />
        <StatCard 
          title="平均单次Token" 
          value={Math.round(avgTokens).toLocaleString()} 
        />
      </Statistics>
      
      <Divider />
      
      <ModelStatsChart>
        <ChartTitle>按模型分类统计（本月）</ChartTitle>
        <BarChart data={tokenStatsByModel} />
      </ModelStatsChart>
    </Section>

    <Section title="🔧 高级设置">
      <FormItem label="检索候选块数">
        <Slider min={10} max={50} value={topK} defaultValue={30} />
        <HelpText>增加召回数量，默认30</HelpText>
      </FormItem>
      <FormItem label="文本块大小">
        <InputNumber min={400} max={800} value={chunkSize} defaultValue={550} />
        <HelpText>针对中文优化，推荐500-600字符</HelpText>
      </FormItem>
      <FormItem label="文本块重叠">
        <InputNumber min={50} max={200} value={chunkOverlap} defaultValue={125} />
        <HelpText>推荐100-150字符</HelpText>
      </FormItem>
      <FormItem label="启用Self-RAG增强验证">
        <Switch checked={enableSelfRAG} defaultChecked={true} />
      </FormItem>
      <FormItem label="启用智能查询路由">
        <Switch checked={enableSmartRouting} defaultChecked={true} />
      </FormItem>
    </Section>
  </SettingsSections>
</SettingsPage>
```

---

### 5.3 FastAPI后端接口规范

#### 5.3.1 小说管理API

```python
# 上传小说
POST /api/novels/upload
Content-Type: multipart/form-data
Body:
  - file: File (TXT/EPUB)
  - title: str
  - author: str (optional)
Response: { "novelId": int, "status": "processing" }

# 获取小说列表
GET /api/novels?page=1&pageSize=10
Response: {
  "items": [{ "id": int, "title": str, ... }],
  "total": int,
  "page": int,
  "pageSize": int
}

# 获取小说详情
GET /api/novels/{novel_id}
Response: {
  "id": int,
  "title": str,
  "author": str,
  "totalChapters": int,
  "totalChars": int,
  "indexStatus": str,
  "indexTokenStats": {  // 索引完成后才有
    "totalTokens": int,
    "embeddingTokens": int,  // Embedding-3消耗
    "chunkCount": int,
    "apiCalls": int
  },
  "uploadDate": str,
  "indexedDate": str
}

# 获取处理进度
GET /api/novels/{novel_id}/progress
Response: {
  "progress": float,  // 0-1
  "currentTask": str,  // "分块中" | "向量化中" | "构建图谱中"
  "status": str,  // "processing" | "completed" | "failed"
  "processedChunks": int,
  "totalChunks": int,
  "currentTokens": int,  // 当前已消耗tokens
  "eta": int  // 预计剩余秒数
}

# 删除小说
DELETE /api/novels/{novel_id}
Response: { "success": bool, "message": str }
```

#### 5.3.2 章节阅读API

```python
# 获取章节列表
GET /api/novels/{novel_id}/chapters
Response: {
  "chapters": [
    { "num": int, "title": str, "charCount": int },
    ...
  ],
  "total": int
}

# 获取章节内容
GET /api/novels/{novel_id}/chapters/{chapter_num}
Response: {
  "chapterNum": int,
  "title": str,
  "content": str,
  "prevChapter": int | null,
  "nextChapter": int | null,
  "totalChapters": int
}
```

#### 5.3.3 智能问答API

**流式查询接口（WebSocket，推荐）**：

```python
# WebSocket连接
WS /api/query/stream

# 客户端发送（建立连接后）
{
  "novelId": int,
  "query": str,
  "model": str  // "GLM-4.5-Flash" | "GLM-4-Flash-250414" | "GLM-4.5-Air" | "GLM-4.5-AirX" | "GLM-4.5-X" | "GLM-4.5" | "GLM-4-Plus" | "GLM-4.6" | "GLM-4-Long"
}

# 服务端发送（多个消息，按顺序）
# 1. 阶段开始
{
  "type": "stage_start",
  "stage": "understand" | "retrieve" | "generate" | "verify"
}

# 2. 阶段完成
{
  "type": "stage_complete",
  "stage": "understand" | "retrieve" | "verify",
  "data": {
    // understand阶段
    "entities": [str, ...],
    "queryType": str,
    
    // retrieve阶段
    "vectorCount": int,
    "graphCount": int,
    
    // verify阶段
    "assertionCount": int,
    "contradictionCount": int,
    "modified": bool
  }
}

# 3. 流式Token（LLM生成阶段）
{
  "type": "stream_token",
  "token": str  // 单个词/字
}

# 4. 查询完成
{
  "type": "query_complete",
  "data": {
    "queryId": int,
    "answer": str,  // 完整答案
    "citations": [
      {
        "id": int,
        "chapterNum": int,
        "text": str
      },
      ...
    ],
    "graphInfo": {
      "entities": [str, ...],
      "relations": [
        { "source": str, "target": str, "type": str },
        ...
      ]
    },
    "contradictions": [
      {
        "id": int,
        "type": str,  // "时间线矛盾" | "角色设定矛盾" | "情节不一致"
        "early": str,
        "late": str,
        "analysis": str
      },
      ...
    ],
    "tokenStats": {
      "totalTokens": int,
      "byModel": {
        "embedding-3": {
          "inputTokens": int
        },
        "glm-4": {  // 或其他使用的模型
          "promptTokens": int,
          "completionTokens": int,
          "totalTokens": int
        }
      }
    },
    "responseTime": float,
    "confidence": str,  // "高" | "中" | "低"
    "model": str,
    "timestamp": str  // ISO 8601格式
  }
}

# 5. 错误消息
{
  "type": "error",
  "error": str  // 错误描述
}
```

**非流式查询接口（HTTP，用于历史记录加载）**：

```python
# 提交查询（等待完整结果）
POST /api/query
Body: {
  "novelId": int,
  "query": str,
  "model": str
}
Response: {
  # 与WebSocket的query_complete.data结构相同
  "queryId": int,
  "answer": str,
  "citations": [...],
  "graphInfo": {...},
  "contradictions": [...],
  "tokenStats": {
    "totalTokens": int,
    "byModel": {...}
  },
  "responseTime": float,
  "confidence": str,
  "model": str,
  "timestamp": str
}

# 获取查询历史
GET /api/query/history?novelId={id}&page=1&pageSize=20
Response: {
  "items": [
    {
      "id": int,
      "novelId": int,
      "query": str,
      "answer": str,  // 简短摘要（前100字）
      "model": str,
      "totalTokens": int,
      "confidence": str,
      "createdAt": str,
      "feedback": "positive" | "negative" | null
    },
    ...
  ],
  "total": int,
  "page": int,
  "pageSize": int
}

# 获取单次查询详情
GET /api/query/{query_id}
Response: {
  # 完整查询结果（与POST /api/query响应结构相同）
  "queryId": int,
  "answer": str,
  "citations": [...],
  # ... 完整字段
}

# 提交反馈
POST /api/query/{query_id}/feedback
Body: {
  "feedback": "positive" | "negative",
  "note": str  // 可选，用户备注
}
Response: {
  "success": bool,
  "message": str
}
```

**WebSocket消息时序示例**：

```
客户端 → 服务端: {"novelId": 1, "query": "萧炎和药老是什么时候相遇的？", "model": "GLM-4.5-Air"}

服务端 → 客户端: {"type": "stage_start", "stage": "understand"}
[1-2秒后]
服务端 → 客户端: {"type": "stage_complete", "stage": "understand", "data": {"entities": ["萧炎", "药老"], "queryType": "事件"}}

服务端 → 客户端: {"type": "stage_start", "stage": "retrieve"}
[3-5秒后]
服务端 → 客户端: {"type": "stage_complete", "stage": "retrieve", "data": {"vectorCount": 8, "graphCount": 2}}

服务端 → 客户端: {"type": "stage_start", "stage": "generate"}
[立即开始流式输出]
服务端 → 客户端: {"type": "stream_token", "token": "萧"}
服务端 → 客户端: {"type": "stream_token", "token": "炎"}
服务端 → 客户端: {"type": "stream_token", "token": "和"}
服务端 → 客户端: {"type": "stream_token", "token": "药"}
...（持续10-30秒）
服务端 → 客户端: {"type": "stage_complete", "stage": "generate"}

服务端 → 客户端: {"type": "stage_start", "stage": "verify"}
[5-10秒后]
服务端 → 客户端: {"type": "stage_complete", "stage": "verify", "data": {...}}

服务端 → 客户端: {"type": "query_complete", "data": {...完整结果...}}
```

#### 5.3.4 可视化API

```python
# 获取角色关系图数据
GET /api/graph/relations/{novel_id}
Response: {
  "nodes": [
    { "id": str, "name": str, "importance": float },
    ...
  ],
  "edges": [
    {
      "source": str,
      "target": str,
      "relationType": str,
      "startChapter": int,
      "endChapter": int | null
    },
    ...
  ]
}

# 获取时间线数据
GET /api/graph/timeline/{novel_id}
Response: {
  "events": [
    {
      "chapterNum": int,
      "narrativeOrder": int,
      "actualTime": str,
      "description": str
    },
    ...
  ]
}

# 获取统计数据
GET /api/graph/statistics/{novel_id}
Response: {
  "totalChars": int,
  "totalChapters": int,
  "characterCount": int,
  "relationCount": int,
  "averageChapterLength": float
}
```

#### 5.3.5 Token统计API

```python
# 获取Token统计（按时间段）
GET /api/stats/tokens?period=month&startDate=2024-01&endDate=2024-02
Response: {
  "totalTokens": int,
  "queryCount": int,
  "indexCount": int,  // 索引操作次数
  "averageTokensPerQuery": int,
  "byModel": {
    "embedding-3": {
      "totalTokens": int,
      "apiCalls": int
    },
    "glm-4": {
      "totalTokens": int,
      "promptTokens": int,
      "completionTokens": int,
      "apiCalls": int
    },
    "glm-4-6": {
      "totalTokens": int,
      "promptTokens": int,
      "completionTokens": int,
      "apiCalls": int
    }
  },
  "byOperation": {
    "index": {
      "totalTokens": int,
      "count": int
    },
    "query": {
      "totalTokens": int,
      "count": int
    }
  },
  "dailyStats": [
    {
      "date": "2024-01-15",
      "totalTokens": int,
      "queryCount": int
    },
    ...
  ]
}

# 获取单次操作Token详情
GET /api/stats/tokens/operation/{operation_id}
Response: {
  "operationId": int,
  "operationType": "query" | "index",
  "timestamp": str,
  "tokenStats": {
    "totalTokens": int,
    "byModel": { ... }
  }
}
```

#### 5.3.6 配置管理API

```python
# 测试API连接
POST /api/config/test-connection
Body: { "apiKey": str }
Response: { "success": bool, "message": str }

# 获取配置
GET /api/config
Response: {
  "defaultModel": str,
  "topK": int,
  "chunkSize": int,
  "enableSelfRAG": bool
}

# 更新配置
PUT /api/config
Body: {
  "defaultModel": str,
  "topK": int,
  "chunkSize": int,
  "enableSelfRAG": bool
}
Response: { "success": bool }
```

#### 5.3.7 WebSocket实时通信

**说明**：系统使用两种独立的WebSocket连接，分别用于不同场景：

```python
# 1. 小说上传进度推送 WebSocket
WS /ws/progress/{novel_id}

# 用途：实时推送小说索引构建进度
# 消息类型：
Messages (Server -> Client):
  - { "type": "progress", "progress": float, "task": str }  # 进度更新
  - { "type": "complete", "novelId": int }                  # 索引完成
  - { "type": "error", "message": str }                     # 处理错误

# 2. 智能问答流式输出 WebSocket
WS /api/query/stream

# 用途：流式问答响应，实时展示查询各阶段进度和LLM生成结果
# 详细消息格式请参考 5.3.3 节"流式查询接口（WebSocket）"
# 消息类型包括：stage_start, stage_complete, stream_token, query_complete, error
```

**角色关系图示例**：

```
┌─────────────────────────────────────────┐
│  📊 角色关系图                           │
├─────────────────────────────────────────┤
│  显示章节范围：[1 ━━━━●━━━━ 1600]       │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │        [萧炎]                      │ │
│  │       /  |  \                     │ │
│  │      /   |   \                    │ │
│  │  [药老] [萧薰儿] [云韵]            │ │
│  │    师徒   恋人     复杂             │ │
│  │                                   │ │
│  │  图例：                            │ │
│  │  ━━ 盟友  ━ ━ 敌对  ••• 复杂      │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [📥 导出PNG]                           │
└─────────────────────────────────────────┘
```


---

## 6. 项目实施计划

### 6.1 开发阶段划分

#### Phase 1：基础架构（5-7周）

**目标**：搭建前后端分离架构，实现基础问答功能

**交付物**：

1. ✅ FastAPI后端框架
2. ✅ React + Next.js前端框架
3. ✅ 文件上传和解析模块
4. ✅ 向量数据库集成（ChromaDB）
5. ✅ 基础RAG流程
6. ✅ 智谱AI API集成
7. ✅ 简单事实查询功能

**详细任务**：
| 周次 | 任务 | 产出 |
|------|------|------|
| W1 | 环境搭建、技术调研 | 技术选型确认 |
| W2 | FastAPI后端脚手架 | API基础框架 |
| W3 | React前端脚手架 | 前端基础框架 |
| W4 | 文件解析和分块 | 处理模块 |
| W5 | 向量化和存储（智谱API） | 索引模块 |
| W6 | RAG流程实现 | 查询引擎 |
| W7 | 前后端联调 | MVP版本 |

**验收标准**：
- ✅ 成功上传和索引500万字小说
- ✅ 智谱API调用成功，向量化完成
- ✅ 基础事实查询准确率>75%（智谱GLM-4增强）
- ✅ WebSocket流式响应正常，LLM输出实时显示
- ✅ 查询5个阶段（理解/检索/生成/验证/汇总）状态正确展示
- ✅ 流式文本框自动滚动功能正常，用户干预滚动有效
- ✅ 查询完成后答案展开，其他信息默认折叠
- ✅ 查询响应时间<1分钟
- ✅ UI操作流畅，无重大bug

#### Phase 2：知识图谱与小说阅读（5-7周）

**目标**：实现叙述诡计处理和在线阅读功能

**交付物**：
1. ✅ 实体识别模块（HanLP）
2. ✅ 知识图谱构建（NetworkX）
3. ✅ GraphRAG集成
4. ✅ 时序关系分析
5. ✅ 矛盾检测功能
6. ✅ Self-RAG自反思机制
7. ✅ 在线阅读页面（React）
8. ✅ 章节管理API（FastAPI）

**详细任务**：
| 周次 | 任务 | 产出 |
|------|------|------|
| W8 | NER模型集成 | 实体提取 |
| W9 | 知识图谱构建 | 图谱模块 |
| W10 | GraphRAG实现 | 双路检索 |
| W11 | 在线阅读前端页面 | 阅读器组件 |
| W12 | 章节API开发 | 后端阅读接口 |
| W13 | 时序关系分析 + Self-RAG | 演变检测与自反思 |
| W14 | 矛盾检测集成 | 诡计识别 |

**验收标准**：
- ✅ 知识图谱构建成功
- ✅ 角色关系识别准确率>75%
- ✅ 矛盾检测召回率>70%（GLM-4推理增强）
- ✅ 诡计识别率>70%
- ✅ 阅读页面加载流畅，支持10万字章节
- ✅ 章节切换快速响应
- ✅ 左侧章节列表完整展示

#### Phase 3：可视化与模型管理（3-4周）

**目标**：完善用户体验，支持模型切换

**交付物**：
1. ✅ 角色关系图可视化
2. ✅ 时间线可视化
3. ✅ 智谱AI多模型支持（GLM-4系列）
4. ✅ 模型切换功能（Plus/标准/Flash）
5. ✅ Token消耗追踪与统计

**详细任务**：
| 周次 | 任务 | 产出 |
|------|------|------|
| W14 | Plotly图表开发 | 可视化模块 |
| W15 | 智谱GLM-4系列集成 | 多模型支持 |
| W16 | Token追踪与统计展示 | Token统计模块 |
| W17 | UI优化与体验提升 | 完整体验 |

**验收标准**：
- ✅ 关系图清晰展示
- ✅ 模型切换成功
- ✅ Token统计准确

#### Phase 4：优化与测试（2-3周）

**目标**：性能优化、bug修复、用户测试

**交付物**：
1. ✅ 性能优化（检索速度、内存占用）
2. ✅ 异常处理完善
3. ✅ 用户文档
4. ✅ 测试报告

**详细任务**：
| 周次 | 任务 | 产出 |
|------|------|------|
| W18 | 性能优化 | 优化版本 |
| W19 | 用户测试 | 测试反馈 |
| W20 | Bug修复 | 稳定版本 |

**验收标准**：
- ✅ 所有核心功能稳定运行
- ✅ 准确率达到目标
- ✅ 用户文档完整

### 6.2 总体时间线

```
Phase 1 (W1-W6)  : 基础架构 ████████
Phase 2 (W7-W13) : 诡计检测 ██████████████
Phase 3 (W14-W17): 可视化   ████████
Phase 4 (W18-W20): 优化     ██████
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计：14-20周（约3.5-5个月）
```

### 6.3 里程碑

| 里程碑 | 时间 | 标志 |
|--------|------|------|
| **M1: MVP发布** | 第6周 | 基础问答可用 |
| **M2: 诡计检测上线** | 第13周 | 核心功能完成 |
| **M3: 功能完整版** | 第17周 | 所有功能就绪 |
| **M4: 正式版本** | 第20周 | 稳定可用 |

---

## 7. 风险评估与应对

### 7.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| **智谱API调用失败** | 高 | 低 | ①实现重试机制 ②错误提示和降级方案 |
| **准确率不达标** | 高 | 低 | ①优化Prompt ②增加Self-RAG深度 ③切换GLM-4-Plus |
| **API成本超预期** | 中 | 中 | ①优先使用GLM-4-Flash ②实现查询缓存 ③设置成本上限 |
| **网络延迟影响体验** | 中 | 中 | ①本地缓存结果 ②异步处理 ③进度提示 |
| **诡计识别效果差** | 高 | 中 | ①丰富图谱属性 ②优化Prompt ③使用GLM-4-Plus |
| **ChromaDB性能瓶颈** | 中 | 低 | ①优化索引参数 ②考虑Milvus/Weaviate |
| **API Key泄露风险** | 高 | 低 | ①环境变量存储 ②.gitignore配置 ③定期轮换 |

### 7.2 数据风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| **小说版权问题** | 低 | 低 | 个人使用，无商业用途 |
| **文件编码错误** | 低 | 中 | 自动检测+手动指定 |
| **索引数据损坏** | 中 | 低 | 定期备份+校验机制 |
| **章节识别失败** | 中 | 中 | 多种正则规则+手动标注 |

### 7.3 项目风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| **开发周期延长** | 中 | 中 | 分阶段交付，优先核心功能 |
| **依赖库更新破坏兼容性** | 低 | 低 | 固定版本号（requirements.txt） |
| **硬件故障** | 低 | 低 | 云端备份代码和数据 |

---

## 8. 成功度量标准

### 8.1 功能度量

| 指标 | MVP目标 | 优化后目标 | 当前状态 |
|------|---------|-----------|----------|
| 事实查询准确率 | 80% | 92% | - |
| 演变分析准确率 | 77% | 87% | - |
| 诡计识别率 | 72% | 88% | - |
| 矛盾检测召回率 | 77% | 90% | - |
| 引用准确性 | 100% | 100% | - |
| 功能可用性 | 95% | 99% | - |

### 8.2 性能度量

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| 索引速度 | 取决于网络和API | - |
| 简单查询响应 | <30秒 | - |
| 复杂查询响应 | <3分钟 | - |
| 知识库加载 | <10秒 | - |
| 模型切换 | <1秒 | - |
| 内存峰值 | <8GB（无需GPU） | - |

### 8.3 Token消耗度量

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| 单次查询Token消耗 | 4000-8000 tokens | - |
| 索引构建Token消耗 | 约300-500万tokens/千万字（一次性） | - |
| 月度Token总消耗（中度使用） | 约100万-200万tokens | - |
| Embedding-3平均消耗 | 约2000 tokens/次查询 | - |
| GLM-4平均消耗 | 约6000 tokens/次查询 | - |

### 8.4 用户满意度

|| 指标 | 目标值 | 评估方式 |
||------|--------|----------|
|| 整体满意度 | 4.5/5.0 | 手动评估 |
|| 答案准确性评分 | 4.3/5.0 | 反馈统计 |
|| 操作便利性 | 4.5/5.0 | 使用体验 |
|| 响应速度满意度 | 4.0/5.0 | 用户反馈 |

---

## 9. 附录：智谱AI配置指南

### 9.1 获取API Key

1. 访问[智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并完成实名认证
3. 进入[API Keys管理页面](https://open.bigmodel.cn/usercenter/apikeys)
4. 点击"创建新的API Key"
5. 复制并妥善保存API Key（仅显示一次）

### 9.2 安装SDK

```bash
pip install zhipuai
```

### 9.3 配置方式

**方式1：环境变量（推荐）**

创建`.env`文件：
```bash
ZHIPU_API_KEY=your_api_key_here
```

在代码中使用：
```python
import os
from zhipuai import ZhipuAI

api_key = os.getenv("ZHIPU_API_KEY")
client = ZhipuAI(api_key=api_key)
```

**方式2：配置文件**

创建`config.yaml`：
```yaml
zhipu:
  api_key: "your_api_key_here"
  default_model: "glm-4"
  max_retries: 3
  timeout: 60
```

### 9.4 基本使用

**核心API调用**：

1. **文本向量化**：`client.embeddings.create(model="embedding-3", input=[texts], dimensions=1024)`
2. **对话生成**：`client.chat.completions.create(model="glm-4", messages=[...])`
3. **流式输出**：在对话生成时添加`stream=True`参数

更多详细示例请参考[智谱AI官方文档](https://docs.bigmodel.cn/)

### 9.5 成本控制建议

1. **开发阶段**：优先使用`glm-4-flash`（¥1/百万tokens）
2. **测试阶段**：混合使用`glm-4-flash`和`glm-4`
3. **生产阶段**：
   - 简单查询：`glm-4-flash`
   - 标准查询：`glm-4`
   - 复杂推理：`glm-4-plus`

4. **实现查询缓存**：相同问题直接返回缓存结果
5. **设置Token上限**：避免单次调用消耗过多
6. **监控成本**：定期查看API使用情况

### 9.6 错误处理

**重试机制**：实现指数退避重试，最多重试3次，延迟时间指数增长（2秒→4秒→8秒）

### 9.7 参考资料

- 智谱AI开放平台：https://open.bigmodel.cn/
- 官方文档：https://docs.bigmodel.cn/
- Python SDK文档：https://docs.bigmodel.cn/cn/guide/develop/python/introduction
- 定价说明：https://open.bigmodel.cn/pricing
- 社区论坛：https://github.com/zhipuai

---

**文档完成**

*本产品需求文档为网络小说智能问答系统的完整规划蓝图，涵盖功能、技术、实施等全方位内容。*

## 关键技术特性总结

### 🏗️ 架构设计
- **前后端分离**：React + Next.js前端 + FastAPI后端
- **现代化技术栈**：TypeScript + Python，支持SSR和SEO优化
- **RESTful API**：标准化接口设计，易于扩展和维护
- **WebSocket实时通信**：流式输出和进度推送

### 🤖 AI能力
- **智谱AI GLM系列**：支持GLM-4.6/4.5/4/4-Plus/4-Flash灵活切换
- **128K超长上下文**：GLM-4.6支持复杂长文本分析
- **Embedding-3向量模型**：1024维高精度文本向量化
- **无需本地GPU**：纯API调用，零硬件门槛

### 📖 核心功能
1. **小说管理**：上传、索引、多本管理
2. **在线阅读**：简洁的分章节阅读界面，快速浏览原文
3. **智能问答**：
   - 流式响应实时展示（WebSocket）
   - 5阶段透明展示（理解→检索→生成→验证→汇总）
   - RAG增强、GraphRAG、Self-RAG自反思
   - 自动滚动与用户干预滚动
   - 完成后答案主显，其他信息折叠
4. **叙述诡计识别**：时序分析、矛盾检测、关系演变
5. **可视化分析**：角色关系图、时间线、统计数据

### 💡 创新亮点
- **流式响应体验**：实时显示LLM生成过程，每个阶段透明可见，答案流式输出
- **智能滚动控制**：自动跟随最新内容，用户干预时暂停，滚动到底部恢复
- **一站式体验**：小说列表集成"查看信息"、"阅读"、"问答"、"查看图谱"等功能
- **模型自由切换**：根据查询复杂度动态选择GLM-4.6/4.5/4等模型
- **Token统计透明**：详细记录各模型Token消耗，按模型分类统计
- **前后端分离**：现代化技术栈，支持移动端适配

### 🔧 核心优化特性（最新）

本文档已整合最新优化方案，针对中文网络小说场景进行深度优化：

#### 1. 分块策略精细化
- **块大小优化**：从800-1200字符调整为**500-600字符**，更适合中文信息密度
- **重叠优化**：从200字符调整为**100-150字符**，减少冗余
- **中文特殊标点**：新增"……"、"——"等分隔符，更好处理中文对话

#### 2. 智能查询路由
- **查询类型分类**：LLM自动识别对话/分析/事实类查询
- **动态策略调整**：
  - 对话类：优先短块，增强引号内容权重
  - 分析类：合并相邻块，扩展上下文
  - 事实类：标准检索策略

#### 3. 增强检索机制
- **混合权重优化**：语义相似度60% + 实体匹配25% + **时序权重15%**（新增）
- **章节重要性动态评分**：基于新增实体、关系变化、事件密度综合计算
- **块质量权重**：优先选择接近550字符的高质量块
- **候选数增加**：从Top-20提升至Top-30，提高召回率

#### 4. GraphRAG增强
- **置信度评分**：根据图谱一致性和向量匹配度综合打分
- **时序信息增强**：图谱明确记录章节重要性，影响检索权重
- **关键转折点优先**：动态调整检索策略，优先关注重要章节

#### 5. Self-RAG验证强化
- **证据质量评分**：时效性、具体性、权威性三维度评估
- **时序一致性检查**：验证事件时间线的合理性
- **角色一致性检查**：验证角色行为逻辑的连贯性
- **多源证据收集**：为每个断言收集多个证据源

#### 6. 性能目标提升
- 事实查询准确率：MVP 80% → **优化后 92%+**
- 诡计识别率：MVP 72% → **优化后 88%+**
- 矛盾检测召回率：MVP 77% → **优化后 90%+**

*系统基于智谱AI开放平台，无需本地GPU，适合个人开发者快速上手。*
