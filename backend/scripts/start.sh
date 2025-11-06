#!/bin/bash
# 后端启动脚本

set -e

echo "======================================"
echo "小说 RAG 分析系统 - 后端启动"
echo "======================================"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，从 env.example 复制..."
    cp env.example .env
    echo "✅ 已创建 .env 文件，请编辑并填入智谱 API Key"
    echo ""
    read -p "按 Enter 继续..."
fi

# 检查 Docker 服务
echo "检查 Docker 服务..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 启动依赖服务
echo "启动 Redis 和 Qdrant..."
docker-compose up -d

# 等待服务就绪
echo "等待服务启动..."
sleep 3

# 验证环境
echo ""
echo "验证环境配置..."
poetry run python verify_env.py

# 启动 FastAPI
echo ""
echo "启动 FastAPI 服务 (http://localhost:8000)..."
echo "API 文档: http://localhost:8000/docs"
echo ""
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

