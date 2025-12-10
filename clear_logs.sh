#!/bin/bash
# 清空日志文件

echo "🧹 清空旧日志..."

# 清空后端日志
> /home/moshu/my_proj/watch_agent_cd/backend.log

echo "✅ 日志已清空"
echo ""
echo "现在可以重新启动服务了："
echo "  cd /home/moshu/my_proj/watch_agent_cd"
echo "  python3 start_services.py"

