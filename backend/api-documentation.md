# 餐饮企业财务分析系统

> ⚠️ 本文件由导出脚本自动生成，用于阅读与检索；请勿手工维护端点明细。
> 
> 如需更新：执行 `python qa_scripts/tools/backend/archive/export_api_docs.py --format both` 重新生成。

> 版本: 1.0.0
> 生成时间: 2026-01-31 20:28:49

餐饮企业财务分析与可视化系统 API

## 认证方式

- **HTTPBearer**: HTTP bearer 认证

## API 端点

### 接口列表

| 方法 | 路径 | 描述 | 标签 |
|------|------|------|------|
| `GET` | `/api/v1/health` | Health Check | 健康检查 |
| `GET` | `/api/v1/health/ready` | Readiness Check | 健康检查 |
| `GET` | `/api/v1/health/live` | Liveness Check | 健康检查 |
| `POST` | `/api/v1/auth/login` | 用户登录 | 认证 |
| `GET` | `/api/v1/auth/me` | 获取当前用户信息 | 认证 |
| `POST` | `/api/v1/auth/logout` | 用户登出 | 认证 |
| `GET` | `/api/v1/stores/all` | 获取所有门店 | 门店管理 |
| `GET` | `/api/v1/stores` | 获取门店列表 | 门店管理 |
| `POST` | `/api/v1/stores` | 创建门店 | 门店管理 |
| `GET` | `/api/v1/stores/{store_id}` | 获取门店详情 | 门店管理 |
| `PUT` | `/api/v1/stores/{store_id}` | 更新门店 | 门店管理 |
| `DELETE` | `/api/v1/stores/{store_id}` | 删除门店 | 门店管理 |
| `GET` | `/api/v1/expense-types/all` | 获取所有费用科目 | 费用科目管理 |
| `GET` | `/api/v1/expense-types` | 获取费用科目列表 | 费用科目管理 |
| `GET` | `/api/v1/expense-types/{expense_type_id}` | 获取费用科目详情 | 费用科目管理 |
| `GET` | `/api/v1/expense-records` | 获取费用记录列表 | 费用记录管理 |
| `POST` | `/api/v1/expense-records` | 创建费用记录 | 费用记录管理 |
| `GET` | `/api/v1/expense-records/export` | 导出费用记录 | 费用记录管理 |
| `GET` | `/api/v1/expense-records/{record_id}` | 获取费用记录详情 | 费用记录管理 |
| `PUT` | `/api/v1/expense-records/{record_id}` | 更新费用记录 | 费用记录管理 |
| `DELETE` | `/api/v1/expense-records/{record_id}` | 删除费用记录 | 费用记录管理 |
| `GET` | `/api/v1/orders` | 获取订单列表 | 订单管理 |
| `POST` | `/api/v1/orders` | 创建订单 | 订单管理 |
| `GET` | `/api/v1/orders/export` | 导出订单 | 订单管理 |
| `GET` | `/api/v1/orders/{order_id}` | 获取订单详情 | 订单管理 |
| `GET` | `/api/v1/kpi/daily` | 获取日常KPI数据 | KPI 数据 |
| `GET` | `/api/v1/kpi/summary` | 获取KPI汇总数据 | KPI 数据 |
| `GET` | `/api/v1/kpi/trend` | 获取KPI趋势数据 | KPI 数据 |
| `GET` | `/api/v1/kpi/expense-category` | 获取费用分类统计 | KPI 数据 |
| `GET` | `/api/v1/kpi/store-ranking` | 获取门店排名 | KPI 数据 |
| `POST` | `/api/v1/kpi/rebuild` | 重建KPI数据 | KPI 数据 |
| `GET` | `/api/v1/audit/logs` | 获取审计日志列表 | 审计日志 |
| `GET` | `/api/v1/audit/logs/{log_id}` | 获取审计日志详情 | 审计日志 |
| `GET` | `/api/v1/audit/actions` | 获取所有操作类型 | 审计日志 |
| `GET` | `/api/v1/audit/resource-types` | 获取所有资源类型 | 审计日志 |
| `POST` | `/api/v1/import-jobs` | Create Import Job | 数据导入 |
| `POST` | `/api/v1/import-jobs` | Create Import Job | 数据导入 |
| `GET` | `/api/v1/import-jobs` | List Import Jobs | 数据导入 |
| `GET` | `/api/v1/import-jobs` | List Import Jobs | 数据导入 |
| `POST` | `/api/v1/import-jobs/{job_id}/run` | Run Import Job | 数据导入 |
| `POST` | `/api/v1/import-jobs/{job_id}/run` | Run Import Job | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}` | Get Import Job | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}` | Get Import Job | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}/errors` | List Import Job Errors | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}/errors` | List Import Job Errors | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}/error-report` | Download Error Report | 数据导入 |
| `GET` | `/api/v1/import-jobs/{job_id}/error-report` | Download Error Report | 数据导入 |
| `GET` | `/api/v1/reports/daily-summary` | Get Daily Summary Report | 报表中心 |
| `GET` | `/api/v1/reports/monthly-summary` | Get Monthly Summary Report | 报表中心 |
| `GET` | `/api/v1/reports/store-performance` | Get Store Performance Report | 报表中心 |
| `GET` | `/api/v1/reports/expense-breakdown` | Get Expense Breakdown Report | 报表中心 |
| `GET` | `/api/v1/reports/export` | Export Report | 报表中心 |
| `GET` | `/api/v1/user-stores` | 查询用户的门店权限 | 用户门店权限 |
| `DELETE` | `/api/v1/user-stores` | 删除用户的所有门店权限 | 用户门店权限 |
| `POST` | `/api/v1/user-stores/assign` | 分配门店权限 | 用户门店权限 |

### 健康检查

#### GET /api/v1/health

**Health Check**

健康检查接口

检查服务状态和数据库连接

Returns:
    Dict[str, Any]: 健康状态信息

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/health/ready

**Readiness Check**

就绪状态检查

检查服务是否准备好接收请求

Returns:
    Dict[str, str]: 就绪状态

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/health/live

**Liveness Check**

存活状态检查

检查服务是否正在运行

Returns:
    Dict[str, str]: 存活状态

**响应:**

- `200`: Successful Response

---

### 认证

#### POST /api/v1/auth/login

**用户登录**

使用用户名和密码登录，返回 JWT 访问令牌

**请求体:** `LoginRequest`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/auth/me

**获取当前用户信息**

获取当前登录用户的详细信息，包含角色、权限和可访问门店

**响应:**

- `200`: Successful Response

---

#### POST /api/v1/auth/logout

**用户登出**

用户登出（前端需清除 token）

**响应:**

- `200`: Successful Response

---

### 门店管理

#### GET /api/v1/stores/all

**获取所有门店**

获取所有激活的门店（不分页）

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/stores

**获取门店列表**

获取门店列表，支持分页和筛选

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `page` | query | integer | 否 |  |
| `page_size` | query | integer | 否 |  |
| `name` | query | string | 否 |  |
| `city` | query | string | 否 |  |
| `status` | query | string | 否 |  |
| `is_active` | query | string | 否 |  |
| `order_by` | query | string | 否 |  |
| `desc` | query | boolean | 否 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/stores

**创建门店**

创建新的门店

**请求体:** `StoreCreate`

**响应:**

- `201`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/stores/{store_id}

**获取门店详情**

根据ID获取门店详情

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### PUT /api/v1/stores/{store_id}

**更新门店**

更新门店信息

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | path | integer | 是 |  |

**请求体:** `StoreUpdate`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### DELETE /api/v1/stores/{store_id}

**删除门店**

删除门店（软删除）

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 费用科目管理

#### GET /api/v1/expense-types/all

**获取所有费用科目**

获取所有激活的费用科目（不分页）

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/expense-types

**获取费用科目列表**

获取费用科目列表（支持分页）

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/expense-types/{expense_type_id}

**获取费用科目详情**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `expense_type_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 费用记录管理

#### GET /api/v1/expense-records

**获取费用记录列表**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | query | integer | 否 | 门店ID |
| `expense_type_id` | query | integer | 否 | 费用类型ID |
| `start_date` | query | string | 否 | 开始日期 |
| `end_date` | query | string | 否 | 结束日期 |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页大小 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/expense-records

**创建费用记录**

创建新的费用记录

**请求体:** `ExpenseRecordCreate`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/expense-records/export

**导出费用记录**

导出费用记录列表为Excel文件

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | query | integer | 否 | 门店ID |
| `expense_type_id` | query | integer | 否 | 费用类型ID |
| `start_date` | query | string | 否 | 开始日期 |
| `end_date` | query | string | 否 | 结束日期 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/expense-records/{record_id}

**获取费用记录详情**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `record_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### PUT /api/v1/expense-records/{record_id}

**更新费用记录**

更新费用记录信息

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `record_id` | path | integer | 是 |  |

**请求体:** `ExpenseRecordUpdate`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### DELETE /api/v1/expense-records/{record_id}

**删除费用记录**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `record_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 订单管理

#### GET /api/v1/orders

**获取订单列表**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | query | integer | 否 | 门店ID |
| `channel` | query | string | 否 | 渠道 |
| `order_no` | query | string | 否 | 订单号 |
| `start_date` | query | string | 否 | 开始日期 |
| `end_date` | query | string | 否 | 结束日期 |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页大小 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/orders

**创建订单**

创建新的订单

**请求体:** `OrderCreate`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/orders/export

**导出订单**

导出订单列表为Excel文件

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | query | integer | 否 | 门店ID |
| `channel` | query | string | 否 | 渠道 |
| `order_no` | query | string | 否 | 订单号 |
| `start_date` | query | string | 否 | 开始日期 |
| `end_date` | query | string | 否 | 结束日期 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/orders/{order_id}

**获取订单详情**

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `order_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### KPI 数据

#### GET /api/v1/kpi/daily

**获取日常KPI数据**

获取门店日常KPI数据

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `store_id` | query | integer | 否 | 门店ID |
| `date_from` | query | string | 否 | 开始日期 |
| `date_to` | query | string | 否 | 结束日期 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/kpi/summary

**获取KPI汇总数据**

获取KPI汇总统计数据

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 否 | 开始日期 |
| `end_date` | query | string | 否 | 结束日期 |
| `store_id` | query | integer | 否 | 门店ID |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/kpi/trend

**获取KPI趋势数据**

获取KPI趋势数据，支持按日、周、月聚合

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 |
| `end_date` | query | string | 是 | 结束日期 |
| `store_id` | query | integer | 否 | 门店ID |
| `granularity` | query | string | 否 | 粒度：day/week/month |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/kpi/expense-category

**获取费用分类统计**

按费用类型统计费用金额和占比

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 |
| `end_date` | query | string | 是 | 结束日期 |
| `store_id` | query | integer | 否 | 门店ID |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/kpi/store-ranking

**获取门店排名**

按营收、利润或利润率对门店进行排名

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 |
| `end_date` | query | string | 是 | 结束日期 |
| `top_n` | query | integer | 否 | Top N，999表示全部 |
| `sort_by` | query | string | 否 | 排序字段：revenue/profit/profit_margin |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/kpi/rebuild

**重建KPI数据**

重建指定日期范围的KPI数据（可选指定门店）

**请求体:** `KpiRebuildRequest`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 审计日志

#### GET /api/v1/audit/logs

**获取审计日志列表**

分页查询审计日志，支持按日期、用户、操作类型、资源类型筛选

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页数量 |
| `user_id` | query | integer | 否 | 用户ID |
| `username` | query | string | 否 | 用户名（模糊查询） |
| `action` | query | string | 否 | 操作类型 |
| `resource_type` | query | string | 否 | 资源类型 |
| `status` | query | string | 否 | 操作结果：success/failure/error |
| `start_date` | query | string | 否 | 开始日期（ISO格式） |
| `end_date` | query | string | 否 | 结束日期（ISO格式） |
| `sort_by` | query | string | 否 | 排序字段 |
| `sort_order` | query | string | 否 | 排序方式：asc/desc |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/audit/logs/{log_id}

**获取审计日志详情**

根据ID获取单条审计日志的详细信息

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `log_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/audit/actions

**获取所有操作类型**

获取系统支持的所有审计操作类型列表

**响应:**

- `200`: Successful Response

---

#### GET /api/v1/audit/resource-types

**获取所有资源类型**

获取系统支持的所有资源类型列表

**响应:**

- `200`: Successful Response

---

### 数据导入

#### POST /api/v1/import-jobs

**Create Import Job**

创建导入任务（上传文件）

- 支持 Excel (.xlsx, .xls) 和 CSV 文件
- 文件大小限制 50MB
- 订单和费用记录导入必须指定门店ID

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/import-jobs

**Create Import Job**

创建导入任务（上传文件）

- 支持 Excel (.xlsx, .xls) 和 CSV 文件
- 文件大小限制 50MB
- 订单和费用记录导入必须指定门店ID

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs

**List Import Jobs**

分页查询导入任务列表

- 支持按目标类型、状态、创建人筛选
- 默认按创建时间倒序

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `target_type` | query | string | 否 | 目标类型筛选 |
| `status` | query | string | 否 | 状态筛选 |
| `created_by_id` | query | integer | 否 | 创建用户ID筛选 |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页数量 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs

**List Import Jobs**

分页查询导入任务列表

- 支持按目标类型、状态、创建人筛选
- 默认按创建时间倒序

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `target_type` | query | string | 否 | 目标类型筛选 |
| `status` | query | string | 否 | 状态筛选 |
| `created_by_id` | query | integer | 否 | 创建用户ID筛选 |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页数量 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/import-jobs/{job_id}/run

**Run Import Job**

执行导入任务

- 解析文件内容
- 校验数据有效性
- 批量写入数据库
- 生成错误报告

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/import-jobs/{job_id}/run

**Run Import Job**

执行导入任务

- 解析文件内容
- 校验数据有效性
- 批量写入数据库
- 生成错误报告

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}

**Get Import Job**

获取导入任务详情

- 包含任务配置、创建者信息等

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}

**Get Import Job**

获取导入任务详情

- 包含任务配置、创建者信息等

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}/errors

**List Import Job Errors**

分页查询导入任务错误记录

- 按行号排序
- 每页最多200条

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页数量 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}/errors

**List Import Job Errors**

分页查询导入任务错误记录

- 按行号排序
- 每页最多200条

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |
| `page` | query | integer | 否 | 页码 |
| `page_size` | query | integer | 否 | 每页数量 |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}/error-report

**Download Error Report**

下载错误报告文件

- 返回 CSV 格式的错误明细
- 包含行号、错误字段、错误信息、原始数据

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/import-jobs/{job_id}/error-report

**Download Error Report**

下载错误报告文件

- 返回 CSV 格式的错误明细
- 包含行号、错误字段、错误信息、原始数据

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `job_id` | path | integer | 是 |  |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 报表中心

#### GET /api/v1/reports/daily-summary

**Get Daily Summary Report**

获取日汇总报表

权限: report:view

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 (YYYY-MM-DD) |
| `end_date` | query | string | 是 | 结束日期 (YYYY-MM-DD) |
| `store_id` | query | string | 否 | 门店ID（为空表示全部门店） |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/reports/monthly-summary

**Get Monthly Summary Report**

获取月汇总报表

权限: report:view

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 (YYYY-MM-DD) |
| `end_date` | query | string | 是 | 结束日期 (YYYY-MM-DD) |
| `store_id` | query | string | 否 | 门店ID（为空表示全部门店） |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/reports/store-performance

**Get Store Performance Report**

获取门店绩效报表

权限: report:view

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 (YYYY-MM-DD) |
| `end_date` | query | string | 是 | 结束日期 (YYYY-MM-DD) |
| `store_id` | query | string | 否 | 门店ID（为空表示全部门店） |
| `top_n` | query | string | 否 | TOP N排名（1-100） |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/reports/expense-breakdown

**Get Expense Breakdown Report**

获取费用明细报表

权限: report:view

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 (YYYY-MM-DD) |
| `end_date` | query | string | 是 | 结束日期 (YYYY-MM-DD) |
| `store_id` | query | string | 否 | 门店ID（为空表示全部门店） |
| `top_n` | query | string | 否 | TOP N排名（1-100） |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### GET /api/v1/reports/export

**Export Report**

导出报表为 Excel 文件

权限: report:export

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `start_date` | query | string | 是 | 开始日期 (YYYY-MM-DD) |
| `end_date` | query | string | 是 | 结束日期 (YYYY-MM-DD) |
| `store_id` | query | string | 否 | 门店ID（为空表示全部门店） |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

### 用户门店权限

#### GET /api/v1/user-stores

**查询用户的门店权限**

查询指定用户被分配的门店权限

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `user_id` | query | integer | 是 | 用户ID |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### DELETE /api/v1/user-stores

**删除用户的所有门店权限**

删除指定用户的所有门店权限

**参数:**

| 名称 | 位置 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| `user_id` | query | integer | 是 | 用户ID |

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

#### POST /api/v1/user-stores/assign

**分配门店权限**

为用户分配门店权限（覆盖式更新）

**请求体:** `UserStoreAssignRequest`

**响应:**

- `200`: Successful Response
- `422`: Validation Error

---

## 数据模型

### AuditLogListResponse

审计日志列表响应 Schema

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `total` | integer | 是 | 总记录数 |
| `page` | integer | 是 | 当前页码 |
| `page_size` | integer | 是 | 每页数量 |
| `total_pages` | integer | 是 | 总页数 |
| `items` | array | 是 | 日志列表 |

### AuditLogResponse

审计日志响应 Schema

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `action` | string | 是 | 操作类型 |
| `resource_type` | any | 否 | 资源类型 |
| `resource_id` | any | 否 | 资源ID |
| `detail` | any | 否 | 操作详情（JSON格式） |
| `ip_address` | any | 否 | 客户端IP地址 |
| `user_agent` | any | 否 | 客户端User-Agent |
| `status` | string | 否 | 操作结果：success/failure/error |
| `error_message` | any | 否 | 错误信息 |
| `id` | integer | 是 | 日志ID |
| `user_id` | any | 否 | 操作用户ID |
| `username` | any | 否 | 操作用户名 |
| `created_at` | string | 是 | 创建时间 |
| `updated_at` | string | 是 | 更新时间 |

### Body_create_import_job_api_v1_import_jobs_post

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `file` | string | 是 | 上传的 Excel 或 CSV 文件 |
| `target_type` | any | 是 | 目标数据类型 |
| `job_name` | string | 否 | 任务名称 |
| `store_id` | integer | 否 | 门店ID (订单和费用记录导入必需) |

### DailySummaryRow

日汇总行

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `biz_date` | string | 是 | 业务日期 |
| `store_id` | any | 否 | 门店ID |
| `store_name` | any | 否 | 门店名称 |
| `revenue` | string | 否 | 营业收入 |
| `net_revenue` | string | 否 | 净收入 |
| `discount_amount` | string | 否 | 优惠金额 |
| `refund_amount` | string | 否 | 退款金额 |
| `cost_total` | string | 否 | 总成本 |
| `cost_material` | string | 否 | 原材料成本 |
| `cost_labor` | string | 否 | 人工成本 |
| `expense_total` | string | 否 | 总费用 |
| `order_count` | integer | 否 | 订单数 |
| `gross_profit` | string | 否 | 毛利润 |
| `operating_profit` | string | 否 | 营业利润 |
| `gross_profit_rate` | any | 否 | 毛利率（%） |
| `operating_profit_rate` | any | 否 | 营业利润率（%） |

### ExpenseBreakdownRow

费用明细行

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `expense_type_id` | integer | 是 | 费用科目ID |
| `expense_type_code` | string | 是 | 费用科目编码 |
| `expense_type_name` | string | 是 | 费用科目名称 |
| `category` | string | 是 | 费用类别 |
| `store_id` | any | 否 | 门店ID |
| `store_name` | any | 否 | 门店名称 |
| `total_amount` | string | 否 | 费用总额 |
| `record_count` | integer | 否 | 记录笔数 |
| `avg_amount` | string | 否 | 平均单笔金额 |
| `percentage` | any | 否 | 占总费用比例（%） |

### ExpenseRecordCreate

创建费用记录请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `store_id` | integer | 是 | 门店ID |
| `expense_type_id` | integer | 是 | 费用类型ID |
| `biz_date` | string | 是 | 业务日期 |
| `amount` | any | 是 | 金额 |
| `remark` | string | 否 | 备注 |

### ExpenseRecordUpdate

更新费用记录请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `store_id` | integer | 否 | 门店ID |
| `expense_type_id` | integer | 否 | 费用类型ID |
| `biz_date` | string | 否 | 业务日期 |
| `amount` | any | 否 | 金额 |
| `remark` | string | 否 | 备注 |

### HTTPValidationError

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `detail` | array | 否 |  |

### ImportJobDetailOut

导入任务详情输出（含配置和创建者信息）

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | integer | 是 |  |
| `job_name` | string | 是 |  |
| `source_type` | ImportSourceType | 是 |  |
| `target_type` | ImportTargetType | 是 |  |
| `status` | ImportJobStatus | 是 |  |
| `file_name` | string | 是 |  |
| `total_rows` | integer | 是 |  |
| `success_rows` | integer | 是 |  |
| `fail_rows` | integer | 是 |  |
| `error_report_path` | any | 是 |  |
| `created_by_id` | any | 是 |  |
| `created_at` | string | 是 |  |
| `updated_at` | string | 是 |  |
| `config` | any | 是 |  |
| `created_by` | any | 否 |  |

### ImportJobErrorListItem

错误列表项（轻量级）

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | integer | 是 |  |
| `row_no` | integer | 是 |  |
| `field` | any | 是 |  |
| `message` | string | 是 |  |

### ImportJobListItem

导入任务列表项（轻量级）

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | integer | 是 |  |
| `job_name` | string | 是 |  |
| `target_type` | ImportTargetType | 是 |  |
| `status` | ImportJobStatus | 是 |  |
| `file_name` | string | 是 |  |
| `total_rows` | integer | 是 |  |
| `success_rows` | integer | 是 |  |
| `fail_rows` | integer | 是 |  |
| `created_by_id` | any | 是 |  |
| `created_at` | string | 是 |  |

### ImportJobOut

导入任务基础输出

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | integer | 是 |  |
| `job_name` | string | 是 |  |
| `source_type` | ImportSourceType | 是 |  |
| `target_type` | ImportTargetType | 是 |  |
| `status` | ImportJobStatus | 是 |  |
| `file_name` | string | 是 |  |
| `total_rows` | integer | 是 |  |
| `success_rows` | integer | 是 |  |
| `fail_rows` | integer | 是 |  |
| `error_report_path` | any | 是 |  |
| `created_by_id` | any | 是 |  |
| `created_at` | string | 是 |  |
| `updated_at` | string | 是 |  |

### ImportJobStatus

导入任务状态

### ImportSourceType

导入源类型

### ImportTargetType

导入目标类型

### KpiRebuildRequest

KPI重建请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `start_date` | string | 是 | 开始日期 |
| `end_date` | string | 是 | 结束日期 |
| `store_id` | integer | 否 | 门店ID（可选，不填则重建所有门店） |

### LoginRequest

登录请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

### MonthlySummaryRow

月汇总行

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `year` | integer | 是 | 年份 |
| `month` | integer | 是 | 月份 |
| `store_id` | any | 否 | 门店ID |
| `store_name` | any | 否 | 门店名称 |
| `revenue` | string | 否 | 营业收入 |
| `net_revenue` | string | 否 | 净收入 |
| `discount_amount` | string | 否 | 优惠金额 |
| `refund_amount` | string | 否 | 退款金额 |
| `cost_total` | string | 否 | 总成本 |
| `expense_total` | string | 否 | 总费用 |
| `order_count` | integer | 否 | 订单数 |
| `gross_profit` | string | 否 | 毛利润 |
| `operating_profit` | string | 否 | 营业利润 |
| `gross_profit_rate` | any | 否 | 毛利率（%） |
| `operating_profit_rate` | any | 否 | 营业利润率（%） |
| `avg_daily_revenue` | string | 否 | 日均收入 |
| `avg_daily_order_count` | string | 否 | 日均订单数 |

### OrderCreate

创建订单请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `store_id` | integer | 是 | 门店ID |
| `channel` | string | 是 | 渠道 |
| `order_no` | string | 是 | 订单号 |
| `net_amount` | any | 是 | 订单金额 |
| `order_time` | string | 是 | 订单时间 |
| `remark` | string | 否 | 备注 |

### PageData_StoreInDB_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `items` | array | 是 | 数据列表 |
| `total` | integer | 是 | 总数 |
| `page` | integer | 是 | 当前页码 |
| `page_size` | integer | 是 | 每页数量 |
| `pages` | integer | 是 | 总页数 |

### PaginatedResponse_List_ImportJobErrorListItem__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据列表 |
| `total` | integer | 否 | 总记录数 |
| `page` | integer | 否 | 当前页码 |
| `page_size` | integer | 否 | 每页数量 |

### PaginatedResponse_List_ImportJobListItem__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据列表 |
| `total` | integer | 否 | 总记录数 |
| `page` | integer | 否 | 当前页码 |
| `page_size` | integer | 否 | 每页数量 |

### Response_AuditLogListResponse_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_AuditLogResponse_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_Dict_str__Any__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_ImportJobDetailOut_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_ImportJobOut_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_DailySummaryRow__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_Dict_str__Any___

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_ExpenseBreakdownRow__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_MonthlySummaryRow__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_StoreInDB__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_StorePerformanceRow__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_dict__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_List_str__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_NoneType_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | null | 否 | 响应数据 |

### Response_PageData_StoreInDB__

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_StoreInDB_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### Response_dict_

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | integer | 否 | 状态码，0 表示成功 |
| `message` | string | 否 | 响应消息 |
| `data` | any | 否 | 响应数据 |

### StoreCreate

创建门店请求模型

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 门店名称 |
| `code` | any | 否 | 门店代码 |
| `address` | any | 否 | 门店地址 |
| `city` | any | 否 | 城市 |
| `phone` | any | 否 | 联系电话 |
| `manager` | any | 否 | 店长姓名 |
| `status` | any | 否 | 门店状态 |
| `is_active` | boolean | 否 | 是否激活 |

### StoreInDB

门店数据库模型

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 门店名称 |
| `code` | any | 否 | 门店代码 |
| `address` | any | 否 | 门店地址 |
| `city` | any | 否 | 城市 |
| `phone` | any | 否 | 联系电话 |
| `manager` | any | 否 | 店长姓名 |
| `status` | any | 否 | 门店状态 |
| `is_active` | boolean | 否 | 是否激活 |
| `id` | integer | 是 | 门店ID |
| `created_at` | string | 是 | 创建时间 |
| `updated_at` | string | 是 | 更新时间 |

### StorePerformanceRow

门店绩效行

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `store_id` | integer | 是 | 门店ID |
| `store_name` | string | 是 | 门店名称 |
| `revenue` | string | 否 | 营业收入 |
| `net_revenue` | string | 否 | 净收入 |
| `order_count` | integer | 否 | 订单数 |
| `avg_order_amount` | string | 否 | 客单价 |
| `gross_profit` | string | 否 | 毛利润 |
| `operating_profit` | string | 否 | 营业利润 |
| `gross_profit_rate` | any | 否 | 毛利率（%） |
| `operating_profit_rate` | any | 否 | 营业利润率（%） |
| `revenue_rank` | any | 否 | 营收排名 |
| `profit_rank` | any | 否 | 利润排名 |

### StoreUpdate

更新门店请求模型

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | any | 否 | 门店名称 |
| `code` | any | 否 | 门店代码 |
| `address` | any | 否 | 门店地址 |
| `city` | any | 否 | 城市 |
| `phone` | any | 否 | 联系电话 |
| `manager` | any | 否 | 店长姓名 |
| `status` | any | 否 | 门店状态 |
| `is_active` | any | 否 | 是否激活 |

### UserStoreAssignRequest

分配门店权限请求

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `user_id` | integer | 是 | 用户ID |
| `store_ids` | array | 是 | 门店ID列表 |

### ValidationError

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `loc` | array | 是 |  |
| `msg` | string | 是 |  |
| `type` | string | 是 |  |
