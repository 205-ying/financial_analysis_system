# Backend Structure

## Directory Layout

```
backend/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── config/            # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py    # 应用配置
│   │   └── database.py    # 数据库配置
│   ├── core/              # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py    # JWT/认证
│   │   ├── deps.py        # 依赖注入
│   │   ├── exceptions.py  # 异常处理
│   │   └── middleware.py  # 中间件
│   ├── models/            # 数据库模型（SQLAlchemy）
│   │   ├── __init__.py
│   │   ├── base.py        # 基础模型
│   │   ├── user.py        # 用户模型
│   │   ├── role.py        # 角色模型
│   │   ├── permission.py  # 权限模型
│   │   ├── store.py       # 门店模型
│   │   ├── order.py       # 订单模型
│   │   ├── expense.py     # 费用模型
│   │   ├── kpi.py         # KPI 模型
│   │   └── audit_log.py   # 审计日志模型
│   ├── schemas/           # Pydantic 模型（API 输入输出）
│   │   ├── __init__.py
│   │   ├── common.py      # 通用响应模型
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── store.py
│   │   ├── order.py
│   │   ├── expense.py
│   │   └── kpi.py
│   ├── services/          # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth.py        # 认证服务
│   │   ├── user.py        # 用户服务
│   │   ├── rbac.py        # 权限服务
│   │   ├── store.py       # 门店服务
│   │   ├── order.py       # 订单服务
│   │   ├── expense.py     # 费用服务
│   │   ├── kpi.py         # KPI 服务
│   │   └── audit_log.py   # 审计日志服务
│   ├── repositories/      # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py        # 基础仓储
│   │   ├── user.py
│   │   ├── store.py
│   │   ├── order.py
│   │   ├── expense.py
│   │   └── kpi.py
│   ├── api/               # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/            # API v1 版本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py    # 认证接口
│   │   │   ├── users.py   # 用户管理接口
│   │   │   ├── stores.py  # 门店管理接口
│   │   │   ├── orders.py  # 订单管理接口
│   │   │   ├── expenses.py # 费用管理接口
│   │   │   ├── kpi.py     # KPI 接口
│   │   │   └── admin.py   # 管理接口（权限、审计等）
│   │   └── deps.py        # API 依赖
│   └── utils/             # 工具函数
│       ├── __init__.py
│       ├── logger.py      # 日志工具
│       ├── security.py    # 安全工具
│       ├── pagination.py  # 分页工具
│       └── validators.py  # 验证工具
├── alembic/               # 数据库迁移
│   ├── versions/          # 迁移版本文件
│   ├── env.py
│   └── alembic.ini
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── conftest.py        # pytest 配置
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_api/          # API 测试
├── requirements.txt       # Python 依赖
├── requirements-dev.txt   # 开发环境依赖
├── .env.example          # 环境变量模板
├── .gitignore
├── pyproject.toml        # 项目配置（linting, formatting）
└── pytest.ini           # pytest 配置
```

## Architecture Principles

1. **Clean Architecture**: 分层设计，依赖倒置
2. **Domain Driven Design**: 按业务域组织代码
3. **SOLID Principles**: 遵循面向对象设计原则
4. **Type Safety**: 严格的类型检查
5. **Test Driven**: 完整的测试覆盖