# 后端Dockerfile - Python FastAPI应用
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/storage/projects /app/storage/uploads /app/logs

# 暴露端口
EXPOSE 10030

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    BACKEND_PORT=10030 \
    HOST=0.0.0.0

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10030", "--reload"]

