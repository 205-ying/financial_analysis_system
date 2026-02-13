# generated 类型目录说明

本目录用于存放基于后端 OpenAPI 自动生成的类型文件。

## 重要约定

- `openapi.ts` 为自动生成文件，不要手工修改
- 若后端接口定义变更，需重新生成并提交

## 生成命令

在 `frontend/` 目录执行：

```bash
npm run openapi:gen
```

一致性检查：

```bash
npm run openapi:check
```

## 生成源

- 输入：`../backend/openapi.json`
- 输出：`src/types/generated/openapi.ts`
