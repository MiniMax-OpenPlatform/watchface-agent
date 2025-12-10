#!/bin/bash
# 重启WatchFace Code Agent服务（使用服务器IP配置）

echo "🛑 停止现有服务..."

# 停止Python后端
pkill -f "python3 main.py" 2>/dev/null
pkill -f "python3 start_services.py" 2>/dev/null

# 停止Node前端
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

sleep 2

echo "✅ 已停止所有服务"
echo ""
echo "🚀 重新启动服务..."
echo ""
echo "请运行以下命令启动服务："
echo ""
echo "  cd /home/moshu/my_proj/watch_agent_cd"
echo "  python3 start_services.py"
echo ""
echo "或者分别启动："
echo ""
echo "  # 终端1 - 后端"
echo "  cd /home/moshu/my_proj/watch_agent_cd/backend"
echo "  source venv/bin/activate"
echo "  export MINIMAX_API_KEY='your-key-here'"
echo "  python3 main.py"
echo ""
echo "  # 终端2 - 前端"
echo "  cd /home/moshu/my_proj/watch_agent_cd/frontend"
echo "  npm run dev"
echo ""
echo "📱 访问地址: http://10.11.17.19:10021"
echo "🔧 API地址: http://10.11.17.19:10020"

