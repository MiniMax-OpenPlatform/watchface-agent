#!/bin/bash

# WatchFace Agent 启动脚本
# 自动启动后端和前端服务

echo "=================================="
echo "🚀 WatchFace Agent 启动脚本"
echo "=================================="
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 检查.env文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  警告: backend/.env 文件不存在"
    echo "   请创建.env文件并设置 MINIMAX_API_KEY"
    echo ""
    echo "创建示例.env文件? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cat > backend/.env << EOF
# MiniMax-M2 API Configuration
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLpmYjlh6_lroEiLCJVc2VyTmFtZSI6IumZiOWHr-WugSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxODM2NzAyODA4NzMzMTI3MDU3IiwiUGhvbmUiOiIxNTg4OTcyOTA0MSIsIkdyb3VwSUQiOiIxODM2NzAyODA4NzI0NzM4NDQ5IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDgtMTQgMDE6NTU6MDAiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.PyP-etho9FgXJD3JwFpY3RezRug_bFmEA-FeicIEpLGocUVQZyPnbtuXrYbAlZD8x25TC2x3MhHkhvYFeP9Ap7JOdBRPPJ-na2hDMEXMTje9yPmQPvdKp7U7VQwSweVNMKreUzU6K0k6l92TN6IwL3Sq9KmNgfJF5P6mvA5j1ooVK0MKKz7AqX9RqjvhN4iNUpR76z3qpOVSLfZb00_kWoNIy9_v3tI-w8K5M_MMd4nzETzIem9I8jMUNx4ChX4Bs_5AVAs5X9Dxy_9Z9X21i4fIKY8OzbWXM_vas1rYQBgtTt2vJ4UW6LKhEyG-6TKG7RlSKqChEB46T-FElP2-xw"

# Server Configuration
BACKEND_PORT=10020
FRONTEND_URL=http://localhost:10021

# Environment
DEBUG=true
LOG_LEVEL=INFO
EOF
        echo "✅ 已创建 backend/.env 文件"
        echo "   请编辑该文件，设置您的 MINIMAX_API_KEY"
        echo ""
    fi
fi

echo "📦 检查依赖..."
echo ""

# 检查后端依赖
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境并安装后端依赖..."
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

# 检查前端依赖
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
cd ..

echo ""
echo "✅ 依赖检查完成"
echo ""

# 启动后端
echo "🔧 启动后端服务 (端口 10020)..."
cd backend
source venv/bin/activate
python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# 检查后端是否启动成功
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败，请查看 backend.log"
    exit 1
fi

# 启动前端
echo "🎨 启动前端服务 (端口 10021)..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

# 检查前端是否启动成功
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
else
    echo "❌ 前端服务启动失败，请查看 frontend.log"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "=================================="
echo "🎉 服务启动成功！"
echo "=================================="
echo ""
echo "🔗 访问地址:"
echo "   前端: http://localhost:10021"
echo "   后端: http://localhost:10020"
echo "   API文档: http://localhost:10020/docs"
echo ""
echo "📝 日志文件:"
echo "   后端: backend.log"
echo "   前端: frontend.log"
echo ""
echo "⚠️  按 Ctrl+C 停止所有服务"
echo ""

# 保存PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo '✅ 服务已停止'; exit 0" INT

# 持续运行
tail -f backend.log &
wait

