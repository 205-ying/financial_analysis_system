# 财务分析系统 - 前端

基于 Vue 3 + TypeScript + Vite + Element Plus 的现代化前端应用。

## 技术栈

- **Vue 3.4.15** - 渐进式 JavaScript 框架
- **TypeScript 5.3.3** - JavaScript 的超集
- **Vite 5.0.11** - 下一代前端构建工具
- **Element Plus 2.5.3** - Vue 3 组件库
- **Pinia 2.1.7** - Vue 状态管理库
- **Vue Router 4.2.5** - Vue 官方路由
- **Axios 1.6.5** - 基于 Promise 的 HTTP 客户端

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动

### 生产环境构建

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

### 类型检查

```bash
npm run type-check
```

## 项目结构

```
src/
├── api/              # API 接口
│   ├── auth.ts      # 认证接口
│   ├── order.ts     # 订单接口
│   ├── expense.ts   # 费用接口
│   ├── store.ts     # 门店接口
│   ├── kpi.ts       # KPI 接口
│   └── index.ts     # 统一导出
├── assets/           # 静态资源
├── components/       # 公共组件
│   └── FilterBar.vue
├── composables/      # 组合式函数
│   ├── useECharts.ts
│   └── index.ts
├── config/           # 配置管理
│   ├── constants.ts # 应用常量
│   ├── env.ts       # 环境配置
│   └── index.ts     # 统一导出
├── directives/       # 自定义指令
│   ├── permission.ts
│   └── index.ts
├── layout/           # 布局组件
│   ├── index.vue
│   └── components/
├── router/           # 路由配置
│   ├── index.ts
│   └── guard.ts
├── stores/           # 状态管理
│   ├── auth.ts      # 认证状态
│   ├── permission.ts
│   └── index.ts
├── types/            # TypeScript 类型定义
│   └── api.ts
├── utils/            # 工具函数
│   ├── request.ts   # HTTP 请求封装
│   ├── format.ts    # 格式化函数
│   ├── validate.ts  # 验证函数
│   └── index.ts     # 统一导出
├── views/            # 页面组件
│   ├── dashboard/   # 仪表盘
│   ├── orders/      # 订单管理
│   ├── expenses/    # 费用管理
│   ├── kpi/         # KPI 分析
│   ├── audit-logs/  # 审计日志
│   ├── login/       # 登录页
│   └── error/       # 错误页
├── App.vue           # 根组件
└── main.ts           # 应用入口
```

## 环境变量

### 开发环境 (.env.development)

```
VITE_API_BASE_URL=http://localhost:8000
```

### 生产环境 (.env.production)

```
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 默认账号

### 超级管理员
- 用户名: `admin`
- 密码: `Admin@123`

### 普通管理员
- 用户名: `manager`
- 密码: `Manager@123`

## 功能特性

### 核心功能
- ✅ **用户认证** - 登录、退出、token 管理
- ✅ **权限路由** - 基于权限的动态路由和菜单
- ✅ **状态持久化** - localStorage 自动持久化
- ✅ **请求拦截** - 自动添加 token，统一错误处理
- ✅ **响应式布局** - 侧边栏折叠、面包屑导航
- ✅ **错误页面** - 403/404 友好提示

### 业务功能
- ✅ **仪表盘** - 数据概览和可视化
- ✅ **订单管理** - 订单列表、查询、统计
- ✅ **费用管理** - 费用记录、分类、分析
- ✅ **门店管理** - 门店信息、业绩统计
- ✅ **KPI 分析** - 关键指标、趋势分析、排名
- ✅ **审计日志** - 操作记录、审计追踪

### 技术特性
- ✅ **配置管理** - 集中式配置，类型安全
- ✅ **工具函数库** - 格式化、验证等通用函数
- ✅ **组合式函数** - 可复用的业务逻辑
- ✅ **统一导出** - 简化模块引用
- ✅ **ECharts 封装** - 开箱即用的图表组件

## 开发规范

### 代码风格
- 使用 TypeScript 严格模式
- 遵循 ESLint 和 Prettier 规则
- 使用 Composition API
- 组件采用 `<script setup>` 语法
- 样式使用 SCSS

### 导入规范
```typescript
// 推荐：使用统一导出
import { authApi, orderApi } from '@/api'
import { formatCurrency, formatDate } from '@/utils'
import { STORAGE_KEYS, REQUEST_TIMEOUT } from '@/config'

// 不推荐：直接导入
import { login } from '@/api/auth'
import { formatCurrency } from '@/utils/format'
```

### 配置使用
```typescript
// 使用配置常量
import { envConfig, API_BASE_URL, PAGINATION } from '@/config'

const baseUrl = envConfig.apiBaseUrl
const pageSize = PAGINATION.DEFAULT_PAGE_SIZE
```

### 工具函数使用
```typescript
import { formatCurrency, formatDate, isEmail } from '@/utils'

// 格式化金额
const price = formatCurrency(1234.56) // "1234.56"

// 格式化日期
const date = formatDate(new Date(), 'YYYY-MM-DD') // "2026-01-23"

// 验证邮箱
const valid = isEmail('test@example.com') // true
```

## 常见问题

### Q: 登录后刷新页面就跳转登录页？
A: 检查浏览器 localStorage 是否正常存储 token。

### Q: 看不到任何菜单？
A: 检查后端返回的 permissions 字段，确保权限码匹配。

### Q: 手动输入 URL 可以访问无权限的页面？
A: 检查路由守卫是否正确执行。

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT
