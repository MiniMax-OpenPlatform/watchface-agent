#!/bin/bash

# 统一镜像构建脚本
# 用途：构建和启动前后端一体化的 Docker 镜像

set -e

echo "🐳 开始构建统一 Docker 镜像（前端 + 后端）..."
echo "================================"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在，正在创建..."
    cat > .env << 'EOF'
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_API_KEY=请在这里填写你的API_KEY
BACKEND_PORT=10030
HOST=0.0.0.0
DEBUG=True
EOF
    echo "✅ 已创建 .env 文件"
    echo "⚠️  请编辑 .env 文件，填写你的 MINIMAX_API_KEY"
    exit 1
fi

# 验证 API Key
if grep -q "请在这里填写你的API_KEY" .env; then
    echo "❌ 错误: MINIMAX_API_KEY 未正确设置"
    echo "请编辑 .env 文件，填写真实的 API Key"
    exit 1
fi

echo ""
echo "📦 构建统一镜像..."
echo "================================"
sudo docker compose -f docker-compose-unified.yml build --no-cache

echo ""
echo "🚀 启动服务..."
echo "================================"
sudo docker compose -f docker-compose-unified.yml up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

echo ""
echo "🔍 检查服务状态..."
echo "================================"
sudo docker compose -f docker-compose-unified.yml ps

echo ""
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "📍 访问地址:"
echo "   应用入口: http://localhost:10031/watch-agent/"
echo "   健康检查: http://localhost:10031/health"
echo "   后端API: http://localhost:10031/api/ (自动代理)"
echo ""
echo "📋 常用命令:"
echo "   查看日志: sudo docker compose -f docker-compose-unified.yml logs -f"
echo "   停止服务: sudo docker compose -f docker-compose-unified.yml down"
echo "   重启服务: sudo docker compose -f docker-compose-unified.yml restart"
echo ""
echo "💡 提示: 访问根路径 http://localhost:10031/ 会自动重定向到 /watch-agent/"
echo ""

