# backend 工具脚本说明

本目录用于存放后端辅助脚本，不参与线上服务请求链路。

## 常用脚本

```bash
python qa_scripts/tools/backend/seed_data.py
python qa_scripts/tools/backend/generate_bulk_data.py
python qa_scripts/tools/backend/clean_bulk_data.py
python qa_scripts/tools/backend/generate_import_test_data.py
python qa_scripts/tools/backend/reset_passwords.py
```

## 维护类脚本

```bash
python qa_scripts/tools/backend/maintenance/performance_baseline.py --start-date 2026-01-01 --end-date 2026-01-31
python qa_scripts/tools/backend/archive/export_api_docs.py --format both
```

## 说明

- 需要数据库的脚本会读取 `backend/.env`
- 执行前请确认虚拟环境与依赖已安装
- 大数据生成脚本建议在测试环境运行
