# Poetry 设置指南

本项目使用Poetry管理Python依赖和虚拟环境。

## 安装Poetry

### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

或者使用pip安装：

```bash
pip install poetry
```

### macOS/Linux

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## 配置Poetry

```bash
# 配置Poetry在项目目录内创建虚拟环境
poetry config virtualenvs.in-project true

# 查看配置
poetry config --list
```

## 指定Python版本

如果系统有多个Python版本，可以指定使用Python 3.12：

```bash
# Windows
poetry env use C:\Python312\python.exe

# macOS/Linux
poetry env use python3.12

# 或者使用which/where找到的Python路径
poetry env use /usr/bin/python3.12
```

## 初始化项目

```bash
# 进入backend目录
cd backend

# 安装依赖
poetry install

# 查看虚拟环境信息
poetry env info
```

## 常用命令

```bash
# 激活虚拟环境
poetry shell

# 安装新包
poetry add <package-name>

# 安装开发依赖
poetry add --group dev <package-name>

# 更新依赖
poetry update

# 查看依赖树
poetry show --tree

# 运行命令（不激活虚拟环境）
poetry run python script.py
poetry run uvicorn app.main:app --reload

# 导出requirements.txt（如需要）
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## 故障排除

### Poetry未找到命令

如果安装后提示找不到poetry命令，需要添加到PATH：

**Windows**: 添加 `%APPDATA%\Python\Scripts` 到系统PATH

**macOS/Linux**: 添加 `$HOME/.local/bin` 到PATH

```bash
# macOS/Linux - 添加到 ~/.bashrc 或 ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Python版本不匹配

```bash
# 查看当前使用的Python版本
poetry env info

# 删除现有虚拟环境
poetry env remove python

# 指定正确的Python版本
poetry env use python3.12

# 重新安装依赖
poetry install
```

### 依赖冲突

```bash
# 清除缓存
poetry cache clear pypi --all

# 更新poetry.lock
poetry lock --no-update

# 重新安装
poetry install
```

## 验证安装

```bash
# 1. 激活虚拟环境
poetry shell

# 2. 查看Python版本
python --version
# 应该显示: Python 3.12.x

# 3. 查看已安装的包
poetry show

# 4. 测试导入关键库
python -c "import fastapi; print(fastapi.__version__)"
```

## 项目启动

```bash
# 方式1: 使用poetry run
poetry run uvicorn app.main:app --reload

# 方式2: 先激活虚拟环境
poetry shell
uvicorn app.main:app --reload
```

完成以上步骤后，访问 http://localhost:8000/docs 查看API文档。

