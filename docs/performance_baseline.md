# 性能基线采集指南

用于采集后端关键查询的执行计划与耗时，形成可回归基线。

## 1. 目标

- 固化核心查询 `EXPLAIN ANALYZE` 输出
- 识别索引命中与慢查询回退
- 为上线前后性能对比提供统一依据

## 2. 脚本位置

- `qa_scripts/tools/backend/maintenance/performance_baseline.py`

## 3. 执行方式

```bash
python qa_scripts/tools/backend/maintenance/performance_baseline.py --start-date 2026-01-01 --end-date 2026-01-31
```

常用参数：

- `--store-id`：限定门店
- `--expense-type-id`：限定费用类型
- `--output`：自定义输出文件

默认输出：

- `backend/logs/performance_baseline_YYYYMMDD_HHMMSS.md`

## 4. 基线覆盖查询

- `orders_list`
- `expense_records_list`
- `kpi_summary_aggregate`

索引审计表：

- `order_headers`
- `expense_records`
- `kpi_daily_stores`
- `user_store_permissions`

## 5. 对比建议

发布前后各采集一次，对比以下指标：

- Execution Time
- 是否命中 Index Scan
- 是否出现大范围 Seq Scan
- 聚合阶段的缓冲区/内存开销

## 6. 回退排查顺序

1. 查询条件是否变更（日期函数、模糊匹配）
2. 过滤和排序字段是否有有效索引
3. 是否需要执行 `ANALYZE`
4. 是否引入了不必要联表或字段
