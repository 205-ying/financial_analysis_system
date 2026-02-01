# 后端架构说明

## 目录结构

```
backend/
├── app/                   # 应用源代码
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── core/             # 核心功能模块
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理（数据库、JWT、CORS等）
│   │   ├── database.py   # 数据库连接和会话管理
│   │   ├── security.py   # 安全功能（密码哈希、JWT）
│   │   ├── exceptions.py # 自定义异常类
│   │   ├── logging.py    # 日志配置
│   │   └── deps.py       # 依赖注入（旧版兼容）
│   ├── models/           # 数据库模型（SQLAlchemy 2.0）
│   │   ├── __init__.py
│   │   ├── base.py       # 基础模型类（BaseModel, SoftDelete等）
│   │   ├── user.py       # 用户、角色、权限模型
│   │   ├── user_store.py # 用户门店权限模型
│   │   ├── store.py      # 门店、产品分类、产品模型
│   │   ├── order.py      # 订单头、订单项模型
│   │   ├── expense.py    # 费用类型、费用记录模型
│   │   ├── kpi.py        # KPI每日数据模型
│   │   ├── audit_log.py  # 审计日志模型
│   │   └── import_job.py # 数据导入任务模型
│   ├── schemas/          # Pydantic 模型（API 输入输出验证）
│   │   ├── __init__.py
│   │   ├── common.py     # 通用响应模型（Response, PaginatedResponse）
│   │   ├── auth.py       # 认证相关Schema（登录、Token）
│   │   ├── store.py      # 门店相关Schema
│   │   ├── kpi.py        # KPI 请求/响应Schema（汇总、趋势、排名）⭐
│   │   ├── audit_log.py  # 审计日志Schema
│   │   ├── import_job.py # 数据导入Schema
│   │   └── report.py     # 报表查询Schema
│   ├── services/         # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── audit_log_service.py  # 审计日志服务
│   │   ├── kpi_calculator.py     # KPI计算引擎
│   │   ├── import_service.py     # 数据导入服务
│   │   ├── report_service.py     # 报表生成服务
│   │   ├── data_scope_service.py # 数据权限服务
│   │   └── audit.py              # 审计服务（旧版兼容）
│   ├── api/              # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py       # 依赖注入（数据库会话、当前用户、权限检查）
│   │   ├── router.py     # 总路由注册器
│   │   └── v1/           # API v1 版本
│   │       ├── __init__.py
│   │       ├── auth.py          # 认证接口（登录、刷新Token）
│   │       ├── health.py        # 健康检查接口
│   │       ├── stores.py        # 门店管理接口
│   │       ├── orders.py        # 订单管理接口
│   │       ├── expense_types.py # 费用类型接口
│   │       ├── expense_records.py # 费用记录接口
│   │       ├── kpi.py           # KPI数据接口
│   │       ├── audit.py         # 审计日志查询接口
│   │       ├── import_jobs.py   # 数据导入接口
│   │       └── reports.py       # 报表中心接口
├── alembic/              # 数据库迁移
│   ├── versions/         # 迁移版本文件
│   │   ├── 0001_initial.py          # 初始数据库结构
│   │   ├── 0002_audit_log.py        # 审计日志表
│   │   ├── 0003_import_jobs.py      # 数据导入表
│   │   └── 0004_user_store_permissions.py # 用户门店权限表
│   ├── env.py           # Alembic环境配置
│   ├── script.py.mako   # 迁移脚本模板
│   └── README           # Alembic说明
├── scripts/              # 维护和测试脚本
│   ├── maintenance/      # 数据库维护脚本
│   ├── testing/          # 测试和验证脚本
│   ├── test_data_import/ # 测试数据文件（CSV等）
│   ├── seed_data.py      # 初始化数据脚本
│   ├── export_api_docs.py     # 导出 OpenAPI 文档（JSON/Markdown）⭐
│   ├── generate_bulk_data.py  # 批量测试数据生成
│   ├── clean_bulk_data.py     # 清理测试数据
│   └── README.md         # 脚本使用文档
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── conftest.py       # pytest 配置和fixtures
│   ├── test_auth.py      # 认证测试
│   ├── test_kpi.py       # KPI测试
│   ├── test_permission.py # 权限测试
│   ├── test_data_scope.py # 数据权限测试
│   ├── test_import_jobs.py # 数据导入测试
│   ├── test_reports.py   # 报表功能测试
│   └── test_main.py      # 主应用测试
├── logs/                 # 日志文件目录
├── uploads/              # 上传文件目录
│   └── imports/          # 导入数据文件
├── venv/                 # Python虚拟环境
├── alembic.ini           # Alembic配置文件
├── dev.py                # 开发辅助脚本（测试、格式化、检查）
├── start_dev.bat         # Windows启动脚本
├── start_dev.ps1         # PowerShell启动脚本
├── requirements.txt      # Python生产依赖
├── requirements_dev.txt  # Python开发依赖
├── pyproject.toml        # 项目配置（ruff, mypy等）
├── pytest.ini            # pytest配置
├── .env.example          # 环境变量模板
└── .gitignore
```

## 架构原则

### 1. 分层架构（Clean Architecture）
```
API Layer (app/api/v1/)      # 路由处理，参数验证
    ↓ 
Service Layer (app/services/) # 业务逻辑，编排多个模型操作
    ↓
Model Layer (app/models/)    # 数据库模型，ORM操作
```

**关键规则**:
- API层仅负责路由和参数验证，不包含业务逻辑
- Service层包含所有业务逻辑，使用数据库会话进行CRUD操作
- Model层是SQLAlchemy模型，不包含业务逻辑

### 2. 异步优先
- 使用 SQLAlchemy 2.0 异步API（AsyncSession）
- 所有数据库操作使用 `async/await`
- 提高并发性能和资源利用率

### 3. 依赖注入
- 使用 FastAPI 的依赖注入系统
- 数据库会话通过 `Depends(get_db)` 注入
- 当前用户通过 `Depends(get_current_user)` 注入
- 权限检查通过 `check_permission()` 函数

### 4. 统一响应格式
所有API响应使用统一格式（`app/schemas/common.py`）:
```python
# 单条数据
Response[T](code=200, data={...}, message="操作成功")

# 分页数据
PaginatedResponse[List[T]](
    code=200,
    data=[...],
    total=100,
    page=1,
    page_size=20
)
```

### 5. 错误处理
使用自定义异常类（`app/core/exceptions.py`）:
- `ValidationException(400)` - 请求参数验证失败
- `AuthenticationException(401)` - 认证失败
- `AuthorizationException(403)` - 无权限
- `NotFoundException(404)` - 资源不存在
- `ConflictException(409)` - 资源冲突
- `BusinessException(422)` - 业务逻辑错误
- `DatabaseException(500)` - 数据库操作失败

## 核心模块说明

### 数据库模型基类（app/models/base.py）
所有模型继承自基类:
- `BaseModel`: ID + 时间戳 (created_at, updated_at)
- `BaseModelWithSoftDelete`: + 软删除 (is_deleted, deleted_at)
- `BaseModelWithUserTracking`: + 用户追踪 (created_by_id, updated_by_id)
- `FullBaseModel`: 包含所有功能

### 认证与权限
- **JWT认证**: 使用 python-jose 生成和验证token
- **RBAC权限**: 基于角色的访问控制
- **权限码格式**: `{resource}:{action}` (如 `store:create`, `kpi:view`)
- **权限检查**: 在API层使用 `await check_permission(user, "resource:action", db)`

### 审计日志
自动记录所有关键操作（`app/services/audit_log_service.py`）:
- 创建/更新/删除资源
- 登录/登出
- 权限变更
- 敏感配置修改

记录内容包括：用户、操作类型、资源类型、资源ID、详细信息、IP地址、时间戳

### KPI计算引擎
`app/services/kpi_calculator.py` 负责:
- 每日KPI数据采集
- 多维度统计分析（按门店、时间、类型）
- 趋势分析（同比、环比）
- 使用SQL聚合而非Python循环，提高性能

### 数据导入服务
`app/services/import_service.py` 负责:
- 批量数据导入（门店、订单、费用）
- CSV文件解析和验证
- 异步任务处理
- 错误记录和报告生成
- 支持增量和全量导入

### 报表生成服务
`app/services/report_service.py` 负责:
- 日汇总报表（按日期维度）
- 月汇总报表（按月份维度）
- 门店绩效报表（排名、对比）
- 费用明细报表（占比分析）
- Excel导出功能

### 数据权限服务
`app/services/data_scope_service.py` 负责:
- 门店级数据权限控制
- 用户可见门店过滤
- 结合RBAC的细粒度权限
- 多租户数据隔离

## API路由结构

所有API端点在 `app/api/router.py` 统一注册，挂载到 `/api/v1` 前缀:

- `/api/v1/auth/*` - 认证和授权
  - POST `/login` - 用户登录
  - POST `/refresh` - 刷新Token
- `/api/v1/health` - 健康检查
- `/api/v1/stores/*` - 门店管理
- `/api/v1/orders/*` - 订单管理
- `/api/v1/expense-types/*` - 费用科目管理
- `/api/v1/expense-records/*` - 费用记录管理
- `/api/v1/kpi/*` - KPI数据查询和导出
- `/api/v1/audit/*` - 审计日志查询
- `/api/v1/import-jobs/*` - 数据导入中心
  - POST `/create` - 创建导入任务
  - POST `/{job_id}/run` - 执行导入
  - GET `/` - 导入任务列表
  - GET `/{job_id}` - 任务详情
  - GET `/{job_id}/errors` - 错误记录
  - GET `/{job_id}/error-report` - 错误报告导出
- `/api/v1/reports/*` - 报表中心
  - GET `/daily-summary` - 日汇总报表
  - GET `/monthly-summary` - 月汇总报表
  - GET `/store-performance` - 门店绩效报表
  - GET `/expense-breakdown` - 费用明细报表
  - GET `/{report_type}/export` - 报表Excel导出

API文档自动生成：http://localhost:8000/docs （Swagger UI）

## 数据库迁移

使用 Alembic 管理数据库版本:

```bash
# 查看当前版本
alembic current

# 应用迁移
alembic upgrade head

# 创建新迁移（自动检测模型变化）
alembic revision --autogenerate -m "描述变更"

# 回滚迁移
alembic downgrade -1              # 回滚一个版本
alembic downgrade <revision_id>   # 回滚到指定版本
```

迁移脚本位置: `alembic/versions/`

## 开发辅助工具

### dev.py 脚本
```bash
python dev.py start      # 启动开发服务器
python dev.py test       # 运行测试
python dev.py test-cov   # 测试+覆盖率
python dev.py lint       # 代码检查
python dev.py format     # 格式化代码
python dev.py type-check # 类型检查
python dev.py all        # 运行所有检查
```

### 数据初始化
```bash
# 初始化基础数据（用户、角色、权限、示例数据）
python scripts/seed_data.py

# 生成批量测试数据
python scripts/generate_bulk_data.py

# 清理测试数据
python scripts/clean_bulk_data.py
```

## 测试

测试框架: pytest + pytest-asyncio + pytest-cov

```bash
# 运行所有测试
pytest

# 测试覆盖率
pytest --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_auth.py
```

测试fixtures定义在 `tests/conftest.py`:
- `db` - 测试数据库会话
- `client` - 测试HTTP客户端
- `test_user` - 测试用户fixture
- `auth_headers` - 认证头fixture

## 相关文档

- [开发指南](development_guide.md) - 项目启动和开发流程
- [前端架构](frontend_structure.md) - 前端项目结构
- [项目历程](project_history.md) - 各阶段开发总结
- [命名规范](naming_conventions.md) - 代码和文件命名约定

---

*最后更新: 2026年1月25日*
