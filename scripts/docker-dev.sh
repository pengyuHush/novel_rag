#!/bin/bash
# 开发环境Docker管理脚本

set -e

PROJECT_NAME="novel-rag"
COMPOSE_FILE="docker-compose.yml"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
function show_help() {
    cat << EOF
网络小说智能问答系统 - 开发环境管理脚本

用法: $0 <command>

命令:
    start       启动所有服务
    stop        停止所有服务
    restart     重启所有服务
    rebuild     重新构建并启动
    logs        查看所有日志
    logs-be     查看后端日志
    logs-fe     查看前端日志
    status      查看服务状态
    clean       清理所有容器和卷
    shell-be    进入后端容器shell
    shell-fe    进入前端容器shell
    test-be     运行后端测试
    help        显示此帮助信息

示例:
    $0 start        # 启动服务
    $0 logs-be      # 查看后端日志
    $0 rebuild      # 重新构建并启动
EOF
}

# 启动服务
function start_services() {
    print_info "启动开发环境..."
    docker-compose -f $COMPOSE_FILE up -d
    print_info "服务已启动！"
    print_info "前端: http://localhost:3000"
    print_info "后端API: http://localhost:8000/docs"
}

# 停止服务
function stop_services() {
    print_info "停止服务..."
    docker-compose -f $COMPOSE_FILE down
    print_info "服务已停止"
}

# 重启服务
function restart_services() {
    print_info "重启服务..."
    docker-compose -f $COMPOSE_FILE restart
    print_info "服务已重启"
}

# 重新构建
function rebuild_services() {
    print_info "重新构建服务..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE up -d
    print_info "重新构建完成！"
}

# 查看日志
function view_logs() {
    docker-compose -f $COMPOSE_FILE logs -f --tail=100
}

function view_backend_logs() {
    docker-compose -f $COMPOSE_FILE logs -f --tail=100 backend
}

function view_frontend_logs() {
    docker-compose -f $COMPOSE_FILE logs -f --tail=100 frontend
}

# 查看状态
function show_status() {
    print_info "服务状态:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    print_info "健康检查:"
    curl -s http://localhost:8000/health | jq . || print_error "后端未响应"
    curl -s http://localhost:3000/ > /dev/null && print_info "前端正常" || print_error "前端未响应"
}

# 清理
function clean_all() {
    print_warn "这将删除所有容器、镜像和卷！"
    read -p "确认继续? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        print_info "清理中..."
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        print_info "清理完成"
    else
        print_info "已取消"
    fi
}

# 进入后端shell
function shell_backend() {
    docker-compose -f $COMPOSE_FILE exec backend /bin/bash
}

# 进入前端shell
function shell_frontend() {
    docker-compose -f $COMPOSE_FILE exec frontend /bin/sh
}

# 运行后端测试
function test_backend() {
    print_info "运行后端测试..."
    docker-compose -f $COMPOSE_FILE exec backend poetry run pytest
}

# 主函数
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    rebuild)
        rebuild_services
        ;;
    logs)
        view_logs
        ;;
    logs-be)
        view_backend_logs
        ;;
    logs-fe)
        view_frontend_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_all
        ;;
    shell-be)
        shell_backend
        ;;
    shell-fe)
        shell_frontend
        ;;
    test-be)
        test_backend
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

