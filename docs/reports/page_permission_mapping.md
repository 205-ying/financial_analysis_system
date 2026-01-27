## 🔗 页面-路由-权限码映射表 (阶段2C分析)

### 路由权限系统架构
- **动态路由生成**: `PermissionStore.generateRoutes()` 根据用户权限动态生成路由
- **路由守卫**: `router/guard.ts` 检查登录状态和权限，动态添加路由  
- **权限指令**: `v-permission` 和 `v-permission-all` 控制元素可见性

### 页面级权限 (路由访问控制)
| 页面名称 | 路由路径 | 权限码 | 组件文件 |
|---------|----------|--------|----------|
| 看板 | `/dashboard` | `dashboard:view` | [dashboard/index.vue](frontend/src/views/dashboard/index.vue) |
| 订单管理 | `/orders` | `order:view` | [orders/index.vue](frontend/src/views/orders/index.vue) |
| 费用管理 | `/expenses` | `expense:view` | [expenses/index.vue](frontend/src/views/expenses/index.vue) |
| KPI分析 | `/kpi` | `kpi:view` | [kpi/index.vue](frontend/src/views/kpi/index.vue) |
| 报表中心 | `/reports` | `report:view` | [analytics/ReportView.vue](frontend/src/views/analytics/ReportView.vue) |
| 审计日志 | `/audit-logs` | `audit:view` | [audit-logs/index.vue](frontend/src/views/audit-logs/index.vue) |
| 数据导入列表 | `/system/import-jobs` | `import_job:view` | [system/import/ImportJobListView.vue](frontend/src/views/system/import/ImportJobListView.vue) |
| 导入详情 | `/system/import-jobs/:id` | `import_job:view` | [system/import/ImportJobDetailView.vue](frontend/src/views/system/import/ImportJobDetailView.vue) |

### 页面内权限 (元素级控制)
#### 订单管理页面 (`/orders`)
- `order:create` - 创建订单按钮
- `order:export` - 导出订单按钮  
- `order:update` - 编辑订单按钮
- `order:delete` - 删除订单按钮

#### 费用管理页面 (`/expenses`)
- `expense:create` - 创建费用按钮
- `expense:export` - 导出费用按钮
- `expense:update` - 编辑费用按钮
- `expense:delete` - 删除费用按钮

#### 看板页面 (`/dashboard`)
- `kpi:rebuild` - KPI重建按钮

#### 报表中心页面 (`/reports`)
- `report:export` - 导出报表按钮

#### 数据导入页面 (`/system/import-jobs`)
- `import_job:create` - 创建导入任务按钮
- `import_job:view` - 查看详情按钮
- `import_job:run` - 执行任务按钮
- `import_job:download` - 下载错误报告按钮

### 权限系统一致性检查 ✅
1. **路由权限一致**: 所有页面权限码格式统一为 `{resource}:view`
2. **元素权限一致**: 页面内权限码遵循 `{resource}:{action}` 格式
3. **权限指令统一**: 全部使用 `v-permission` 指令，没有重复实现
4. **权限检查集中**: 权限逻辑集中在 `PermissionStore` 和 `AuthStore` 中

### 动态路由生成流程
1. 用户登录后，`router/guard.ts` 触发权限检查
2. 调用 `AuthStore.getUserInfo()` 获取用户权限列表
3. 调用 `PermissionStore.generateRoutes()` 根据权限过滤路由
4. 动态添加路由到 Layout 组件
5. 最后添加 404 通配路由

### 收敛建议 ✅
**路由系统已充分收敛**，无需额外重构：
- 单一路由配置源: [router/index.ts](frontend/src/router/index.ts)
- 统一权限检查: [stores/permission.ts](frontend/src/stores/permission.ts)
- 集中路由守卫: [router/guard.ts](frontend/src/router/guard.ts)
- 标准权限指令: [directives/permission.ts](frontend/src/directives/permission.ts)