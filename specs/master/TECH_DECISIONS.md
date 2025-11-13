# 技术决策记录

**项目:** 网络小说智能问答系统  
**最后更新:** 2025-11-13

---

## 决策记录

### TD-001: UI组件库选择

**决策日期:** 2025-11-13  
**决策者:** 开发团队  
**状态:** ✅ 已确认

#### 背景

项目需要选择一个成熟的React UI组件库，用于构建前端界面。初期方案考虑了Ant Design和shadcn/ui两个选项。

#### 考虑因素

| 因素 | Ant Design 5.x | shadcn/ui |
|-----|---------------|-----------|
| **成熟度** | ⭐⭐⭐⭐⭐ 企业级，久经考验 | ⭐⭐⭐ 较新，社区成长中 |
| **组件丰富度** | ⭐⭐⭐⭐⭐ 60+组件，覆盖全面 | ⭐⭐⭐⭐ 基础组件齐全 |
| **中文文档** | ⭐⭐⭐⭐⭐ 完善的中文文档 | ⭐⭐⭐ 主要英文文档 |
| **国际化** | ⭐⭐⭐⭐⭐ 内置i18n支持 | ⭐⭐⭐ 需手动配置 |
| **TypeScript** | ⭐⭐⭐⭐⭐ 原生TS支持 | ⭐⭐⭐⭐⭐ 原生TS支持 |
| **定制能力** | ⭐⭐⭐⭐ 主题配置系统 | ⭐⭐⭐⭐⭐ 完全控制样式 |
| **生态系统** | ⭐⭐⭐⭐⭐ Pro Components等扩展 | ⭐⭐⭐ 社区插件 |
| **学习曲线** | ⭐⭐⭐⭐ 中等，文档丰富 | ⭐⭐⭐⭐ 中等，需了解Radix |
| **打包体积** | ⭐⭐⭐ 较大（支持按需加载） | ⭐⭐⭐⭐⭐ 极小（复制粘贴模式） |
| **适配复杂场景** | ⭐⭐⭐⭐⭐ Table/Form等复杂组件 | ⭐⭐⭐ 需自行扩展 |

#### 决策

**选择: Ant Design 5.x**

#### 理由

1. **项目特点匹配:**
   - 本项目是数据密集型应用，需要复杂的Table、Form、Modal等组件
   - Ant Design提供开箱即用的高级组件（如ProTable、ProForm）

2. **开发效率:**
   - 完善的中文文档，降低学习成本
   - 丰富的示例代码，加速开发
   - 企业级最佳实践内置

3. **技术栈一致性:**
   - 与智谱AI、ChromaDB等后端技术栈的成熟度匹配
   - 适合快速迭代的MVP开发

4. **长期维护:**
   - 蚂蚁集团持续维护，版本稳定
   - 大量企业应用案例，问题解决方案丰富

5. **项目需求:**
   - 需要流式文本框、进度条、图表等复杂交互
   - Ant Design的配置型组件更适合快速实现

#### 实施计划

**Phase 1（项目初始化）：**
- T003: 初始化Next.js项目时安装 `antd@5.x`
- T006: 配置ESLint规则，支持Ant Design组件
- T027-T032: 使用Ant Design组件创建基础布局

**配置要求：**
```json
// package.json
{
  "dependencies": {
    "antd": "^5.12.0",
    "react": "^18.2.0",
    "next": "^14.0.0"
  }
}
```

**主题配置：**
```typescript
// theme/themeConfig.ts
import type { ThemeConfig } from 'antd';

const theme: ThemeConfig = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  },
};
```

#### 替代方案

**shadcn/ui（未选择）:**
- 优势：完全控制样式、极小打包体积、现代化设计
- 劣势：需要更多手动配置、复杂组件需自行实现、中文文档有限
- 适用场景：更适合设计驱动、定制化需求强的项目

#### 影响范围

**受影响的文档：**
- ✅ `plan.md` - 技术栈描述已更新
- ✅ `tasks.md` - 前端任务描述已更新
- ✅ `PRD` - UI组件库说明（如有引用）

**受影响的任务：**
- T027-T032: 前端基础组件（使用Ant Design组件）
- T047-T051: 小说管理UI（使用Ant Design表单、卡片）
- T068-T075: 智能问答UI（使用Ant Design布局、输入框）
- T079-T084: 阅读器UI（使用Ant Design侧边栏、导航）
- T125-T130: 可视化UI（使用Ant Design Tabs）

#### 后续决策

如在实施过程中发现重大问题，可考虑：
1. 评估是否需要切换到shadcn/ui
2. 混合使用（Ant Design主体 + shadcn/ui特定组件）
3. 自定义组件库

#### 参考资料

- [Ant Design 官网](https://ant.design/)
- [Ant Design 5.x 文档](https://ant.design/docs/react/introduce-cn)
- [Ant Design Pro Components](https://procomponents.ant.design/)
- [shadcn/ui 官网](https://ui.shadcn.com/)

---

## 未来决策待定

### TD-002: 状态管理库（待Phase 2确认）

**候选方案:**
- Zustand (计划使用)
- Redux Toolkit
- Jotai

**决策时机:** Phase 2开始前

---

### TD-003: 图表库细节（待Phase 7确认）

**候选方案:**
- Plotly.js (计划使用)
- ECharts
- D3.js

**决策时机:** Phase 7开始前

---

**文档维护:** 每次重大技术决策后更新此文件

