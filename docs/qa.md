# QA 与验证指南

本文档合并 QA 脚本、命名规则、验收入口和性能基线采集说明。

## 1. 目录职责

```text
tooling/qa/
├─ checks/                 # 只读检查：结构、字段、权限、数据状态
├─ diagnostics/            # 故障定位：导入耗时、启动链路、依赖加载
├─ smoke_tests/            # 快速冒烟：数据库连通、模块导入、路由导入
└─ verifications/          # 功能验收与回归验证

tooling/api/
├─ seed_data.py            # 基础数据初始化
├─ generate_bulk_data.py   # 批量测试数据
├─ clean_bulk_data.py      # 批量数据清理
├─ maintenance/            # 数据库维护与性能基线脚本
└─ archive/                # 归档工具与生成脚本
```

## 2. 常用入口

```bash
python tooling/qa/verifications/system/verify_system_integrity.py
python tooling/qa/verifications/backend/verify_backend_run_all.py
python tooling/api/seed_data.py
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
```

## 3. 命名规则

脚本命名优先使用：

```text
<kind>_<scope>_<topic>.py
```

- `kind`：`check`、`smoke`、`diag`、`verify`
- `scope`：`backend`、`frontend`、`system`
- `topic`：简短描述检查或验证目标

示例：

```text
check_backend_data_counts.py
diag_backend_route_import_timing.py
smoke_backend_db_connection.py
verify_backend_reports.py
verify_system_integrity.py
```

## 4. 使用约定

- `checks/` 脚本应保持只读，不执行数据写入。
- `diagnostics/` 可以输出详细日志，但不要修改业务数据。
- `verifications/` 可以组合多个检查，用于发布前验收。
- `tooling/api/maintenance/` 中的脚本可能修改数据库，执行前需要确认目标环境。
- 需要数据库的脚本会读取 `services/api/.env`。

## 5. API 文档导出

```bash
python tooling/api/archive/export_api_docs.py --format both
```

导出的 Markdown 文档统一放在 `docs/api/backend-api.md`，OpenAPI 基线放在 `docs/api/openapi-baseline.json`。

## 6. 性能基线

性能基线用于采集后端关键查询的执行计划与耗时，形成可回归基线。

脚本位置：

```bash
python tooling/api/maintenance/performance_baseline.py --start-date 2026-01-01 --end-date 2026-01-31
```

常用参数：

- `--store-id`：限定门店
- `--expense-type-id`：限定费用类型
- `--output`：自定义输出文件

默认输出建议放入 `runtime/logs/api/test-runs/` 或自定义 runtime 路径。

基线覆盖查询：

- `orders_list`
- `expense_records_list`
- `kpi_summary_aggregate`

索引审计表：

- `order_headers`
- `expense_records`
- `kpi_daily_stores`
- `user_store_permissions`

发布前后各采集一次，重点对比：

- Execution Time
- 是否命中 Index Scan
- 是否出现大范围 Seq Scan
- 聚合阶段的缓冲区和内存开销

## 7. 回退排查顺序

1. 查询条件是否变更，例如日期函数、模糊匹配。
2. 过滤和排序字段是否有有效索引。
3. 是否需要执行 `ANALYZE`。
4. 是否引入了不必要联表或字段。
