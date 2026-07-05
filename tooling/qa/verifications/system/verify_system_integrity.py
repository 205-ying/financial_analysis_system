"""
系统功能验证测试脚本 - 简化版

用于检查关键源码目录、配置文件、文档入口和脚本入口是否完整。
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
os.chdir(PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.failed_items = []
    
    def test(self, name, condition):
        self.total += 1
        if condition:
            self.passed += 1
            print(f"✅ {name}")
        else:
            self.failed += 1
            self.failed_items.append(name)
            print(f"❌ {name}")
    
    def summary(self):
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)
        print(f"总测试数: {self.total}")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        pass_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"通过率: {pass_rate:.1f}%\n")
        
        if self.failed > 0:
            print("失败项目:")
            for item in self.failed_items:
                print(f"  - {item}")
            print()
        
        if pass_rate == 100:
            print("🎉 所有测试通过！系统功能完整！")
            return 0
        elif pass_rate >= 90:
            print(f"⚠️  大部分测试通过，但还有 {self.failed} 项需要修复")
            return 1
        else:
            print(f"❌ 测试失败过多，需要修复 {self.failed} 项问题")
            return 1

result = TestResult()

print("="*60)
print("📁 文件系统结构检查")
print("="*60)

result.test("后端主应用目录存在", Path("services/api/app").exists())
result.test("后端 API 路由目录存在", Path("services/api/app/api/v1").exists())
result.test("后端数据模型目录存在", Path("services/api/app/models").exists())
result.test("后端核心配置目录存在", Path("services/api/app/core").exists())
result.test("前端源码目录存在", Path("apps/web/src").exists())
result.test("前端视图目录存在", Path("apps/web/src/views").exists())
result.test("前端 API 客户端目录存在", Path("apps/web/src/api").exists())
result.test("前端配置目录存在", Path("apps/web/src/config").exists())

print("\n" + "="*60)
print("📄 后端关键文件检查")
print("="*60)

result.test("后端主入口文件存在", Path("services/api/app/main.py").exists())
result.test("健康检查端点存在", Path("services/api/app/api/v1/health.py").exists())
result.test("KPI 端点（Stage 6核心）存在", Path("services/api/app/api/v1/kpi.py").exists())
result.test("订单端点存在", Path("services/api/app/api/v1/orders.py").exists())
result.test("费用记录端点存在", Path("services/api/app/api/v1/expense_records.py").exists())
result.test("费用类型端点存在", Path("services/api/app/api/v1/expense_types.py").exists())
result.test("门店端点存在", Path("services/api/app/api/v1/stores.py").exists())
result.test("核心配置存在", Path("services/api/app/core/config.py").exists())
result.test("数据库配置存在", Path("services/api/app/core/database.py").exists())
result.test("Python 依赖存在", Path("services/api/requirements.txt").exists())

print("\n" + "="*60)
print("📄 前端关键文件检查")
print("="*60)

result.test("前端入口文件存在", Path("apps/web/src/main.ts").exists())
result.test("根组件存在", Path("apps/web/src/App.vue").exists())
result.test("Dashboard 页面存在", Path("apps/web/src/views/dashboard/index.vue").exists())
result.test("KPI 分析页面存在", Path("apps/web/src/views/kpi/index.vue").exists())
result.test("订单页面存在", Path("apps/web/src/views/orders/index.vue").exists())
result.test("费用页面存在", Path("apps/web/src/views/expenses/index.vue").exists())
result.test("KPI API 客户端存在", Path("apps/web/src/api/kpi.ts").exists())
result.test("配置常量存在", Path("apps/web/src/config/constants.ts").exists())
result.test("格式化工具存在", Path("apps/web/src/utils/format.ts").exists())
result.test("前端依赖配置存在", Path("apps/web/package.json").exists())

print("\n" + "="*60)
print("🎯 Stage 6 核心功能检查 - KPI 端点实现")
print("="*60)

kpi_file = Path("services/api/app/api/v1/kpi.py")
if kpi_file.exists():
    content = kpi_file.read_text(encoding='utf-8')
    result.test("KPI Summary 端点实现", 'get_kpi_summary' in content or '@router.get("/summary")' in content)
    result.test("KPI Trend 端点实现", 'get_kpi_trend' in content or '@router.get("/trend")' in content)
    result.test("KPI Expense Category 端点实现", 'get_expense_category' in content or '@router.get("/expense-category")' in content)
    result.test("KPI Store Ranking 端点实现", 'get_store_ranking' in content or '@router.get("/store-ranking")' in content)
else:
    result.test("KPI 文件存在", False)

print("\n" + "="*60)
print("📦 前端类型定义模块化检查")
print("="*60)

result.test("类型模块化目录存在", Path("apps/web/src/types/modules").exists())
result.test("通用类型定义存在", Path("apps/web/src/types/modules/common.ts").exists())
result.test("认证类型定义存在", Path("apps/web/src/types/modules/auth.ts").exists())
result.test("KPI 类型定义存在", Path("apps/web/src/types/modules/kpi.ts").exists())
result.test("类型统一导出文件存在", Path("apps/web/src/types/index.ts").exists())

print("\n" + "="*60)
print("🧩 前端组件结构检查")
print("="*60)

result.test("通用组件目录存在", Path("apps/web/src/components/common").exists())
result.test("FilterBar 组件存在", Path("apps/web/src/components/common/FilterBar.vue").exists())
result.test("组件统一导出存在", Path("apps/web/src/components/index.ts").exists())

print("\n" + "="*60)
print("⚙️ 配置文件检查")
print("="*60)

result.test("后端 .env 示例存在", Path("services/api/.env.example").exists())
result.test("后端覆盖率配置存在", Path("services/api/.coveragerc").exists())
result.test("前端开发环境配置存在", Path("apps/web/.env.development").exists())
result.test("前端生产环境配置存在", Path("apps/web/.env.production").exists())
result.test("前端 Vite 配置存在", Path("apps/web/vite.config.ts").exists())
result.test("前端 TypeScript 配置存在", Path("apps/web/tsconfig.json").exists())

config_file = Path("services/api/app/core/config.py")
if config_file.exists():
    config_content = config_file.read_text(encoding="utf-8")
    result.test("运行时根目录配置存在", "runtime_dir" in config_content)
    result.test("上传文件目录配置存在", "upload_dir" in config_content)
    result.test("日志文件路径解析存在", "log_file_path" in config_content)
else:
    result.test("运行时根目录配置存在", False)
    result.test("上传文件目录配置存在", False)
    result.test("日志文件路径解析存在", False)

print("\n" + "="*60)
print("📚 文档完整性检查")
print("="*60)

result.test("文档中心 README 存在", Path("docs/README.md").exists())
result.test("项目结构文档存在", Path("docs/architecture/project-structure.md").exists())
result.test("开发整合文档存在", Path("docs/development.md").exists())
result.test("API 文档存在", Path("docs/api/backend-api.md").exists())
result.test("QA 整合文档存在", Path("docs/qa.md").exists())

print("\n" + "="*60)
print("✨ 代码质量检查")
print("="*60)

result.test("后端 .gitignore 存在", Path("services/api/.gitignore").exists())
result.test("前端 .gitignore 存在", Path("apps/web/.gitignore").exists())
result.test("项目根 README 存在", Path("README.md").exists())
result.test("Windows 命令入口存在", Path("dev.bat").exists())
result.test("Windows 启动脚本存在", Path("tooling/dev/start.bat").exists())
result.test("Linux/Mac 启动脚本存在", Path("tooling/dev/start.sh").exists())
result.test("运行时目录说明存在", Path("runtime/README.md").exists())
result.test("运行时目录忽略规则存在", Path("runtime/.gitignore").exists())
result.test("后端测试产物目录说明存在", Path("runtime/test-results/api/README.md").exists())

# 输出汇总
exit_code = result.summary()
exit(exit_code)
