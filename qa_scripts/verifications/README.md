# verifications 目录说明

用于功能验收与回归验证，适合发布前执行。

## 常用脚本

### 后端验证

```bash
python qa_scripts/verifications/backend/verify_backend_run_all.py
python qa_scripts/verifications/backend/verify_backend_import_e2e.py
python qa_scripts/verifications/backend/verify_backend_reports.py
```

### 系统级验证

```bash
python qa_scripts/verifications/system/verify_system_integrity.py
```

## 使用建议

- 合并前执行后端 run_all + 系统完整性检查
- 涉及导入或报表改动时，额外执行对应专项验证
