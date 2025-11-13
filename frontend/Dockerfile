# 网络小说智能问答系统 - Frontend Dockerfile
# 多阶段构建，优化镜像大小

# === 依赖安装阶段 ===
FROM node:18-alpine AS deps

# 安装libc6-compat以兼容某些npm包
RUN apk add --no-cache libc6-compat

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖（使用npm ci以获得可重现的构建）
RUN npm ci

# === 构建阶段 ===
FROM node:18-alpine AS builder

WORKDIR /app

# 从deps阶段复制node_modules
COPY --from=deps /app/node_modules ./node_modules

# 复制应用代码
COPY . .

# 设置环境变量（生产构建）
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# 构建应用
RUN npm run build

# === 运行阶段 ===
FROM node:18-alpine AS runner

WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# 复制必要文件
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 设置主机名（避免Next.js警告）
ENV HOSTNAME="0.0.0.0"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# 启动命令（生产模式）
CMD ["node", "server.js"]

