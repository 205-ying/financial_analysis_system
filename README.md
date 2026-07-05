# 餐饮企业财务分析系统

前后端分离的餐饮财务分析平台，覆盖认证授权、门店管理、订单/费用管理、KPI 统计、预算、CVP、本量利分析、产品分析、报表导出、审计日志与数据导入。

## 技术栈

- 后端：FastAPI、SQLAlchemy 2.0 异步 ORM、PostgreSQL、Alembic、JWT、RBAC
- 前端：Vue 3、TypeScript、Vite、Element Plus、Pinia、ECharts
- 质量保障：pytest、ruff、mypy、ESLint、Prettier、Vitest

## 目录概览

```text
financial_analysis_system/
├─ services/api/            # FastAPI 后端
├─ apps/web/                # Vue 3 前端
├─ docs/                    # 项目文档中心
├─ tooling/api/             # 后端数据、维护与归档工具
├─ tooling/qa/              # 检查、诊断、冒烟与验收脚本
├─ tooling/dev/             # 跨端启动脚本
├─ runtime/                 # 本地日志、上传和临时文件边界
├─ dev.bat                  # Windows 常用命令入口
└─ Makefile                 # Linux/Mac/CI 常用命令入口
```

详细目录规则见 `docs/architecture/project-structure.md`。

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 2. 安装依赖

Windows：

```bat
dev.bat install
```

Linux/Mac/CI：

```bash
make install
```

也可以分别安装：

```bash
cd services/api
pip install -r requirements_dev.txt

cd ../../apps/web
npm install
```

### 3. 配置环境变量

复制后端环境变量示例：

```bat
copy services\api\.env.example services\api\.env
```

Linux/Mac：

```bash
cp services/api/.env.example services/api/.env
```

至少配置：

```ini
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/financial_analysis
JWT_SECRET_KEY=your-secret-key
```

前端默认通过 `apps/web/.env.development` 访问后端 API。

### 4. 初始化数据库和基础数据

```bash
cd services/api
alembic upgrade head
cd ../..
python tooling/api/seed_data.py
```

### 5. 启动服务

分别启动后端和前端：

```bat
dev.bat dev-backend
dev.bat dev-frontend
```

或使用跨端启动脚本：

```bat
tooling\dev\start.bat
```

Linux/Mac：

```bash
make dev-backend
make dev-frontend
```

服务地址：

- 前端页面：<http://localhost:3000>
- 后端接口：<http://localhost:8000>
- OpenAPI 文档：<http://localhost:8000/docs>

## 常用命令

```bash
make check
make test-backend
make check-frontend
make migrate
```

Windows 可使用同名 `dev.bat` 命令：

```bat
dev.bat check
dev.bat test-backend
dev.bat check-frontend
dev.bat migrate
```

## 默认账号

- admin / Admin@123（系统管理员）
- manager / Manager@123（门店经理）
- cashier / Cashier@123（收银员）

## 测试数据

```bash
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
```

批量数据用于报表、导入、性能验证，建议只在开发或测试数据库中使用。

## 文档导航

- `docs/README.md`：文档中心入口
- `docs/architecture/project-structure.md`：项目结构与前后端架构
- `docs/development.md`：本地开发、依赖、运行时文件、启动、测试与排障
- `docs/api/backend-api.md`：后端 API 导出文档
- `docs/qa.md`：QA 脚本、验证入口和性能基线采集说明

## 提交前建议

```bash
dev.bat check-backend
cd apps/web
npm run lint
npm run type-check
```

API 变更后同步执行：

```bash
cd apps/web
npm run openapi:gen
npm run openapi:check
```

## 许可证

MIT
