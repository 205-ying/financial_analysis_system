# diagnostics 目录说明

用于故障定位与性能分析，允许输出更详细日志。

## 适用场景

- 启动卡顿分析
- 路由导入耗时分析
- 依赖加载问题排查

## 运行示例

```bash
python tooling/qa/diagnostics/services/api/diag_backend_route_import_timing.py
```

说明：部分脚本会在 `services/api/` 下输出日志文件，请按脚本提示查看。
