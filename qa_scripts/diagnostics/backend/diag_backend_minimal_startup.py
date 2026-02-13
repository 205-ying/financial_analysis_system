#!/usr/bin/env python
"""最小化启动测试"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

print("Step 1: 导入 FastAPI...")
try:
    from fastapi import FastAPI
    print("✅  FastAPI 导入成功")
except Exception as e:
    print(f"❌ FastAPI 导入失败: {e}")
    exit(1)

print("\nStep 2: 导入 app.core.config...")
try:
    from app.core.config import settings
    print(f"✅ settings 导入成功, DATABASE_URL: {settings.database_url[:40]}...")
except Exception as e:
    print(f"❌ settings 导入失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 3: 导入 app.api.router...")
try:
    from app.api.router import api_router
    print(f"✅ api_router 导入成功")
except Exception as e:
    print(f"❌ api_router 导入失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 4: 导入 app.main...")
try:
    from app.main import app
    print(f"✅ app 导入成功: {app}")
except Exception as e:
    print(f"❌ app 导入失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("所有导入都成功！现在可以启动服务器。")
print("="*60)
