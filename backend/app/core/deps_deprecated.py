"""
⚠️ 此文件已废弃 - 请使用 app.api.deps

历史原因：
    早期依赖注入实现放在 core/ 层，后迁移到 api/ 层以符合 Clean Architecture。
    2026-01-27 删除了 app/core/deps.py 完整实现（201行），保留此转发层。

当前状态：
    此文件仅作兼容转发，防止误用旧导入路径。
    所有依赖注入已移至 app/api/deps.py（唯一权威实现）。

✅ 正确用法：
    from app.api.deps import get_current_user, get_db, check_permission

❌ 请勿使用：
    from app.core.deps import ...  # 已废弃，会触发此兼容层

如果您看到此导入，请立即修改为从 app.api.deps 导入。
"""
from app.api.deps import get_current_user, get_db, check_permission

__all__ = ["get_current_user", "get_db", "check_permission"]