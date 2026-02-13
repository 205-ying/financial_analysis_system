# 开发指南

本文档提供本项目在本地开发、调试、测试和日常排障的推荐流程。

## 1. 环境准备

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

后端环境变量：

1. 复制 `backend/.env.example` 到 `backend/.env`
2. 至少配置 `DATABASE_URL` 与 `JWT_SECRET_KEY`

## 2. 统一命令入口

### Windows（推荐）

```bash
dev.bat help
dev.bat install
dev.bat dev-backend
dev.bat dev-frontend
dev.bat test-backend
dev.bat check-backend
dev.bat migrate
```

### Linux/Mac/CI

```bash
make help
make install
make dev-backend
make dev-frontend
make test-backend
make check-backend
make migrate
```

## 3. 首次启动流程

```bash
# 安装依赖
dev.bat install

# 初始化数据库
cd backend
alembic upgrade head
python scripts/seed_data.py

# 启动后端
python dev.py start
```

前端另开终端：

```bash
cd frontend
npm run dev
```

## 4. 后端开发命令（backend/dev.py）

```bash
python dev.py start
python dev.py test
python dev.py test-cov
python dev.py lint
python dev.py format
python dev.py format-check
python dev.py type-check
python dev.py all
python dev.py migrate
```

## 5. 前端开发命令（frontend/package.json）

```bash
npm run dev
npm run build
npm run lint
npm run format
npm run type-check
npm run test
npm run openapi:gen
npm run openapi:check
```

## 6. 数据与验证脚本

### 初始化/清理测试数据

```bash
cd backend
python scripts/seed_data.py
python scripts/generate_bulk_data.py
python scripts/clean_bulk_data.py
```

### QA 脚本中心

```bash
python qa_scripts/verifications/system/verify_system_integrity.py
python qa_scripts/verifications/backend/verify_backend_run_all.py
```

## 7. 数据库迁移流程

```bash
cd backend
alembic current
alembic upgrade head
alembic revision --autogenerate -m "描述变更"
alembic downgrade -1
```

约定：

- 先改模型，再生成迁移，再人工审查迁移内容
- 生产环境迁移前先做数据库备份

## 8. 常见问题

### 1) 启动后报数据库连接失败

- 检查 `backend/.env` 的 `DATABASE_URL`
- 确认 PostgreSQL 服务已启动
- 确认数据库已创建且用户权限正确

### 2) 登录后接口 401

- 检查前端本地存储 token 是否存在
- 检查后端 `JWT_SECRET_KEY` 是否变更
- 检查系统时间是否异常（影响 token 过期校验）

### 3) 路由权限异常

- 确认用户角色和权限已初始化
- 确认前端动态路由已根据权限重新生成
- 确认后端 `check_permission` 使用的是正确权限码

## 9. 提交前检查清单

- 后端：`python dev.py all`
- 前端：`npm run lint` + `npm run type-check`
- API 变更后：`npm run openapi:gen` 并检查类型更新
- 文档变更后：更新相关 README 与使用示例
