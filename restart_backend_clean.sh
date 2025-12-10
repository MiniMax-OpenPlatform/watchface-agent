#!/bin/bash
# 重启后端并清空日志，查看增强后的日志

echo "🔄 重启后端并清空日志..."
echo ""

# 停止后端
echo "1️⃣ 停止后端进程..."
pkill -f "python3 main.py" 2>/dev/null
pkill -f "python main.py" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
sleep 2

# 检查端口
if lsof -i :10020 >/dev/null 2>&1; then
    echo "⚠️  端口 10020 仍被占用，强制清理..."
    lsof -ti :10020 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 清空日志
echo ""
echo "2️⃣ 清空旧日志..."
LOG_FILE="/home/moshu/my_proj/watch_agent_cd/logs/backend.log"
if [ -f "$LOG_FILE" ]; then
    > "$LOG_FILE"
    echo "✅ 日志文件已清空: $LOG_FILE"
else
    echo "⚠️  日志文件不存在，将自动创建"
fi

echo ""
echo "3️⃣ 准备重启后端..."
echo ""
echo "📋 接下来请执行："
echo ""
echo "  cd /home/moshu/my_proj/watch_agent_cd/backend"
echo "  source venv/bin/activate"
echo "  export MINIMAX_API_KEY=\"your-key-here\""
echo "  python3 main.py"
echo ""
echo "或者使用Python启动脚本："
echo ""
echo "  cd /home/moshu/my_proj/watch_agent_cd"
echo "  python3 start_services.py"
echo ""
echo "📊 启动后，实时查看详细日志："
echo ""
echo "  tail -f $LOG_FILE"
echo ""
echo "🎯 发送一个请求后，您将在日志中看到："
echo "   - 完整的请求参数（System Prompt、User Message）"
echo "   - MiniMax API的原始响应"
echo "   - 提取的代码"
echo "   - Agent思考过程"
echo "   - 代码统计信息"
echo ""


