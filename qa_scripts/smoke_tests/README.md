# smoke_tests 目录说明

用于快速验证系统关键路径是否可用。

## 适用场景

- 数据库连接可达
- 核心模块可导入
- 路由注册无阻塞错误

## 运行示例

```bash
python qa_scripts/smoke_tests/backend/smoke_backend_route_imports.py
```

## 设计原则

- 执行快（秒级）
- 依赖少
- 输出明确，便于 CI 快速失败
