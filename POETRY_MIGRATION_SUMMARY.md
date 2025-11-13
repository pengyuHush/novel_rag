# Poetry迁移总结

**迁移日期**: 2025-11-13  
**原因**: Python 3.14太新，部分库（如HanLP）不兼容，改用Python 3.12 + Poetry管理

---

## ✅ 已完成的变更

### 1. 删除旧的虚拟环境
- ✅ 删除 `backend/venv/` 目录
- ✅ 清理旧的pip依赖管理

### 2. 创建Poetry配置
- ✅ 创建 `backend/pyproject.toml` - Poetry配置文件
- ✅ 指定Python版本: `>=3.12,<3.14`
- ✅ 配置所有项目依赖（生产+开发）
- ✅ 配置代码质量工具（Black, Flake8, MyPy）
- ✅ 配置测试工具（Pytest, Coverage）

### 3. 更新Docker配置
- ✅ 更新 `backend/Dockerfile` - 使用Python 3.12 + Poetry
- ✅ 配置Poetry环境变量
- ✅ 优化镜像构建流程

### 4. 更新文档
- ✅ 更新 `README.md` - 主文档
- ✅ 更新 `backend/README.md` - 后端文档
- ✅ 更新 `PHASE1_COMPLETION_REPORT.md` - 完成报告
- ✅ 创建 `backend/SETUP_INSTRUCTIONS.md` - 详细设置指南
- ✅ 创建 `backend/poetry_setup_guide.md` - Poetry使用指南
- ✅ 创建 `backend/PYTHON_VERSION_NOTE.md` - Python版本说明

### 5. 更新.gitignore
- ✅ 添加Poetry相关忽略规则（`poetry.lock`, `.poetry/`）

---

## 📋 用户需要执行的操作

### 前置要求检查

1. **Python 3.12**: 确认已安装
   ```bash
   py -3.12 --version    # Windows
   python3.12 --version  # macOS/Linux
   ```

2. **Poetry**: 确认已安装（已验证：Poetry 2.2.1 ✅）
   ```bash
   poetry --version
   ```

### 快速设置步骤

```bash
# 1. 进入后端目录
cd backend

# 2. 配置Poetry使用Python 3.12（重要！）
# 方式A: 使用py启动器（Windows推荐）
poetry env use py -3.12

# 方式B: 指定Python 3.12完整路径（如果方式A不工作）
# 先找到Python 3.12路径：
# py -3.12 -c "import sys; print(sys.executable)"
# 然后使用该路径：
# poetry env use C:\Python312\python.exe

# 3. 安装依赖
poetry install

# 4. 验证Python版本（应显示3.12.x）
poetry env info

# 5. 配置环境变量
cp .env.example .env
# 编辑.env，填写智谱AI API Key

# 6. 启动服务
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者先激活环境
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 详细文档索引

| 文档 | 用途 |
|------|------|
| `backend/SETUP_INSTRUCTIONS.md` | **必读** - 详细设置步骤和故障排除 |
| `backend/poetry_setup_guide.md` | Poetry安装和使用指南 |
| `backend/PYTHON_VERSION_NOTE.md` | 为什么使用Python 3.12的说明 |
| `backend/README.md` | 后端开发文档（已更新） |
| `README.md` | 项目总文档（已更新） |

---

## ⚠️ 重要提示

### Python版本要求
- ✅ **支持**: Python 3.12.x（推荐）
- ✅ **支持**: Python 3.13.x（如需要）
- ❌ **不支持**: Python 3.14+（HanLP等库未适配）
- ❌ **不支持**: Python 3.11及以下（太旧）

### 常见问题

**Q1: 我只有Python 3.14，怎么办？**

A: 需要安装Python 3.12：
- 下载: https://www.python.org/downloads/release/python-3120/
- Python 3.12和3.14可以共存
- 使用`py -3.12`或`poetry env use`指定版本

**Q2: Poetry env use失败？**

A: 请尝试以下方法：
```bash
# 方法1: 使用py启动器
poetry env use py -3.12

# 方法2: 使用完整路径
py -3.12 -c "import sys; print(sys.executable)"
# 复制输出的路径，然后：
poetry env use <上面输出的路径>

# 方法3: 如果安装在标准位置
poetry env use C:\Python312\python.exe
```

**Q3: 依赖安装失败？**

A: 清除缓存后重试：
```bash
poetry cache clear pypi --all
poetry install --no-cache
```

---

## 🎯 验证清单

安装完成后，请验证以下内容：

- [ ] Poetry版本 ≥ 1.7.0
- [ ] Python版本 = 3.12.x
- [ ] 依赖安装成功（`poetry show`）
- [ ] 服务可启动（`poetry run uvicorn app.main:app`）
- [ ] 健康检查通过（http://localhost:8000/health）
- [ ] API文档可访问（http://localhost:8000/docs）

---

## 🔄 与旧方式的对比

| 项目 | 旧方式 (venv + pip) | 新方式 (Poetry) |
|------|---------------------|-----------------|
| 虚拟环境管理 | `python -m venv venv` | `poetry install` |
| 激活环境 | `venv\Scripts\activate` | `poetry shell` |
| 安装依赖 | `pip install -r requirements.txt` | `poetry install` |
| 添加依赖 | 手动编辑requirements.txt | `poetry add <pkg>` |
| 运行命令 | `python script.py` | `poetry run python script.py` |
| 依赖锁定 | requirements.txt | pyproject.toml + poetry.lock |
| Python版本管理 | 手动切换 | `poetry env use python3.12` |

---

## 💡 Poetry优势

1. **依赖管理更智能**: 自动解析依赖冲突
2. **版本锁定**: poetry.lock确保团队环境一致
3. **开发/生产分离**: `--no-dev`轻松切换
4. **虚拟环境自动化**: 无需手动创建和激活
5. **Python版本控制**: 明确指定兼容版本
6. **项目打包**: 支持发布到PyPI

---

## 📞 需要帮助？

如遇到问题，请查看：
1. `backend/SETUP_INSTRUCTIONS.md` - 详细故障排除
2. `backend/poetry_setup_guide.md` - Poetry使用指南
3. Poetry官方文档: https://python-poetry.org/docs/

---

**迁移完成！** 🎉

现在可以按照上述步骤进行测试。如有任何问题，请参考详细文档或询问。

