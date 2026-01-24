# 项目命名和结构规范

**版本**: 1.0  
**生效日期**: 2026年1月23日  
**适用范围**: 餐饮财务分析系统

---

## 📁 目录结构规范

### 后端结构 (backend/)

```
backend/
├── alembic/                    # 数据库迁移脚本
│   └── versions/              # 迁移版本文件
├── docs/                       # 后端文档
├── logs/                       # 日志文件（运行时生成）
├── scripts/                    # 工具脚本
│   ├── seed_data.py          # 种子数据生成
│   └── verify_constraints.py # 约束验证
├── src/
│   ├── __init__.py
│   └── app/                   # 应用主目录
│       ├── __init__.py
│       ├── main.py           # 应用入口
│       ├── api/              # API路由层
│       │   ├── __init__.py
│       │   ├── router.py     # 路由聚合
│       │   └── v1/           # v1版本API
│       │       ├── __init__.py
│       │       ├── auth.py           # 认证相关API
│       │       ├── kpi.py            # KPI相关API
│       │       ├── stores.py         # 门店管理API
│       │       ├── expense_types.py  # 费用类型API
│       │       ├── expense_records.py # 费用记录API
│       │       └── order_headers.py  # 订单API
│       ├── core/             # 核心配置
│       │   ├── __init__.py
│       │   ├── config.py     # 配置管理
│       │   ├── database.py   # 数据库连接
│       │   ├── deps.py       # 依赖注入
│       │   └── security.py   # 安全相关
│       ├── models/           # 数据模型（SQLAlchemy）
│       │   ├── __init__.py
│       │   ├── base.py       # 基础模型
│       │   ├── user.py       # 用户模型
│       │   ├── store.py      # 门店模型
│       │   ├── expense.py    # 费用模型
│       │   ├── order.py      # 订单模型
│       │   └── kpi.py        # KPI模型
│       ├── schemas/          # 请求/响应模型（Pydantic）
│       │   ├── __init__.py
│       │   ├── common.py     # 通用schemas
│       │   ├── auth.py       # 认证schemas
│       │   ├── store.py      # 门店schemas
│       │   ├── expense.py    # 费用schemas
│       │   ├── order.py      # 订单schemas
│       │   └── kpi.py        # KPI schemas
│       └── services/         # 业务逻辑层
│           ├── __init__.py
│           ├── audit.py      # 审计日志服务
│           └── kpi_calculator.py # KPI计算服务
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── alembic.ini               # Alembic配置
├── pyproject.toml            # 项目元数据
├── requirements.txt          # 生产依赖
└── requirements-dev.txt      # 开发依赖
```

### 前端结构 (frontend/)

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── App.vue               # 根组件
│   ├── main.ts               # 应用入口
│   ├── api/                  # API调用层
│   │   ├── auth.ts          # 认证API
│   │   ├── kpi.ts           # KPI API
│   │   ├── store.ts         # 门店API
│   │   ├── expense.ts       # 费用API
│   │   └── order.ts         # 订单API
│   ├── assets/              # 资源文件
│   ├── components/          # 通用组件
│   │   └── FilterBar.vue   # 筛选条件组件
│   ├── composables/         # Vue3 Composition API Hooks
│   │   └── useECharts.ts   # ECharts封装
│   ├── directives/          # 自定义指令
│   │   └── permission.ts   # 权限指令
│   ├── layout/              # 布局组件
│   │   ├── index.vue
│   │   └── components/
│   ├── router/              # 路由配置
│   │   ├── index.ts
│   │   └── guard.ts        # 路由守卫
│   ├── stores/              # Pinia状态管理
│   │   ├── index.ts
│   │   ├── auth.ts         # 认证状态
│   │   └── permission.ts   # 权限状态
│   ├── types/               # TypeScript类型定义
│   │   └── api.ts          # API类型
│   ├── utils/               # 工具函数
│   │   └── request.ts      # HTTP请求封装
│   └── views/               # 页面组件
│       ├── dashboard/       # 仪表盘
│       ├── kpi/            # KPI分析
│       ├── expenses/       # 费用管理
│       ├── orders/         # 订单管理
│       ├── login/          # 登录
│       └── error/          # 错误页面
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 📝 命名规范

### 1. 文件命名

#### 后端 Python 文件

```python
# 模块文件 - 蛇形命名法 (snake_case)
user_management.py         ✅
expense_calculator.py      ✅
kpi_service.py            ✅

# 避免
UserManagement.py          ❌ (PascalCase用于类名)
user-management.py         ❌ (连字符不符合Python规范)
usermgmt.py               ❌ (缩写不清晰)
```

#### 前端 TypeScript/Vue 文件

```typescript
// TypeScript文件 - 驼峰命名法 (camelCase)
userService.ts            ✅
apiClient.ts              ✅
dateUtils.ts              ✅

// Vue组件文件 - 大驼峰命名法 (PascalCase)
FilterBar.vue             ✅
DataTable.vue             ✅
UserProfile.vue           ✅

// Composables - use前缀 + 驼峰
useECharts.ts             ✅
useAuth.ts                ✅
usePermission.ts          ✅

// 避免
filter-bar.vue            ❌ (kebab-case在文件名中不推荐)
use_auth.ts               ❌ (蛇形命名法不符合TS规范)
```

### 2. 目录命名

```bash
# 统一使用小写 + 连字符（或下划线）
backend/src/app/api/           ✅
frontend/src/components/       ✅
backend/src/app/expense_types/ ✅

# 避免
backend/src/app/API/           ❌ (全大写)
frontend/src/Components/       ❌ (首字母大写)
```

### 3. 变量和函数命名

#### 后端 Python

```python
# 变量 - 蛇形命名法
user_name = "admin"           ✅
total_amount = 100.0          ✅
is_active = True              ✅

# 函数 - 蛇形命名法
def get_user_list():          ✅
def calculate_total_cost():   ✅
async def create_order():     ✅

# 类 - 大驼峰命名法 (PascalCase)
class UserService:            ✅
class KpiCalculator:          ✅
class ExpenseRecord:          ✅

# 常量 - 全大写 + 下划线
MAX_PAGE_SIZE = 100           ✅
DEFAULT_TIMEOUT = 30          ✅
API_VERSION = "v1"            ✅

# 避免
userName = "admin"            ❌ (驼峰不符合Python规范)
def GetUserList():            ❌ (函数名大驼峰)
class userService:            ❌ (类名小写)
maxPageSize = 100             ❌ (常量应全大写)
```

#### 前端 TypeScript

```typescript
// 变量 - 驼峰命名法
const userName = 'admin'              ✅
const totalAmount = 100.0             ✅
const isActive = true                 ✅

// 函数 - 驼峰命名法
function getUserList() { }            ✅
function calculateTotalCost() { }     ✅
async function createOrder() { }      ✅

// 类/接口 - 大驼峰命名法
class UserService { }                 ✅
interface UserInfo { }                ✅
type ApiResponse = { }                ✅

// 常量 - 全大写 + 下划线
const MAX_PAGE_SIZE = 100             ✅
const DEFAULT_TIMEOUT = 30            ✅
const API_BASE_URL = '/api'           ✅

// 枚举 - 大驼峰命名法，成员全大写
enum UserRole {                       ✅
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user'
}

// 避免
const user_name = 'admin'             ❌ (蛇形不符合TS规范)
function GetUserList() { }            ❌ (函数名大驼峰)
const maxPageSize = 100               ❌ (常量应全大写)
```

### 4. API路由命名

#### RESTful API规范

```python
# 资源路由 - 复数名词 + 动词通过HTTP方法表达
GET    /api/v1/stores              ✅ 获取门店列表
POST   /api/v1/stores              ✅ 创建门店
GET    /api/v1/stores/{id}         ✅ 获取门店详情
PUT    /api/v1/stores/{id}         ✅ 更新门店
DELETE /api/v1/stores/{id}         ✅ 删除门店

# 特殊操作 - 动词形式
POST   /api/v1/kpi/rebuild-daily   ✅ 重建KPI
GET    /api/v1/kpi/export          ✅ 导出KPI
POST   /api/v1/auth/login          ✅ 登录
POST   /api/v1/auth/logout         ✅ 登出

# 层级关系 - 嵌套资源
GET    /api/v1/stores/{id}/orders  ✅ 获取门店的订单
GET    /api/v1/orders/{id}/items   ✅ 获取订单的项目

# 避免
GET    /api/v1/getStores           ❌ (动词在路径中)
POST   /api/v1/store/create        ❌ (单数 + 冗余动词)
GET    /api/v1/storeList           ❌ (驼峰命名)
```

### 5. 数据库命名

```sql
-- 表名 - 小写 + 下划线 + 单数或复数（根据语义）
store                      ✅ (门店)
expense_type               ✅ (费用类型)
expense_record             ✅ (费用记录)
order_header               ✅ (订单头)
kpi_daily_store            ✅ (每日门店KPI)

-- 字段名 - 小写 + 下划线
user_name                  ✅
created_at                 ✅
total_amount               ✅
is_active                  ✅

-- 主键
id                         ✅ (自增主键)

-- 外键 - 表名单数 + _id
store_id                   ✅
user_id                    ✅
expense_type_id            ✅

-- 索引 - idx_ + 表名 + 字段名
idx_store_code             ✅
idx_expense_record_date    ✅
idx_order_store_date       ✅

-- 避免
Store                      ❌ (大写)
expenseType                ❌ (驼峰)
user-name                  ❌ (连字符)
storeID                    ❌ (驼峰后缀)
```

---

## 🎨 代码风格规范

### Python代码规范 (遵循PEP 8)

```python
# 导入顺序
# 1. 标准库
import os
import sys
from datetime import date, datetime

# 2. 第三方库
from fastapi import APIRouter
from sqlalchemy import select

# 3. 本地模块
from app.models.user import User
from app.schemas.common import Response

# 函数定义
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    根据ID获取用户
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        用户对象或None
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# 类定义
class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, username: str) -> User:
        """创建用户"""
        user = User(username=username)
        self.db.add(user)
        await self.db.commit()
        return user
```

### TypeScript代码规范

```typescript
// 导入顺序
// 1. Vue相关
import { ref, reactive, computed, onMounted } from 'vue'

// 2. 第三方库
import { ElMessage } from 'element-plus'

// 3. 本地模块
import { getUserList } from '@/api/user'
import type { UserInfo } from '@/types/api'

// 接口定义
interface UserQuery {
  page: number
  pageSize: number
  keyword?: string
}

// 函数定义
async function loadUserList(query: UserQuery): Promise<void> {
  try {
    const res = await getUserList(query)
    userList.value = res.data.items
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

// 组件定义
const userList = ref<UserInfo[]>([])
const loading = ref(false)
const total = computed(() => userList.value.length)

onMounted(() => {
  loadUserList({ page: 1, pageSize: 20 })
})
```

---

## 📦 模块组织规范

### 后端模块职责划分

```python
# models/ - 数据模型层
# 职责: 定义数据库表结构，不包含业务逻辑
class Store(Base):
    __tablename__ = "store"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# schemas/ - 数据传输对象层  
# 职责: 定义API请求/响应格式，数据验证
class StoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class StoreInDB(BaseModel):
    id: int
    name: str
    created_at: datetime

# services/ - 业务逻辑层
# 职责: 复杂业务逻辑，跨表操作，计算
class KpiCalculator:
    async def calculate_daily_kpi(self, date: date) -> Dict:
        # 复杂的KPI计算逻辑
        pass

# api/ - 路由层
# 职责: 处理HTTP请求，调用service，返回响应
@router.get("/stores")
async def list_stores(
    db: AsyncSession = Depends(get_db)
) -> Response[List[StoreInDB]]:
    stores = await get_store_list(db)
    return success(data=stores)
```

### 前端模块职责划分

```typescript
// types/ - 类型定义
// 职责: 定义数据结构
export interface UserInfo {
  id: number
  username: string
}

// api/ - API调用层
// 职责: 封装HTTP请求
export function getUserList(params: UserQuery) {
  return request.get('/api/v1/users', { params })
}

// stores/ - 状态管理层
// 职责: 全局状态管理
export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!user.value)
  
  function setUser(newUser: UserInfo) {
    user.value = newUser
  }
  
  return { user, isLoggedIn, setUser }
})

// composables/ - 组合式函数
// 职责: 可复用的逻辑
export function useUserList() {
  const list = ref<UserInfo[]>([])
  const loading = ref(false)
  
  async function loadList() {
    loading.value = true
    const res = await getUserList()
    list.value = res.data
    loading.value = false
  }
  
  return { list, loading, loadList }
}

// views/ - 页面组件
// 职责: 页面级组件，组合各种逻辑
<script setup lang="ts">
const { list, loading, loadList } = useUserList()
onMounted(() => loadList())
</script>
```

---

## 🔍 命名检查清单

### 创建新文件前检查

- [ ] 文件名是否符合命名规范？
- [ ] 文件是否放在正确的目录？
- [ ] 是否有重复的文件？

### 编写代码时检查

- [ ] 变量名是否清晰表达含义？
- [ ] 函数名是否使用动词开头？
- [ ] 类名是否使用名词？
- [ ] 常量是否全大写？

### 创建API时检查

- [ ] 路由是否使用复数名词？
- [ ] HTTP方法是否正确？
- [ ] 路径是否符合RESTful规范？

### 数据库设计时检查

- [ ] 表名是否小写+下划线？
- [ ] 字段名是否清晰？
- [ ] 外键是否遵循 表名_id 格式？

---

## 📚 参考资料

### Python
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### TypeScript
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

### API设计
- [RESTful API Design Best Practices](https://restfulapi.net/)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)

### Vue3
- [Vue 3 Style Guide](https://vuejs.org/style-guide/)
- [Vue 3 Composition API](https://vuejs.org/api/composition-api-setup.html)

---

**文档维护者**: 开发团队  
**最后更新**: 2026年1月23日
