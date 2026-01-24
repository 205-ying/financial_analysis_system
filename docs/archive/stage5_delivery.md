# 阶段五交付文档

## 一、目标回顾

本阶段目标：**搭建 Vue3 前端工程，实现登录、token 管理、权限路由、基础后台布局**

### 核心需求
- ✅ 搭建 Vue3 + TypeScript + Vite 前端工程
- ✅ 集成 Element Plus、Pinia、Vue Router、Axios
- ✅ 工程化配置：ESLint + Prettier + TypeScript 严格模式
- ✅ 环境变量配置（开发/生产环境）
- ✅ Axios 封装：请求拦截器自动带 token，响应拦截器 401 自动跳转，统一错误提示
- ✅ 登录功能：表单校验，登录成功保存 token 与 user_info（Pinia + localStorage）
- ✅ 权限路由：根据 permissions 动态生成侧边菜单（看板、订单、费用、KPI 分析、审计日志）
- ✅ Layout 布局：左侧菜单（支持折叠）、顶部用户信息/退出、面包屑、内容区

---

## 二、技术栈

### 前端
- **Vue**: 3.4.15 (Composition API)
- **TypeScript**: 5.3.3 (strict mode)
- **Vite**: 5.0.11
- **UI 组件库**: Element Plus 2.5.3
- **状态管理**: Pinia 2.1.7 + pinia-plugin-persistedstate 3.2.1
- **路由**: Vue Router 4.2.5
- **HTTP 客户端**: Axios 1.6.5
- **代码规范**: ESLint + Prettier

### 后端（新增接口）
- **FastAPI**: 0.109.0
- **新增接口**: GET /api/v1/auth/me（获取当前用户信息）

---

## 三、前端目录结构

```
frontend/
├── public/
│   └── index.html                  # HTML 模板
├── src/
│   ├── api/                        # API 接口
│   │   └── auth.ts                 # 认证相关接口
│   ├── assets/                     # 静态资源
│   ├── components/                 # 公共组件
│   ├── layout/                     # 布局组件
│   │   ├── index.vue               # 主布局容器
│   │   └── components/
│   │       └── SidebarItem.vue     # 侧边栏菜单项
│   ├── router/                     # 路由配置
│   │   ├── index.ts                # 路由入口
│   │   └── guard.ts                # 路由守卫
│   ├── services/                   # 业务服务
│   ├── stores/                     # 状态管理
│   │   ├── index.ts                # Pinia 入口
│   │   ├── auth.ts                 # 认证状态管理
│   │   └── permission.ts           # 权限路由管理
│   ├── types/                      # 类型定义
│   │   └── api.ts                  # API 类型
│   ├── utils/                      # 工具函数
│   │   └── request.ts              # Axios 封装
│   ├── views/                      # 页面组件
│   │   ├── login/                  # 登录页
│   │   │   └── index.vue
│   │   ├── error/                  # 错误页
│   │   │   ├── 403.vue             # 无权限
│   │   │   └── 404.vue             # 页面不存在
│   │   ├── dashboard/              # 看板
│   │   │   └── index.vue
│   │   ├── orders/                 # 订单管理
│   │   │   └── index.vue
│   │   ├── expenses/               # 费用管理
│   │   │   └── index.vue
│   │   ├── kpi/                    # KPI 分析
│   │   │   └── index.vue
│   │   └── audit-logs/             # 审计日志
│   │       └── index.vue
│   ├── App.vue                     # 根组件
│   └── main.ts                     # 应用入口
├── .env.development                # 开发环境变量
├── .env.production                 # 生产环境变量
├── .eslintrc.cjs                   # ESLint 配置
├── .prettierrc.json                # Prettier 配置
├── .gitignore                      # Git 忽略配置
├── package.json                    # 项目依赖
├── tsconfig.json                   # TypeScript 配置
├── tsconfig.node.json              # Vite TypeScript 配置
└── vite.config.ts                  # Vite 配置
```

---

## 四、核心功能实现

### 1. Axios 封装（src/utils/request.ts）

```typescript
// 请求拦截器：自动添加 token
config.headers.Authorization = `Bearer ${authStore.token}`

// 响应拦截器：统一错误处理
- 401: 清除 token，跳转登录页
- 403: 跳转无权限页
- 404/500: 统一错误提示
- 业务错误(code !== 0): 显示错误消息
```

### 2. 认证状态管理（src/stores/auth.ts）

**State:**
- `token`: JWT 令牌
- `userInfo`: 用户信息
- `permissions`: 权限列表

**Actions:**
- `login(loginData)`: 登录并保存 token/userInfo/permissions
- `getUserInfo()`: 获取当前用户信息
- `logout()`: 退出登录，清除本地数据，跳转登录页
- `hasPermission(permission)`: 检查单个权限
- `hasPermissions(requiredPermissions)`: 检查多个权限（全部满足）
- `hasAnyPermission(requiredPermissions)`: 检查任一权限

**持久化:**
- localStorage 存储 token、userInfo、permissions
- 页面刷新不丢失登录状态

### 3. 权限路由管理（src/stores/permission.ts）

**动态路由:**
- `/dashboard` - 看板（权限：`dashboard:view`）
- `/orders` - 订单管理（权限：`order:view`）
- `/expenses` - 费用管理（权限：`expense:view`）
- `/kpi` - KPI 分析（权限：`kpi:view`）
- `/audit-logs` - 审计日志（权限：`audit:view`）

**Actions:**
- `generateRoutes()`: 根据用户权限过滤动态路由
- `filterAsyncRoutes(routes, permissions)`: 递归过滤路由
- `hasPermission(permissions, route)`: 检查路由权限（支持 `*:*:*` 超管权限）

### 4. 路由守卫（src/router/guard.ts）

**核心逻辑:**

```typescript
router.beforeEach(async (to, from, next) => {
  // 1. 设置页面标题
  document.title = `${to.meta.title} - 财务分析系统`
  
  // 2. 检查登录状态
  if (authStore.isLoggedIn) {
    if (to.path === '/login') {
      next('/')  // 已登录，访问登录页 -> 重定向首页
    } else {
      const hasRoutes = permissionStore.routes.length > 0
      if (hasRoutes) {
        next()  // 已生成路由，直接放行
      } else {
        // 未生成路由，动态生成
        await authStore.getUserInfo()
        const accessRoutes = permissionStore.generateRoutes()
        router.addRoute({
          path: '/',
          component: Layout,
          children: accessRoutes
        })
        router.addRoute({
          path: '/:pathMatch(.*)*',
          redirect: '/404'
        })
        next({ ...to, replace: true })  // 重新导航
      }
    }
  } else {
    // 未登录
    if (whiteList.includes(to.path)) {
      next()  // 在白名单，直接放行
    } else {
      next(`/login?redirect=${to.path}`)  // 跳转登录页
    }
  }
})
```

### 5. Layout 布局（src/layout/index.vue）

**组件结构:**
- **侧边栏**: 根据 `permissionStore.routes` 动态生成菜单，支持折叠
- **顶部栏**: 显示用户名和角色，退出按钮调用 `authStore.logout()`
- **面包屑**: 根据 `route.matched` 自动生成
- **内容区**: `<router-view>` 包裹，带过渡动画

### 6. 登录页（src/views/login/index.vue）

**功能:**
- 表单验证：用户名（2-50 字符）、密码（6-50 字符）
- 登录逻辑：调用 `authStore.login()` -> 成功跳转 redirect 或首页
- 支持 Enter 键登录
- 显示默认账号提示（admin/Admin@123, manager/Manager@123）

---

## 五、后端新增接口

### GET /api/v1/auth/me

**功能:** 获取当前登录用户的详细信息

**请求头:**
```
Authorization: Bearer <token>
```

**响应示例:**
```json
{
  "code": 0,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "系统管理员",
    "is_active": true,
    "is_superuser": true,
    "roles": ["admin"],
    "permissions": ["*:*:*"]
  }
}
```

---

## 六、验收步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动后端服务

```bash
cd backend
# 使用 start_dev.bat (Windows) 或 start_dev.sh (Linux/Mac)
./start_dev.bat
```

后端服务启动在 `http://localhost:8000`

### 3. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端服务启动在 `http://localhost:5173`

### 4. 功能测试

#### 4.1 登录测试

1. 访问 `http://localhost:5173`
2. 自动跳转到登录页 `/login`
3. 使用默认账号登录：
   - 超级管理员: `admin` / `Admin@123`
   - 普通管理员: `manager` / `Manager@123`
4. 登录成功后跳转到首页（看板页面）

#### 4.2 权限路由测试

**超级管理员（admin）:**
- 应该能看到所有菜单：看板、订单管理、费用管理、KPI 分析、审计日志
- 可以访问所有页面

**普通管理员（manager）:**
- 根据权限显示相应菜单
- 尝试手动输入无权限的 URL（如 `/audit-logs`），应该被拦截并跳转 403 页面

#### 4.3 Token 管理测试

1. 登录后刷新页面，应该保持登录状态（不会跳转登录页）
2. 清除浏览器 localStorage，刷新页面应该跳转登录页
3. 点击顶部栏"退出登录"，确认退出，应该跳转登录页

#### 4.4 后端 401 自动跳转测试

1. 登录后，使用浏览器开发者工具清除 localStorage 中的 token
2. 刷新页面或访问任意页面
3. 应该自动跳转到登录页，并显示"认证令牌无效或已过期"提示

#### 4.5 侧边栏折叠测试

1. 点击顶部栏左侧的折叠图标
2. 侧边栏应该折叠/展开，菜单项图标和文字显示正常

#### 4.6 面包屑测试

1. 访问不同页面（如订单管理、费用管理）
2. 面包屑应该显示当前路径
3. 点击面包屑可以跳转

---

## 七、权限机制说明

### 权限码格式
- `resource:action:scope`
- 示例：`order:view:*` 表示查看所有订单

### 超级管理员
- 权限码：`*:*:*`
- 拥有所有权限，可以访问所有页面

### 权限检查优先级
1. 超级管理员（`*:*:*`）-> 直接通过
2. 路由未配置 `permissions` -> 直接通过
3. 用户权限列表包含路由所需权限 -> 通过
4. 否则 -> 拒绝访问

---

## 八、环境变量配置

### 开发环境（.env.development）
```
VITE_API_BASE_URL=http://localhost:8000
```

### 生产环境（.env.production）
```
VITE_API_BASE_URL=https://api.yourdomain.com
```

**注意:** 生产环境需要将 `api.yourdomain.com` 替换为实际的后端 API 地址

---

## 九、常见问题

### Q1: 登录后刷新页面就跳转登录页？
**A:** 检查浏览器 localStorage 是否正常存储 token。确认 `pinia-plugin-persistedstate` 正确配置。

### Q2: 登录成功但看不到任何菜单？
**A:** 检查后端返回的 permissions 字段，确保权限码与前端路由配置的 `meta.permissions` 匹配。

### Q3: 手动输入 URL 可以访问无权限的页面？
**A:** 检查路由守卫是否正确执行，确认 `permissionStore.generateRoutes()` 正确过滤了路由。

### Q4: Axios 请求 401 没有自动跳转登录页？
**A:** 检查 `request.ts` 响应拦截器是否正确处理 401 状态码，确认 `authStore.logout()` 被调用。

### Q5: 生产环境构建失败？
**A:** 检查 TypeScript 类型错误，运行 `npm run type-check` 查看详细错误。

---

## 十、下一阶段规划

阶段五已完成前端基础架构，下一阶段（阶段六）将实现具体业务功能：

1. **看板页面**: KPI 数据展示、图表可视化
2. **订单管理**: 订单列表、新增/编辑/删除、搜索/筛选
3. **费用管理**: 费用类型、费用记录 CRUD、数据汇总
4. **KPI 分析**: 多维度 KPI 查询、趋势图、对比分析
5. **审计日志**: 操作日志列表、高级筛选、导出功能

---

## 十一、交付清单

### 前端
- ✅ 18 个配置文件（package.json、vite.config.ts、tsconfig 系列、eslint、prettier、env、gitignore）
- ✅ 1 个 Axios 封装（request.ts）
- ✅ 3 个 API 接口（auth.ts）
- ✅ 3 个 Pinia Store（auth.ts、permission.ts、index.ts）
- ✅ 2 个路由文件（index.ts、guard.ts）
- ✅ 2 个布局组件（layout/index.vue、SidebarItem.vue）
- ✅ 1 个登录页面（login/index.vue）
- ✅ 2 个错误页面（403.vue、404.vue）
- ✅ 5 个业务页面骨架（dashboard、orders、expenses、kpi、audit-logs）
- ✅ 2 个应用入口文件（App.vue、main.ts）

### 后端
- ✅ 1 个新增接口（GET /api/v1/auth/me）

### 文档
- ✅ 本交付文档（stage5_delivery.md）

---

## 十二、总结

阶段五成功搭建了 Vue3 前端工程，完成了以下核心目标：

1. **工程化配置**: TypeScript 严格模式、ESLint、Prettier、环境变量
2. **Axios 封装**: 请求/响应拦截器，自动带 token，统一错误处理
3. **状态管理**: Pinia + localStorage 持久化，认证和权限管理
4. **路由系统**: 动态路由生成，权限守卫，白名单机制
5. **登录功能**: 表单验证，登录逻辑，token 管理
6. **Layout 布局**: 侧边栏、顶部栏、面包屑、内容区
7. **权限控制**: 基于 permissions 的菜单显示和路由拦截

前端核心架构已完成，为后续业务功能开发奠定了坚实基础。
