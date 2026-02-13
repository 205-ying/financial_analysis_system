# 餐饮企业财务分析系统

前后端分离的餐饮财务分析平台，覆盖认证授权、门店管理、订单/费用管理、KPI 统计、报表导出、审计日志与数据导入。

## 技术栈

- 后端：FastAPI、SQLAlchemy 2.0（异步）、PostgreSQL、Alembic、JWT、RBAC
- 前端：Vue 3、TypeScript、Vite、Element Plus、Pinia、ECharts
- 质量保障：pytest、ruff、mypy、ESLint、Prettier、Vitest

## 目录概览

```text
financial_analysis_system/
├─ backend/                 # FastAPI 后端
├─ frontend/                # Vue3 前端
├─ docs/                    # 架构与开发文档
├─ qa_scripts/              # 检查/诊断/验证脚本
├─ scripts/                 # 一键启动脚本
├─ dev.bat                  # Windows 统一开发入口
└─ Makefile                 # Linux/Mac 统一开发入口
```

## 快速开始

### 1) 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 2) 首次安装

Windows：

```bash
dev.bat install
```

Linux/Mac：

```bash
make install
```

### 3) 配置后端环境变量

复制 `backend/.env.example` 为 `backend/.env`，至少配置：

```ini
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/financial_analysis
JWT_SECRET_KEY=your-secret-key
```

### 4) 初始化数据库与基础数据

```bash
cd backend
alembic upgrade head
python scripts/seed_data.py
```

### 5) 启动服务

Windows：

```bash
dev.bat dev-backend
dev.bat dev-frontend
```

Linux/Mac：

```bash
make dev-backend
make dev-frontend
```

- 后端接口：<http://localhost:8000>
- OpenAPI 文档：<http://localhost:8000/docs>
- 前端页面：<http://localhost:3000>

## 常用命令

```bash
dev.bat test-backend
dev.bat lint-backend
dev.bat check-backend
dev.bat migrate

make test-backend
make lint-backend
make check-backend
make migrate
```

## 默认账号

- admin / Admin@123（系统管理员）
- manager / Manager@123（门店经理）
- cashier / Cashier@123（收银员）

## 测试数据

```bash
cd backend
python scripts/generate_bulk_data.py
```

批量数据用于报表、导入、性能验证。清理命令：

```bash
python scripts/clean_bulk_data.py
```

## 文档导航

- `docs/development_guide.md`：开发流程、启动与排障
- `docs/backend_structure.md`：后端分层与关键模块
- `docs/frontend_structure.md`：前端路由、状态与模块组织
- `docs/dependency_guide.md`：后端依赖管理规范
- `docs/performance_baseline.md`：性能基线采集与对比
- `qa_scripts/README.md`：QA 脚本总览

## 质量检查建议

提交前建议至少执行：

```bash
dev.bat check-backend
cd frontend && npm run lint && npm run type-check
```

## 许可证

MIT
