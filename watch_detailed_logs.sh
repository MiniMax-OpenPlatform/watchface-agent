#!/bin/bash
# 查看增强后的详细日志 - 多种查看方式

LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_menu() {
    echo ""
    echo "==============================================="
    echo "  📊 WatchFace Agent - 详细日志查看工具"
    echo "==============================================="
    echo ""
    echo "选择查看方式："
    echo ""
    echo "  ${GREEN}1)${NC} 实时查看所有日志 (tail -f)"
    echo "  ${GREEN}2)${NC} 只看关键信息 (成功✅/失败❌)"
    echo "  ${GREEN}3)${NC} 只看API请求和响应 (📤📥)"
    echo "  ${GREEN}4)${NC} 只看生成的代码"
    echo "  ${GREEN}5)${NC} 只看Agent思考过程"
    echo "  ${GREEN}6)${NC} 只看代码差异分析"
    echo "  ${GREEN}7)${NC} 只看错误日志"
    echo "  ${GREEN}8)${NC} 查看最后一次完整请求"
    echo "  ${GREEN}9)${NC} 统计信息"
    echo "  ${RED}0)${NC} 退出"
    echo ""
    echo -n "请输入选项 (0-9): "
}

# 检查日志文件
check_log_file() {
    if [ ! -f "$LOG_FILE" ]; then
        echo ""
        echo "${RED}❌ 日志文件不存在: $LOG_FILE${NC}"
        echo ""
        echo "请先启动后端服务，或检查日志配置。"
        echo ""
        exit 1
    fi
    
    if [ ! -s "$LOG_FILE" ]; then
        echo ""
        echo "${YELLOW}⚠️  日志文件为空${NC}"
        echo ""
        echo "请发送一些请求来生成日志。"
        echo ""
    fi
}

# 1. 实时查看所有日志
watch_all() {
    echo ""
    echo "${CYAN}📋 实时查看所有日志...${NC}"
    echo "按 Ctrl+C 退出"
    echo ""
    tail -f "$LOG_FILE"
}

# 2. 只看关键信息
watch_summary() {
    echo ""
    echo "${CYAN}📋 实时查看关键信息 (成功/失败)...${NC}"
    echo "按 Ctrl+C 退出"
    echo ""
    tail -f "$LOG_FILE" | grep --line-buffered -E "✅|❌|🤖|处理开始|处理完成|处理异常"
}

# 3. 只看API交互
watch_api() {
    echo ""
    echo "${CYAN}📋 实时查看API请求和响应...${NC}"
    echo "按 Ctrl+C 退出"
    echo ""
    tail -f "$LOG_FILE" | grep --line-buffered -E "📤|📥|MiniMax API|请求详情|响应详情|Response ID|模型:|温度:|原始内容"
}

# 4. 只看生成的代码
watch_code() {
    echo ""
    echo "${CYAN}📋 查看最近生成的代码 (前500字符预览)...${NC}"
    echo ""
    grep -A 10 "提取的代码" "$LOG_FILE" | tail -50
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 5. 只看思考过程
watch_thinking() {
    echo ""
    echo "${CYAN}📋 查看Agent思考过程...${NC}"
    echo ""
    grep -A 8 "Agent思考过程" "$LOG_FILE" | tail -50
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 6. 只看代码差异
watch_diff() {
    echo ""
    echo "${CYAN}📋 查看代码差异分析...${NC}"
    echo ""
    grep -A 20 "代码差异分析" "$LOG_FILE" | tail -50
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 7. 只看错误
watch_errors() {
    echo ""
    echo "${RED}📋 查看错误日志...${NC}"
    echo ""
    grep -i "❌\|ERROR\|Exception\|Traceback" "$LOG_FILE" | tail -50
    
    if [ $? -ne 0 ]; then
        echo "${GREEN}✅ 没有错误日志！${NC}"
    fi
    
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 8. 查看最后一次完整请求
watch_last_request() {
    echo ""
    echo "${CYAN}📋 最后一次完整请求日志...${NC}"
    echo ""
    
    # 找到最后一个"Code Agent 处理开始"的位置
    last_start=$(grep -n "🤖 Code Agent 处理开始" "$LOG_FILE" | tail -1 | cut -d: -f1)
    
    if [ -z "$last_start" ]; then
        echo "${YELLOW}⚠️  没有找到完整请求记录${NC}"
    else
        # 从该位置开始，显示接下来的100行（覆盖一次完整请求）
        tail -n +$last_start "$LOG_FILE" | head -150
    fi
    
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 9. 统计信息
show_stats() {
    echo ""
    echo "${CYAN}📊 日志统计信息${NC}"
    echo "=========================================="
    
    total_requests=$(grep -c "🤖 Code Agent 处理开始" "$LOG_FILE" 2>/dev/null)
    echo "总请求数: ${GREEN}${total_requests}${NC}"
    
    success_count=$(grep -c "✅ Code Agent 处理完成" "$LOG_FILE" 2>/dev/null)
    echo "成功数量: ${GREEN}${success_count}${NC}"
    
    error_count=$(grep -c "❌.*失败\|❌.*异常" "$LOG_FILE" 2>/dev/null)
    echo "失败数量: ${RED}${error_count}${NC}"
    
    if [ $total_requests -gt 0 ]; then
        success_rate=$(echo "scale=1; $success_count * 100 / $total_requests" | bc 2>/dev/null)
        echo "成功率: ${GREEN}${success_rate}%${NC}"
    fi
    
    echo ""
    new_count=$(grep -c "场景类型: 新建表盘" "$LOG_FILE" 2>/dev/null)
    edit_count=$(grep -c "场景类型: 修改表盘" "$LOG_FILE" 2>/dev/null)
    echo "新建表盘: ${BLUE}${new_count}${NC}"
    echo "修改表盘: ${BLUE}${edit_count}${NC}"
    
    echo ""
    api_requests=$(grep -c "📤 MiniMax API 请求详情" "$LOG_FILE" 2>/dev/null)
    echo "MiniMax API 调用: ${PURPLE}${api_requests}${NC}"
    
    thinking_count=$(grep -c "Agent思考过程" "$LOG_FILE" 2>/dev/null)
    echo "包含思考过程: ${PURPLE}${thinking_count}${NC}"
    
    echo ""
    log_size=$(du -h "$LOG_FILE" | cut -f1)
    log_lines=$(wc -l < "$LOG_FILE")
    echo "日志文件大小: ${CYAN}${log_size}${NC}"
    echo "日志总行数: ${CYAN}${log_lines}${NC}"
    
    echo "=========================================="
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 主循环
main() {
    clear
    check_log_file
    
    while true; do
        clear
        show_menu
        read choice
        
        case $choice in
            1) watch_all ;;
            2) watch_summary ;;
            3) watch_api ;;
            4) watch_code ;;
            5) watch_thinking ;;
            6) watch_diff ;;
            7) watch_errors ;;
            8) watch_last_request ;;
            9) show_stats ;;
            0) 
                echo ""
                echo "👋 再见！"
                echo ""
                exit 0
                ;;
            *)
                echo ""
                echo "${RED}❌ 无效选项，请重试${NC}"
                sleep 1
                ;;
        esac
    done
}

# 运行
main


