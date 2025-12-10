#!/bin/bash
# 日志查看工具

echo "📋 WatchFace Code Agent - 日志查看工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo "请选择要查看的日志："
    echo ""
    echo "  1) 查看后端日志（最新50行）"
    echo "  2) 实时跟踪后端日志"
    echo "  3) 查看后端错误日志"
    echo "  4) 查看进程状态"
    echo "  5) 查看API请求日志"
    echo "  6) 清空日志文件"
    echo "  7) 查看完整后端日志"
    echo "  0) 退出"
    echo ""
}

# 查看最新日志
view_recent_logs() {
    echo -e "${BLUE}📝 后端最新50行日志:${NC}"
    echo "----------------------------------------"
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  未找到日志文件: $LOG_FILE${NC}"
        echo "提示: 请先启动服务"
        echo ""
        echo "启动命令:"
        echo "  cd /home/moshu/my_proj/watch_agent_cd"
        echo "  python3 start_services.py"
    fi
}

# 实时跟踪日志
follow_logs() {
    echo -e "${BLUE}📊 实时跟踪后端日志 (Ctrl+C 退出):${NC}"
    echo "----------------------------------------"
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  未找到日志文件: $LOG_FILE${NC}"
    fi
}

# 查看错误日志
view_errors() {
    echo -e "${RED}❌ 后端错误日志:${NC}"
    echo "----------------------------------------"
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    if [ -f "$LOG_FILE" ]; then
        grep -i "error\|exception\|traceback\|failed" "$LOG_FILE" | tail -20
        if [ $? -ne 0 ]; then
            echo -e "${GREEN}✅ 未发现错误${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未找到日志文件: $LOG_FILE${NC}"
    fi
}

# 查看进程状态
view_processes() {
    echo -e "${BLUE}🔍 服务进程状态:${NC}"
    echo "----------------------------------------"
    
    # 后端进程
    echo -e "${GREEN}后端进程:${NC}"
    ps aux | grep "[p]ython3 main.py" || echo "  后端未运行"
    
    echo ""
    
    # 前端进程
    echo -e "${GREEN}前端进程:${NC}"
    ps aux | grep "[v]ite" || echo "  前端未运行"
    
    echo ""
    
    # 端口监听
    echo -e "${GREEN}端口监听:${NC}"
    netstat -tuln | grep -E "10020|10021" || echo "  未发现服务端口"
}

# 查看API请求
view_api_requests() {
    echo -e "${BLUE}🌐 API请求日志:${NC}"
    echo "----------------------------------------"
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    if [ -f "$LOG_FILE" ]; then
        grep -E "Received generate request|Health check" "$LOG_FILE" | tail -20
        if [ $? -ne 0 ]; then
            echo "  暂无API请求记录"
        fi
    else
        echo -e "${YELLOW}⚠️  未找到日志文件: $LOG_FILE${NC}"
    fi
}

# 清空日志
clear_logs() {
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    echo -e "${YELLOW}⚠️  确定要清空日志文件吗? (y/N)${NC}"
    read -r confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if [ -f "$LOG_FILE" ]; then
            > "$LOG_FILE"
            echo -e "${GREEN}✅ 日志已清空${NC}"
        else
            echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
        fi
    else
        echo "取消操作"
    fi
}

# 查看完整日志
view_full_logs() {
    echo -e "${BLUE}📄 完整后端日志:${NC}"
    echo "----------------------------------------"
    LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
    if [ -f "$LOG_FILE" ]; then
        less "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  未找到日志文件: $LOG_FILE${NC}"
    fi
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-7): " choice
    echo ""
    
    case $choice in
        1)
            view_recent_logs
            ;;
        2)
            follow_logs
            ;;
        3)
            view_errors
            ;;
        4)
            view_processes
            ;;
        5)
            view_api_requests
            ;;
        6)
            clear_logs
            ;;
        7)
            view_full_logs
            ;;
        0)
            echo "👋 再见!"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选项${NC}"
            ;;
    esac
    
    echo ""
    echo "按回车继续..."
    read
    clear
done

