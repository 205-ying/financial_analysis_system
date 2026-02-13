#!/usr/bin/env python
"""逐个测试路由模块导入"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

modules_to_test = [
    ("health", "app.api.v1.health"),
    ("auth", "app.api.v1.auth"),
    ("stores", "app.api.v1.stores"),
    ("orders", "app.api.v1.orders"),
    ("kpi", "app.api.v1.kpi"),
    ("audit", "app.api.v1.audit"),
    ("expense_types", "app.api.v1.expense_types"),
    ("expense_records", "app.api.v1.expense_records"),
    ("import_jobs", "app.api.v1.import_jobs"),
    ("reports", "app.api.v1.reports"),
    ("user_stores", "app.api.v1.user_stores"),
    ("roles", "app.api.v1.roles"),
    ("permissions", "app.api.v1.permissions"),
]

for name, module_path in modules_to_test:
    try:
        print(f"正在导入 {name:15} ({module_path})... ", end="", flush=True)
        __import__(module_path)
        print("✅")
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n" + "="*60)
print("所有路由模块导入成功！")
print("="*60)
