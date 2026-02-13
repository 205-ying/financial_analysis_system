#!/usr/bin/env python
"""详细测试哪个路由模块导致启动延迟"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# 测试导入各个路由模块
modules_to_test = [
    ("health", "app.api.v1.health"),
    ("auth", "app.api.v1.auth"),
    ("stores", "app.api.v1.stores"),
    ("expense_types", "app.api.v1.expense_types"),
    ("expense_records", "app.api.v1.expense_records"),
    ("orders", "app.api.v1.orders"),
    ("kpi", "app.api.v1.kpi"),
    ("audit", "app.api.v1.audit"),
    ("import_jobs", "app.api.v1.import_jobs"),
    ("reports", "app.api.v1.reports"),
    ("user_stores", "app.api.v1.user_stores"),
    ("roles", "app.api.v1.roles"),
    ("permissions", "app.api.v1.permissions"),
]

log_path = BACKEND_DIR / "import_timing.log"
log_path.write_text("")

def log(message: str) -> None:
    log_path.write_text(log_path.read_text() + message + "\n")

print("=" * 70, flush=True)
log("开始测试路由模块导入")
print("测试各个路由模块导入时间", flush=True)
log("测试各个路由模块导入时间")
print("=" * 70, flush=True)
log("=" * 70)
print(flush=True)

total_start = time.time()
slow_modules = []

for name, module_path in modules_to_test:
    start = time.time()
    try:
        print(f"导入 {name:15} ({module_path})... ", end="", flush=True)
        log(f"开始导入: {name} ({module_path})")
        __import__(module_path)
        duration = time.time() - start
        
        if duration > 1.0:
            status = f"⚠️  慢 ({duration:.2f}s)"
            slow_modules.append((name, duration))
        elif duration > 0.5:
            status = f"⚡ 稍慢 ({duration:.2f}s)"
        else:
            status = f"✅  快 ({duration:.3f}s)"
        
        print(status, flush=True)
        log(f"导入完成: {name} - {status}")
    except Exception as e:
        duration = time.time() - start
        print(f"❌ 失败 ({duration:.2f}s): {type(e).__name__}: {e}", flush=True)
        log(f"导入失败: {name} - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

total_duration = time.time() - total_start

print(flush=True)
print("=" * 70, flush=True)
print(f"总耗时: {total_duration:.2f}s", flush=True)
log(f"总耗时: {total_duration:.2f}s")

if slow_modules:
    print(f"\n⚠️  发现 {len(slow_modules)} 个慢模块(>1s):", flush=True)
    log(f"慢模块数量: {len(slow_modules)}")
    for name, duration in slow_modules:
        print(f"  - {name}: {duration:.2f}s", flush=True)
        log(f"慢模块: {name} - {duration:.2f}s")
else:
    print("\n✅ 所有模块导入速度正常", flush=True)
    log("所有模块导入速度正常")

print("=" * 70, flush=True)
log("测试结束")
