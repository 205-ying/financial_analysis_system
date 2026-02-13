# 前端架构说明

## 1. 技术栈

- Vue 3 + TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios
- ECharts

## 2. 目录结构

```text
frontend/
├─ src/
│  ├─ api/                # API 模块封装
│  ├─ components/         # 通用组件
│  ├─ composables/        # 复用逻辑
│  ├─ config/             # 常量与权限路由配置
│  ├─ directives/         # 自定义指令（权限）
│  ├─ layout/             # 主布局
│  ├─ router/             # 路由与守卫
│  ├─ stores/             # Pinia 状态管理
│  ├─ types/              # TS 类型与 OpenAPI 生成类型
│  ├─ utils/              # request/format/validate 等工具
│  └─ views/              # 页面视图
├─ scripts/               # OpenAPI 类型生成脚本
└─ package.json
```

## 3. 路由与权限

- 登录白名单路由：`/login`、`/403`、`/404`
- 首次进入受保护页面时：
  1. 拉取用户信息与权限
  2. 生成动态路由
  3. 注入路由并跳转目标页面
- 权限不足时跳转 `403` 或 `404`

## 4. 状态管理

核心 Store：

- `auth`：token、用户信息、登录状态、权限校验函数
- `permission`：动态路由与菜单
- 其他业务 Store：按模块拆分（如门店、KPI 等）

## 5. HTTP 约定

统一使用 `src/utils/request.ts`：

- 请求拦截：自动附加 Bearer Token
- 响应拦截：统一处理 401/403/500
- 响应结构：对接后端统一格式 `{ code, message, data }`

## 6. 类型管理

- 手写业务类型放在 `src/types/modules/`
- OpenAPI 自动生成类型放在 `src/types/generated/openapi.ts`

生成与检查：

```bash
cd frontend
npm run openapi:gen
npm run openapi:check
```

## 7. 开发命令

```bash
cd frontend
npm run dev
npm run lint
npm run type-check
npm run test
npm run build
```

## 8. 约定与建议

- 组件文件使用 PascalCase
- 变量与函数使用 camelCase
- 页面权限优先在路由层声明，按钮权限用指令控制
- 列表页优先复用 composables，避免重复分页/筛选逻辑
