#!/bin/bash
cd "$(dirname "$0")/backend"
source venv/bin/activate

# 从环境变量读取API密钥，如果没有则提示用户设置
if [ -z "$MINIMAX_API_KEY" ]; then
    echo "❌ 错误: 请设置 MINIMAX_API_KEY 环境变量"
    echo "   export MINIMAX_API_KEY=\"your_api_key_here\""
    exit 1
fi

export MINIMAX_BASE_URL="${MINIMAX_BASE_URL:-https://api.minimaxi.com/v1}"
export BACKEND_PORT="${BACKEND_PORT:-10030}"

echo "🚀 Starting WatchFace Code Agent Backend on port $BACKEND_PORT..."
python3 main.py

