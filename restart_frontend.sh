#!/bin/bash
# 快速重启前端服务

echo "🔄 重启前端服务..."
echo ""

# 停止前端
echo "1️⃣ 停止现有前端进程..."
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
sleep 2

# 检查端口
echo "2️⃣ 检查端口状态..."
if lsof -i :10021 >/dev/null 2>&1; then
    echo "⚠️  端口 10021 仍被占用"
    lsof -i :10021
else
    echo "✅ 端口 10021 已释放"
fi

echo ""
echo "3️⃣ 启动前端..."
echo ""
echo "请在此终端运行以下命令："
echo ""
echo "  cd /home/moshu/my_proj/watch_agent_cd/frontend"
echo "  npm run dev"
echo ""
echo "或者在新终端中运行上述命令"

