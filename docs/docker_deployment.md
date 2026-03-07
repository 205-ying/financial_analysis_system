# Docker 部署说明

本文档提供两种 Docker 部署方式：

- 本地构建镜像后运行
- 直接拉取已发布镜像运行

## 部署内容

- PostgreSQL 15 数据库
- FastAPI 后端服务
- Vue 3 前端静态站点
- Nginx 前端托管与 API 反向代理

## 文件说明

- backend/Dockerfile
- backend/.dockerignore
- frontend/Dockerfile
- frontend/.dockerignore
- frontend/nginx.conf
- docker-compose.yml
- docker-compose.images.yml
- .env.docker.example
- .env.images.example

## 方式一：本地构建镜像后运行

## 使用步骤

### 1. 准备环境变量

在项目根目录执行：

```bash
cp .env.docker.example .env
```

Windows PowerShell 可执行：

```powershell
Copy-Item .env.docker.example .env
```

然后至少修改以下配置：

- POSTGRES_PASSWORD
- JWT_SECRET_KEY
- CORS_ORIGINS

### 2. 构建并启动

```bash
docker compose up -d --build
```

### 3. 查看服务状态

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. 访问地址

- 前端首页: http://localhost
- 后端接口: http://localhost:8000
- Swagger 文档: http://localhost:8000/docs

## 方式二：直接拉取镜像运行

这种方式适合目标电脑没有 Python、Node.js、PostgreSQL 开发环境，只安装了 Docker 的场景。

### 1. 准备镜像部署环境变量

在项目根目录执行：

```bash
cp .env.images.example .env
```

Windows PowerShell 可执行：

```powershell
Copy-Item .env.images.example .env
```

至少修改以下配置：

- BACKEND_IMAGE
- FRONTEND_IMAGE
- POSTGRES_PASSWORD
- JWT_SECRET_KEY
- CORS_ORIGINS

### 2. 登录镜像仓库

如果镜像仓库是私有的，需要先登录，例如 GHCR：

```bash
docker login ghcr.io
```

### 3. 拉取并启动

```bash
docker compose -f docker-compose.images.yml pull
docker compose -f docker-compose.images.yml up -d
```

### 4. 访问地址

- 前端首页: http://localhost
- 后端接口: http://localhost:8000
- Swagger 文档: http://localhost:8000/docs

## 自动发布镜像

仓库已增加 GitHub Actions 工作流 [publish-images.yml](../.github/workflows/publish-images.yml)，在以下场景会自动构建并推送镜像到 GHCR：

- push 到 main 分支
- 手动触发 workflow_dispatch

当前仓库默认镜像名：

- ghcr.io/205-ying/financial-analysis-system-backend:latest
- ghcr.io/205-ying/financial-analysis-system-frontend:latest

首次发布前的 GitHub 仓库设置检查，见 [github_ghcr_setup.md](github_ghcr_setup.md)。

## 启动行为

backend 服务启动时会自动执行：

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

这意味着数据库迁移会在容器启动时自动应用。

## 常用命令

停止服务：

```bash
docker compose down
```

镜像模式停止服务：

```bash
docker compose -f docker-compose.images.yml down
```

删除容器并清理匿名网络：

```bash
docker compose down --remove-orphans
```

删除数据库卷并完全重置：

```bash
docker compose down -v
```

仅重建前端：

```bash
docker compose build frontend
docker compose up -d frontend
```

仅重建后端：

```bash
docker compose build backend
docker compose up -d backend
```

## 说明

- 前端容器通过 Nginx 代理 /api/* 到 backend:8000。
- 前端构建默认使用 VITE_API_BASE_URL=/api/v1，因此浏览器访问时不会暴露内部容器地址。
- backend 的 Alembic 已调整为优先读取运行时 DATABASE_URL，避免容器里误连 alembic.ini 中的本地数据库地址。
- 如果需要接入外部 PostgreSQL，可以去掉 compose 中的 postgres 服务，并把 DATABASE_URL 指向外部实例。
- docker-compose.yml 适合本地从源码构建镜像。
- docker-compose.images.yml 适合目标机器只通过 docker pull 拉取镜像运行。