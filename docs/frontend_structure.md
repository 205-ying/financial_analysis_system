# Frontend Structure

## Directory Layout

```
frontend/
├── public/                # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/                   # 源代码目录
│   ├── main.ts           # 应用入口
│   ├── App.vue           # 根组件
│   ├── assets/           # 静态资源
│   │   ├── images/
│   │   ├── styles/       # 全局样式
│   │   │   ├── index.scss
│   │   │   ├── variables.scss
│   │   │   └── mixins.scss
│   │   └── icons/
│   ├── components/       # 通用组件
│   │   ├── common/       # 基础组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── ConfirmDialog.vue
│   │   ├── forms/        # 表单组件
│   │   │   ├── BaseForm.vue
│   │   │   ├── FormItem.vue
│   │   │   └── ValidationMessage.vue
│   │   ├── charts/       # 图表组件
│   │   │   ├── BaseChart.vue
│   │   │   ├── LineChart.vue
│   │   │   ├── BarChart.vue
│   │   │   ├── PieChart.vue
│   │   │   └── TrendChart.vue
│   │   └── tables/       # 表格组件
│   │       ├── BaseTable.vue
│   │       ├── DataTable.vue
│   │       └── ExportButton.vue
│   ├── views/            # 页面组件
│   │   ├── auth/         # 认证相关
│   │   │   ├── LoginView.vue
│   │   │   └── ForgotPasswordView.vue
│   │   ├── dashboard/    # 仪表板
│   │   │   └── DashboardView.vue
│   │   ├── stores/       # 门店管理
│   │   │   ├── StoreListView.vue
│   │   │   ├── StoreDetailView.vue
│   │   │   └── StoreFormView.vue
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
│   │   ├── users.ts      # 用户服务
│   │   ├── stores.ts     # 门店服务
│   │   ├── orders.ts     # 订单服务
│   │   ├── expenses.ts   # 费用服务
│   │   ├── analytics.ts  # 分析服务
│   │   └── system.ts     # 系统服务
│   ├── types/            # TypeScript 类型定义
│   │   ├── index.ts
│   │   ├── api.ts        # API 响应类型
│   │   ├── auth.ts       # 认证相关类型
│   │   ├── user.ts       # 用户类型
│   │   ├── store.ts      # 门店类型
│   │   ├── order.ts      # 订单类型
│   │   ├── expense.ts    # 费用类型
│   │   ├── chart.ts      # 图表类型
│   │   └── common.ts     # 通用类型
│   ├── composables/      # Vue3 Composables
│   │   ├── useAuth.ts    # 认证逻辑
│   │   ├── usePermission.ts # 权限检查
│   │   ├── useTable.ts   # 表格逻辑
│   │   ├── useChart.ts   # 图表逻辑
│   │   ├── useForm.ts    # 表单逻辑
│   │   └── useRequest.ts # 请求逻辑
│   ├── utils/            # 工具函数
│   │   ├── index.ts
│   │   ├── format.ts     # 格式化工具
│   │   ├── validate.ts   # 验证工具
│   │   ├── date.ts       # 日期工具
│   │   ├── number.ts     # 数字工具
│   │   ├── storage.ts    # 存储工具
│   │   └── constants.ts  # 常量定义
│   ├── directives/       # Vue 指令
│   │   ├── index.ts
│   │   ├── permission.ts # 权限指令
│   │   └── loading.ts    # 加载指令
│   └── plugins/          # 插件配置
│       ├── index.ts
│       ├── element-plus.ts
│       ├── echarts.ts
│       └── router.ts
├── tests/                # 测试文件
│   ├── unit/             # 单元测试
│   ├── e2e/              # 端到端测试
│   └── __mocks__/        # Mock 文件
├── package.json          # 依赖和脚本配置
├── package-lock.json     # 依赖锁定
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
├── tsconfig.node.json    # Node.js TypeScript 配置
├── .env.example          # 环境变量模板
├── .env.development      # 开发环境变量
├── .env.production       # 生产环境变量
├── .gitignore
├── .eslintrc.js          # ESLint 配置
├── .prettierrc           # Prettier 配置
├── .stylelintrc.js       # Stylelint 配置
└── vitest.config.ts      # 测试配置
```

## Architecture Principles

1. **Component-Based**: 组件化开发
2. **Composition API**: 使用 Vue3 Composition API
3. **Type Safety**: 严格的 TypeScript 类型检查
4. **Modular Design**: 模块化设计
5. **Reusable Components**: 可复用组件
6. **State Management**: 统一的状态管理
7. **Responsive Design**: 响应式设计