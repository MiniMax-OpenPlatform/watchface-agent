#!/bin/bash

# Docker 统一镜像管理脚本
# 用途：快速管理前后端一体化的 Docker 服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Docker Compose 文件
COMPOSE_FILE="docker-compose-unified.yml"

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 显示帮助
show_help() {
    cat << EOF
🐳 WatchFace Agent - 统一镜像管理脚本

用法: $0 [命令]

命令:
  start       启动服务
  stop        停止服务
  restart     重启服务
  build       重新构建镜像
  rebuild     完全重新构建（清除缓存）
  status      查看服务状态
  logs        查看实时日志
  shell       进入容器Shell
  clean       停止并删除容器
  info        显示服务信息
  help        显示此帮助

示例:
  $0 start    # 启动服务
  $0 logs     # 查看日志
  $0 status   # 查看状态
EOF
}

# 启动服务
start_service() {
    print_header "启动服务"
    sudo docker compose -f $COMPOSE_FILE up -d
    sleep 3
    print_info "服务已启动"
    show_info
}

# 停止服务
stop_service() {
    print_header "停止服务"
    sudo docker compose -f $COMPOSE_FILE down
    print_info "服务已停止"
}

# 重启服务
restart_service() {
    print_header "重启服务"
    sudo docker compose -f $COMPOSE_FILE restart
    sleep 3
    print_info "服务已重启"
    show_info
}

# 构建镜像
build_image() {
    print_header "构建镜像"
    sudo docker compose -f $COMPOSE_FILE build
    print_info "镜像构建完成"
}

# 完全重新构建
rebuild_image() {
    print_header "完全重新构建（清除缓存）"
    sudo docker compose -f $COMPOSE_FILE build --no-cache
    print_info "镜像重新构建完成"
    
    print_info "重启服务..."
    sudo docker compose -f $COMPOSE_FILE up -d --force-recreate
    sleep 3
    show_info
}

# 查看状态
show_status() {
    print_header "容器状态"
    sudo docker compose -f $COMPOSE_FILE ps
    
    echo ""
    print_header "资源使用"
    sudo docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep -E "(NAME|watchface)"
}

# 查看日志
show_logs() {
    print_header "实时日志 (Ctrl+C 退出)"
    sudo docker compose -f $COMPOSE_FILE logs -f --tail=100
}

# 进入Shell
enter_shell() {
    print_header "进入容器 Shell"
    print_info "输入 'exit' 退出容器"
    sudo docker compose -f $COMPOSE_FILE exec watchface-agent bash
}

# 清理
clean_service() {
    print_warn "这将停止并删除容器（不包括数据）"
    read -p "确定要继续吗? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_header "清理容器"
        sudo docker compose -f $COMPOSE_FILE down
        print_info "清理完成"
    else
        print_info "已取消"
    fi
}

# 显示服务信息
show_info() {
    print_header "服务信息"
    echo "📍 访问地址:"
    echo "   🌐 前端: http://10.11.17.19:10031/watch-agent/"
    echo "   🔧 API:  http://10.11.17.19:10031/api/"
    echo "   ❤️  健康: http://10.11.17.19:10031/health"
    echo ""
    echo "📂 数据目录:"
    echo "   项目: ./storage/projects/"
    echo "   素材: ./storage/uploads/"
    echo "   日志: ./logs/"
    echo ""
    
    # 测试健康检查
    if curl -s http://localhost:10031/health > /dev/null 2>&1; then
        print_info "服务状态: 健康 ✓"
    else
        print_error "服务状态: 不可用 ✗"
    fi
}

# 主逻辑
main() {
    case "${1:-help}" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        build)
            build_image
            ;;
        rebuild)
            rebuild_image
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        shell)
            enter_shell
            ;;
        clean)
            clean_service
            ;;
        info)
            show_info
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
}

main "$@"

