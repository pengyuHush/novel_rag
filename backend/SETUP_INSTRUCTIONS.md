# 后端设置说明 - Poetry + Python 3.12

## ⚠️ 重要提示

本项目要求使用 **Python 3.12**，因为Python 3.14太新，部分依赖库（如HanLP）尚未完全适配。

当前系统默认Python版本是 **3.14.0**，需要配置Poetry使用Python 3.12。

---

## 设置步骤

### 步骤1: 确认Python 3.12已安装

请确认您的系统已安装Python 3.12。如未安装，请先从官网下载安装：
https://www.python.org/downloads/

### 步骤2: 找到Python 3.12的路径

**Windows PowerShell**:
```powershell
# 方式1: 使用py启动器
py -3.12 --version
py -3.12 -c "import sys; print(sys.executable)"

# 方式2: 直接查找
Get-Command python3.12 -ErrorAction SilentlyContinue
Get-Command python312 -ErrorAction SilentlyContinue

# 方式3: 常见安装位置
# C:\Python312\python.exe
# C:\Users\<用户名>\AppData\Local\Programs\Python\Python312\python.exe
```

**macOS/Linux**:
```bash
which python3.12
# 或
whereis python3.12
```

### 步骤3: 配置Poetry使用Python 3.12

```bash
# 进入backend目录
cd backend

# 方式1: 使用py启动器（Windows推荐）
poetry env use py -3.12

# 方式2: 指定完整路径（根据步骤2找到的路径）
poetry env use C:\Python312\python.exe
# 或
poetry env use C:\Users\<你的用户名>\AppData\Local\Programs\Python\Python312\python.exe

# 方式3: macOS/Linux
poetry env use python3.12
```

### 步骤4: 安装依赖

```bash
# 安装所有依赖（包括开发依赖）
poetry install

# 查看虚拟环境信息（确认Python版本）
poetry env info
```

应该看到类似输出：
```
Python:         3.12.x
Implementation: CPython
...
```

### 步骤5: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填写智谱AI API Key
# Windows: notepad .env
# macOS/Linux: nano .env
```

### 步骤6: 启动服务

```bash
# 方式1: 使用poetry run
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2: 先激活虚拟环境
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤7: 验证

访问以下地址验证服务正常运行：
- http://localhost:8000 - API根路径
- http://localhost:8000/health - 健康检查
- http://localhost:8000/docs - Swagger UI文档

---

## 故障排除

### 问题1: 找不到Python 3.12

**解决方案**: 
1. 下载安装Python 3.12: https://www.python.org/downloads/release/python-3120/
2. 安装时勾选"Add Python to PATH"
3. 重启终端后重试

### 问题2: Poetry环境使用了错误的Python版本

```bash
# 删除现有虚拟环境
poetry env remove python

# 或删除所有虚拟环境
poetry env remove --all

# 重新指定Python 3.12
poetry env use C:\Python312\python.exe  # 替换为实际路径

# 重新安装依赖
poetry install
```

### 问题3: 依赖安装失败

```bash
# 清除Poetry缓存
poetry cache clear pypi --all

# 更新lock文件
poetry lock --no-update

# 重新安装
poetry install --no-cache
```

### 问题4: 找不到poetry命令

**Windows**:
Poetry通常安装在 `%APPDATA%\Python\Scripts\poetry.exe`
需要添加到系统PATH环境变量。

**macOS/Linux**:
```bash
# 添加到~/.bashrc或~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # 或 source ~/.zshrc
```

---

## 快速命令参考

```bash
# Poetry环境管理
poetry env use python3.12    # 指定Python版本
poetry env info              # 查看环境信息
poetry env list              # 列出所有虚拟环境
poetry env remove python     # 删除虚拟环境

# 依赖管理
poetry install               # 安装依赖
poetry add <package>         # 添加依赖
poetry add --group dev <pkg> # 添加开发依赖
poetry update                # 更新依赖
poetry show                  # 查看已安装包
poetry show --tree           # 查看依赖树

# 运行项目
poetry shell                 # 激活虚拟环境
poetry run <command>         # 在虚拟环境中运行命令
exit                         # 退出虚拟环境
```

---

## 推荐工作流

```bash
# 1. 一次性设置
cd backend
poetry env use py -3.12      # 或指定完整路径
poetry install
cp .env.example .env
# 编辑.env填写API Key

# 2. 日常开发
poetry shell                 # 激活环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 添加新依赖
poetry add <package-name>

# 4. 运行测试
poetry run pytest

# 5. 代码格式化
poetry run black app/
```

---

如有问题，请参考：
- Poetry官方文档: https://python-poetry.org/docs/
- Python 3.12发行说明: https://docs.python.org/3.12/whatsnew/3.12.html

