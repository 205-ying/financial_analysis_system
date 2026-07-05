"""
功能验证脚本统一入口

用途：运行所有功能验证脚本，用于回归测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

import subprocess


def run_script(script_name: str, description: str) -> bool:
    """运行单个验证脚本"""
    print(f"\n{'=' * 60}")
    print(f"🔍 {description}")
    print(f"{'=' * 60}")
    
    script_path = Path(__file__).parent / script_name
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"✅ {description} - 通过")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败")
        return False
    except FileNotFoundError:
        print(f"⚠️ {description} - 脚本不存在: {script_name}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 开始运行功能验证脚本")
    print("=" * 60)
    
    # 定义验证脚本列表
    scripts = [
        ("verify_backend_import_feature.py", "数据导入功能验证"),
        ("verify_backend_frontend_import.py", "前端导入功能验证"),
        ("verify_backend_reports.py", "报表功能验证"),
    ]
    
    results = []
    for script_name, description in scripts:
        success = run_script(script_name, description)
        results.append((description, success))
    
    # 输出汇总
    print("\n" + "=" * 60)
    print("📊 验证结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {description}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有验证脚本通过！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个验证脚本失败，请检查日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
