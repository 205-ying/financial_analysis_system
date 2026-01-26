# Copilot Instructions - 餐饮企业财务分析系统

## 项目架构

这是一个**前后端分离**的餐饮企业财务分析系统:
- **后端**: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + JWT认证 + RBAC权限
- **前端**: Vue3 + TypeScript + Vite + Element Plus + ECharts + Pinia
- **环境**: 主要面向 Windows 开发环境，使用 `.bat` 脚本和 PowerShell

## 核心架构原则

### 后端分层架构
严格遵循 **Clean Architecture** 分层设计，依赖方向：API → Service → Model

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

### 数据库模型基类系统
所有模型继承自 [app/models/base.py](backend/app/models/base.py) 的基类:
- `BaseModel`: ID + 时间戳 (created_at, updated_at)
- `BaseModelWithSoftDelete`: + 软删除 (is_deleted, deleted_at)
- `BaseModelWithUserTracking`: + 用户追踪 (created_by_id, updated_by_id)
- `FullBaseModel`: 包含所有功能

**示例**: 大多数业务表使用 `BaseModel`，核心数据表如Order使用 `BaseModelWithSoftDelete`

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

## 开发工作流

### 环境配置
**必须先配置**: 复制 `backend/.env.example` → `backend/.env`，设置数据库连接:
```ini
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/financial_analysis
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### 启动项目 (Windows环境)
```bash
# 方法1: 使用统一脚本 (推荐)
dev.bat dev-backend      # 启动后端 (http://localhost:8000)
dev.bat dev-frontend     # 启动前端 (http://localhost:5173)

# 方法2: 直接启动
cd backend && python dev.py start      # 或 start_dev.bat
cd frontend && npm run dev

# 方法3: 使用虚拟环境 (PowerShell)
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**首次启动前**: 必须执行数据库迁移和初始化数据。

### 数据库迁移工作流
```bash
cd backend

# 1. 应用已有迁移
alembic upgrade head

# 2. 修改模型后创建迁移（Alembic 会自动检测变化）
alembic revision --autogenerate -m "描述变更"

# 3. 查看迁移历史
alembic history

# 4. 回滚到指定版本
alembic downgrade -1              # 回滚一个版本
alembic downgrade <revision_id>   # 回滚到指定版本
```

**迁移脚本位置**: [alembic/versions/](backend/alembic/versions/)
- 每个迁移文件包含 `upgrade()` 和 `downgrade()` 函数
- 自动生成的迁移需要人工审查，特别是删除列、修改列类型等危险操作

### 初始化数据
首次部署或重置数据库后运行:
```bash
cd backend
python scripts/seed_data.py
```
自动创建:
- **默认用户**: 
  - admin/Admin@123 (系统管理员，所有权限)
  - manager/Manager@123 (门店经理，运营权限)
  - cashier/Cashier@123 (收银员，基本权限)
- **权限**: 28+ 个细粒度权限 (user:view, store:create, kpi:export等)
- **角色**: 3个预定义角色
- **示例数据**: 门店、产品分类、产品、费用类型

**批量测试数据生成**: `python scripts/generate_bulk_data.py` (生成大量订单和KPI用于性能测试)

### 测试和代码质量
```bash
cd backend
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
- 测试文件在 [backend/tests/](backend/tests/)
- [conftest.py](backend/tests/conftest.py) 提供数据库fixtures和测试客户端
- 使用 `@pytest.mark.asyncio` 标记异步测试

## 关键约定

### 后端命名规范
- **文件名**: snake_case (user_service.py, order_header.py)
- **类名**: PascalCase (OrderHeader, KpiCalculator)
- **函数/变量**: snake_case (get_current_user, total_amount)
- **数据库表名**: snake_case + 复数 (users, order_headers, kpi_daily_stores)
- **API路由**: kebab-case (/api/v1/expense-records)

### 前端命名规范
- **组件文件**: PascalCase (StoreListView.vue, FilterBar.vue)
- **函数/变量**: camelCase (getCurrentUser, totalAmount)
- **类型定义**: PascalCase (UserInfo, StoreDetail)
- **Store模块**: camelCase (useAuthStore, useStoreStore)

### API响应格式
所有API响应使用统一格式 ([app/schemas/common.py](backend/app/schemas/common.py)):
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
```

### API路由结构
所有API端点在 [app/api/router.py](backend/app/api/router.py) 统一注册，挂载到 `/api/v1` 前缀:
- `/api/v1/auth/*` - 认证和授权 (login, refresh)
- `/api/v1/stores/*` - 门店管理
- `/api/v1/orders/*` - 订单管理
- `/api/v1/expense-types/*` - 费用科目管理
- `/api/v1/expense-records/*` - 费用记录管理
- `/api/v1/kpi/*` - KPI数据查询和导出
- `/api/v1/audit/*` - 审计日志查询

**新增API端点流程**:
1. 在 [app/api/v1/](backend/app/api/v1/) 创建或修改路由文件
2. 在 [app/api/router.py](backend/app/api/router.py) 中注册路由
3. 实现对应的Service层方法
4. 定义Schema用于请求/响应验证

### 错误处理模式
使用自定义异常类 ([app/core/exceptions.py](backend/app/core/exceptions.py)) 而非直接抛出 `HTTPException`:
```python
# ✅ 推荐 - 使用语义化异常
from app.core.exceptions import NotFoundException, ValidationException

if not store:
    raise NotFoundException(f"门店 {store_id} 不存在")

# ❌ 避免 - 直接使用HTTPException
raise HTTPException(status_code=404, detail="Not found")
```

**可用异常类**:
- `ValidationException(400)`: 请求参数验证失败
- `AuthenticationException(401)`: 认证失败
- `AuthorizationException(403)`: 无权限
- `NotFoundException(404)`: 资源不存在
- `ConflictException(409)`: 资源冲突（如重复创建）
- `BusinessException(422)`: 业务逻辑错误
- `DatabaseException(500)`: 数据库操作失败

### 依赖注入模式
使用 FastAPI 的依赖注入系统 ([app/api/deps.py](backend/app/api/deps.py)):
```python
from app.api.deps import get_db, get_current_user

@router.get("/items")
async def get_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 业务逻辑
```

**关键依赖**:
- `get_db()`: 自动管理数据库会话生命周期，请求结束时自动关闭
- `get_current_user()`: 从JWT token提取用户，自动401响应无效token
- 依赖会被缓存在同一请求中，多次调用不会重复执行

### 权限检查
使用 `check_permission` 函数 ([app/api/deps.py](backend/app/api/deps.py)):
```python
from app.api.deps import check_permission

@router.post("/stores")
async def create_store(
    data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_permission(current_user, "store:create", db)
    # 创建门店逻辑
```

**权限码格式**: `{resource}:{action}` (如 `store:create`, `kpi:view`, `audit:view`)
- 权限存储在数据库 `permissions` 表，通过角色关联到用户
- 超级管理员自动拥有所有权限
- 抛出 `HTTPException(403)` 表示无权限

### KPI计算引擎
[app/services/kpi_calculator.py](backend/app/services/kpi_calculator.py) 使用SQL聚合而非Python循环:
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

## 前端关键模式

### 路由结构和守卫
路由配置在 [frontend/src/router/index.ts](frontend/src/router/index.ts)，守卫在 [frontend/src/router/guard.ts](frontend/src/router/guard.ts):
- **动态路由生成**: 根据用户权限动态添加路由
- **登录检查**: 未登录自动跳转 `/login?redirect=目标路径`
- **白名单机制**: `/login`, `/403`, `/404` 无需认证
- **页面标题**: 自动设置 `document.title`

**关键流程**:
```typescript
1. 检查登录状态 (authStore.isLoggedIn)
2. 首次访问时获取用户信息 (authStore.getUserInfo())
3. 根据权限生成路由 (permissionStore.generateRoutes())
4. 动态添加路由到 Layout 组件
5. 404 路由必须最后添加
```

### 状态管理 (Pinia)
使用 Pinia 按业务域划分 Store ([frontend/src/stores/](frontend/src/stores/)):
- **authStore**: 登录状态、token、用户信息、权限列表
  - `isLoggedIn`: 登录状态
  - `hasPermission(code)`: 检查单个权限
  - `hasAnyPermission(codes)`: 检查是否有任一权限
  - `hasPermissions(codes)`: 检查是否有全部权限
- **permissionStore**: 动态路由、菜单生成
- **业务Store**: 按模块划分 (storeStore, kpiStore等)

### API封装和错误处理
HTTP客户端 [frontend/src/utils/request.ts](frontend/src/utils/request.ts) 自动处理:
- **请求拦截**: 自动添加 `Authorization: Bearer {token}` 头
- **响应拦截**: 
  - 401 → 清除登录状态，跳转登录页
  - 403 → 提示无权限，跳转 `/403`
  - 404/500 → 显示友好错误提示
- **统一响应格式**: 返回 `{ code, message, data }` 结构

```typescript
// API 定义模式
export const storeApi = {
  getList: (params: StoreListParams) => request.get('/stores', { params }),
  create: (data: StoreCreate) => request.post('/stores', data),
  update: (id: number, data: StoreUpdate) => request.put(`/stores/${id}`, data)
}
```

### 权限指令
两个自定义指令 ([frontend/src/directives/permission.ts](frontend/src/directives/permission.ts)):
```vue
<!-- 单个权限或任一权限满足 -->
<el-button v-permission="'store:create'">创建门店</el-button>
<el-button v-permission="['store:edit', 'store:delete']">编辑或删除</el-button>

<!-- 必须同时拥有所有权限 -->
<el-button v-permission-all="['store:create', 'store:approve']">创建并审批</el-button>
```

**实现原理**: 元素挂载时检查权限，无权限则从DOM中移除（`el.parentNode.removeChild(el)`）

### 审计日志系统
自动记录所有关键操作 ([app/services/audit_log_service.py](backend/app/services/audit_log_service.py)):

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

## 常见陷阱

1. **不要混用同步/异步数据库API** - 必须全部使用 `AsyncSession` 和 `await`
2. **数据库会话管理** - 使用 `Depends(get_db)` 而非手动创建会话
3. **KPI计算性能** - 大数据量计算必须在数据库端完成，不要加载到Python内存
4. **软删除查询** - 查询时记得过滤 `is_deleted=False`
5. **CORS配置** - 开发环境已配置5173/5174端口，修改需同步 [backend/app/core/config.py](backend/app/core/config.py)
6. **前端路由404** - 动态路由必须在最后添加404通配路由，否则先添加会拦截所有路由
7. **权限指令失效** - 确保在 `main.ts` 中调用 `setupPermissionDirective(app)` 注册指令
8. **异常处理层级** - Service层抛出自定义异常，API层捕获后返回统一格式，避免在多处重复处理

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
1. **使用 dev.bat**: 统一脚本管理所有命令，避免记忆多个命令
2. **利用 Alembic 自动生成**: 修改模型后让 Alembic 自动生成迁移，再人工审查
3. **pytest fixtures**: 测试数据在 conftest.py 中复用，避免重复创建
4. **API文档**: 后端启动后访问 http://localhost:8000/docs 查看自动生成的API文档

## 项目文档

- [docs/development_guide.md](docs/development_guide.md): 完整开发指南（包含架构图和数据模型ER图）
- [docs/backend_structure.md](docs/backend_structure.md): 后端架构详解
- [docs/frontend_structure.md](docs/frontend_structure.md): 前端架构详解
- [docs/naming_conventions.md](docs/naming_conventions.md): 命名规范详解
- [backend/scripts/README.md](backend/scripts/README.md): 维护脚本说明（数据库备份、清理、测试数据生成）
- [docs/archive/](docs/archive/): 30+ 历史交付和测试报告
