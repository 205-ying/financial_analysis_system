# Copilot Instructions - 餐饮企业财务分析系统

> **给AI代理的提示**: 本文档通过"快速导航"和"为什么"解释，帮助你快速理解这个项目的设计哲学。这不仅是技术选择，更是为了让代码易于维护、扩展和测试。当你看到某个设计决策时，理解"为什么"会帮助你做出正确的实现选择。

## 快速导航 - 关键文件位置

| 功能 | 文件位置 | 说明 |
|-----|-------|------|
| **API路由注册** | [services/api/app/api/router.py](services/api/app/api/router.py) | 所有路由端点的单一入口 |
| **依赖注入** | [services/api/app/api/deps.py](services/api/app/api/deps.py) | `get_db`, `get_current_user`, `check_permission` |
| **异常处理** | [services/api/app/core/exceptions.py](services/api/app/core/exceptions.py) | 自定义异常类和全局处理器 |
| **数据库配置** | [services/api/app/core/database.py](services/api/app/core/database.py) | AsyncSession、引擎配置 |
| **模型基类** | [services/api/app/models/base.py](services/api/app/models/base.py) | BaseModel、Mixin组件 |
| **路由守卫** | [apps/web/src/router/guard.ts](apps/web/src/router/guard.ts) | 前端权限检查和登录跳转 |
| **状态管理** | [apps/web/src/stores/](apps/web/src/stores/) | Pinia Store (authStore, permissionStore等) |
| **权限指令** | [apps/web/src/directives/permission.ts](apps/web/src/directives/permission.ts) | v-permission, v-permission-all 指令 |
| **开发脚本** | [services/api/dev.py](services/api/dev.py) | test, lint, format, type-check 等命令 |
| **数据库迁移** | [services/api/alembic/versions/](services/api/alembic/versions/) | Alembic 迁移脚本 |

## 项目架构

这是一个**前后端分离**的餐饮企业财务分析系统:
- **后端**: FastAPI + SQLAlchemy 2.0 (async/await) + PostgreSQL 15+ + JWT认证 + RBAC权限
- **前端**: Vue3 + TypeScript + Vite + Element Plus + ECharts + Pinia + vue-router
- **环境**: 支持 Windows/Mac/Linux，使用 `dev.bat`/Makefile 脚本和统一的 Python CLI (`services/api/dev.py`)
- **测试**: pytest + pytest-asyncio 用于后端单元/集成测试
- **代码质量**: ruff (代码检查+格式化) + mypy (类型检查)

## 核心架构原则

### 后端分层架构
严格遵循 **Clean Architecture** 分层设计，依赖方向：API → Service → Model

```mermaid
graph TD
    A[客户端请求] --> B[API Layer<br/>路由处理、参数验证]
    B --> C[Service Layer<br/>业务逻辑、事务管理]
    C --> D[Model Layer<br/>数据库模型、ORM操作]
    D --> E[(PostgreSQL<br/>数据库)]
    
    F[依赖注入] -.-> B
    F -.-> C
    G[异常处理器] -.-> B
    G -.-> C
    
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#f0f0f0
    style E fill:#e8f5e9
```

**关键规则**:
- API层仅负责路由和参数验证，不包含业务逻辑
- Service层包含所有业务逻辑，使用数据库会话进行CRUD操作
- Model层是SQLAlchemy模型，不包含业务逻辑

**为什么这样设计？**
1. **关注点分离** - 每层职责单一，便于理解和维护。修改业务逻辑时无需触及API路由定义
2. **易于测试** - Service层可独立测试，不需要模拟HTTP请求。API层只需测试参数验证和路由
3. **代码复用** - Service层的业务逻辑可被多个API端点调用，或由定时任务/导入任务复用
4. **可扩展性** - 添加新端点时无需重写业务逻辑，只需新增API层和Service调用
5. **易于重构** - 业务逻辑集中在Service，大规模重构时影响范围小

### 数据库模型基类系统
所有模型继承自 [services/api/app/models/base.py](services/api/app/models/base.py) 的基类:
- `BaseModel`: ID + 时间戳 (created_at, updated_at)
- `BaseModelWithSoftDelete`: + 软删除 (is_deleted, deleted_at)
- `BaseModelWithUserTracking`: + 用户追踪 (created_by_id, updated_by_id)
- `FullBaseModel`: 包含所有功能

**示例**: 大多数业务表使用 `BaseModel`，核心数据表如Order使用 `BaseModelWithSoftDelete`

**为什么使用 Mixin 基类而非直接继承？**
1. **灵活组合** - 不同表可选择需要的功能：有些表只需时间戳，有些需要软删除+用户追踪
2. **DRY原则** - 避免在每个模型中重复定义相同的字段和逻辑
3. **一致性** - 所有表的 ID、时间戳、软删除逻辑保持一致，便于查询和业务逻辑处理
4. **审计追踪** - 通过 `created_by_id/updated_by_id` 记录数据变更人，支持操作审计

**为什么某些表使用软删除而不是硬删除？**
- **数据安全** - 误删操作可恢复，财务数据不丢失
- **业务需求** - 订单一旦创建就不应物理删除（可能涉及财务对账）
- **历史追踪** - 保留删除时间和删除者信息，便于审计
- **级联影响** - 避免删除订单导致关联数据（明细、费用）的级联删除问题

### 异步数据库操作
**必须**使用 SQLAlchemy 2.0 异步风格:
```python
# ✅ 正确
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_store(db: AsyncSession, store_id: int):
    result = await db.execute(select(Store).where(Store.id == store_id))
    return result.scalar_one_or_none()

# ❌ 错误 - 不要使用同步查询
store = db.query(Store).filter(Store.id == store_id).first()
```

**为什么使用异步而不是同步？**

| 对比维度 | 异步 (AsyncSession) | 同步 (Session) | 性能差异 |
|---------|-------------------|---------------|--------|
| **并发处理** | 1个线程处理1000请求 | 需要1000个线程 | 📈 内存节省99.9% |
| **响应时间** | IO等待时处理其他请求 | IO等待时线程阻塞 | 📈 吞吐量提升10-100倍 |
| **资源占用** | 事件循环，低开销 | 线程池，高开销 | 📈 CPU使用降低80% |
| **框架兼容** | FastAPI原生支持 | 需要线程池适配 | ⚠️ 混用会性能下降 |
| **错误检测** | Session关闭后强制报错 | 惰性加载可能延迟报错 | ✅ 提前发现问题 |

**核心原因**:
1. **高并发** - 异步IO在网络IO等待时不阻塞线程，同时处理更多请求
2. **资源效率** - 1000并发只需1线程 vs 同步需1000线程，内存节省99.9%
3. **框架一致性** - FastAPI本身异步，混用同步会反向性能更差
4. **错误避免** - Session关闭后无法访问关联数据，强制规范化查询

## 开发工作流

### 环境配置
**必须先配置**: 复制 `services/api/.env.example` → `services/api/.env`，设置数据库连接:
```ini
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/financial_analysis
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### 启动项目 (Windows环境)
```bash
# 方法1: 使用统一脚本 (推荐)
dev.bat dev-backend      # 启动后端 (http://localhost:8000)
dev.bat dev-frontend     # 启动前端 (http://localhost:3000)

# 方法2: 使用Python CLI脚本
cd services/api
python dev.py start      # 或 python dev.py --help 查看全部命令

# 方法3: 直接使用 uvicorn (需先配置虚拟环境)
cd services/api
.\venv\Scripts\Activate.ps1   # Windows PowerShell
source venv/bin/activate      # Unix/Mac
uvicorn app.main:app --reload

# 启动前端
cd apps/web
npm run dev              # Vite 开发服务器在 http://localhost:3000
```

**首次启动必须**:
1. 复制 `services/api/.env.example` → `services/api/.env`，配置数据库连接
2. 运行数据库迁移: `alembic upgrade head`
3. 初始化数据: `python tooling/api/seed_data.py` (创建 default users)

**后端命令详解**:
```bash
# 通过 dev.py 脚本运行
python dev.py test            # 运行测试
python dev.py test-cov        # 测试 + 覆盖率报告
python dev.py lint            # 代码检查 (ruff)
python dev.py format          # 格式化代码
python dev.py format-check    # 仅检查格式（不修改）
python dev.py type-check      # 类型检查 (mypy)
python dev.py all             # 运行所有检查

# 或通过 dev.bat (同时支持前后端)
dev.bat test-backend          # 运行后端测试
dev.bat check-backend         # 运行所有检查
```

### 初始化数据
首次部署或重置数据库后在项目根目录运行:
```bash
python tooling/api/seed_data.py
```
自动创建:
- **默认用户**: 
  - admin/Admin@123 (系统管理员，所有权限)
  - manager/Manager@123 (门店经理，运营权限)
  - cashier/Cashier@123 (收银员，基本权限)
- **权限**: 28+ 个细粒度权限 (user:view, store:create, kpi:export等)
- **角色**: 3个预定义角色
- **示例数据**: 门店、产品分类、产品、费用类型

**批量测试数据生成**: `python tooling/api/generate_bulk_data.py`
- **用途**: 生成大量真实、详细的中文测试数据，用于性能测试、功能验证和演示
- **数据量**: 50,000+订单，72个真实菜品，7,000+费用记录，5,400+ KPI记录
- **时间范围**: 完整365天（一整年数据）
- **特点**: 真实的中餐菜品（川菜、粤菜、家常菜等），真实的时间分布（午晚餐高峰期），详细的供应商和费用描述
- **测试账号**: cashier001~018 / manager001~009 / accountant001~003，密码：Test@123
- **详细说明**: 参见 [docs/qa/scripts.md](docs/qa/scripts.md)
- **清理数据**: `python tooling/api/clean_bulk_data.py` (保留 admin 和基础配置)

### 数据库迁移工作流 (Alembic)
```bash
cd services/api

# 1. 应用已有迁移到数据库
alembic upgrade head              # 应用所有待处理迁移

# 2. 修改模型后创建新迁移（Alembic自动检测变化）
alembic revision --autogenerate -m "描述变更内容"

# 3. 查看迁移历史和状态
alembic history                   # 查看所有迁移版本
alembic current                   # 查看当前数据库版本

# 4. 回滚迁移
alembic downgrade -1              # 回滚一个版本
alembic downgrade base            # 回滚到初始状态
```

**迁移脚本位置**: `services/api/alembic/versions/` (已有4个历史迁移)
- 每个迁移文件包含 `upgrade()` 和 `downgrade()` 函数
- 自动生成的迁移需要审查，特别是删除列、修改类型等危险操作
- 文件命名格式: `YYYYMMDD_HHMM_{revision_id}_{description}.py`

**关键约定**:
- 所有迁移必须在服务器停止状态下执行
- 生产环境迁移前必须备份数据库: `python scripts/maintenance/backup_database.py`

### 测试和代码质量
```bash
cd services/api
python dev.py test        # 运行所有测试 (pytest)
python dev.py test-cov    # 测试 + 覆盖率报告
python dev.py lint        # Ruff代码检查
python dev.py format      # 格式化代码 (Ruff)
python dev.py type-check  # MyPy类型检查
python dev.py all         # 运行所有检查 (lint + format + type + test)

# 或使用统一脚本
dev.bat test-backend
dev.bat check-backend     # 运行所有检查
```

**测试框架**: pytest + pytest-asyncio + pytest-cov
- 测试文件在 [services/api/tests/](services/api/tests/)
- [conftest.py](services/api/tests/conftest.py) 提供数据库fixtures和测试客户端
- 使用 `@pytest.mark.asyncio` 标记异步测试

**为什么选择 pytest？**
1. **异步支持** - pytest-asyncio 原生支持异步测试，无需复杂配置
2. **Fixture系统** - 灵活的依赖注入，相比unittest的setUp/tearDown更清晰
3. **插件生态** - pytest-cov、pytest-mock等丰富的插件支持
4. **参数化测试** - @pytest.mark.parametrize 支持数据驱动测试
5. **测试发现** - 自动发现test_*.py和*_test.py文件，无需配置


## 关键约定

### 后端命名规范
- **文件名**: snake_case (user_service.py, order_header.py)
- **类名**: PascalCase (OrderHeader, KpiCalculator)
- **函数/变量**: snake_case (get_current_user, total_amount)
- **数据库表名**: snake_case + 复数 (users, order_headers, kpi_daily_stores)
- **API路由**: kebab-case (/api/v1/expense-records)
- **模型字段**: snake_case with 中文注释 (created_by_id = Column(..., comment="创建者ID"))

### 前端命名规范
- **组件文件**: PascalCase (StoreListView.vue, FilterBar.vue)
- **函数/变量**: camelCase (getCurrentUser, totalAmount)
- **类型定义**: PascalCase (UserInfo, StoreDetail)
- **Store模块**: camelCase (useAuthStore, useStoreStore)
- **API文件**: 业务域+Api (storeApi.ts, kpiApi.ts)

### API响应格式
所有API响应使用统一格式 ([app/schemas/common.py](services/api/app/schemas/common.py)):
```python
# 单条数据
Response[UserSchema](code=200, data={...}, message="操作成功")

# 分页数据
PaginatedResponse[List[StoreSchema]](
    code=200,
    data=[...],
    total=100,
    page=1,
    page_size=20
)

# 错误响应 - 由 app/core/exceptions.py 中的全局异常处理器自动生成
{
    "code": 400,
    "message": "数据验证失败",
    "detail": "额外的错误信息",
    "timestamp": "2024-01-01T00:00:00"
}
```

### API路由结构
所有API端点在 [app/api/router.py](services/api/app/api/router.py) 统一注册，挂载到 `/api/v1` 前缀:
- `/api/v1/auth/*` - 认证和授权 (login, refresh)
- `/api/v1/stores/*` - 门店管理
- `/api/v1/user-stores/*` - 用户门店权限管理（数据权限）
- `/api/v1/orders/*` - 订单管理
- `/api/v1/expense-types/*` - 费用科目管理
- `/api/v1/expense-records/*` - 费用记录管理
- `/api/v1/kpi/*` - KPI数据查询和导出
- `/api/v1/reports/*` - 报表中心（日汇总、月汇总、门店绩效）
- `/api/v1/import-jobs/*` - 数据导入任务（Excel/CSV导入）
- `/api/v1/audit/*` - 审计日志查询
- `/api/v1/roles/*` - 角色管理（CRUD、权限分配）
- `/api/v1/permissions/*` - 权限查询（列表、资源类型）

**新增API端点流程**:
1. 在 [app/api/v1/](services/api/app/api/v1/) 创建或修改路由文件
2. 在 [app/api/router.py](services/api/app/api/router.py) 中注册路由 (include_router)
3. 实现对应的Service层方法
4. 定义Schema用于请求/响应验证 (Pydantic BaseModel)

### 错误处理模式
使用自定义异常类 ([app/core/exceptions.py](services/api/app/core/exceptions.py)) 而非直接抛出 `HTTPException`:
```python
# ✅ 推荐 - 使用语义化异常
from app.core.exceptions import NotFoundException, ValidationException, BusinessException

if not store:
    raise NotFoundException(f"门店 {store_id} 不存在")

if total_amount < 0:
    raise ValidationException("金额不能为负数")

if inventory < quantity:
    raise BusinessException("库存不足")

# ❌ 避免 - 直接使用HTTPException
raise HTTPException(status_code=404, detail="Not found")
```

**可用异常类** (app/core/exceptions.py):
- `ValidationException(400)`: 请求参数验证失败
- `AuthenticationException(401)`: 认证失败（无登陆凭证）
- `AuthorizationException(403)`: 无权限（无操作权限）
- `NotFoundException(404)`: 资源不存在
- `ConflictException(409)`: 资源冲突（如重复创建）
- `BusinessException(422)`: 业务逻辑错误（库存不足、重复操作等）
- `DatabaseException(500)`: 数据库操作失败

**为什么不直接用 HTTPException？**
1. **统一响应格式** - 全局异常处理器保证所有错误格式一致（code, message, detail, timestamp），客户端易于处理
2. **语义化** - `NotFoundException` 比 `HTTPException(404)` 更清晰地表达意图，代码可读性更高
3. **集中处理** - 异常处理逻辑集中在 `app/core/exceptions.py`，修改响应格式只需改一处
4. **可扩展** - 可以轻松添加新的异常类型，而无需改变API层代码

**异常处理工作流**:

```mermaid
sequenceDiagram
    participant C as 客户端
    participant A as API Layer
    participant S as Service Layer
    participant D as Database
    participant H as 异常处理器
    
    C->>A: HTTP 请求
    A->>S: 调用业务逻辑
    S->>D: 查询数据
    D-->>S: 数据不存在
    S->>S: raise NotFoundException("资源不存在")
    S--xA: 抛出异常
    A->>H: FastAPI自动捕获
    H->>H: 转换为ErrorResponse
    H-->>C: {"code": 404, "message": "资源不存在", "timestamp": "..."}
    
    Note over S,H: API层无需捕获<br/>全局处理器统一处理
```

**流程说明**:
1. Service层抛出自定义异常
2. API层不需要捕获，FastAPI自动调用 `base_api_exception_handler`
3. 处理器自动转换为统一的 `ErrorResponse` JSON格式（code, message, detail, timestamp）

### 依赖注入模式
使用 FastAPI 的依赖注入系统 ([app/api/deps.py](services/api/app/api/deps.py)):
```python
from app.api.deps import get_db, get_current_user, check_permission

@router.get("/items")
async def get_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 业务逻辑
    pass

@router.post("/stores")
async def create_store(
    data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 权限检查
    await check_permission(current_user, "store:create", db)
    # 创建门店逻辑
    pass
```

**关键依赖**:
- `get_db()`: 自动管理数据库会话生命周期，请求结束时自动关闭
- `get_current_user()`: 从JWT token提取用户，自动401响应无效token
- `check_permission(user, permission_code, db)`: 检查权限，无权限抛出403
- 依赖会被缓存在同一请求中，多次调用不会重复执行

**为什么使用依赖注入而不是全局变量或在函数中创建？**
1. **自动生命周期管理** - FastAPI自动创建和清理资源（数据库连接、临时数据），无需手动管理
2. **易于测试** - 可以注入 mock 对象，不需要修改被测代码，实现真正的单元测试
3. **避免全局污染** - 不使用全局变量，每个请求都有独立的资源，避免并发问题
4. **缓存优化** - FastAPI智能缓存依赖，同一请求中多次依赖调用只执行一次
5. **权限检查简洁** - 直接在路由参数中声明权限，无需在函数体中编写样板代码

**权限码格式**: `{resource}:{action}` (如 `store:create`, `kpi:view`, `audit:view`)
- 权限存储在数据库 `permissions` 表，通过角色关联到用户
- 超级管理员自动拥有所有权限
- 权限检查失败自动抛出403

### KPI计算引擎
[app/services/kpi_calculator.py](services/api/app/services/kpi_calculator.py) 使用SQL聚合而非Python循环:
```python
# ✅ 正确 - 数据库端聚合
result = await db.execute(
    select(func.sum(OrderHeader.total_amount))
    .where(OrderHeader.store_id == store_id)
)

# ❌ 错误 - 避免加载所有数据到内存
orders = await db.execute(select(OrderHeader))
total = sum(order.total_amount for order in orders)
```

**为什么在数据库端计算而不是Python？**

| 对比项 | SQL聚合 (✅ 推荐) | Python循环 (❌ 避免) | 差异 |
|-------|----------------|-----------------|------|
| **100万条记录** | 100ms | 10-30秒 | 🚀 快100-300倍 |
| **内存占用** | < 10MB | 2-5GB | 💾 节省99.5%内存 |
| **网络传输** | 仅返回结果(几KB) | 传输全部数据(GB级) | 📡 减少99.99%流量 |
| **计算精度** | Decimal精确 | Float浮点误差 | ✅ 财务计算必须精确 |
| **数据增长10倍** | +10ms | +100秒 | 📈 线性 vs 指数增长 |
| **并发支持** | 数据库优化 | Python GIL限制 | ⚡ 并发性能好10倍+ |

**实际案例** - 计算100万订单总额：
```python
# ✅ SQL聚合：100ms，10MB内存
result = await db.execute(
    select(func.sum(OrderHeader.total_amount))
    .where(OrderHeader.store_id == store_id)
)
total = result.scalar()  # 只返回一个数字

# ❌ Python循环：15秒，3GB内存
orders = await db.execute(select(OrderHeader))  # 加载100万条
total = sum(order.total_amount for order in orders.scalars())  # 内存溢出
```

**核心原因**:
1. **性能差异巨大** - 数据库索引+优化器，100万记录100ms vs Python 10秒+
2. **内存安全** - 数据库流式处理，Python需要全部加载到内存
3. **网络高效** - 只返回聚合结果而非全部数据
4. **精度保证** - Decimal精确计算，避免浮点误差
5. **扩展性** - 数据量增长时，SQL几乎不受影响

## 前端关键模式

### 路由结构和守卫
路由配置在 [apps/web/src/router/index.ts](apps/web/src/router/index.ts)，守卫在 [apps/web/src/router/guard.ts](apps/web/src/router/guard.ts):
- **动态路由生成**: 根据用户权限动态添加路由
- **登录检查**: 未登录自动跳转 `/login?redirect=目标路径`
- **白名单机制**: `/login`, `/403`, `/404` 无需认证
- **页面标题**: 自动设置 `document.title`

**关键流程**:

```mermaid
flowchart TD
    A[用户访问页面] --> B{已登录?}
    B -->|否| C[跳转 /login?redirect=目标路径]
    B -->|是| D{白名单路由?<br/>/login, /403, /404}
    D -->|是| E[直接访问]
    D -->|否| F{已获取用户信息?}
    F -->|否| G[调用 getUserInfo API]
    G --> H[保存用户信息和权限]
    H --> I[根据权限生成路由]
    I --> J[动态添加路由到router]
    J --> K{用户有此路由权限?}
    F -->|是| K
    K -->|有| L[访问页面]
    K -->|无| M[跳转 /404]
    
    N[最后添加404通配路由<br/>path: '/:pathMatch(.*)'] -.-> J
    
    style B fill:#e1f5ff
    style K fill:#fff4e1
    style L fill:#e8f5e9
    style M fill:#ffebee
```

**流程步骤**:
1. 检查登录状态 (authStore.isLoggedIn)
2. 首次访问时获取用户信息 (authStore.getUserInfo())
3. 根据权限生成路由 (permissionStore.generateRoutes())
4. 动态添加路由到 Layout 组件
5. 404 路由必须最后添加（否则会拦截所有路由）

**为什么使用动态路由而不是全量路由？**
1. **安全性** - 用户无权限的菜单项和路由不会被加载到前端，避免被开发者工具发现
2. **菜单一致性** - 菜单和可访问路由完全匹配，无需维护两份配置
3. **性能** - 只加载用户有权限的路由代码，减少初始加载时间
4. **易于维护** - 权限变更自动反映到前端，无需硬编码权限检查
5. **404处理** - 访问无权限路由自动跳转404，而不是显示错误页面

### 状态管理 (Pinia)
使用 Pinia 按业务域划分 Store ([apps/web/src/stores/](apps/web/src/stores/)):
- **authStore**: 登录状态、token、用户信息、权限列表
  - `isLoggedIn`: 登录状态
  - `hasPermission(code)`: 检查单个权限
  - `hasAnyPermission(codes)`: 检查是否有任一权限
  - `hasPermissions(codes)`: 检查是否有全部权限
- **permissionStore**: 动态路由、菜单生成
- **业务Store**: 按模块划分 (storeStore, kpiStore等)

**为什么使用 Pinia 而不是 props drilling 或上下文API？**
1. **集中管理** - 所有状态集中在Store中，跨组件通信无需层层传递
2. **持久化** - 配合pinia-plugin-persistedstate，token等数据自动保存到localStorage
3. **调试便利** - Pinia DevTools可视化所有状态变化，便于调试复杂交互
4. **代码分离** - Store逻辑与组件分离，便于单元测试和重用
5. **性能优化** - Store响应式只在状态改变时更新依赖组件，避免全树重渲染

### API封装和错误处理
HTTP客户端 [apps/web/src/utils/request.ts](apps/web/src/utils/request.ts) 自动处理:
- **请求拦截**: 自动添加 `Authorization: Bearer {token}` 头
- **响应拦截**: 
  - 401 → 清除登录状态，跳转登录页
  - 403 → 提示无权限，跳转 `/403`
  - 404/500 → 显示友好错误提示
- **统一响应格式**: 返回 `{ code, message, data }` 结构

**为什么要封装HTTP客户端而不是直接使用axios？**
1. **自动权限处理** - 无需在每个请求中手动添加Authorization头
2. **统一错误处理** - 全局捕获并处理所有错误，包括认证过期、权限不足等
3. **自动跳转** - 401时自动清除登录状态并跳转，无需在每个API调用中处理
4. **拦截器灵活性** - 可在一处添加日志、性能监控、请求去重等功能
5. **响应格式统一** - 后端可能响应格式变化，封装层可灵活适配

```typescript
// API 定义模式
export const storeApi = {
  getList: (params: StoreListParams) => request.get('/stores', { params }),
  create: (data: StoreCreate) => request.post('/stores', data),
  update: (id: number, data: StoreUpdate) => request.put(`/stores/${id}`, data)
}
```

### 权限指令
两个自定义指令 ([apps/web/src/directives/permission.ts](apps/web/src/directives/permission.ts)):
```vue
<!-- 单个权限或任一权限满足 -->
<el-button v-permission="'store:create'">创建门店</el-button>
<el-button v-permission="['store:edit', 'store:delete']">编辑或删除</el-button>

<!-- 必须同时拥有所有权限 -->
<el-button v-permission-all="['store:create', 'store:approve']">创建并审批</el-button>
```

**实现原理**: 元素挂载时检查权限，无权限则从DOM中移除（`el.parentNode.removeChild(el)`）

### 审计日志系统
自动记录所有关键操作 ([app/services/audit_log_service.py](services/api/app/services/audit_log_service.py)):

**自动触发场景**:
- 创建/更新/删除资源 (门店、订单、费用等)
- 登录/登出
- 权限变更
- 敏感配置修改

**手动记录审计日志**:
```python
from app.services.audit_log_service import log_audit

# 在Service层或API层记录操作
await log_audit(
    db=db,
    user_id=current_user.id,
    action="export_kpi",
    resource_type="kpi",
    resource_id=None,
    detail={"date_range": "2024-01-01 to 2024-01-31"},
    ip_address=request.client.host
)
```

**日志字段**:
- `user_id`: 操作用户
- `action`: 操作类型 (create, update, delete, view, export等)
- `resource_type`: 资源类型 (store, order, kpi等)
- `resource_id`: 资源ID
- `detail`: JSON格式的详细信息（变更前后对比等）
- `ip_address`: 操作IP
- `created_at`: 操作时间

### 数据权限系统（门店访问控制）
基于用户-门店关联控制数据访问范围 ([app/services/data_scope_service.py](services/api/app/services/data_scope_service.py)):

**核心功能**:
- 超级管理员：访问所有门店数据
- 普通用户：仅访问授权门店数据
- 向后兼容：无门店权限记录时默认可访问全部

**为什么分离 RBAC 权限和数据权限？**

```mermaid
graph TB
    U[用户 User] --> R[角色 Roles]
    R --> P[权限 Permissions<br/>RBAC功能权限]
    U --> S[门店权限 UserStores<br/>数据权限]
    
    P --> |"order:view<br/>能否看订单"| F1[功能级别控制]
    S --> |"可以看哪些门店"| F2[数据级别控制]
    
    F1 --> E1["示例：有order:view权限"]
    F2 --> E2["示例：只能看店铺A和B"]
    E1 --> R1["✅ 可以访问订单功能"]
    E2 --> R2["✅ 但只能看A和B的订单"]
    
    style P fill:#e1f5ff
    style S fill:#fff4e1
    style F1 fill:#f0f0f0
    style F2 fill:#f0f0f0
    style R1 fill:#e8f5e9
    style R2 fill:#fff9c4
```

**两层权限控制**:
- **RBAC权限** (`roles.permissions`) 控制"能否操作某个功能"（如：能否创建订单？）
- **数据权限** (`user_stores`) 控制"能看哪些数据"（如：只能看店铺A的订单？）
- **独立管理** - 同一个"查看订单"权限，有人能看全部门店，有人只能看指定门店，无需创建多个权限

**为什么用user_stores表而不是在User表存储？**
1. **数据库规范** - 用户和门店是多对多关系，应该用关联表
2. **可扩展** - 添加"访问时间限制"等扩展属性时无需修改User表结构
3. **查询效率** - 关联表可以建索引和单独优化，用户查询性能不受影响
4. **向后兼容** - 升级时现有用户默认无记录（返回None=全部可见），不需要数据迁移

**使用模式**:

```mermaid
flowchart TD
    A[用户请求数据] --> B{是超级管理员?}
    B -->|是| C[返回 None<br/>可访问全部门店]
    B -->|否| D[查询 user_stores 表]
    D --> E{有门店权限记录?}
    E -->|无| F[返回 None<br/>向后兼容，可访问全部]
    E -->|有| G[返回授权门店ID列表<br/>[1, 2, 3]]
    
    C --> H[SQL: 不添加门店过滤条件]
    F --> H
    G --> I[SQL: WHERE store_id IN (1,2,3)]
    
    H --> J[查询全部门店数据]
    I --> K[查询授权门店数据]
    
    style B fill:#e1f5ff
    style E fill:#fff4e1
    style J fill:#e8f5e9
    style K fill:#fff9c4
```

```python
from app.services.data_scope_service import get_accessible_store_ids, assert_store_access

# 获取用户可访问的门店ID列表
store_ids = await get_accessible_store_ids(db, current_user)
if store_ids is not None:
    # 限制查询范围
    query = query.where(Store.id.in_(store_ids))

# 断言用户有权访问特定门店（无权限抛403）
await assert_store_access(db, current_user, store_id=123)
```

**管理端点**: 
- `POST /api/v1/user-stores` - 授权用户访问门店
- `DELETE /api/v1/user-stores/{user_id}/{store_id}` - 撤销门店权限
- `GET /api/v1/user-stores/user/{user_id}` - 查询用户门店权限

### 数据导入系统
支持Excel/CSV批量导入订单和费用记录 ([app/services/import_service.py](services/api/app/services/import_service.py)):

**工作流程**:
```
1. 上传文件（POST /api/v1/import-jobs）
   ↓
2. 文件解析和数据校验（pandas）
   ↓
3. 批量写入数据库（bulk_insert_mappings）
   ↓
4. 错误记录生成（可下载）
```

**关键特性**:
- 支持 .xlsx, .xls, .csv 格式
- 最大文件 50MB，单次最多 10,000 行
- 异步处理大文件导入
- 详细的错误报告（行号、字段、错误原因）
- 导入任务状态跟踪（pending → processing → completed/failed）

**使用示例**:
```python
from app.services.import_service import ImportService

# 创建导入任务
job = await ImportService.create_job(
    db=db,
    file=uploaded_file,
    target_type="order",  # 或 "expense_record"
    store_id=123,
    user_id=current_user.id
)

# 执行导入
result = await ImportService.execute_job(db, job.id)

# 下载错误报告（如果有）
error_file = await ImportService.download_error_report(db, job.id)
```

**导入文件格式**:
- 订单: biz_date, order_no, total_amount, payment_method, product_name, quantity, unit_price
- 费用记录: biz_date, expense_type_name, amount, description

### 报表中心
提供多维度汇总报表和导出功能 ([app/services/report_service.py](services/api/app/services/report_service.py)):

**可用报表**:
1. **日汇总报表**: 按日期汇总营收、订单数、客单价、费用
2. **月汇总报表**: 按月汇总关键指标，支持同比/环比
3. **门店绩效报表**: 多门店对比分析（排名、占比）
4. **费用明细报表**: 费用类型分解和趋势分析

**API端点**:
- `GET /api/v1/reports/daily-summary` - 日汇总数据
- `GET /api/v1/reports/daily-summary/export` - Excel导出
- `GET /api/v1/reports/monthly-summary` - 月汇总数据
- `GET /api/v1/reports/store-performance` - 门店绩效对比

**Excel导出模式**:
```python
from app.services.report_service import export_daily_summary_excel

# 流式导出避免内存溢出
buffer = await export_daily_summary_excel(db, filters, current_user)
return StreamingResponse(
    buffer,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f"attachment; filename={filename}"}
)
```

## 常见陷阱

1. **不要混用同步/异步数据库API** - 必须全部使用 `AsyncSession` 和 `await`，不能调用 `.first()` 等同步方法，必须用 `await db.execute()` 后再调用 `.scalar_one_or_none()` 或 `.all()`
2. **数据库会话管理** - 使用 `Depends(get_db)` 而非手动创建会话，自动生命周期管理
3. **KPI计算性能** - 大数据量计算必须在数据库端完成，不要加载到Python内存（使用SQL的 `func.sum()`, `func.count()` 等）
4. **软删除查询** - 查询业务数据时记得过滤 `is_deleted=False`，或在基础 Query 中自动添加此条件
5. **CORS配置** - 开发环境已配置 http://localhost:5173、5174 端口，生产修改需同步 [services/api/app/core/config.py](services/api/app/core/config.py)
6. **前端路由404** - 动态路由必须在最后添加404通配路由，否则先添加会拦截所有路由
7. **权限指令失效** - 确保在 [apps/web/src/main.ts](apps/web/src/main.ts) 中调用 `setupPermissionDirective(app)` 注册指令
8. **异常处理层级** - Service层抛出自定义异常，FastAPI 全局异常处理器自动转换为统一响应格式，API层无需额外捕获处理
9. **模型关系加载** - 使用 `selectinload()` 而非懒加载关联数据，避免异步session关闭后访问导致错误
10. **导入文件验证** - 导入服务会自动验证文件格式和数据，无需在API层重复验证

## 实践指导

### 添加新API端点时的步骤

遵循设计原则，这样做能确保代码质量和可维护性：

```mermaid
flowchart LR
    A["1️⃣ 定义Schema<br/>app/schemas/<br/>请求/响应模型"] --> B["2️⃣ 编写Service<br/>app/services/<br/>业务逻辑"] 
    B --> C["3️⃣ 创建API路由<br/>app/api/v1/<br/>参数验证"]
    C --> D["4️⃣ 注册路由<br/>app/api/router.py<br/>include_router"]
    D --> E["5️⃣ 编写测试<br/>tests/<br/>单元+集成"]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#f0f0f0
    style D fill:#e8f5e9
    style E fill:#fff9c4
```

**为什么这个顺序很重要？**
- 先从数据结构(Schema)开始，明确输入输出
- Service层包含所有逻辑，可独立测试
- API层最后，作为业务逻辑的"门面"
- 这样即使API改变，Service逻辑保持不变

### 处理数据库查询时

始终遵循这个思路链：

```python
# 问自己：这个操作涉及多少数据？
# - 如果 < 1000条：可以在Python中处理
# - 如果 >= 1000条：必须在数据库端聚合/分页

# 如果需要在Python中处理，记住：
# 1. 使用 .all() 并明确获取所有数据
# 2. 不要迭代关联数据（会导致N+1查询）
# 3. 使用 selectinload() 预加载

# 例子
async def get_store_summary(db, store_id):
    # ❌ 错误：N+1查询
    store = await db.execute(select(Store).where(Store.id == store_id))
    orders = await db.execute(select(Order).where(Order.store_id == store_id))
    
    # ✅ 正确：数据库端聚合
    result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
        .where(Order.store_id == store_id)
    )
    count, total = result.one()
```

### 权限检查的正确方式

始终在依赖层做权限检查，不要在Service层重复检查：

```python
# ✅ 正确
@router.post("/stores")
async def create_store(
    data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 权限在路由层检查
    await check_permission(current_user, "store:create", db)
    # Service层信任权限已检查
    return await StoreService.create(db, data, current_user)

# ❌ 错误：在Service层重复检查
async def create_store(data):
    if not user.has_permission("store:create"):  # 不要这样
        raise PermissionError()
```

**为什么？**
- 权限是跨API端点的公共关注点
- 在依赖层处理，一次修改，所有端点生效
- Service层只关注业务逻辑，不关注权限
- 测试更简单：Mock一次依赖即可

## 完整请求处理流程

从客户端发起请求到返回响应的完整调用链：

```mermaid
sequenceDiagram
    participant C as 客户端<br/>(Browser)
    participant F as 前端<br/>(Vue3)
    participant I as HTTP拦截器<br/>(request.ts)
    participant A as API层<br/>(FastAPI)
    participant D as 依赖注入<br/>(deps.py)
    participant S as Service层<br/>(业务逻辑)
    participant M as Model层<br/>(SQLAlchemy)
    participant DB as 数据库<br/>(PostgreSQL)
    
    C->>F: 点击按钮/提交表单
    F->>I: axios.get('/api/v1/stores')
    I->>I: 添加 Authorization: Bearer {token}
    I->>A: HTTP GET /api/v1/stores
    
    A->>D: Depends(get_db)
    D->>D: 创建 AsyncSession
    A->>D: Depends(get_current_user)
    D->>D: 验证 JWT token
    D-->>A: 返回 User 对象
    
    A->>D: check_permission(user, "store:view")
    D->>DB: 查询用户权限
    DB-->>D: 权限列表
    D-->>A: ✅ 权限验证通过
    
    A->>S: StoreService.get_list(db, filters)
    S->>S: 构建查询条件
    S->>M: select(Store).where(...)
    M->>DB: SQL: SELECT * FROM store WHERE ...
    DB-->>M: 查询结果
    M-->>S: Store 对象列表
    S-->>A: 返回业务数据
    
    A->>A: Response[List[StoreSchema]]
    A-->>I: {"code": 200, "data": [...], "total": 10}
    I->>I: 检查响应状态
    I-->>F: 返回 data
    F->>F: 更新 Store state
    F-->>C: 渲染页面/显示数据
    
    Note over D,DB: 异常处理：任何层抛出异常<br/>都会被全局异常处理器捕获<br/>统一转换为 ErrorResponse
```

**关键节点说明**:
1. **HTTP拦截器** - 自动添加认证头、处理401/403错误
2. **依赖注入** - FastAPI自动管理DB会话、用户认证、权限验证
3. **分层处理** - API验证参数 → Service处理业务 → Model查询数据
4. **异常捕获** - 全局异常处理器统一格式化错误响应
5. **状态管理** - 前端Pinia自动更新响应式状态

## 设计决策总结

| 决策 | 选择 | 核心原因 | 对应文档 |
|-----|------|--------|--------|
| **架构分层** | Clean Architecture | 关注点分离、易于测试和复用 | [后端分层架构](#后端分层架构) |
| **模型基类** | Mixin 组合 | 灵活组合、DRY、一致性、审计追踪 | [数据库模型基类系统](#数据库模型基类系统) |
| **删除策略** | 软删除 | 数据安全、业务需求、历史追踪、避免级联 | [为什么某些表使用软删除](#数据库模型基类系统) |
| **数据库操作** | 异步 (AsyncSession) | 高并发、资源效率、框架一致性、规范化 | [异步数据库操作](#异步数据库操作) |
| **异常处理** | 自定义异常类 | 统一响应、语义清晰、集中管理、可扩展 | [错误处理模式](#错误处理模式) |
| **依赖注入** | FastAPI Depends | 生命周期管理、易于测试、避免全局污染 | [依赖注入模式](#依赖注入模式) |
| **权限系统** | RBAC + 数据权限 | 细粒度控制、功能权限独立、数据权限独立 | [数据权限系统](#数据权限系统门店访问控制) |
| **门店权限** | user_stores 关联表 | 数据库规范、可扩展、查询高效、向后兼容 | [为什么用user_stores表](#数据权限系统门店访问控制) |
| **KPI计算** | SQL 聚合 | 性能差异巨大、内存安全、网络高效、精度保证 | [KPI计算引擎](#kpi计算引擎) |
| **状态管理** | Pinia | 集中管理、持久化、调试便利、性能优化 | [状态管理](#状态管理-pinia) |
| **前端路由** | 动态路由 | 安全、一致性、性能、易维护、404处理 | [路由结构和守卫](#路由结构和守卫) |
| **HTTP封装** | 拦截器模式 | 自动权限、统一错误、自动跳转、可扩展 | [API封装和错误处理](#api封装和错误处理) |
| **测试框架** | pytest | 异步支持、灵活fixture、丰富插件、自动发现 | [测试和代码质量](#测试和代码质量) |

## 性能优化要点

### 数据库查询优化
1. **使用索引**: 关键字段已建索引 (store_id, biz_date, user_id等)
2. **批量操作**: 使用 `bulk_insert_mappings` 而非逐条插入
3. **分页查询**: 大数据量必须分页，使用 `limit().offset()`
4. **聚合下推**: KPI计算使用SQL聚合函数，不要在Python中循环
5. **避免N+1查询**: 使用 `joinedload()` 或 `selectinload()` 预加载关联数据

```python
# ✅ 正确 - 预加载关联数据
result = await db.execute(
    select(Order).options(selectinload(Order.details)).where(...)
)

# ❌ 错误 - N+1查询
orders = await db.execute(select(Order))
for order in orders:
    details = await db.execute(select(OrderDetail).where(OrderDetail.order_id == order.id))
```

### 前端性能优化
1. **组件懒加载**: 路由使用 `() => import()` 动态导入
2. **虚拟滚动**: 大列表使用 Element Plus 的虚拟滚动
3. **防抖节流**: 搜索框使用防抖，滚动事件使用节流
4. **缓存Store数据**: Pinia Store 数据缓存，避免重复请求

### 开发效率技巧
1. **使用 dev.bat / Makefile**: 统一脚本管理常用命令，避免记忆多个命令
2. **利用 Alembic 自动生成**: 修改模型后让 Alembic 自动生成迁移，再人工审查
3. **pytest fixtures**: 测试数据在 conftest.py 中复用，避免重复创建
4. **API文档**: 后端启动后访问 http://localhost:8000/docs 查看自动生成的API文档

### 维护脚本
[tooling/api/](tooling/api/) 目录包含数据库维护和测试工具:

**数据初始化**:
- `seed_data.py`: 创建初始用户、角色、权限、示例门店
- `generate_bulk_data.py`: 生成大量真实测试数据（50,000+订单，72个真实菜品，详细费用记录）
- `clean_bulk_data.py`: 清理测试数据（保留admin和基础配置）

**数据库维护** (scripts/maintenance/):
- `backup_database.py`: PostgreSQL数据库备份
- `clean_old_audit_logs.py`: 清理过期审计日志
- `verify_data_integrity.py`: 数据完整性检查

**验证脚本** (`tooling/qa/verifications/`):
- `verify_backend_import_feature.py`: 测试导入功能端到端
- `verify_backend_import_e2e.py`: 完整导入流程集成测试
- `verify_backend_reports.py`: 验证报表计算准确性
- `verify_system_integrity.py`: 系统级完整性检查

**使用方式**:
```bash
cd services/api
python tooling/api/seed_data.py           # 初始化数据
python tooling/api/generate_bulk_data.py  # 生成测试数据
```

## 项目文档

- [docs/README.md](docs/README.md): 文档中心入口
- [docs/architecture/project-structure.md](docs/architecture/project-structure.md): 项目结构与前后端架构
- [docs/development/guide.md](docs/development/guide.md): 本地开发、启动、测试与排障
- [docs/development/dependencies.md](docs/development/dependencies.md): 后端依赖说明
- [docs/qa/scripts.md](docs/qa/scripts.md): QA 脚本分类与命名规则
- [docs/api/backend-api.md](docs/api/backend-api.md): 后端 API 导出文档
