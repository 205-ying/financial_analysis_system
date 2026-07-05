"""
前端数据导入功能验收检查脚本
检查所有必需文件是否存在
"""
import os
from pathlib import Path

# 项目根目录（backend的上级目录）
PROJECT_ROOT = Path(__file__).resolve().parents[4]
FRONTEND_DIR = PROJECT_ROOT / "apps" / "web"

# 必需的文件列表
REQUIRED_FILES = [
    # 类型定义
    "src/types/modules/import_job.ts",
    
    # API封装
    "src/api/import_jobs.ts",
    
    # 页面组件
    "src/views/system/import/ImportJobListView.vue",
    "src/views/system/import/ImportJobDetailView.vue",
]

# 需要修改的文件
MODIFIED_FILES = [
    "src/types/index.ts",
    "src/stores/permission.ts",
]


def check_file_exists(file_path: str) -> tuple[bool, str]:
    """检查文件是否存在"""
    full_path = FRONTEND_DIR / file_path
    exists = full_path.exists()
    status = "✅" if exists else "❌"
    return exists, f"{status} {file_path}"


def check_file_content(file_path: str, search_text: str) -> tuple[bool, str]:
    """检查文件内容是否包含指定文本"""
    full_path = FRONTEND_DIR / file_path
    
    if not full_path.exists():
        return False, f"❌ {file_path} - 文件不存在"
    
    try:
        content = full_path.read_text(encoding='utf-8')
        contains = search_text in content
        status = "✅" if contains else "❌"
        return contains, f"{status} {file_path} - {'包含' if contains else '缺少'}: {search_text[:50]}..."
    except Exception as e:
        return False, f"❌ {file_path} - 读取失败: {e}"


def main():
    print("=" * 60)
    print("数据导入中心前端功能验收检查")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 检查新增文件
    print("\n📋 步骤1: 检查新增文件...")
    for file_path in REQUIRED_FILES:
        exists, message = check_file_exists(file_path)
        print(f"   {message}")
        if not exists:
            all_passed = False
    
    # 2. 检查类型导出
    print("\n📋 步骤2: 检查类型导出...")
    exists, message = check_file_content(
        "src/types/index.ts",
        "export * from './modules/import_job'"
    )
    print(f"   {message}")
    if not exists:
        all_passed = False
    
    # 3. 检查路由配置
    print("\n📋 步骤3: 检查路由配置...")
    checks = [
        ("src/stores/permission.ts", "Upload"),
        ("src/stores/permission.ts", "/system/import-jobs"),
        ("src/stores/permission.ts", "ImportJobListView"),
        ("src/stores/permission.ts", "ImportJobDetailView"),
        ("src/stores/permission.ts", "import_job:view"),
    ]
    
    for file_path, search_text in checks:
        exists, message = check_file_content(file_path, search_text)
        print(f"   {message}")
        if not exists:
            all_passed = False
    
    # 4. 检查权限指令
    print("\n📋 步骤4: 检查权限指令使用...")
    checks = [
        ("src/views/system/import/ImportJobListView.vue", "v-permission=\"'import_job:create'\""),
        ("src/views/system/import/ImportJobListView.vue", "v-permission=\"'import_job:run'\""),
        ("src/views/system/import/ImportJobDetailView.vue", "v-permission=\"'import_job:download'\""),
    ]
    
    for file_path, search_text in checks:
        exists, message = check_file_content(file_path, search_text)
        print(f"   {message}")
        if not exists:
            all_passed = False
    
    # 5. 检查API封装
    print("\n📋 步骤5: 检查API封装...")
    api_functions = [
        ("createImportJob", "export function createImportJob"),
        ("runImportJob", "export function runImportJob"),
        ("getImportJobList", "export function getImportJobList"),
        ("getImportJobDetail", "export function getImportJobDetail"),
        ("getImportJobErrors", "export function getImportJobErrors"),
        ("downloadErrorReport", "export async function downloadErrorReport"),
    ]
    
    for func_name, search_text in api_functions:
        exists, message = check_file_content(
            "src/api/import_jobs.ts",
            search_text
        )
        print(f"   {message}")
        if not exists:
            all_passed = False
    
    # 6. 检查类型定义
    print("\n📋 步骤6: 检查类型定义...")
    type_checks = [
        "ImportSourceType",
        "ImportTargetType",
        "ImportJobStatus",
        "ImportJob",
        "ImportJobDetail",
        "ImportJobError",
        "ImportJobStatusMap",
        "ImportTargetTypeMap",
    ]
    
    for type_name in type_checks:
        exists, message = check_file_content(
            "src/types/modules/import_job.ts",
            type_name
        )
        print(f"   {message}")
        if not exists:
            all_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！前端数据导入功能已正确实现！")
        print("\n下一步：")
        print("1. 启动后端: cd services/api && .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        print("2. 启动前端: cd apps/web && npm run dev")
        print("3. 浏览器访问: http://localhost:3000")
        print("4. 使用 admin/Admin@123 登录")
        print("5. 查看侧边栏是否显示 '数据导入' 菜单")
    else:
        print("❌ 部分检查未通过，请检查上述失败项！")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
