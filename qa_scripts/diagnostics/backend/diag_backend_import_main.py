#!/usr/bin/env python
"""调试 app.main 导入卡住的问题"""
import faulthandler
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

faulthandler.enable()
faulthandler.dump_traceback_later(5, repeat=True)

print("开始导入 app.main...", flush=True)
try:
    from app import main  # noqa: F401
    print("导入 app.main 成功", flush=True)
except Exception as exc:
    print(f"导入失败: {type(exc).__name__}: {exc}", flush=True)
    sys.exit(1)
