# QA 脚本中心

`qa_scripts/` 用于统一管理质量保障相关脚本，避免和业务代码混杂。

## 目录职责

- `checks/`：只读检查（结构、状态、数据一致性）
- `smoke_tests/`：快速连通性与模块可导入校验
- `diagnostics/`：故障定位与性能诊断
- `verifications/`：功能验收与回归验证
- `tools/backend/`：后端辅助工具脚本（初始化、维护、归档）

## 命名规则

统一格式：`<kind>_<scope>_<topic>.py`

- kind：`check` / `smoke` / `diag` / `verify`
- scope：`backend` / `frontend` / `system`

详细规则见：`qa_scripts/NAMING_RULES.md`

## 运行方式

建议在项目根目录执行脚本：

```bash
python qa_scripts/verifications/system/verify_system_integrity.py
python qa_scripts/verifications/backend/verify_backend_run_all.py
```
