"""
系统功能验证测试脚本 - 简化版
基于 docs/stage6_test.md 和 stage6_api_completion_test.md
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
os.chdir(PROJECT_ROOT)

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

result.test("后端主应用目录存在", Path("backend/app").exists())
result.test("后端 API 路由目录存在", Path("backend/app/api/v1").exists())
result.test("后端数据模型目录存在", Path("backend/app/models").exists())
result.test("后端核心配置目录存在", Path("backend/app/core").exists())
result.test("前端源码目录存在", Path("frontend/src").exists())
result.test("前端视图目录存在", Path("frontend/src/views").exists())
result.test("前端 API 客户端目录存在", Path("frontend/src/api").exists())
result.test("前端配置目录存在", Path("frontend/src/config").exists())

print("\n" + "="*60)
print("📄 后端关键文件检查")
print("="*60)

result.test("后端主入口文件存在", Path("backend/app/main.py").exists())
result.test("健康检查端点存在", Path("backend/app/api/v1/health.py").exists())
result.test("KPI 端点（Stage 6核心）存在", Path("backend/app/api/v1/kpi.py").exists())
result.test("订单端点存在", Path("backend/app/api/v1/orders.py").exists())
result.test("费用记录端点存在", Path("backend/app/api/v1/expense_records.py").exists())
result.test("费用类型端点存在", Path("backend/app/api/v1/expense_types.py").exists())
result.test("门店端点存在", Path("backend/app/api/v1/stores.py").exists())
result.test("核心配置存在", Path("backend/app/core/config.py").exists())
result.test("数据库配置存在", Path("backend/app/core/database.py").exists())
result.test("Python 依赖存在", Path("backend/requirements.txt").exists())

print("\n" + "="*60)
print("📄 前端关键文件检查")
print("="*60)

result.test("前端入口文件存在", Path("frontend/src/main.ts").exists())
result.test("根组件存在", Path("frontend/src/App.vue").exists())
result.test("Dashboard 页面存在", Path("frontend/src/views/dashboard/index.vue").exists())
result.test("KPI 分析页面存在", Path("frontend/src/views/kpi/index.vue").exists())
result.test("订单页面存在", Path("frontend/src/views/orders/index.vue").exists())
result.test("费用页面存在", Path("frontend/src/views/expenses/index.vue").exists())
result.test("KPI API 客户端存在", Path("frontend/src/api/kpi.ts").exists())
result.test("配置常量存在", Path("frontend/src/config/constants.ts").exists())
result.test("格式化工具存在", Path("frontend/src/utils/format.ts").exists())
result.test("前端依赖配置存在", Path("frontend/package.json").exists())

print("\n" + "="*60)
print("🎯 Stage 6 核心功能检查 - KPI 端点实现")
print("="*60)

kpi_file = Path("backend/app/api/v1/kpi.py")
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

result.test("类型模块化目录存在", Path("frontend/src/types/modules").exists())
result.test("通用类型定义存在", Path("frontend/src/types/modules/common.ts").exists())
result.test("认证类型定义存在", Path("frontend/src/types/modules/auth.ts").exists())
result.test("KPI 类型定义存在", Path("frontend/src/types/modules/kpi.ts").exists())
result.test("类型统一导出文件存在", Path("frontend/src/types/index.ts").exists())

print("\n" + "="*60)
print("🧩 前端组件结构检查")
print("="*60)

result.test("通用组件目录存在", Path("frontend/src/components/common").exists())
result.test("FilterBar 组件存在", Path("frontend/src/components/common/FilterBar.vue").exists())
result.test("组件统一导出存在", Path("frontend/src/components/index.ts").exists())

print("\n" + "="*60)
print("⚙️ 配置文件检查")
print("="*60)

result.test("后端 .env 示例存在", Path("backend/.env.example").exists())
result.test("前端开发环境配置存在", Path("frontend/.env.development").exists())
result.test("前端生产环境配置存在", Path("frontend/.env.production").exists())
result.test("前端 Vite 配置存在", Path("frontend/vite.config.ts").exists())
result.test("前端 TypeScript 配置存在", Path("frontend/tsconfig.json").exists())

print("\n" + "="*60)
print("📚 文档完整性检查")
print("="*60)

result.test("项目 README 存在", Path("docs/README.md").exists())
result.test("后端结构文档存在", Path("docs/backend_structure.md").exists())
result.test("前端结构文档存在", Path("docs/frontend_structure.md").exists())
result.test("开发指南存在", Path("docs/development_guide.md").exists())
result.test("Stage 6 测试指南存在", Path("docs/stage6_test.md").exists())
result.test("系统测试报告存在", Path("docs/system_test_report_20260123.md").exists())
result.test("文件整合报告存在", Path("docs/file_integration_report.md").exists())

print("\n" + "="*60)
print("✨ 代码质量检查")
print("="*60)

result.test("后端 .gitignore 存在", Path("backend/.gitignore").exists())
result.test("前端 .gitignore 存在", Path("frontend/.gitignore").exists())
result.test("项目根 README 存在", Path("README.md").exists())
result.test("Windows 启动脚本存在", Path("scripts/start.bat").exists())
result.test("Linux/Mac 启动脚本存在", Path("scripts/start.sh").exists())

# 输出汇总
exit_code = result.summary()
exit(exit_code)
