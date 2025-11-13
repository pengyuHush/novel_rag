# 快速开始指南

**Created:** 2025-11-13  
**Version:** 1.0.0

## 目录

1. [系统要求](#系统要求)
2. [环境准备](#环境准备)
3. [后端设置](#后端设置)
4. [前端设置](#前端设置)
5. [首次运行](#首次运行)
6. [基本使用](#基本使用)
7. [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|----------|
| **CPU** | 4核 | 8核+ |
| **内存** | 8GB | 16GB+ |
| **存储** | 50GB可用空间 | 100GB+ SSD |
| **显卡** | ❌ 不需要GPU | ❌ 不需要GPU |
| **网络** | 稳定互联网连接 | 100Mbps+ |

**说明：** 本系统使用智谱AI API，无需本地GPU！

### 软件要求

| 软件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 后端运行环境 |
| **Node.js** | 18+ | 前端构建和运行 |
| **Git** | 2.0+ | 代码管理 |
| **智谱AI账号** | - | API服务（必需） |

---

## 环境准备

### 1. 安装Python 3.10+

#### Windows

访问 [Python官网](https://www.python.org/downloads/) 下载安装包。

**验证安装：**
```bash
python --version
# 输出: Python 3.10.x 或更高
```

#### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# macOS (使用Homebrew)
brew install python@3.10
```

### 2. 安装Node.js 18+

访问 [Node.js官网](https://nodejs.org/) 下载LTS版本。

**验证安装：**
```bash
node --version  # v18.x.x或更高
npm --version   # 9.x.x或更高
```

### 3. 获取智谱AI API Key

#### 步骤：

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并完成实名认证
3. 进入 [API Keys管理](https://open.bigmodel.cn/usercenter/apikeys)
4. 点击"创建新的API Key"
5. **复制并妥善保存API Key**（仅显示一次！）
6. 充值账户余额（建议¥50起，用于测试）

**定价参考：**
- Embedding-3: ¥1/百万tokens
- GLM-4-Flash: ¥1/百万tokens
- GLM-4: ¥50/百万tokens

---

## 后端设置

### 1. 克隆仓库

```bash
git clone https://github.com/your-repo/novel-qa-system.git
cd novel-qa-system
```

### 2. 创建虚拟环境

```bash
cd backend
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt内容：**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
websockets==12.0
langchain==0.1.0
chromadb==0.4.18
zhipuai==2.0.1
hanlp==2.1.0b54
networkx==3.2
plotly==5.18.0
sqlalchemy==2.0.23
ebooklib==0.18
chardet==5.2.0
python-dotenv==1.0.0
```

### 4. 配置环境变量

创建 `backend/.env` 文件：

```bash
# 智谱AI配置
ZHIPU_API_KEY=your_api_key_here

# 数据库配置
SQLITE_DB_PATH=./data/sqlite/metadata.db
CHROMADB_PATH=./data/chromadb
GRAPHS_PATH=./data/graphs
UPLOADS_PATH=./data/uploads

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS配置（前端地址）
CORS_ORIGINS=http://localhost:3000
```

**重要：** 将 `your_api_key_here` 替换为你的真实API Key！

### 5. 创建数据目录

```bash
mkdir -p data/sqlite data/chromadb data/graphs data/uploads
```

### 6. 初始化数据库

```bash
python -m app.db.init_db
```

### 7. 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功标志：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**测试后端：**
访问 http://localhost:8000/docs 查看API文档（Swagger UI）。

---

## 前端设置

### 1. 进入前端目录

```bash
cd frontend  # 从项目根目录
```

### 2. 安装依赖

```bash
npm install
```

**如果遇到网络问题，使用国内镜像：**
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 3. 配置环境变量（可选）

**注意：** 环境变量配置是可选的，代码中已包含默认值 `http://localhost:8000`。

如需自定义后端地址，可创建 `frontend/.env.local` 文件：

```bash
# 后端API地址（可选，默认: http://localhost:8000）
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket地址（可选，默认: ws://localhost:8000）
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 4. 启动前端服务

```bash
npm run dev
```

**成功标志：**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.5s
```

**访问前端：**
打开浏览器访问 http://localhost:3000

---

## 首次运行

### 1. 访问主页

打开浏览器访问 http://localhost:3000，你将看到：

```
┌─────────────────────────────────────────┐
│  📚 网络小说智能问答系统                  │
├─────────────────────────────────────────┤
│                                         │
│  [📤 上传小说]                           │
│                                         │
│  尚无小说，请先上传小说文件。             │
│                                         │
└─────────────────────────────────────────┘
```

### 2. 上传测试小说

#### 准备测试文件

**方式1：下载开源小说**
- 从[起点中文网](https://www.qidian.com/)等网站下载TXT格式小说（需合法授权）
- 建议使用短篇（10万字以内）进行首次测试

**方式2：创建测试文件**

创建 `test_novel.txt`：

```txt
第一章 测试

萧炎，斗气大陆加玛帝国乌坦城的少年。

三年前，他还是众人眼中的天才，家族的骄傲。

三年后，天赋消失，成为废物。

第二章 戒指

一枚古朴的戒指，是萧炎母亲的遗物。

三年来，萧炎一直佩戴着它。

今夜，戒指突然发出微弱的光芒。

第三章 药老

"小家伙，终于醒了。"

一个苍老的声音从戒指中传出。

萧炎震惊地发现，戒指中居然住着一位灵魂体。

老者自称药尘，曾是斗气大陆的炼药宗师。

（为测试方便，这里仅3章，实际小说可达数千章）
```

#### 上传步骤

1. 点击"上传小说"按钮
2. 选择文件：`test_novel.txt`
3. 填写信息：
   - 书名：`测试小说`
   - 作者：`测试作者`
4. 点击"开始上传"
5. 等待索引构建（显示进度条）

**预计时间：**
- 10万字小说：约5-10分钟
- 100万字小说：约30-60分钟
- 1000万字小说：约3-5小时

**索引过程：**
```
[████████░░░░░░░░░░░] 40%
当前任务：向量化嵌入中...
已处理：120/300 chunks
预计剩余：5分钟
```

### 3. 首次查询

索引完成后：

1. 点击"智能问答"按钮
2. 选择模型：`GLM-4`（标准，推荐）
3. 输入问题：`萧炎的天赋为什么消失了？`
4. 点击"查询"

**流式响应过程：**
```
🔍 查询理解
  提取实体：萧炎
  查询类型：事实查询

📚 检索相关内容
  ├─ 向量检索：找到8个候选文本块
  └─ 图谱检索：找到2个相关角色关系

💭 生成答案
  根据第一章和第二章的描述，萧炎的天赋消失...
  （实时逐字显示）

🔄 验证答案一致性
  ├─ 提取了2个关键断言
  └─ 验证完成，无矛盾

✅ 查询完成
```

### 4. 查看可视化

1. 返回小说列表
2. 点击"查看图谱"
3. 查看角色关系图：

```
     [萧炎]
      / \
     /   \
 [药老] [萧薰儿]
  师徒    恋人
```

---

## 基本使用

### 场景1：阅读小说

1. 小说列表 → 点击"阅读"
2. 左侧：章节列表
3. 右侧：章节内容
4. 底部：上一章/下一章按钮

### 场景2：角色查询

**查询示例：**
```
Q: 萧炎和药老是什么关系？
A: 萧炎和药老是师徒关系。药老（药尘）是一位灵魂体...

原文引用：
  第三章："老者自称药尘，曾是斗气大陆的炼药宗师。"
```

### 场景3：时间线梳理

**查询示例：**
```
Q: 萧炎的天赋什么时候消失的？
A: 根据第一章的描述，萧炎的天赋在"三年前"消失...
```

### 场景4：矛盾检测

**查询示例：**
```
Q: 药老的实力前后有矛盾吗？
A: 检测到以下矛盾：
  早期描述（第3章）："曾是炼药宗师"
  后期描述（第50章）："斗圣强者"
  分析：这可能是作者刻意隐藏药老真实实力的叙述诡计。
```

---

## 常见问题

### Q1: 安装依赖时报错 "No matching distribution found"

**原因：** Python版本过低

**解决：**
```bash
python --version  # 检查版本
# 如果<3.10，请升级Python
```

### Q2: 后端启动失败 "Address already in use"

**原因：** 8000端口被占用

**解决：**
```bash
# 查看占用进程
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# 杀死进程或更换端口
uvicorn app.main:app --reload --port 8001
```

### Q3: 智谱API调用失败 "Invalid API Key"

**原因：** API Key配置错误

**解决：**
1. 检查 `backend/.env` 文件
2. 确认API Key正确（无多余空格）
3. 访问 [智谱AI控制台](https://open.bigmodel.cn/usercenter/apikeys) 重新生成

### Q4: 索引构建卡住不动

**原因：** 网络问题或API限流

**解决：**
1. 检查网络连接
2. 查看后端日志：`backend/logs/app.log`
3. 智谱API有QPS限制（免费版：10次/秒），大文件需耐心等待

### Q5: 前端页面空白

**原因：** 后端未启动或CORS配置错误

**解决：**
1. 确认后端已启动：访问 http://localhost:8000/health
2. 检查 `backend/.env` 中 `CORS_ORIGINS` 包含前端地址
3. 清除浏览器缓存

### Q6: Token消耗太快

**解决：**
1. 优先使用 `GLM-4-Flash` 模型（简单查询）
2. 启用查询缓存（相同问题直接返回）
3. 减少检索块数（在设置中调整 `topK`）

### Q7: 查询结果不准确

**优化建议：**
1. 切换到 `GLM-4-Plus` 模型（更强推理）
2. 启用 `Self-RAG` 增强验证
3. 调整分块大小（设置 → 高级设置）
4. 检查小说章节识别是否正确

---

## 下一步

### 学习文档

- [API文档](./contracts/README.md) - 完整API规范
- [数据模型](./data-model.md) - 数据库设计
- [研究文档](./research.md) - 技术选型和最佳实践
- [实现计划](./plan.md) - 开发路线图

### 高级配置

- 调整分块大小和重叠
- 配置多模型自动路由
- 启用Docker部署
- 配置定时备份

### 开发指南

- 后端开发：`backend/README.md`
- 前端开发：`frontend/README.md`
- 贡献指南：`CONTRIBUTING.md`

---

## 技术支持

- **文档：** https://github.com/your-repo/novel-qa-system/wiki
- **Issues：** https://github.com/your-repo/novel-qa-system/issues
- **智谱AI文档：** https://docs.bigmodel.cn/

---

**祝使用愉快！** 🎉

如果遇到问题，请先查看 [常见问题](#常见问题) 或提交Issue。

---

**维护者：** Development Team  
**最后更新：** 2025-11-13

