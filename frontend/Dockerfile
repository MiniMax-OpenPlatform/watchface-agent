# 前端Dockerfile - 多阶段构建
# 阶段1: 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 设置环境变量（指向后端服务）
ENV VITE_API_BASE_URL=http://localhost:10030

# 构建生产版本
RUN npm run build

# 阶段2: 运行阶段
FROM nginx:alpine

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 10031

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]

