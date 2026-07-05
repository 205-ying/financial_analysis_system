# 项目结构与架构说明

本文档说明项目当前推荐的目录组织、前后端分层和文件归位规则。

## 1. 根目录结构

```text
financial_analysis_system/
├─ services/api/            # FastAPI 后端应用、迁移、测试与后端配置
├─ apps/web/                # Vue 3 前端应用
├─ docs/                    # 项目文档中心
│  ├─ architecture/         # 架构与目录结构说明
│  ├─ development/          # 开发、依赖、运行与排障指南
│  ├─ api/                  # API 文档与 OpenAPI 基线
│  └─ qa/                   # QA、验证、性能基线说明
├─ tooling/api/             # 后端数据、维护与归档工具
├─ tooling/qa/              # 可执行检查、诊断、冒烟和验收脚本
├─ tooling/dev/             # 跨端开发启动脚本
├─ runtime/                 # 本地运行时文件边界，仅跟踪说明和忽略规则
├─ Makefile                 # Linux/Mac/CI 常用命令入口
├─ dev.bat                  # Windows 常用命令入口
└─ README.md                # 项目总览与快速开始
```

## 2. 后端结构

```text
services/api/
├─ app/
│  ├─ api/                  # 路由层：参数校验、鉴权依赖、响应封装
│  │  ├─ deps.py
│  │  ├─ router.py
│  │  └─ v1/
│  ├─ core/                 # 配置、数据库、异常、安全、日志
│  ├─ models/               # SQLAlchemy 模型
│  ├─ schemas/              # Pydantic 请求/响应模型
│  └─ services/             # 业务逻辑与事务编排
├─ alembic/                 # 数据库迁移
├─ tests/                   # pytest 测试
├─ dev.py                   # 后端开发命令入口
├─ pyproject.toml           # ruff/mypy/工具配置
├─ requirements.txt         # 运行依赖
└─ requirements_dev.txt     # 开发依赖
```

后端依赖方向：

```text
API -> Service -> Model
```

- API 层只处理参数、鉴权、响应封装和服务调用。
- Service 层承载业务规则、聚合查询和事务边界。
- Model 层只描述数据库实体与关系，不放业务流程。

## 3. 前端结构

```text
apps/web/
├─ scripts/                 # 前端专用生成脚本
├─ src/
│  ├─ api/                  # 按业务域封装接口
│  ├─ components/           # 通用组件
│  ├─ composables/          # 复用逻辑
│  ├─ config/               # 常量、环境、权限路由配置
│  ├─ directives/           # 权限等自定义指令
│  ├─ layout/               # 后台主布局
│  ├─ router/               # 静态路由与路由守卫
│  ├─ stores/               # Pinia 状态管理
│  ├─ styles/               # 全局样式、变量、主题
│  ├─ types/                # 手写类型与 OpenAPI 生成类型
│  ├─ utils/                # request、format、colors 等工具
│  └─ views/                # 页面视图
└─ package.json
```

前端路由和权限以 `src/config/permission-routes.ts` 为单一配置源。登录后由路由守卫拉取用户权限，动态生成菜单和可访问路由。

## 4. 文档归位规则

- 项目级说明统一放在 `docs/`。
- 自动生成的 API 文档放在 `docs/api/`。
- 可执行脚本说明放在 `docs/qa.md` 或对应脚本目录的局部 README。
- 根 `README.md` 只保留快速开始、目录导航和常用命令。

## 5. 脚本归位规则

- 开发启动脚本放在 `tooling/dev/`。
- 后端数据初始化、批量数据、维护脚本放在 `tooling/api/`。
- 检查、诊断、冒烟、验收脚本分别放在 `tooling/qa/checks/`、`tooling/qa/diagnostics/`、`tooling/qa/smoke_tests/`、`tooling/qa/verifications/`。

## 6. 运行时文件归位规则

- 本地日志、轮转日志、上传文件、导入错误报告统一归入 `runtime/`。
- `runtime/logs/api/` 存放 FastAPI 应用日志。
- `runtime/uploads/imports/` 存放数据导入上传源文件和错误报告。
- `runtime/test-results/api/` 存放后端覆盖率报告和测试产物。
- `runtime/` 下实际生成内容不提交到 Git，只保留 `runtime/README.md` 和 `runtime/.gitignore`。
- 生产环境可通过 `RUNTIME_DIR`、`UPLOAD_DIR`、`LOG_FILE` 配置为绝对路径或挂载卷。

## 7. 核心业务链路

1. 订单、费用、门店、商品、预算等数据进入后端业务表。
2. KPI 计算服务按门店和日期汇总到 `kpi_daily_store`。
3. 仪表盘、报表、对比分析、产品分析、预算和 CVP 模块读取业务表或 KPI 汇总表。
4. RBAC 权限控制功能入口，用户门店权限控制可访问的数据范围。

## 8. 开发注意事项

- 新接口遵循“先 Schema、再 Service、后 API 注册”的顺序。
- 大数据统计优先数据库聚合，避免 Python 层全量循环。
- 查询关联数据使用 `selectinload` 或 `joinedload` 避免 N+1。
- 涉及删除的核心业务表优先使用软删除策略。
- 文档路径变更后同步更新 `README.md` 和系统完整性验证脚本。
