# 开发与运行指南

本文档合并本地开发、依赖、运行时文件、迁移、测试和排障说明。根目录 `README.md` 保留快速开始，这里作为日常开发的完整入口。

## 1. 环境准备

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

后端环境变量：

1. 复制 `services/api/.env.example` 到 `services/api/.env`
2. 配置 `DATABASE_URL` 与 `JWT_SECRET_KEY`

前端默认使用 `apps/web/.env.development`，本地后端地址默认代理到 `http://localhost:8000`。

## 2. 统一命令入口

Windows：

```bat
dev.bat help
dev.bat install
dev.bat dev-backend
dev.bat dev-frontend
dev.bat test-backend
dev.bat check-backend
dev.bat migrate
```

Linux/Mac/CI：

```bash
make help
make install
make dev-backend
make dev-frontend
make test-backend
make check-backend
make migrate
```

跨端一键启动脚本：

```bat
tooling\dev\start.bat
```

```bash
bash tooling/dev/start.sh
```

## 3. 首次启动流程

```bash
make install

cd services/api
alembic upgrade head
cd ../..
python tooling/api/seed_data.py
```

启动后端：

```bash
cd services/api
python dev.py start
```

启动前端：

```bash
cd apps/web
npm run dev
```

访问地址：

- 前端：<http://localhost:3000>
- 后端：<http://localhost:8000>
- OpenAPI：<http://localhost:8000/docs>

## 4. 后端依赖

依赖文件：

- `services/api/requirements.txt`：运行时依赖
- `services/api/requirements_dev.txt`：开发依赖

安装开发依赖：

```bash
cd services/api
pip install -r requirements_dev.txt
```

主要分组：

- Web 与 API：FastAPI、Uvicorn、Pydantic、pydantic-settings
- 数据库：SQLAlchemy、Alembic、asyncpg、psycopg2-binary
- 安全认证：python-jose、passlib、bcrypt
- 数据处理：pandas、openpyxl
- 测试与质量：pytest、pytest-asyncio、pytest-cov、ruff、mypy

## 5. 前端命令

```bash
cd apps/web
npm run dev
npm run build
npm run lint
npm run format
npm run type-check
npm run test
npm run openapi:gen
npm run openapi:check
```

## 6. 运行时文件

运行时生成文件统一放在项目根目录 `runtime/`，实际内容不提交到 Git：

```text
runtime/
├─ logs/
│  └─ api/                 # FastAPI 日志与轮转归档
│     └─ test-runs/        # 本地测试、检查和诊断日志
├─ uploads/
│  └─ imports/             # 数据导入上传文件与错误报告
├─ test-results/
│  └─ api/                 # 后端覆盖率报告和测试产物
└─ tmp/                    # 本地临时文件
```

后端环境变量：

```ini
RUNTIME_DIR=runtime
UPLOAD_DIR=runtime/uploads/imports
LOG_FILE=runtime/logs/api/app.log
```

相对路径会解析到项目根目录。生产环境可配置为绝对路径或挂载卷。旧配置 `LOG_FILE=logs/app.log` 会兼容映射到 `runtime/logs/api/app.log`。

## 7. 数据与验证脚本

```bash
python tooling/api/seed_data.py
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
python tooling/qa/verifications/system/verify_system_integrity.py
python tooling/qa/verifications/backend/verify_backend_run_all.py
```

更多 QA 脚本说明见 `docs/qa.md`。

## 8. 数据库迁移

```bash
cd services/api
alembic current
alembic upgrade head
alembic revision --autogenerate -m "描述变更"
alembic downgrade -1
```

约定：

- 先改模型，再生成迁移，再人工审查迁移内容。
- 生产环境迁移前先做数据库备份。
- 不要手写会重复创建既有表的迁移。

## 9. OpenAPI 类型同步

后端 API 变更后：

```bash
cd apps/web
npm run openapi:gen
npm run openapi:check
```

自动导出的 API 阅读文档位于 `docs/api/backend-api.md`。

## 10. 常见问题

### 启动后数据库连接失败

- 检查 `services/api/.env` 的 `DATABASE_URL`
- 确认 PostgreSQL 服务已启动
- 确认数据库已创建且用户权限正确

### 登录后接口 401

- 检查前端本地存储 token 是否存在
- 检查后端 `JWT_SECRET_KEY` 是否变更
- 检查系统时间是否异常

### 路由权限异常

- 确认用户角色和权限已初始化
- 确认前端动态路由已根据权限重新生成
- 确认后端 `check_permission` 使用的是正确权限码

### 安装依赖失败

```bash
python -m pip install --upgrade pip
pip install -r requirements_dev.txt
```

如果仍有版本冲突，确认是否混用了全局 Python 与虚拟环境，再重建虚拟环境。

## 11. 提交前检查

```bash
dev.bat check-backend
cd apps/web
npm run lint
npm run type-check
npm run build
```

Linux/Mac/CI 可使用：

```bash
make check
```
