#!/usr/bin/env python
"""测试导入app.main模块"""
import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

try:
    print("开始导入 app.main...")
    from app import main
    print("✅ 导入成功！")
    print(f"app 对象: {main.app}")
except Exception as e:
    print(f"❌ 导入失败！")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    print("\n完整堆栈追踪:")
    traceback.print_exc()
    sys.exit(1)
