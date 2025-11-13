# 网络小说智能问答系统 - Backend Dockerfile
# Python 3.12 + Poetry

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖和Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# 配置Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安装依赖（不包含dev依赖）
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

# 复制应用代码
COPY . .

# 安装项目本身
RUN poetry install --no-dev

# 创建必要的目录
RUN mkdir -p data/chromadb data/sqlite data/graphs data/uploads data/backups logs

# 暴露端口
EXPOSE 8000

# 启动命令（使用Poetry运行）
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
