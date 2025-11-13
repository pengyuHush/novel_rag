# 网络小说智能问答系统 - Backend Dockerfile
# 多阶段构建，优化镜像大小

# === 构建阶段 ===
FROM python:3.12-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# 配置Poetry（在项目中创建虚拟环境）
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安装依赖（分离缓存层以优化构建速度）
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-root --only main

# === 运行阶段 ===
FROM python:3.12-slim AS runtime

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录并设置权限
RUN mkdir -p data/chromadb data/sqlite data/graphs data/uploads data/backups logs \
    && chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 设置Python路径
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令（生产模式）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
