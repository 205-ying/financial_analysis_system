# backend 工具脚本说明

本目录用于存放后端辅助脚本，不参与线上服务请求链路。

完整 QA 脚本分类和命名规则见：`docs/qa.md`。

## 常用脚本

```bash
python tooling/api/seed_data.py
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
python tooling/api/generate_import_test_data.py
python tooling/api/reset_passwords.py
```

## 维护类脚本

```bash
python tooling/api/maintenance/performance_baseline.py --start-date 2026-01-01 --end-date 2026-01-31
python tooling/api/archive/export_api_docs.py --format both
```

## 说明

- 需要数据库的脚本会读取 `services/api/.env`
- 执行前请确认虚拟环境与依赖已安装
- 大数据生成脚本建议在测试环境运行
