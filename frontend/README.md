# 前端应用说明

## 技术栈

- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios

## 启动与构建

```bash
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

默认开发地址：<http://localhost:3000>

## 代码质量

```bash
npm run lint
npm run format
npm run type-check
npm run test
npm run test:coverage
```

## OpenAPI 类型生成

```bash
npm run openapi:gen
npm run openapi:check
```

生成结果位于：`src/types/generated/openapi.ts`。

## 目录要点

- `src/api`：按业务域封装接口
- `src/router`：路由配置与守卫
- `src/stores`：Pinia 状态管理
- `src/views`：页面组件
- `src/utils/request.ts`：统一请求拦截与错误处理
- `src/config/permission-routes.ts`：权限与菜单单一配置源

## 开发约定

- 组件使用 PascalCase 文件名
- 业务变量与函数使用 camelCase
- 页面级权限在路由层控制，按钮级权限用权限指令
- API 变更后同步更新 OpenAPI 生成类型
