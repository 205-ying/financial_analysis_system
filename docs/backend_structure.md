# 后端架构说明

## 1. 技术栈

- FastAPI
- SQLAlchemy 2.0 异步 ORM（AsyncSession）
- PostgreSQL + Alembic
- Pydantic v2
- JWT + RBAC 权限模型

## 2. 目录结构

```text
backend/
├─ app/
│  ├─ api/                 # 路由层（参数校验、权限依赖、响应封装）
│  │  ├─ deps.py
│  │  ├─ router.py
│  │  └─ v1/
│  ├─ core/                # 配置、数据库、异常、安全
│  ├─ models/              # SQLAlchemy 模型
│  ├─ schemas/             # 请求/响应模型
│  └─ services/            # 业务逻辑层
├─ alembic/                # 迁移脚本
├─ tests/                  # pytest 测试
├─ scripts/                # 数据与维护脚本
├─ dev.py                  # 开发命令入口
└─ pyproject.toml          # ruff/mypy/pytest 配置
```

## 3. 分层约束

依赖方向：API → Service → Model

- API 层：只做参数验证、鉴权依赖、调用服务
- Service 层：承载业务逻辑与事务编排
- Model 层：实体与关系映射，不放业务流程代码

## 4. 关键设计

### 异步优先

- 所有数据库访问使用 `AsyncSession`
- 查询统一采用 `await db.execute(select(...))`
- 禁止在新代码中使用同步 ORM 查询写法

### 统一异常

- 使用 `app/core/exceptions.py` 中自定义异常
- 由全局异常处理器转换为统一错误响应结构

### 统一响应

- 普通响应：`Response[T]`
- 分页响应：`PaginatedResponse[T]`

### 权限与数据权限分离

- RBAC 权限决定“能否操作某功能”
- user-store 数据权限决定“可访问哪些门店数据”

## 5. 请求处理链路

1. 路由接收请求并解析参数
2. 依赖注入生成 DB 会话与当前用户
3. 权限校验通过后调用 Service
4. Service 执行数据库操作并返回 DTO/模型
5. API 层包装统一响应返回客户端

## 6. 核心模块

- `services/kpi_calculator.py`：KPI 聚合计算
- `services/report_service.py`：报表查询与导出
- `services/import_service.py`：导入任务与错误报告
- `services/data_scope_service.py`：门店级数据权限
- `services/audit_log_service.py`：审计日志记录

## 7. 迁移与测试

### Alembic

```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "描述"
```

### pytest

```bash
cd backend
python dev.py test
python dev.py test-cov
```

## 8. 开发注意事项

- 新接口遵循“先 Schema、再 Service、后 API 注册”的顺序
- 大数据统计优先 SQL 聚合，避免 Python 层全量循环
- 查询关联数据使用 `selectinload` 或 `joinedload` 避免 N+1
- 涉及删除的核心业务表优先软删除策略
