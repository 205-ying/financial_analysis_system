# 餐饮企业财务分析数据分析与可视化系统 —— 论文事实库（Fact Sheet, 可追溯版）

> 目的：为论文全章写作提供“统一口径 + 可追溯证据（文件与行号）”的事实底稿。  
> 规则：每条可在论文中引用的“事实”都尽量给出【证据：文件 + 行号】；暂时无法证据化的条目统一标注 **⚠️待补证据**（你后续补文件/补截图后我会立刻回填）。

---

## A. 项目概述

### A1. 系统名称
- 中文名：餐饮企业财务分析数据分析与可视化系统（简称：财务分析系统）  
  - **证据1（后端配置）**: `backend/app/core/config.py`
    ```python
    app_name: str = Field(default="餐饮企业财务分析系统", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    ```
  - **证据2（前端登录页）**: `frontend/src/views/login/index.vue`
    ```vue
    <div class="login-header">
      <h2>财务分析系统</h2>
      <p>Financial Analysis System</p>
    </div>
    ```

### A2. 系统定位
- 面向餐饮企业的“数据导入 → 清洗校验 → 财务指标计算 → 报表/看板可视化 → 审计留痕”的一体化 Web 系统。  
  - 证据（模块存在性）：数据导入任务表与错误表、状态枚举与索引等在迁移脚本中可见。:contentReference[oaicite:0]{index=0}

### A3. 目标用户
- 普通用户：查看权限范围内门店的经营/费用/订单汇总数据  
- 财务人员：导入订单/费用数据、生成报表、核对数据质量、查看 KPI  
- 管理员/超级管理员：用户/角色/权限、门店数据权限分配、审计日志查看、全局兜底授权  
  - 证据（超级用户字段）：用户模型包含 `is_superuser` 字段。:contentReference[oaicite:1]{index=1}

### A4. 核心价值
- 统一数据口径：通过导入任务（含配置映射）沉淀结构化数据，支持持续复用  
  - 证据：导入任务表含 `config(JSONB)`、行统计、错误报告路径等。:contentReference[oaicite:2]{index=2}
- 降低数据风险：导入过程可追溯、失败行可定位（row_no/field/message/raw_data）  
  - 证据：错误表字段定义（row_no/field/message/raw_data）。:contentReference[oaicite:3]{index=3}
- 强化内控：审计日志留痕（谁在何时对何资源做了何动作）  
  - ⚠️待补证据：审计日志表结构（0002_audit_log.py）与写入逻辑（audit_log_service.py）对应行号（需要你确认当前版本文件是否与迁移一致）

### A5. 主要创新点（必须可证据化）
> 创新点必须落到“代码/表结构/接口/测试用例”层面，能给出证据行号。

1. **导入任务工程化：任务表 + 错误明细表 + 状态机 + 关键索引**  
   - 证据：`data_import_jobs` 任务表字段、状态枚举、索引创建；`data_import_job_errors` 错误表字段。:contentReference[oaicite:4]{index=4}

2. **软删除与用户追踪 Mixin（提升审计与数据治理能力）**  
   - 证据：`SoftDeleteMixin(is_deleted, deleted_at)` 与 `UserTrackingMixin(created_by_id, updated_by_id)`。:contentReference[oaicite:5]{index=5}

3. **RBAC（用户-角色-权限）+ 超级管理员兜底**  
   - 证据：多对多关联表 `user_role`、`role_permission`；用户 `is_superuser` 字段。:contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}

> ⚠️待补证据（创新点候选，但缺行号支撑）：  
- “数据权限（门店维度）过滤与兜底策略”的具体实现逻辑（data_scope_service.py / deps.py）  
- “审计日志写入触发点覆盖关键操作”的接口层证据（audit.py / services / routers）

### A6. 适用场景
- 连锁餐饮：多门店经营数据归集、门店维度权限隔离  
- 单店精细化：费用结构分析、订单与费用对账、月/季报表输出  
- 教学/毕设：展示数据工程（导入/校验/追溯）、权限体系与审计能力

---

## B. 技术栈

> 仅写“证据化”的技术栈；未证据化条目标注 ⚠️。

### B1. 后端
- 框架：FastAPI  
  - ⚠️待补证据：main.py 中 FastAPI 初始化与中间件注册行号
- ORM：SQLAlchemy（Declarative）  
  - 证据：`declarative_base()` 与模型 Mixin 定义。:contentReference[oaicite:8]{index=8}
- 迁移：Alembic  
  - 证据：迁移脚本 `0003_import_jobs.py` 存在且创建表/索引。:contentReference[oaicite:9]{index=9}

### B2. 数据库
- PostgreSQL（使用 JSONB、Enum 等特性）  
  - 证据：迁移脚本中 `postgresql.JSONB` 字段。:contentReference[oaicite:10]{index=10}

### B3. 鉴权方案
- RBAC：用户-角色、角色-权限（多对多）  
  - 证据：`user_role`、`role_permission` 两个关联表定义。:contentReference[oaicite:11]{index=11}
- 超级管理员兜底：`is_superuser`  
  - 证据：字段定义。:contentReference[oaicite:12]{index=12}
- JWT：⚠️待补证据（security.py / deps.py / config.py 的 JWT 编解码、过期时间字段与刷新策略行号）

### B4. 前端
- Vue3 + 路由守卫（guard.ts）+ 权限控制（permission.ts）  
  - ⚠️待补证据：guard.ts/permission.ts 具体权限判断逻辑与路由动态注入行号
- UI/可视化组件：⚠️待补证据（dashboard/index.vue、kpi/index.vue 中的图表库引用与组件使用）

### B5. 部署方式
- ⚠️待补证据：README / development_guide 是否明确部署方式（本地/容器/反向代理等）

---

## C. 功能模块（按角色）

> 每个模块：功能点 / 输入 / 输出 / 关键校验（校验要尽量可证据化：Pydantic schema、服务层校验、权限依赖等）。

### C1. 普通用户
1. 登录 / 获取个人信息
   - 输入：用户名/密码  
   - 输出：token、用户信息  
   - 校验：密码哈希校验、账号状态校验（⚠️待补证据：security.py / auth 路由文件行号）

2. 看板（Dashboard）
   - 功能：经营数据概览、关键指标展示  
   - ⚠️待补证据：views_dashboard_index.vue 具体组件与字段口径

### C2. 财务人员
1. 订单管理（Orders）
   - 功能：查询订单、筛选、汇总  
   - ⚠️待补证据：orders.py 路由参数、SQL 聚合口径行号；views_orders_index.vue 交互

2. 费用管理（Expenses）
   - 功能：费用类型、费用记录维护/查询、统计  
   - ⚠️待补证据：expense_types.py / expense_records.py 路由与校验；views_expenses_index.vue

3. 数据导入（Import Jobs）
   - 功能：上传 Excel/CSV，导入到订单/费用/门店/费用类型等目标表；记录任务状态与错误  
   - 输入：文件、目标类型、映射配置（config）  
   - 输出：任务 id、状态、成功/失败行数、错误报告路径  
   - 校验：目标类型枚举、文件类型枚举、导入状态机  
   - 证据：`source_type`、`target_type`、`status`、`config(JSONB)`、行统计字段。:contentReference[oaicite:13]{index=13}

4. KPI（指标计算）
   - 功能：按门店/时间范围计算 KPI（毛利率、费用率、客单价等）  
   - ⚠️待补证据：kpi_calculator.py / kpi.py 的指标口径与公式行号；views_kpi_index.vue 展示字段

5. 报表（Reports）
   - 功能：报表查询、导出  
   - ⚠️待补证据：reports.py / report_service.py 的查询条件与导出格式（xlsx/csv/pdf）行号；ReportView.vue 展示口径

### C3. 管理员/超级管理员
1. 权限管理（RBAC）
   - 功能：用户-角色分配；角色-权限分配；权限码校验；超级管理员兜底  
   - 证据：RBAC 关联表定义 + is_superuser 字段。:contentReference[oaicite:14]{index=14}:contentReference[oaicite:15]{index=15}
   - ⚠️待补证据：后端 `check_permission` 实现（deps.py）与前端 permission.ts 的权限路由过滤行号

2. 门店数据权限（Data Scope）
   - 功能：按门店限制数据可见范围，防止越权查看  
   - ⚠️待补证据：data_scope_service.py / user_store.py 的数据范围算法与依赖注入行号（需要你确认最终版文件）

3. 审计日志（Audit Logs）
   - 功能：查看系统关键操作日志（导入、导出、权限变更等）  
   - ⚠️待补证据：audit.py 路由、audit_log_service 写入触发点、前端 views_audit-logs_index.vue 的字段与筛选交互行号

---

## D. 数据库（表清单 / 主键 / 关键字段 / 关系 / 索引 / 约束）

> 当前已证据化的表结构来自：模型文件、Base Mixin、导入任务迁移脚本。其余表待补迁移/模型证据。

### D1. 基础通用字段（全局口径）
- created_at / updated_at（时间戳）  
  - 证据：TimestampMixin 定义。:contentReference[oaicite:16]{index=16}
- 软删除：is_deleted / deleted_at  
  - 证据：SoftDeleteMixin 定义。:contentReference[oaicite:17]{index=17}
- 创建/更新用户追踪：created_by_id / updated_by_id  
  - 证据：UserTrackingMixin 定义。:contentReference[oaicite:18]{index=18}

### D2. 用户与权限（RBAC）
1. user（用户表）
   - 主键：id（IDMixin）  
   - 关键字段：username（唯一）、email（唯一）、password_hash、is_superuser  
   - 约束：UniqueConstraint(username/email)  
   - 证据：user 表字段与约束。:contentReference[oaicite:19]{index=19}:contentReference[oaicite:20]{index=20}
2. role（角色表）
   - ⚠️待补证据：role 表字段（code/name/desc等）与唯一约束行号（user.py 后半段未截取到）
3. permission（权限表）
   - ⚠️待补证据：permission 表字段（code/name）与约束行号（user.py 后半段未截取到）
4. user_role（用户-角色关联）
   - 复合主键：(user_id, role_id)  
   - 证据：关联表定义。:contentReference[oaicite:21]{index=21}
5. role_permission（角色-权限关联）
   - 复合主键：(role_id, permission_id)  
   - 证据：关联表定义。:contentReference[oaicite:22]{index=22}

### D3. 数据导入
1. data_import_jobs（导入任务表）
   - 主键：id  
   - 关键字段：source_type、target_type、status、file_name、file_path、total_rows、success_rows、fail_rows、error_report_path、config(JSONB)、created_by_id、created_at、updated_at  
   - 外键：created_by_id → user.id（ondelete=SET NULL）  
   - 索引：status / target_type / created_at / created_by_id  
   - 证据：字段+外键+索引定义。:contentReference[oaicite:23]{index=23}
2. data_import_job_errors（导入错误明细表）
   - 主键：id  
   - 关键字段：job_id、row_no、field、message、raw_data(JSONB)  
   - 证据：字段定义。:contentReference[oaicite:24]{index=24}

### D4. 订单/费用/门店/KPI 等业务表
- ⚠️待补证据：0001_initial.py / 对应 models（order.py、expense.py、store.py、kpi.py）中表名、主键、外键、索引、约束行号（当前未抽取到可引用片段）

---

## E. 核心接口（路径 / 方法 / 请求响应示例）

> 以 openapi.json / api-documentation.md 为准；每个接口条目必须能从 OpenAPI 追溯到行号。  
> 注意：以下“示例 JSON”是结构示例，字段以 OpenAPI schema 为准；若 schema 未抽取到则标 ⚠️。

### E1. 认证与用户
- `POST /api/v1/auth/login`
  - 说明：登录获取 token  
  - ⚠️待补证据：请求体字段与响应体 schema（需从 openapi.json 对应 schema 节点抽取）
  - 证据（接口存在）：openapi.json 路径中包含 login。:contentReference[oaicite:25]{index=25}

- `GET /api/v1/auth/me`
  - 说明：获取当前用户信息  
  - 证据（接口存在）：openapi.json paths 中包含 me。:contentReference[oaicite:26]{index=26}

### E2. 权限（RBAC）
- ⚠️待补证据：/roles /permissions /users 等管理接口是否存在（需要 openapi.json 对应 paths 片段）

### E3. 审计日志
- `GET /api/v1/audit-logs`
  - 说明：查询审计日志（支持筛选：⚠️待补证据）  
  - 证据（接口存在）：openapi.json paths 中包含 audit-logs。:contentReference[oaicite:27]{index=27}

### E4. 报表与导出
- `GET /api/v1/reports`
  - 说明：查询报表数据（时间范围、门店、维度等）  
  - 证据（接口存在）：openapi.json paths 中包含 reports。:contentReference[oaicite:28]{index=28}

- `GET /api/v1/reports/export`
  - 说明：导出报表（xlsx/csv 等：⚠️待补证据）  
  - 证据（接口存在）：openapi.json paths 中包含 export。:contentReference[oaicite:29]{index=29}

### E5. 数据导入
- `POST /api/v1/import-jobs`
  - 说明：创建导入任务/上传文件（multipart：⚠️待补证据）  
  - 证据（接口存在）：openapi.json paths 中包含 import-jobs。:contentReference[oaicite:30]{index=30}

- `GET /api/v1/import-jobs`
  - 说明：导入任务列表  
  - 证据（接口存在）：openapi.json paths 中包含 import-jobs。:contentReference[oaicite:31]{index=31}

- `GET /api/v1/import-jobs/{id}`
  - 说明：导入任务详情（含错误统计、错误明细：⚠️待补证据）  
  - 证据（接口存在）：openapi.json paths 中包含 import-jobs/{id}。:contentReference[oaicite:32]{index=32}

### E6. 订单/费用/KPI/门店
- `GET /api/v1/orders`、`GET /api/v1/expense-records`、`GET /api/v1/kpi`、`GET /api/v1/stores`
  - 证据（接口存在）：openapi.json paths 列表包含 orders/expense-records/kpi/stores。:contentReference[oaicite:33]{index=33}
  - ⚠️待补证据：各接口查询参数、返回字段口径（需抽取 openapi.json 中 parameters/schema 具体行号）

---

## F. 前端页面（清单 / 路由 / 关键交互 / 截图编号占位）

> 你已提供多个 Vue 文件，但当前未抽取到可引用的行号证据，因此先按“页面口径模板”固化，后续补证据。

### F1. 页面清单（已存在文件）
- 登录页：`views/login/index.vue` ⚠️待补证据（标题/字段/交互行号）
- 看板：`views/dashboard/index.vue` ⚠️待补证据
- 订单页：`views/orders/index.vue` ⚠️待补证据
- 费用页：`views/expenses/index.vue` ⚠️待补证据
- KPI 页：`views/kpi/index.vue` ⚠️待补证据
- 报表页：`views/reports/ReportView.vue` ⚠️待补证据
- 导入任务：`views/system/ImportJobListView.vue`、`ImportJobDetailView.vue` ⚠️待补证据
- 审计日志：`views/audit-logs/index.vue` ⚠️待补证据
- 异常页：403/404（system 文件夹中）⚠️待补证据
- 布局与侧边栏：`layout/index.vue`、`components/SidebarItem.vue` ⚠️待补证据

### F2. 路由与权限
- 路由守卫：`router/guard.ts` ⚠️待补证据（未登录跳转、白名单、动态路由加载）
- 权限判断：`permission.ts` ⚠️待补证据（meta.permissions 与后端 permission code 的映射规则）
- 状态管理：`store.ts`、API：`auth.ts` ⚠️待补证据

### F3. 截图编号占位（论文用）
- 图 F-01 登录页
- 图 F-02 看板总览
- 图 F-03 订单管理
- 图 F-04 费用管理
- 图 F-05 KPI 指标页
- 图 F-06 报表查询与导出
- 图 F-07 导入任务列表
- 图 F-08 导入任务详情/错误明细
- 图 F-09 审计日志列表
- 图 F-10 权限不足（403）

---

## G. 测试

### G1. 黑盒用例列表（模板，可直接进论文）
> 每条用例后续可补：接口路径、期望码、边界值。

1. 登录成功：正确账号密码 → 返回 token、可访问受保护接口  
2. 登录失败：错误密码 → 401/提示信息  
3. 无权限访问：无某权限访问受控接口 → 403  
4. 数据权限：用户仅能查询授权门店数据 → 结果集限制  
5. 导入任务创建：上传合法文件 → 任务状态 pending→running→success  
6. 导入任务失败：格式错误/字段缺失 → fail_rows 增加，errors 表记录  
7. 报表导出：合法查询条件 → 返回文件流（Content-Type 正确）  
8. 审计日志：关键操作后可查询到日志记录

### G2. 白盒/单元测试点（已存在测试文件，但需补证据）
- pytest：conftest.py、test_auth.py、test_permission.py、test_reports.py、test_import_jobs.py、test_kpi.py、test_data_scope.py 等  
  - ⚠️待补证据：每个测试覆盖的断言点、fixture、关键路径（需要抽取对应测试文件片段与行号）

### G3. 已发现问题与修复记录
- ⚠️待补证据：project_history.md 中的 bugfix/里程碑记录行号（或你提供 commit/issue）

---

## H. 性能与安全

### H1. 性能指标
- 并发/响应时间：⚠️待补证据（若无压测数据：建议用 locust/jmeter 生成并写入此表）

### H2. 安全策略（证据化优先）
1. 密码安全：password_hash（数据库不存明文）  
   - 证据：用户表字段为 `password_hash`。:contentReference[oaicite:34]{index=34}
   - ⚠️待补证据：具体哈希算法（bcrypt/passlib）与校验函数（security.py 行号）

2. 权限兜底：超级管理员 `is_superuser`  
   - 证据：字段定义。:contentReference[oaicite:35]{index=35}

3. 软删除：防止误删数据不可恢复（审计/追责）  
   - 证据：SoftDeleteMixin。:contentReference[oaicite:36]{index=36}

4. 审计留痕：关键操作写入 audit logs  
   - ⚠️待补证据：audit_log_service.py 写入点与字段（ip、user_agent、resource_type、action 等）

5. CORS：⚠️待补证据（main.py 中 CORSMiddleware 配置行号）

---

## I. 开发计划（里程碑 / WBS / 甘特图数据）

> 若 project_history.md / development_guide.md 未给出具体日期，先给“可填模板”。

### I1. 里程碑（模板）
- M1 需求分析完成：YYYY-MM-DD  
- M2 数据库与迁移完成：YYYY-MM-DD  
- M3 RBAC 闭环完成：YYYY-MM-DD  
- M4 导入任务闭环完成：YYYY-MM-DD  
- M5 报表&看板完成：YYYY-MM-DD  
- M6 审计日志&安全加固完成：YYYY-MM-DD  
- M7 测试与文档完成：YYYY-MM-DD  
- M8 论文撰写与答辩材料：YYYY-MM-DD

### I2. WBS（模板，可直接贴论文）
1. 项目初始化与脚手架（前后端）  
2. 数据库建模与迁移（用户/权限/业务表/导入表/审计表）  
3. 认证鉴权（JWT）  
4. RBAC 权限体系与兜底策略  
5. 门店数据权限（Data Scope）  
6. 业务模块：订单、费用、门店、KPI、报表  
7. 数据导入：任务、错误明细、重试/错误报告  
8. 审计日志：写入/查询/筛选  
9. 前端页面：路由、权限路由、页面交互与可视化  
10. 测试：单元/集成/回归  
11. 文档：API、部署、用户手册  
12. 性能与安全：CORS、限流（可选）、日志、压测

### I3. 甘特图数据（CSV 模板）
```csv
phase,task,start_date,end_date,owner,acceptance
需求分析,需求调研与用例,YYYY-MM-DD,YYYY-MM-DD,你,"需求文档通过评审"
数据库,表设计与迁移脚本,YYYY-MM-DD,YYYY-MM-DD,你,"alembic upgrade 成功"
鉴权,RBAC/JWT,YYYY-MM-DD,YYYY-MM-DD,你,"受控接口 401/403 正常"
数据导入,导入任务闭环,YYYY-MM-DD,YYYY-MM-DD,你,"成功/失败行可追溯"
报表,查询与导出,YYYY-MM-DD,YYYY-MM-DD,你,"导出文件正确"
审计,审计留痕与查询,YYYY-MM-DD,YYYY-MM-DD,你,"关键操作可检索"
测试,pytest与用例,YYYY-MM-DD,YYYY-MM-DD,你,"核心模块覆盖率达标"
论文,章节撰写,YYYY-MM-DD,YYYY-MM-DD,你,"全章口径一致"
