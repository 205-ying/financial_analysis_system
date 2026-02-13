# checks 目录说明

用于放置只读检查脚本，不做业务写入操作。

## 适用场景

- 数据库结构与字段检查
- 关键表数据状态检查
- 权限或配置完整性检查

## 运行示例

```bash
python qa_scripts/checks/backend/check_backend_data_counts.py
```

## 编写建议

- 输出结论要清晰（通过/失败）
- 失败时给出可操作的修复提示
- 避免在检查脚本中执行写操作
