#!/bin/bash

# Docker 构建和启动脚本
# 用途：快速构建和启动 WatchFace Code Agent 系统

set -e

echo "🐳 开始构建 Docker 镜像..."
echo "================================"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "正在创建 .env 文件..."
    cat > .env << 'EOF'
# MiniMax API配置
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_API_KEY=请在这里填写你的API_KEY

# 后端配置
BACKEND_PORT=10030
HOST=0.0.0.0
DEBUG=True
EOF
    echo "✅ 已创建 .env 文件"
    echo "⚠️  请编辑 .env 文件，填写你的 MINIMAX_API_KEY"
    echo ""
    read -p "是否现在编辑 .env 文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    else
        echo "请手动编辑 .env 文件后再运行此脚本"
        exit 1
    fi
fi

# 验证 API Key 是否已设置
if grep -q "请在这里填写你的API_KEY" .env || grep -q "your_actual_api_key_here" .env; then
    echo "❌ 错误: MINIMAX_API_KEY 未正确设置"
    echo "请编辑 .env 文件，填写真实的 API Key"
    exit 1
fi

echo ""
echo "📦 构建 Docker 镜像..."
echo "================================"
docker compose build --no-cache

echo ""
echo "🚀 启动服务..."
echo "================================"
docker compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

echo ""
echo "🔍 检查服务状态..."
echo "================================"
docker compose ps

echo ""
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:10031"
echo "   后端: http://localhost:10030"
echo "   健康检查: http://localhost:10030/health"
echo ""
echo "📋 常用命令:"
echo "   查看日志: docker compose logs -f"
echo "   停止服务: docker compose down"
echo "   重启服务: docker compose restart"
echo ""
echo "💡 提示: 使用 Ctrl+C 不会停止服务，使用 docker compose down 来停止"
echo ""

