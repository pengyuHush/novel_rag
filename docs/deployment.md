# 网络小说智能问答系统 - 部署文档

## 📋 目录

1. [部署前准备](#部署前准备)
2. [Docker部署](#docker部署)
3. [手动部署](#手动部署)
4. [生产环境配置](#生产环境配置)
5. [监控和维护](#监控和维护)
6. [故障排查](#故障排查)

---

## 部署前准备

### 系统要求

#### 硬件要求
- **CPU**: 4核心及以上
- **内存**: 8GB及以上（推荐16GB）
- **存储**: 50GB及以上可用空间
- **网络**: 稳定的互联网连接

#### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+推荐) / macOS / Windows Server
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 获取智谱AI API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账号
3. 在"API Keys"页面创建新密钥
4. 保存密钥以备后用

---

## Docker部署

### 方式一：开发环境快速部署

适用于本地开发和测试。

#### 1. 克隆代码

```bash
git clone <repository-url>
cd novel_rag_spec_kit
```

#### 2. 配置环境变量

```bash
# 后端配置
cd backend
cp .env.example .env
```

编辑 `backend/.env`：
```ini
ZHIPU_API_KEY=your_api_key_here
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
# 前端配置
cd ../frontend
cp .env.example .env.local
```

编辑 `frontend/.env.local`：
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

#### 3. 启动服务

```bash
cd ..
docker-compose up -d
```

#### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

#### 5. 访问应用

- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

#### 6. 停止服务

```bash
docker-compose down
```

---

### 方式二：生产环境部署

适用于生产环境，包含性能优化和安全加固。

#### 1. 准备生产配置

```bash
# 后端生产配置
cd backend
cp .env.example .env.production
```

编辑 `backend/.env.production`：
```ini
ZHIPU_API_KEY=your_production_api_key
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com
```

#### 2. 构建生产镜像

```bash
cd ..
docker-compose -f docker-compose.prod.yml build
```

#### 3. 启动生产服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. 配置Nginx（可选）

如果使用Nginx反向代理：

```bash
# 准备SSL证书（如果使用HTTPS）
mkdir -p nginx/ssl
cp /path/to/cert.pem nginx/ssl/
cp /path/to/key.pem nginx/ssl/

# 编辑nginx配置
nano nginx/nginx.conf
# 取消HTTPS相关注释，修改server_name

# 重启服务
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 5. 验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost:3000/

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 手动部署

### 后端部署

#### 1. 安装Python 3.12+

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# CentOS/RHEL
sudo yum install python312 python312-devel
```

#### 2. 安装Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

#### 3. 安装依赖

```bash
cd backend
poetry install --only main
```

#### 4. 配置环境

```bash
cp .env.example .env
nano .env  # 编辑配置
```

#### 5. 初始化数据库

```bash
poetry run python -m app.db.init_db
```

#### 6. 启动服务

```bash
# 开发模式
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式（使用gunicorn）
poetry run gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

#### 7. 配置systemd服务（Linux）

创建 `/etc/systemd/system/novel-rag-backend.service`：

```ini
[Unit]
Description=Novel RAG Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/novel_rag_spec_kit/backend
Environment="PATH=/opt/novel_rag_spec_kit/backend/.venv/bin"
ExecStart=/opt/novel_rag_spec_kit/backend/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable novel-rag-backend
sudo systemctl start novel-rag-backend
sudo systemctl status novel-rag-backend
```

### 前端部署

#### 1. 安装Node.js 18+

```bash
# 使用nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

#### 2. 安装依赖

```bash
cd frontend
npm ci
```

#### 3. 配置环境

```bash
cp .env.example .env.local
nano .env.local  # 编辑配置
```

#### 4. 构建生产版本

```bash
npm run build
```

#### 5. 启动服务

```bash
# 使用Next.js内置服务器
npm start

# 使用PM2（推荐）
npm install -g pm2
pm2 start npm --name "novel-rag-frontend" -- start
pm2 save
pm2 startup
```

---

## 生产环境配置

### 1. 安全配置

#### 更改默认端口

编辑 `backend/.env.production`：
```ini
PORT=8080  # 避免使用默认端口
```

#### 配置CORS

```ini
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

#### 启用HTTPS

使用Let's Encrypt获取免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 性能优化

#### 数据库优化

```ini
# backend/.env.production
CHROMA_PERSIST_DIR=/mnt/ssd/chromadb  # 使用SSD存储
```

#### 缓存配置

考虑添加Redis缓存：
```bash
docker run -d --name redis \
    -p 6379:6379 \
    redis:alpine
```

#### CDN配置

将静态资源部署到CDN：
- 前端静态文件: `frontend/public/`, `frontend/.next/static/`
- 配置Next.js使用CDN: 编辑 `frontend/next.config.js`

### 3. 监控配置

#### 日志聚合

使用ELK Stack或Loki收集日志：
```bash
# 配置日志输出到syslog
# backend/.env.production
LOG_OUTPUT=syslog
```

#### 应用监控

集成Prometheus + Grafana：
```bash
# 添加metrics端点
# backend/app/api/metrics.py
```

### 4. 备份策略

#### 自动备份脚本

创建 `scripts/backup.sh`：
```bash
#!/bin/bash
BACKUP_DIR="/backup/novel-rag/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据库
cp -r backend/data/sqlite $BACKUP_DIR/
cp -r backend/data/chromadb $BACKUP_DIR/

# 备份上传文件
tar -czf $BACKUP_DIR/uploads.tar.gz backend/data/uploads

# 备份配置
cp backend/.env.production $BACKUP_DIR/

# 清理旧备份（保留30天）
find /backup/novel-rag -type d -mtime +30 -exec rm -rf {} \;
```

配置cron定时任务：
```bash
# 每天凌晨2点执行备份
0 2 * * * /opt/novel_rag_spec_kit/scripts/backup.sh
```

---

## 监控和维护

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细健康检查
curl http://localhost:8000/health/detailed
```

### 性能监控

监控关键指标：
- API响应时间
- LLM调用延迟
- 数据库查询性能
- 内存和CPU使用率
- 磁盘空间

### 日志查看

```bash
# Docker环境
docker-compose logs -f --tail=100

# 手动部署
tail -f backend/logs/app.log
tail -f /var/log/nginx/access.log
```

### 更新部署

#### Docker环境

```bash
# 拉取最新代码
git pull

# 重建镜像
docker-compose -f docker-compose.prod.yml build

# 滚动更新
docker-compose -f docker-compose.prod.yml up -d
```

#### 手动部署

```bash
# 后端更新
cd backend
git pull
poetry install --only main
sudo systemctl restart novel-rag-backend

# 前端更新
cd frontend
git pull
npm ci
npm run build
pm2 restart novel-rag-frontend
```

---

## 故障排查

### 常见问题

#### 1. ChromaDB启动失败

**症状**: 后端无法连接ChromaDB

**解决方案**:
```bash
# 清理锁文件
rm backend/data/chromadb/*.wal
rm backend/data/chromadb/*.shm

# 重启服务
docker-compose restart backend
```

#### 2. 内存不足

**症状**: 容器频繁重启，OOM错误

**解决方案**:
```bash
# 增加Docker内存限制
docker-compose -f docker-compose.prod.yml up -d --scale backend=1 --memory=4g

# 或修改docker-compose.prod.yml中的资源限制
```

#### 3. 磁盘空间不足

**症状**: 无法上传文件，日志报错

**解决方案**:
```bash
# 清理Docker缓存
docker system prune -a

# 清理日志文件
find backend/logs -name "*.log" -mtime +7 -delete

# 清理ChromaDB旧数据（谨慎操作）
```

#### 4. API调用失败

**症状**: 智谱AI API返回错误

**解决方案**:
- 检查API密钥是否正确
- 检查账户余额
- 检查网络连接
- 查看API限流状态

```bash
# 测试API连接
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4-flash","messages":[{"role":"user","content":"hello"}]}'
```

#### 5. 前端无法连接后端

**症状**: 前端显示网络错误

**解决方案**:
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查CORS配置
# 编辑backend/.env，确保ALLOWED_ORIGINS包含前端域名

# 检查网络连接
docker network inspect novel-rag-network
```

### 调试模式

启用详细日志：
```ini
# backend/.env
LOG_LEVEL=DEBUG
```

查看详细错误堆栈：
```bash
docker-compose logs -f backend | grep -A 10 "ERROR"
```

---

## 容量规划

### 存储需求

- **小说文件**: 约100MB/本 × 100本 = 10GB
- **ChromaDB索引**: 约200MB/本 × 100本 = 20GB
- **SQLite数据库**: 约10MB/本 × 100本 = 1GB
- **日志文件**: 约100MB/天 × 30天 = 3GB
- **总计**: ~35GB（推荐预留50GB）

### 性能基准

典型配置（4核CPU + 8GB内存）：
- **并发用户**: 50+
- **API响应时间**: <500ms（中位数）
- **LLM生成速度**: 2-5秒/次
- **上传速度**: 5-10MB/s
- **索引速度**: 1-2分钟/万字

---

## 安全检查清单

部署前检查：

- [ ] 已更改所有默认密码和密钥
- [ ] 已配置HTTPS/SSL
- [ ] 已设置CORS白名单
- [ ] 已配置防火墙规则
- [ ] 已启用日志记录
- [ ] 已配置自动备份
- [ ] 已设置监控告警
- [ ] 已测试灾难恢复流程
- [ ] 已更新所有依赖到最新稳定版
- [ ] 已进行安全漏洞扫描

---

**最后更新**: 2025-11-13  
**文档版本**: v1.0  
**维护者**: Operations Team

