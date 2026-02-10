# 前端架构说明

## 目录结构

```
frontend/
├── public/                # 静态资源
│   └── favicon.ico
├── src/                   # 源代码目录
│   ├── main.ts           # 应用入口
│   ├── App.vue           # 根组件
│   ├── vite-env.d.ts     # Vite类型定义
│   ├── assets/           # 静态资源
│   │   ├── images/       # 图片资源
│   │   ├── styles/       # 全局样式
│   │   └── icons/        # 图标资源
│   ├── components/       # 通用组件
│   │   ├── index.ts      # 组件导出
│   │   ├── StoreSelect.vue     # 门店选择器
│   │   ├── common/       # 基础组件
│   │   │   └── FilterBar.vue   # 过滤条组件
│   │   ├── charts/       # 图表组件（ECharts封装）
│   │   │   ├── BarChart.vue    # 柱状图
│   │   │   ├── LineChart.vue   # 折线图
│   │   │   └── PieChart.vue    # 饼图
│   │   └── dialogs/      # 对话框组件
│   │       ├── CreateExpenseDialog.vue  # 创建费用对话框
│   │       ├── CreateOrderDialog.vue    # 创建订单对话框
│   │       ├── EditRoleDialog.vue       # 角色编辑对话框
│   │       └── AssignPermissionsDialog.vue # 权限分配对话框
│   ├── layout/           # 布局组件
│   │   ├── index.vue           # 主布局
│   │   └── components/
│   │       └── SidebarItem.vue # 侧边栏项
│   ├── views/            # 页面组件
│   │   ├── login/        # 登录页面
│   │   │   └── index.vue
│   │   ├── dashboard/    # 仪表板
│   │   │   └── index.vue
│   │   ├── orders/       # 订单管理
│   │   │   └── index.vue
│   │   ├── expenses/     # 费用管理
│   │   │   └── index.vue
│   │   ├── kpi/          # KPI数据
│   │   │   └── index.vue
│   │   ├── analytics/    # 报表中心
│   │   │   └── ReportView.vue
│   │   ├── audit-logs/   # 审计日志
│   │   │   └── index.vue
│   │   ├── system/       # 系统管理
│   │   │   ├── import/   # 数据导入
│   │   │   │   ├── ImportJobListView.vue   # 导入任务列表
│   │   │   │   └── ImportJobDetailView.vue # 导入任务详情
│   │   │   └── roles/    # 角色管理
│   │   │       └── index.vue       # 角色管理页面
│   │   └── error/        # 错误页面
│   │       ├── 403.vue   # 无权限
│   │       └── 404.vue   # 未找到
│   ├── router/           # 路由配置
│   │   ├── index.ts      # 路由主文件
│   │   └── guard.ts      # 路由守卫（权限检查）
│   ├── stores/           # Pinia状态管理
│   │   ├── index.ts      # Store注册
│   │   ├── auth.ts       # 认证状态
│   │   ├── permission.ts # 权限状态
│   │   └── store.ts      # 门店状态
│   ├── api/              # API服务封装
│   │   ├── index.ts      # API导出
│   │   ├── auth.ts       # 认证API
│   │   ├── store.ts      # 门店API
│   │   ├── order.ts      # 订单API
│   │   ├── expense.ts    # 费用API
│   │   ├── kpi.ts        # KPI API
│   │   ├── audit.ts      # 审计日志API
│   │   ├── import_jobs.ts # 数据导入API
│   │   ├── reports.ts    # 报表API
│   │   ├── user_stores.ts # 用户门店权限API
│   │   ├── role.ts       # 角色管理API
│   │   └── permission.ts # 权限查询API
│   ├── types/            # TypeScript类型定义（模块化）
│   │   ├── index.ts      # 类型导出
│   │   └── modules/      # 按模块分类
│   │       ├── auth.ts       # 认证类型
│   │       ├── common.ts     # 通用类型
│   │       ├── store.ts      # 门店类型
│   │       ├── order.ts      # 订单类型
│   │       ├── expense.ts    # 费用类型
│   │       ├── kpi.ts        # KPI类型
│   │       ├── import_job.ts # 数据导入类型
│   │       └── report.ts     # 报表类型
│   ├── composables/      # Vue3 Composables（可复用逻辑）
│   │   ├── index.ts      # Composables导出
│   │   └── useECharts.ts # ECharts通用逻辑
│   ├── directives/       # Vue自定义指令
│   │   ├── index.ts      # 指令注册
│   │   └── permission.ts # 权限指令（v-permission）
│   ├── config/           # 配置管理
│   │   ├── index.ts      # 配置导出
│   │   ├── constants.ts  # 常量定义
│   │   └── env.ts        # 环境变量
│   └── utils/            # 工具函数
│       ├── index.ts      # 工具导出
│       ├── request.ts    # HTTP客户端（Axios）
│       ├── format.ts     # 格式化工具（日期、金额）
│       └── validate.ts   # 验证工具
├── .env.development      # 开发环境变量
├── .env.production       # 生产环境变量
├── .env.example          # 环境变量模板
├── package.json          # 依赖和脚本
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
├── .eslintrc.cjs         # ESLint配置
├── .prettierrc.json      # Prettier配置
├── auto-imports.d.ts     # 自动导入类型声明
├── components.d.ts       # 组件类型声明
└── .gitignore
```
│   │   ├── orders/       # 订单管理
│   │   │   ├── OrderListView.vue
│   │   │   ├── OrderDetailView.vue
│   │   │   └── OrderAnalysisView.vue
│   │   ├── expenses/     # 费用管理
│   │   │   ├── ExpenseListView.vue
│   │   │   ├── ExpenseFormView.vue
│   │   │   └── ExpenseCategoryView.vue
│   │   ├── analytics/    # 数据分析
│   │   │   ├── FinancialAnalysisView.vue
│   │   │   ├── KpiDashboardView.vue
│   │   │   └── ReportView.vue
│   │   ├── system/       # 系统管理
│   │   │   ├── UserManagementView.vue
│   │   │   ├── RoleManagementView.vue
│   │   │   ├── PermissionView.vue
│   │   │   └── AuditLogView.vue
│   │   └── error/        # 错误页面
│   │       ├── 404View.vue
│   │       └── 500View.vue
│   ├── layouts/          # 布局组件
│   │   ├── DefaultLayout.vue
│   │   ├── AuthLayout.vue
│   │   └── BlankLayout.vue
│   ├── router/           # 路由配置
│   │   ├── index.ts      # 路由入口
│   │   ├── routes.ts     # 路由定义
│   │   ├── guards.ts     # 路由守卫
│   │   └── modules/      # 路由模块
│   │       ├── auth.ts
│   │       ├── dashboard.ts
│   │       ├── stores.ts
│   │       ├── orders.ts
│   │       ├── expenses.ts
│   │       ├── analytics.ts
│   │       └── system.ts
│   ├── stores/           # Pinia 状态管理
│   │   ├── index.ts      # Store 入口
│   │   ├── auth.ts       # 认证状态
│   │   ├── user.ts       # 用户状态
│   │   ├── app.ts        # 应用状态
│   │   ├── stores.ts     # 门店状态
│   │   ├── orders.ts     # 订单状态
│   │   ├── expenses.ts   # 费用状态
│   │   └── analytics.ts  # 分析状态
│   ├── services/         # API 服务
│   │   ├── index.ts      # 服务入口
│   │   ├── http.ts       # HTTP 客户端配置
│   │   ├── auth.ts       # 认证服务

## 架构原则

### 1. 组件化开发
- 使用 Vue3 Composition API
- 单文件组件（SFC）
- 组件职责单一，高内聚低耦合
- 可复用组件抽取到 components/

### 2. 类型安全
- 严格的 TypeScript 类型检查
- 所有API响应定义类型
- Props和Emits类型声明
- 避免使用 `any` 类型

### 3. 状态管理
- 使用 Pinia 管理全局状态
- 按业务域划分Store（auth, store, kpi等）
- 避免组件间直接通信

### 4. 路由管理
- 动态路由生成（基于权限）
- 路由守卫实现权限控制
- 懒加载优化首屏性能
- 路由元信息存储页面配置

### 5. API封装
- 统一的HTTP客户端（Axios）
- 请求拦截：自动添加Token
- 响应拦截：统一错误处理
- API按模块组织

## 核心模块说明

### 核心模块功能（完整列表）

| 模块 | 功能 |
|------|------|
| **登录模块** | 用户认证、Token管理 |
| **仪表板** | KPI概览、图表可视化 |
| **门店管理** | 门店CRUD、基础信息维护 |
| **订单管理** | 订单录入、明细查看 |
| **费用管理** | 费用录入、科目管理 |
| **KPI数据** | 日报表、月报表、数据导出 |
| **审计日志** | 操作记录查看、筛选导出 |
| **报表中心** | 多维度报表生成、图表可视化 |
| **数据导入** | 批量数据导入、任务管理、错误处理 |

### 页面路由（完整映射）

| 路由路径 | 组件 | 权限要求 |
|----------|------|----------|
| `/login` | views/login/index.vue | 无 |
| `/` | views/dashboard/index.vue | `dashboard:view` |
| `/orders` | views/orders/index.vue | `order:view` |
| `/expenses` | views/expenses/index.vue | `expense:view` |
| `/kpi` | views/kpi/index.vue | `kpi:view` |
| `/audit-logs` | views/audit-logs/index.vue | `audit:view` |
| `/analytics/reports` | views/analytics/ReportView.vue | `report:view` |
| `/system/import` | views/system/import/ImportJobListView.vue | `import:view` |
| `/system/import/:id` | views/system/import/ImportJobDetailView.vue | `import:view` |
| `/system/roles` | views/system/roles/index.vue | `role:view` |
| `/403` | views/error/403.vue | 无 |
| `/404` | views/error/404.vue | 无 |

### API服务（完整列表）

| API模块 | 端点 |
|---------|------|
| auth.ts | `/api/v1/auth/login`, `/api/v1/auth/refresh` |
| store.ts | `/api/v1/stores`, `/api/v1/stores/{id}` |
| order.ts | `/api/v1/orders`, `/api/v1/orders/{id}` |
| expense.ts | `/api/v1/expense-records`, `/api/v1/expense-types` |
| kpi.ts | `/api/v1/kpi/daily`, `/api/v1/kpi/monthly` |
| audit.ts | `/api/v1/audit-logs` |
| reports.ts | `/api/v1/reports/generate`, `/api/v1/reports/templates` |
| import_jobs.ts | `/api/v1/import-jobs`, `/api/v1/import-jobs/{id}` |
| user_stores.ts | `/api/v1/user-stores` |
| role.ts | `/api/v1/roles`, `/api/v1/roles/{id}`, `/api/v1/roles/{id}/permissions` |
| permission.ts | `/api/v1/permissions`, `/api/v1/permissions/all`, `/api/v1/permissions/resources` |

### 状态管理（完整Store列表）

| Store模块 | 功能 | 关键状态 |
|-----------|------|----------|
| authStore | 认证管理 | `token`, `user`, `isLoggedIn`, `permissions` |
| permissionStore | 权限管理、动态路由 | `permissions`, `routes`, `menus` |
| storeStore | 门店管理、数据权限 | `currentStore`, `allowedStores`, `storeList` |
| kpiStore | KPI缓存 | `dailyKpiData`, `monthlyKpiData` |

### 路由系统（router/）
**路由守卫流程**:
1. 检查登录状态
2. 首次访问时获取用户信息
3. 根据权限动态生成路由
4. 检查路由权限
5. 未授权跳转403页面

**关键文件**:
- `index.ts` - 路由配置和导出
- `guard.ts` - 路由守卫实现
- `routes.ts` - 静态路由定义

### 状态管理（stores/）
**核心Store**:
- `auth.ts` - 登录状态、token、用户信息
  - `isLoggedIn` - 登录状态
  - `hasPermission(code)` - 权限检查
  - `getUserInfo()` - 获取用户信息
- `permission.ts` - 动态路由、菜单生成
- 业务Store - 按模块划分（storeStore, kpiStore等）

### API封装（api/）
**HTTP客户端特性**:
- 请求拦截：自动添加 `Authorization: Bearer {token}`
- 响应拦截：
  - 401 → 清除登录状态，跳转登录页
  - 403 → 提示无权限，跳转403页面
  - 其他错误 → 显示友好提示
- 统一响应格式：`{ code, message, data }`

**API定义模式**:
```typescript
export const storeApi = {
  getList: (params) => request.get('/stores', { params }),
  create: (data) => request.post('/stores', data),
  update: (id, data) => request.put(`/stores/${id}`, data)
}
```

### 权限指令（directives/）
**两个自定义指令**:
```vue
<!-- 单个权限或任一权限满足 -->
<el-button v-permission="'store:create'">创建</el-button>
<el-button v-permission="['store:edit', 'store:delete']">编辑或删除</el-button>

<!-- 必须同时拥有所有权限 -->
<el-button v-permission-all="['store:create', 'store:approve']">创建并审批</el-button>
```

无权限时元素从DOM中移除。

### 类型定义（types/）
**模块化类型定义**:
- 按业务模块划分类型文件
- 避免类型定义重复
- 导出所有类型到 `index.ts`
- 使用接口（interface）而非类型别名（type）

**示例**:
```typescript
// types/user.ts
export interface UserInfo {
  id: number
  username: string
  email: string
  roles: string[]
  permissions: string[]
}

export interface LoginRequest {
  username: string
  password: string
}
```

## 开发规范

### 组件命名
- 文件名: PascalCase（StoreListView.vue）
- 组件名: PascalCase
- Props: camelCase
- Events: kebab-case

### 代码风格
- 使用 ESLint + Prettier
- 缩进: 2空格
- 引号: 单引号
- 分号: 不使用

### 状态管理
- 不要在组件中直接修改Store状态
- 使用Store的actions修改状态
- 计算属性使用getters

### API调用
- 使用 async/await
- 统一错误处理
- Loading状态管理

## 性能优化

### 1. 路由懒加载
```typescript
const StoreList = () => import('@/views/stores/StoreListView.vue')
```

### 2. 组件懒加载
```typescript
const ChartComponent = defineAsyncComponent(() => 
  import('@/components/charts/LineChart.vue')
)
```

### 3. 虚拟滚动
大列表使用 Element Plus 的虚拟滚动

### 4. 防抖节流
搜索框使用防抖，滚动事件使用节流

### 5. 缓存Store数据
避免重复请求相同数据

## 开发工具

### 启动开发服务器
```bash
npm run dev       # 启动开发服务器（http://localhost:5173）
```

### 构建
```bash
npm run build     # 生产构建
npm run preview   # 预览生产构建
```

### 代码检查
```bash
npm run lint      # ESLint检查
npm run format    # Prettier格式化
```

### 类型检查
```bash
npm run type-check  # TypeScript类型检查
```

### 依赖项（核心）

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7",
    "axios": "^1.6.0",
    "element-plus": "^2.5.0",
    "echarts": "^5.5.0",
    "@element-plus/icons-vue": "^2.3.1",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "eslint": "^8.56.0",
    "prettier": "^3.2.0",
    "unplugin-auto-import": "^0.17.3",
    "unplugin-vue-components": "^0.26.0"
  }
}
```

## 相关文档

- [开发指南](development_guide.md) - 项目启动和开发流程
- [后端架构](backend_structure.md) - 后端架构说明
- [项目历程](project_history.md) - 各阶段开发总结
- [命名规范](naming_conventions.md) - 代码和文件命名约定

---

*最后更新: 2026年2月8日*