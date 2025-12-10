#!/bin/bash

# 统一启动脚本 - 使用Python同时服务前端和后端

cd /app/backend

# 启动 FastAPI 服务（同时提供API和静态文件服务）
exec python3 -m uvicorn main_unified:app \
    --host 0.0.0.0 \
    --port 10031 \
    --log-level info

