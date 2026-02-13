# QA 脚本命名规范

## 统一格式

`<kind>_<scope>_<topic>.py`

- `kind`
  - `check`：只读检查
  - `smoke`：冒烟测试
  - `diag`：诊断排障
  - `verify`：验收验证
- `scope`
  - `backend` / `frontend` / `system`
- `topic`
  - 主题描述，使用 snake_case

## 示例

- `check_backend_data_counts.py`
- `smoke_backend_route_imports.py`
- `diag_backend_route_import_timing.py`
- `verify_system_integrity.py`

## 额外约定

- 文件名全部小写
- 不在 `qa_scripts/` 使用 `test_*.py`，避免与 pytest 自动发现冲突
- 批量执行入口建议命名为 `verify_<scope>_run_all.py`
