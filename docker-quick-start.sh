#!/bin/bash

# Docker 快速启动脚本 - 适用于已配置好环境的情况
# 用途：快速启动/停止服务，无需每次重新构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
🐳 WatchFace Code Agent - Docker 快速管理脚本

用法: $0 [命令]

命令:
  start         启动所有服务
  stop          停止所有服务
  restart       重启所有服务
  status        查看服务状态
  logs          查看实时日志
  logs-backend  查看后端日志
  logs-frontend 查看前端日志
  build         重新构建镜像并启动
  clean         停止并清理所有容器和镜像
  clean-data    停止并清理所有数据（⚠️  危险操作）
  help          显示此帮助信息

示例:
  $0 start      # 启动服务
  $0 logs       # 查看日志
  $0 status     # 查看状态
EOF
}

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
}

# 启动服务
start_services() {
    print_info "启动服务..."
    docker compose up -d
    
    print_info "等待服务就绪..."
    sleep 5
    
    print_info "服务状态:"
    docker compose ps
    
    echo ""
    print_info "访问地址:"
    echo "  📱 前端: http://localhost:10031"
    echo "  🔧 后端: http://localhost:10030"
    echo "  📋 API文档: http://localhost:10030/docs"
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    docker compose down
    print_info "服务已停止"
}

# 重启服务
restart_services() {
    print_info "重启服务..."
    docker compose restart
    print_info "服务已重启"
    docker compose ps
}

# 查看状态
show_status() {
    print_info "服务状态:"
    docker compose ps
    
    echo ""
    print_info "资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# 查看日志
show_logs() {
    print_info "显示实时日志 (Ctrl+C 退出)..."
    docker compose logs -f --tail=100
}

# 查看后端日志
show_backend_logs() {
    print_info "显示后端日志 (Ctrl+C 退出)..."
    docker compose logs -f --tail=100 backend
}

# 查看前端日志
show_frontend_logs() {
    print_info "显示前端日志 (Ctrl+C 退出)..."
    docker compose logs -f --tail=100 frontend
}

# 重新构建
rebuild_services() {
    print_info "重新构建镜像..."
    docker compose build --no-cache
    
    print_info "启动服务..."
    docker compose up -d
    
    print_info "构建完成！"
    docker compose ps
}

# 清理
clean_all() {
    print_warn "这将停止并删除所有容器和镜像（不包括数据）"
    read -p "确定要继续吗? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "清理中..."
        docker compose down --rmi all
        print_info "清理完成"
    else
        print_info "已取消"
    fi
}

# 清理数据
clean_data() {
    print_error "⚠️  危险操作: 这将删除所有项目数据和上传的文件！"
    print_warn "此操作不可恢复！"
    echo ""
    read -p "确定要继续吗? 输入 'YES' 确认: " confirm
    
    if [ "$confirm" = "YES" ]; then
        print_info "清理数据中..."
        docker compose down -v
        rm -rf storage/projects/* storage/uploads/*
        print_info "数据已清理"
    else
        print_info "已取消"
    fi
}

# 主逻辑
main() {
    check_docker
    
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        logs-backend)
            show_backend_logs
            ;;
        logs-frontend)
            show_frontend_logs
            ;;
        build)
            rebuild_services
            ;;
        clean)
            clean_all
            ;;
        clean-data)
            clean_data
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

