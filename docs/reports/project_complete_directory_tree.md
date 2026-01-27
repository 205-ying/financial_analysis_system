# 餐饮企业财务分析系统 - 完整项目目录树

> 📅 生成日期: 2026年1月27日  
> 🏗️ 架构: FastAPI (后端) + Vue3 (前端)  
> 📦 版本: v1.1.0-production-ready

---

## 📊 项目统计

| 类别 | 数量 | 说明 |
|------|------|------|
| **后端文件** | 120+ | Python (FastAPI + SQLAlchemy 2.0) |
| **前端文件** | 80+ | Vue3 + TypeScript + Vite |
| **文档文件** | 45+ | Markdown (开发指南、架构文档、交付报告) |
| **测试文件** | 15+ | Pytest (后端) + 测试数据 |
| **配置文件** | 20+ | 环境配置、构建配置、CI/CD |
| **总计** | 280+ | 完整项目文件 |

---

## 📁 项目根目录

```
financial_analysis_system/
├── 📄 README.md                           # 项目总览和快速开始
├── 📄 Makefile                            # 跨平台构建脚本
├── 📄 dev.bat                             # 统一开发脚本（Windows）
├── 📄 .gitignore                          # Git 忽略配置
├── 📄 .pre-commit-config.yaml             # 代码质量检查钩子
│
├── 📁 backend/                            # 后端服务（FastAPI）
├── 📁 frontend/                           # 前端应用（Vue3）
├── 📁 docs/                               # 项目文档中心
├── 📁 scripts/                            # 跨平台工具脚本
└── 📁 .github/                            # GitHub 配置（CI/CD、Copilot）
```

---

## 🔧 后端目录结构 (backend/)

### 核心应用 (app/)

```
backend/
├── 📄 .env                                # 环境变量配置（本地，不提交）
├── 📄 .env.example                        # 环境变量模板
├── 📄 .gitignore                          # 后端 Git 忽略
├── 📄 requirements.txt                    # 生产依赖
├── 📄 requirements_dev.txt                # 开发依赖
├── 📄 pyproject.toml                      # 项目元数据和工具配置
├── 📄 pytest.ini                          # Pytest 配置
├── 📄 alembic.ini                         # Alembic 数据库迁移配置
├── 📄 dev.py                              # 开发辅助脚本
├── 📄 start_dev.bat                       # Windows 启动脚本
├── 📄 start_dev.ps1                       # PowerShell 启动脚本
│
├── 📁 app/                                # 主应用目录
│   ├── 📄 __init__.py
│   ├── 📄 main.py                         # FastAPI 应用入口 ⭐
│   │
│   ├── 📁 api/                            # API 路由层
│   │   ├── 📄 __init__.py
│   │   ├── 📄 deps.py                     # 依赖注入（数据库会话、用户认证）⭐
│   │   ├── 📄 router.py                   # API 路由注册中心 ⭐
│   │   └── 📁 v1/                         # API v1 版本端点
│   │       ├── 📄 __init__.py
│   │       ├── 📄 health.py               # 健康检查端点
│   │       ├── 📄 auth.py                 # 认证（登录、刷新token）
│   │       ├── 📄 stores.py               # 门店管理
│   │       ├── 📄 orders.py               # 订单管理
│   │       ├── 📄 expense_types.py        # 费用科目管理
│   │       ├── 📄 expense_records.py      # 费用记录管理
│   │       ├── 📄 kpi.py                  # KPI 数据查询
│   │       ├── 📄 reports.py              # 报表中心（日汇总、月汇总、绩效）
│   │       ├── 📄 import_jobs.py          # 数据导入任务
│   │       ├── 📄 audit.py                # 审计日志查询
│   │       └── 📄 user_stores.py          # 用户门店权限管理
│   │
│   ├── 📁 core/                           # 核心配置和工具
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                   # 应用配置（环境变量、CORS）⭐
│   │   ├── 📄 database.py                 # 数据库连接（AsyncSession）⭐
│   │   ├── 📄 security.py                 # JWT 认证和密码加密 ⭐
│   │   ├── 📄 exceptions.py               # 自定义异常类
│   │   ├── 📄 logging.py                  # 日志配置
│   │   ├── 📄 deps.py                     # （待整合，备用依赖注入）
│   │   └── 📄 deps_deprecated.py          # （待删除，已废弃）
│   │
│   ├── 📁 models/                         # 数据库模型（SQLAlchemy ORM）
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py                     # 基础模型类（ID、时间戳、软删除）⭐
│   │   ├── 📄 user.py                     # 用户、角色、权限模型
│   │   ├── 📄 store.py                    # 门店、产品分类、产品模型
│   │   ├── 📄 order.py                    # 订单头、订单明细模型
│   │   ├── 📄 expense.py                  # 费用科目、费用记录模型
│   │   ├── 📄 kpi.py                      # KPI 日数据模型
│   │   ├── 📄 audit_log.py                # 审计日志模型
│   │   ├── 📄 import_job.py               # 数据导入任务模型
│   │   └── 📄 user_store.py               # 用户门店权限关联模型
│   │
│   ├── 📁 schemas/                        # Pydantic 数据验证模式
│   │   ├── 📄 __init__.py
│   │   ├── 📄 common.py                   # 通用 Schema（Response、PaginatedResponse）⭐
│   │   ├── 📄 auth.py                     # 认证相关 Schema（Token、Login）
│   │   ├── 📄 store.py                    # 门店相关 Schema（CRUD）
│   │   ├── 📄 audit_log.py                # 审计日志 Schema
│   │   ├── 📄 import_job.py               # 导入任务 Schema
│   │   └── 📄 report.py                   # 报表 Schema
│   │
│   └── 📁 services/                       # 业务逻辑服务层
│       ├── 📄 __init__.py
│       ├── 📄 audit.py                    # 审计日志服务（函数式API）⭐
│       ├── 📄 audit_log_service.py        # 审计日志服务（面向对象API）⭐
│       ├── 📄 kpi_calculator.py           # KPI 计算引擎 ⭐
│       ├── 📄 data_scope_service.py       # 数据权限服务（门店访问控制）⭐
│       ├── 📄 import_service.py           # 数据导入服务（Excel/CSV）⭐
│       └── 📄 report_service.py           # 报表生成服务（Excel导出）⭐
│
├── 📁 alembic/                            # 数据库迁移脚本
│   ├── 📄 env.py                          # Alembic 环境配置
│   ├── 📄 README
│   ├── 📄 script.py.mako                  # 迁移脚本模板
│   └── 📁 versions/                       # 迁移版本文件
│       ├── 📄 0001_initial.py             # 初始表结构
│       ├── 📄 0002_audit_log.py           # 审计日志表
│       ├── 📄 0003_import_jobs.py         # 数据导入任务表
│       └── 📄 0004_user_store_permissions.py  # 用户门店权限表
│
├── 📁 scripts/                            # 维护和测试脚本
│   ├── 📄 README.md                       # 脚本使用指南 ⭐
│   ├── 📄 seed_data.py                    # 初始化种子数据 ⭐
│   ├── 📄 generate_bulk_data.py           # 生成批量测试数据
│   ├── 📄 clean_bulk_data.py              # 清理批量测试数据
│   ├── 📄 generate_import_test_data.py    # 生成导入测试数据
│   ├── 📄 add_data_scope_permission.py    # 添加数据权限到数据库
│   ├── 📄 list_users.py                   # 列出所有用户
│   ├── 📄 check_import_db.py              # 检查导入数据库状态
│   ├── 📄 test_import_e2e.py              # 导入功能端到端测试
│   │
│   ├── 📁 maintenance/                    # 数据库修复和迁移辅助（一次性）
│   │   ├── 📄 add_audit_permission.py
│   │   ├── 📄 add_soft_delete_columns.py
│   │   ├── 📄 fix_audit_log_table.py
│   │   ├── 📄 fix_detail_column.py
│   │   ├── 📄 fix_resource_column.py
│   │   └── 📄 mark_migration_done.py
│   │
│   ├── 📁 devtools/                       # 开发调试工具（原 testing/）
│   │   ├── 📄 check_audit_data.py
│   │   ├── 📄 check_audit_table.py
│   │   ├── 📄 check_users.py
│   │   ├── 📄 simple_password_test.py
│   │   └── 📄 test_password.py
│   │
│   └── 📁 verify/                         # 功能验证脚本（回归测试）
│       ├── 📄 run_all.py                  # 统一验证入口 ⭐
│       ├── 📄 verify_frontend_import.py
│       ├── 📄 verify_import_feature.py
│       └── 📄 verify_reports.py
│
├── 📁 tests/                              # 测试文件（Pytest）
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                     # Pytest 配置和 fixtures ⭐
│   ├── 📄 test_auth.py                    # 认证测试
│   ├── 📄 test_main.py                    # 主应用测试
│   ├── 📄 test_permission.py              # 权限测试
│   ├── 📄 test_kpi.py                     # KPI 测试
│   ├── 📄 test_data_scope.py              # 数据权限测试
│   ├── 📄 test_import_jobs.py             # 数据导入测试
│   ├── 📄 test_reports.py                 # 报表测试
│   └── 📁 fixtures/                       # 测试数据和 fixtures
│       └── 📁 import/                     # 导入测试数据
│           ├── 📄 README.md               # 测试数据说明
│           ├── 📄 stores_import_test.csv
│           ├── 📄 stores_import_test.xlsx
│           ├── 📄 orders_import_test.csv
│           ├── 📄 orders_import_test.xlsx
│           ├── 📄 expense_records_import_test.csv
│           ├── 📄 expense_records_import_test.xlsx
│           ├── 📄 expense_types_import_test.csv
│           └── 📄 expense_types_import_test.xlsx
│
└── 📁 logs/                               # 应用日志目录
```

---

## 🎨 前端目录结构 (frontend/)

### Vue3 应用 (src/)

```
frontend/
├── 📄 .env.development                    # 开发环境变量
├── 📄 .env.production                     # 生产环境变量
├── 📄 .env.example                        # 环境变量模板
├── 📄 .gitignore                          # 前端 Git 忽略
├── 📄 .eslintrc.cjs                       # ESLint 配置
├── 📄 .eslintrc-auto-import.json          # 自动导入 ESLint 配置
├── 📄 .prettierrc.json                    # Prettier 代码格式化
├── 📄 package.json                        # NPM 依赖和脚本
├── 📄 package-lock.json                   # 依赖锁定文件
├── 📄 tsconfig.json                       # TypeScript 配置
├── 📄 tsconfig.node.json                  # Node.js TypeScript 配置
├── 📄 vite.config.ts                      # Vite 构建配置 ⭐
├── 📄 index.html                          # HTML 入口
├── 📄 auto-imports.d.ts                   # 自动导入类型声明（生成）
├── 📄 components.d.ts                     # 组件类型声明（生成）
├── 📄 README.md
│
├── 📁 public/                             # 静态资源（空目录，保留给 Vite）
│
└── 📁 src/                                # 源代码目录
    ├── 📄 main.ts                         # 应用入口文件 ⭐
    ├── 📄 App.vue                         # 根组件
    ├── 📄 vite-env.d.ts                   # Vite 环境类型声明
    │
    ├── 📁 api/                            # API 客户端封装
    │   ├── 📄 index.ts                    # API 统一导出
    │   ├── 📄 auth.ts                     # 认证 API
    │   ├── 📄 store.ts                    # 门店 API
    │   ├── 📄 order.ts                    # 订单 API
    │   ├── 📄 expense.ts                  # 费用 API
    │   ├── 📄 kpi.ts                      # KPI API
    │   ├── 📄 reports.ts                  # 报表 API
    │   ├── 📄 import_jobs.ts              # 数据导入 API
    │   ├── 📄 audit.ts                    # 审计日志 API
    │   └── 📄 user_stores.ts              # 用户门店权限 API
    │
    ├── 📁 assets/                         # 静态资源（图片、字体等）
    │
    ├── 📁 components/                     # Vue 组件
    │   ├── 📄 index.ts                    # 组件统一导出 ⭐
    │   ├── 📄 StoreSelect.vue             # 门店选择组件
    │   ├── 📁 common/                     # 通用组件
    │   │   └── 📄 FilterBar.vue           # 筛选条件栏
    │   ├── 📁 charts/                     # 图表组件
    │   │   ├── 📄 LineChart.vue           # 折线图
    │   │   ├── 📄 BarChart.vue            # 柱状图
    │   │   └── 📄 PieChart.vue            # 饼图
    │   └── 📁 dialogs/                    # 对话框组件
    │
    ├── 📁 composables/                    # 组合式函数（Composition API）
    │   └── 📄 useECharts.ts               # ECharts 封装
    │
    ├── 📁 config/                         # 配置文件
    │   ├── 📄 index.ts                    # 配置统一导出
    │   ├── 📄 constants.ts                # 常量定义
    │   └── 📄 env.ts                      # 环境变量封装
    │
    ├── 📁 directives/                     # 自定义指令
    │   ├── 📄 index.ts                    # 指令统一导出
    │   └── 📄 permission.ts               # 权限指令（v-permission）⭐
    │
    ├── 📁 layout/                         # 布局组件
    │   ├── 📄 index.vue                   # 主布局（侧边栏+顶部栏）⭐
    │   └── 📁 components/
    │       └── 📄 SidebarItem.vue         # 侧边栏菜单项
    │
    ├── 📁 router/                         # Vue Router 路由配置
    │   ├── 📄 index.ts                    # 路由定义 ⭐
    │   └── 📄 guard.ts                    # 路由守卫（权限检查）⭐
    │
    ├── 📁 stores/                         # Pinia 状态管理
    │   ├── 📄 index.ts                    # Store 统一导出
    │   ├── 📄 auth.ts                     # 认证状态（用户、token）⭐
    │   ├── 📄 permission.ts               # 权限状态（动态路由）⭐
    │   └── 📄 store.ts                    # 门店状态
    │
    ├── 📁 types/                          # TypeScript 类型定义
    │   ├── 📄 index.ts                    # 类型统一导出
    │   └── 📁 modules/                    # 模块化类型定义
    │       ├── 📄 auth.ts                 # 认证类型
    │       ├── 📄 common.ts               # 通用类型（Response、Pagination）
    │       ├── 📄 store.ts                # 门店类型
    │       ├── 📄 order.ts                # 订单类型
    │       ├── 📄 expense.ts              # 费用类型
    │       ├── 📄 kpi.ts                  # KPI 类型
    │       ├── 📄 report.ts               # 报表类型
    │       └── 📄 import_job.ts           # 数据导入类型
    │
    ├── 📁 utils/                          # 工具函数
    │   ├── 📄 request.ts                  # Axios 封装（统一拦截器）⭐
    │   ├── 📄 format.ts                   # 格式化函数（日期、金额）
    │   └── 📄 validate.ts                 # 表单验证规则
    │
    └── 📁 views/                          # 页面视图组件
        ├── 📁 login/                      # 登录页
        │   └── 📄 index.vue
        │
        ├── 📁 dashboard/                  # 仪表盘（首页）
        │   └── 📄 index.vue
        │
        ├── 📁 orders/                     # 订单管理
        │   └── 📄 index.vue
        │
        ├── 📁 expenses/                   # 费用管理
        │   └── 📄 index.vue
        │
        ├── 📁 kpi/                        # KPI 分析
        │   └── 📄 index.vue
        │
        ├── 📁 analytics/                  # 报表中心
        │   └── 📄 ReportView.vue
        │
        ├── 📁 system/                     # 系统管理
        │   └── 📁 import/                 # 数据导入
        │       ├── 📄 ImportJobListView.vue
        │       └── 📄 ImportJobDetailView.vue
        │
        ├── 📁 audit-logs/                 # 审计日志
        │
        └── 📁 error/                      # 错误页面
            ├── 📄 403.vue                 # 无权限
            └── 📄 404.vue                 # 未找到
```

---

## 📚 文档目录结构 (docs/)

### L0 级核心文档

```
docs/
├── 📄 README.md                           # 文档索引（文档分层说明）⭐
│
├── 📌 L0 级文档（核心文档，持续维护）
├── 📄 development_guide.md                # 开发指南（启动、配置、测试）⭐
├── 📄 project_history.md                  # 项目开发历程（Stage 2-11）⭐
├── 📄 backend_structure.md                # 后端架构详解 ⭐
├── 📄 frontend_structure.md               # 前端架构详解 ⭐
├── 📄 naming_conventions.md               # 命名规范（前后端统一）⭐
│
├── 📌 L1 级文档（参考文档，归档保留）
├── 📄 optimization_complete.md            # 项目整体优化完成总结
├── 📄 backend_refactoring_guide.md        # 后端重构指南
├── 📄 dependency_guide.md                 # 依赖管理指南
├── 📄 development_roadmap.md              # 开发路线图
├── 📄 openapi_baseline.json               # API 合约基线（用于回归测试）
│
├── 📁 reports/                            # 历史报告和分析（L2 级，不再修改）
│   ├── 📄 project_structure_optimization_delivery_report.md         # 完整交付报告 ⭐
│   ├── 📄 documentation_governance_report.md             # 批次1报告
│   ├── 📄 restrained_structure_optimization_report.md       # 批次2报告
│   ├── 📄 same_function_file_integration_analysis.md       # 批次3分析
│   ├── 📄 project_complete_directory_tree.md               # 本文件 ⭐
│   ├── 📄 repository_cleanup_report.md
│   ├── 📄 repository_cleanup_changelog.md
│   ├── 📄 code_slimming_redundancy_cleanup.md
│   ├── 📄 cross_platform_consistency_audit.md
│   ├── 📄 frontend_cleanup_completion_report.md
│   ├── 📄 type_constant_deduplication_analysis.md
│   ├── 📄 page_permission_mapping.md
│   ├── 📄 project_file_directory_tree.md
│   ├── 📄 file_naming_normalization_report.md
│   ├── 📄 frontend_optimization_report.md
│   └── 📄 project_structure_optimization_report.md
│
└── 📁 archive/                            # 阶段交付文档（L2 级，历史归档）
    ├── 📄 INDEX.md                        # 归档索引（25个文档）⭐
    │
    ├── 📌 Stage 2-8 交付文档
    ├── 📄 stage2_delivery.md              # 数据库模型与迁移
    ├── 📄 stage3_delivery.md              # 业务逻辑与 API 接口
    ├── 📄 stage3_test.md
    ├── 📄 stage4_delivery.md              # KPI 计算引擎与批量运算
    ├── 📄 stage4_test.md
    ├── 📄 stage5_delivery.md              # Vue3 前端工程与权限路由
    ├── 📄 stage5_test.md
    ├── 📄 stage5_test_report.md
    ├── 📄 stage6_delivery.md              # 前端业务页面与权限指令
    ├── 📄 stage6_test.md
    ├── 📄 stage6_api_completion_summary.md
    ├── 📄 stage6_api_completion_test.md
    ├── 📄 stage6_verification_report.md
    ├── 📄 stage6_final_verification.md
    ├── 📄 stage7_delivery.md              # 系统验证与部署准备
    ├── 📄 stage7_test.md
    ├── 📄 stage7_deployment.md
    ├── 📄 stage7_summary.md
    ├── 📄 stage8_delivery.md              # 增强功能与性能优化
    │
    ├── 📌 Stage 9-11 功能专项交付
    ├── 📄 store_level_data_scope_delivery.md   # 门店级数据权限
    ├── 📄 data_import_full_delivery.md         # 数据导入中心（完整）
    ├── 📄 data_import_delivery.md              # 数据导入（后端）
    ├── 📄 data_import_file_list.md             # 数据导入文件清单
    ├── 📄 frontend_import_delivery.md          # 数据导入（前端）
    ├── 📄 reports_delivery.md                  # 报表中心（后端）
    └── 📄 reports_frontend_delivery.md         # 报表中心（前端）
```

---

## 🛠️ 跨平台脚本 (scripts/)

```
scripts/
├── 📄 start.bat                           # Windows 统一启动脚本
├── 📄 start.sh                            # Linux/Mac 统一启动脚本
└── 📄 verify_system.py                    # 系统完整性验证（57项检查）
```

---

## 🔧 GitHub 配置 (.github/)

```
.github/
├── 📄 copilot-instructions.md             # GitHub Copilot 项目指引 ⭐
└── 📁 workflows/
    └── 📄 ci.yml                          # CI/CD 配置（GitHub Actions）
```

---

## 📦 依赖和配置文件

### 根目录配置

| 文件 | 说明 |
|------|------|
| `.gitignore` | Git 忽略配置（venv、node_modules、.env 等） |
| `.pre-commit-config.yaml` | 代码提交前检查（格式化、Lint） |
| `Makefile` | 跨平台构建任务 |
| `dev.bat` | 统一开发脚本（Windows） |

### 后端依赖 (backend/)

| 文件 | 说明 |
|------|------|
| `requirements.txt` | 生产依赖（FastAPI、SQLAlchemy、Alembic 等） |
| `requirements_dev.txt` | 开发依赖（pytest、ruff、mypy 等） |
| `pyproject.toml` | 项目元数据和工具配置（ruff、mypy） |
| `pytest.ini` | Pytest 配置 |
| `alembic.ini` | Alembic 数据库迁移配置 |

### 前端依赖 (frontend/)

| 文件 | 说明 |
|------|------|
| `package.json` | NPM 依赖和脚本（Vue3、Element Plus、ECharts 等） |
| `package-lock.json` | 依赖锁定文件 |
| `tsconfig.json` | TypeScript 配置 |
| `vite.config.ts` | Vite 构建配置 |
| `.eslintrc.cjs` | ESLint 代码检查 |
| `.prettierrc.json` | Prettier 代码格式化 |

---

## 🎯 关键文件说明

### 后端关键文件 ⭐

| 文件 | 作用 | 重要度 |
|------|------|--------|
| `app/main.py` | FastAPI 应用入口，路由注册 | ⭐⭐⭐⭐⭐ |
| `app/api/deps.py` | 依赖注入（数据库会话、用户认证） | ⭐⭐⭐⭐⭐ |
| `app/api/router.py` | API 路由注册中心 | ⭐⭐⭐⭐⭐ |
| `app/core/config.py` | 应用配置（环境变量、CORS） | ⭐⭐⭐⭐⭐ |
| `app/core/database.py` | 数据库连接池 | ⭐⭐⭐⭐⭐ |
| `app/core/security.py` | JWT 认证和密码加密 | ⭐⭐⭐⭐⭐ |
| `app/models/base.py` | 基础模型类（所有模型继承） | ⭐⭐⭐⭐⭐ |
| `app/schemas/common.py` | 通用 Schema（Response、Pagination） | ⭐⭐⭐⭐ |
| `app/services/kpi_calculator.py` | KPI 计算引擎 | ⭐⭐⭐⭐ |
| `app/services/audit_log_service.py` | 审计日志服务 | ⭐⭐⭐⭐ |
| `scripts/seed_data.py` | 初始化种子数据 | ⭐⭐⭐⭐ |

### 前端关键文件 ⭐

| 文件 | 作用 | 重要度 |
|------|------|--------|
| `src/main.ts` | Vue 应用入口 | ⭐⭐⭐⭐⭐ |
| `src/router/index.ts` | 路由定义 | ⭐⭐⭐⭐⭐ |
| `src/router/guard.ts` | 路由守卫（权限检查） | ⭐⭐⭐⭐⭐ |
| `src/stores/auth.ts` | 认证状态（用户、token） | ⭐⭐⭐⭐⭐ |
| `src/stores/permission.ts` | 权限状态（动态路由） | ⭐⭐⭐⭐⭐ |
| `src/utils/request.ts` | Axios 封装（统一拦截器） | ⭐⭐⭐⭐⭐ |
| `src/directives/permission.ts` | 权限指令（v-permission） | ⭐⭐⭐⭐ |
| `src/layout/index.vue` | 主布局（侧边栏+顶部栏） | ⭐⭐⭐⭐ |
| `vite.config.ts` | Vite 构建配置 | ⭐⭐⭐⭐ |

### 文档关键文件 ⭐

| 文件 | 作用 | 重要度 |
|------|------|--------|
| `docs/README.md` | 文档索引和分层说明 | ⭐⭐⭐⭐⭐ |
| `docs/development_guide.md` | 开发指南 | ⭐⭐⭐⭐⭐ |
| `docs/backend_structure.md` | 后端架构详解 | ⭐⭐⭐⭐⭐ |
| `docs/frontend_structure.md` | 前端架构详解 | ⭐⭐⭐⭐⭐ |
| `docs/archive/INDEX.md` | 归档索引（25个文档） | ⭐⭐⭐⭐ |
| `docs/reports/project_structure_optimization_delivery_report.md` | 完整交付报告 | ⭐⭐⭐⭐ |

---

## 📊 目录约定和规范

### 后端目录约定

| 目录 | 用途 | 命名规范 |
|------|------|----------|
| `app/api/v1/` | API 端点 | snake_case (auth.py, user_stores.py) |
| `app/models/` | 数据库模型 | snake_case (order.py, user_store.py) |
| `app/schemas/` | Pydantic Schema | snake_case (common.py, import_job.py) |
| `app/services/` | 业务逻辑服务 | snake_case (kpi_calculator.py) |
| `scripts/maintenance/` | 一次性修复脚本 | snake_case (fix_*.py) |
| `scripts/devtools/` | 开发调试工具 | snake_case (check_*.py) |
| `scripts/verify/` | 功能验证脚本 | snake_case (verify_*.py) |
| `tests/` | 测试文件 | snake_case (test_*.py) |
| `tests/fixtures/` | 测试数据 | snake_case (import/) |

### 前端目录约定

| 目录 | 用途 | 命名规范 |
|------|------|----------|
| `src/api/` | API 客户端 | camelCase (auth.ts, importJobs.ts) |
| `src/components/` | Vue 组件 | PascalCase (FilterBar.vue, StoreSelect.vue) |
| `src/views/` | 页面视图 | PascalCase (index.vue, ReportView.vue) |
| `src/stores/` | Pinia Store | camelCase (auth.ts, permission.ts) |
| `src/types/modules/` | 类型定义 | camelCase (auth.ts, importJob.ts) |
| `src/utils/` | 工具函数 | camelCase (request.ts, format.ts) |
| `src/composables/` | 组合式函数 | camelCase (useECharts.ts) |

### 文档目录约定

| 目录/级别 | 用途 | 维护频率 |
|-----------|------|----------|
| **L0 级**（docs/*.md） | 核心文档 | 持续更新 |
| **L1 级**（docs/*.md） | 参考文档 | 归档保留 |
| **L2 级**（docs/reports/） | 历史报告 | 不再修改 |
| **L2 级**（docs/archive/） | 阶段交付 | 不再修改 |

---

## 🚀 快速导航

### 新手入门
1. 📄 [README.md](../../README.md) - 项目总览和快速开始
2. 📄 [docs/development_guide.md](../development_guide.md) - 开发指南
3. 📄 [docs/project_history.md](../project_history.md) - 项目发展历程

### 架构了解
1. 📄 [docs/backend_structure.md](../backend_structure.md) - 后端架构
2. 📄 [docs/frontend_structure.md](../frontend_structure.md) - 前端架构
3. 📄 [docs/naming_conventions.md](../naming_conventions.md) - 命名规范

### 脚本使用
1. 📄 [backend/scripts/README.md](../../backend/scripts/README.md) - 后端脚本指南
2. 📄 [scripts/verify_system.py](../../scripts/verify_system.py) - 系统验证

### 历史追溯
1. 📄 [docs/archive/INDEX.md](../archive/INDEX.md) - 归档索引
2. 📄 [docs/reports/project_structure_optimization_delivery_report.md](project_structure_optimization_delivery_report.md) - 最新交付报告

---

## 📝 维护说明

### 目录树更新频率
- **自动生成**: 每次重大结构变更后
- **手动更新**: 新增核心目录或文件时
- **生成命令**: 
  ```bash
  cd C:\Users\29624\Desktop\financial_analysis_system
  Get-ChildItem -Recurse -Force | Where-Object { $_.FullName -notmatch '(node_modules|venv|__pycache__|\.git\\objects|\.git\\logs|dist|\.vite|\.ruff_cache|logs\\|\.pyc$|\.pyo$)' } | Select-Object -First 500 FullName | ForEach-Object { $_.FullName -replace [regex]::Escape($PWD.Path), '' } | Sort-Object | Out-File -FilePath "project_structure_list.txt" -Encoding UTF8
  ```

### 图标说明
- ⭐ 核心文件（必读/必用）
- 📄 文件
- 📁 目录
- 📌 重要标记
- 🆕 新增
- ✅ 已完成
- ⏸️ 待处理
- ❌ 待删除

---

**生成日期**: 2026年1月27日  
**版本**: v1.0  
**维护**: 重大结构变更时更新
