#!/bin/bash
# 生产环境Docker管理脚本

set -e

PROJECT_NAME="novel-rag"
COMPOSE_FILE="docker-compose.prod.yml"

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
网络小说智能问答系统 - 生产环境管理脚本

用法: $0 <command>

命令:
    deploy      部署服务（构建+启动）
    start       启动所有服务
    stop        停止所有服务
    restart     重启所有服务
    update      更新服务（拉取代码+重新构建）
    logs        查看所有日志
    status      查看服务状态和健康检查
    backup      备份数据
    restore     恢复数据
    scale       扩展服务实例
    help        显示此帮助信息

示例:
    $0 deploy       # 首次部署
    $0 update       # 更新到最新版本
    $0 backup       # 备份数据
    $0 scale backend=4  # 扩展后端到4个实例
EOF
}

# 部署服务
function deploy_services() {
    print_info "开始生产环境部署..."
    
    # 检查配置文件
    if [ ! -f "backend/.env.production" ]; then
        print_error "未找到backend/.env.production文件！"
        print_info "请从.env.example复制并配置"
        exit 1
    fi
    
    # 构建镜像
    print_info "构建Docker镜像..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # 启动服务
    print_info "启动服务..."
    docker-compose -f $COMPOSE_FILE up -d
    
    # 等待服务就绪
    print_info "等待服务就绪..."
    sleep 10
    
    # 健康检查
    check_health
    
    print_info "部署完成！"
}

# 启动服务
function start_services() {
    print_info "启动生产服务..."
    docker-compose -f $COMPOSE_FILE up -d
    print_info "服务已启动"
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

# 更新服务
function update_services() {
    print_warn "准备更新服务..."
    
    # 备份数据
    print_info "备份当前数据..."
    backup_data
    
    # 拉取最新代码
    print_info "拉取最新代码..."
    git pull
    
    # 重新构建
    print_info "重新构建镜像..."
    docker-compose -f $COMPOSE_FILE build
    
    # 滚动更新
    print_info "执行滚动更新..."
    docker-compose -f $COMPOSE_FILE up -d --no-deps --build
    
    # 健康检查
    sleep 10
    check_health
    
    print_info "更新完成！"
}

# 查看日志
function view_logs() {
    docker-compose -f $COMPOSE_FILE logs -f --tail=200
}

# 查看状态
function show_status() {
    print_info "=== 服务状态 ==="
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    
    print_info "=== 健康检查 ==="
    check_health
    
    echo ""
    print_info "=== 资源使用 ==="
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# 健康检查
function check_health() {
    # 后端健康检查
    if curl -sf http://localhost:8000/health > /dev/null; then
        print_info "✓ 后端服务正常"
        # 详细健康信息
        curl -s http://localhost:8000/health/detailed | jq .
    else
        print_error "✗ 后端服务异常"
        return 1
    fi
    
    # 前端健康检查
    if curl -sf http://localhost:3000/ > /dev/null; then
        print_info "✓ 前端服务正常"
    else
        print_error "✗ 前端服务异常"
        return 1
    fi
    
    # Nginx健康检查（如果启用）
    if docker-compose -f $COMPOSE_FILE ps | grep -q nginx; then
        if curl -sf http://localhost/health > /dev/null; then
            print_info "✓ Nginx正常"
        else
            print_error "✗ Nginx异常"
            return 1
        fi
    fi
}

# 备份数据
function backup_data() {
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    print_info "备份到: $BACKUP_DIR"
    
    # 备份数据卷
    docker run --rm \
        -v novel-rag-backend-data:/data \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar czf /backup/backend-data.tar.gz -C /data .
    
    docker run --rm \
        -v novel-rag-backend-logs:/logs \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar czf /backup/backend-logs.tar.gz -C /logs .
    
    # 备份配置
    cp backend/.env.production $BACKUP_DIR/
    
    print_info "备份完成: $BACKUP_DIR"
}

# 恢复数据
function restore_data() {
    if [ -z "$2" ]; then
        print_error "请指定备份目录"
        echo "用法: $0 restore <backup_directory>"
        ls -d backups/*/
        exit 1
    fi
    
    BACKUP_DIR=$2
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi
    
    print_warn "准备从 $BACKUP_DIR 恢复数据..."
    read -p "确认继续? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        print_info "已取消"
        exit 0
    fi
    
    # 停止服务
    print_info "停止服务..."
    docker-compose -f $COMPOSE_FILE down
    
    # 恢复数据
    print_info "恢复数据..."
    docker run --rm \
        -v novel-rag-backend-data:/data \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine sh -c "cd /data && tar xzf /backup/backend-data.tar.gz"
    
    # 恢复配置
    cp $BACKUP_DIR/.env.production backend/
    
    # 重启服务
    print_info "重启服务..."
    docker-compose -f $COMPOSE_FILE up -d
    
    print_info "恢复完成"
}

# 扩展服务
function scale_services() {
    if [ -z "$2" ]; then
        print_error "请指定扩展参数"
        echo "用法: $0 scale <service>=<count>"
        echo "示例: $0 scale backend=4"
        exit 1
    fi
    
    print_info "扩展服务: $2"
    docker-compose -f $COMPOSE_FILE up -d --scale $2
    print_info "扩展完成"
}

# 主函数
case "$1" in
    deploy)
        deploy_services
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    update)
        update_services
        ;;
    logs)
        view_logs
        ;;
    status)
        show_status
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$@"
        ;;
    scale)
        scale_services "$@"
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

