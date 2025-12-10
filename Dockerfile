# 统一 Dockerfile - 前后端一体化镜像（优化版）
# 使用Python同时服务前端静态文件和后端API，无需Nginx

# ============= 阶段1: 构建前端 =============
FROM node:18-alpine AS frontend-builder

# 使用阿里云镜像源（Alpine）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

WORKDIR /app/frontend

# 设置 npm 使用淘宝镜像
RUN npm config set registry https://registry.npmmirror.com

# 复制前端依赖文件
COPY frontend/package*.json ./
RUN npm ci

# 复制前端源码并构建
COPY frontend/ ./
RUN npm run build

# ============= 阶段2: 最终镜像 =============
FROM python:3.10-slim

# 使用阿里云 Debian 镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 只安装必要的工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 使用清华大学 pip 镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端依赖文件并安装
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 从前端构建阶段复制构建产物到后端的static目录
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# 创建必要的目录
RUN mkdir -p /app/storage/projects /app/storage/uploads /app/logs

# 暴露端口（只需要一个端口）
EXPOSE 10031

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    BACKEND_PORT=10030 \
    FRONTEND_PORT=10031

# 复制启动脚本
COPY start-unified.sh /app/
RUN chmod +x /app/start-unified.sh

# 启动脚本会同时启动后端API和前端静态文件服务
CMD ["/app/start-unified.sh"]
