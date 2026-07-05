# QA 脚本中心

`tooling/qa/` 用于统一管理质量保障相关脚本，避免和业务代码混杂。

完整分类、命名规则和运行约定见：

- `docs/qa.md`

常用入口：

```bash
python tooling/qa/verifications/system/verify_system_integrity.py
python tooling/qa/verifications/backend/verify_backend_run_all.py
python tooling/api/seed_data.py
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
```
