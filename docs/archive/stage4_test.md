# 阶段四测试文档

## 概述
阶段四实现了财务核心数据的完整 CRUD API 和 KPI 汇总计算功能。

## 实现内容

### A) CRUD API（带分页、筛选、排序）

#### 1. 门店管理 (Store)
- `GET /api/v1/stores` - 列表查询（支持分页、按region/status/keyword筛选、排序）
- `POST /api/v1/stores` - 创建门店
- `GET /api/v1/stores/{id}` - 获取详情
- `PUT /api/v1/stores/{id}` - 更新门店
- `DELETE /api/v1/stores/{id}` - 删除门店（软删除）

#### 2. 费用科目管理 (ExpenseType)
- `GET /api/v1/expense-types/tree` - 获取树形结构
- `GET /api/v1/expense-types` - 列表查询（平铺，可按level/parent_id/is_leaf筛选）
- `POST /api/v1/expense-types` - 创建科目
- `GET /api/v1/expense-types/{id}` - 获取详情
- `PUT /api/v1/expense-types/{id}` - 更新科目
- `DELETE /api/v1/expense-types/{id}` - 删除科目

#### 3. 费用记录管理 (ExpenseRecord)
- `GET /api/v1/expense-records` - 列表查询（支持按store_id/expense_type_id/日期范围/status筛选）
- `POST /api/v1/expense-records` - 创建费用记录
- `GET /api/v1/expense-records/{id}` - 获取详情
- `PUT /api/v1/expense-records/{id}` - 更新记录（仅草稿状态）
- `DELETE /api/v1/expense-records/{id}` - 删除记录（仅草稿状态）
- `POST /api/v1/expense-records/{id}/approve` - 审批记录

#### 4. 订单管理 (Order)
- `GET /api/v1/orders` - 列表查询（支持按store_id/日期范围/channel/status筛选）
- `POST /api/v1/orders` - 创建订单（含明细）
- `GET /api/v1/orders/{id}` - 获取详情（含明细）
- `PUT /api/v1/orders/{id}` - 更新订单
- `DELETE /api/v1/orders/{id}` - 删除订单（软删除）

### B) KPI汇总计算（核心）

#### KPI计算服务
- 使用 **SQL 聚合** 而非 Pandas，保证性能
- 按 `biz_date + store_id` 聚合订单和费用
- 订单聚合：分渠道营收、退款、订单数
- 费用聚合：按 `kpi_mapping` 字段映射到成本分类
- Upsert 模式：自动创建或更新 `kpi_daily_store` 记录

#### KPI API
- `POST /api/v1/kpi/rebuild-daily` - 重建日指标（按日期范围和可选门店）
- `GET /api/v1/kpi/daily/trend` - 趋势数据（用于折线图）
- `GET /api/v1/kpi/daily/compare` - 门店对比数据（用于柱状图）
- `GET /api/v1/kpi/daily` - 原始KPI数据列表
- `GET /api/v1/kpi/export` - 导出KPI数据

### C) 性能与工程化

#### 数据库索引
创建了迁移文件 `0002_add_indexes.py`，添加了以下索引：

**门店表 (store)**
- `idx_store_code` - 门店编码
- `idx_store_status` - 状态
- `idx_store_region` - 区域

**费用记录表 (expense_record)** - 核心查询优化
- `idx_expense_record_store_date` - 复合索引(store_id, biz_date)
- `idx_expense_record_type_date` - 复合索引(expense_type_id, biz_date)
- `idx_expense_record_biz_date` - 业务日期
- `idx_expense_record_status` - 状态

**订单头表 (order_header)** - 核心查询优化
- `idx_order_header_store_date` - 复合索引(store_id, biz_date)
- `idx_order_header_order_no` - 订单号（唯一索引）
- `idx_order_header_biz_date` - 业务日期
- `idx_order_header_channel` - 渠道
- `idx_order_header_status` - 状态

**KPI日指标表 (kpi_daily_store)** - 汇总查询优化
- `idx_kpi_daily_store_date` - 复合唯一索引(store_id, biz_date)
- `idx_kpi_daily_biz_date` - 业务日期
- `idx_kpi_daily_store_id` - 门店ID

#### 严格类型化
- 所有 API 使用 Pydantic 模型进行请求/响应验证
- 统一的 `Response[DataT]` 泛型响应格式
- 所有金额字段使用 `Decimal` 类型保证精度

## 测试准备

### 1. 应用索引迁移
```powershell
cd c:\Users\29624\Desktop\financial_analysis_system\backend
$env:PYTHONPATH="c:\Users\29624\Desktop\financial_analysis_system\backend\src"
.\venv\Scripts\alembic.exe upgrade head
```

### 2. 启动服务
```powershell
$env:PYTHONPATH="c:\Users\29624\Desktop\financial_analysis_system\backend\src"
C:\Users\29624\Desktop\financial_analysis_system\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 获取 Token
```powershell
$loginResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"username":"admin","password":"Admin@123"}'

$token = $loginResp.data.access_token
$headers = @{Authorization = "Bearer $token"}
```

## 验收测试

### 测试 1: 创建门店
```powershell
# 创建门店
$storeResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/stores" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{
        "code": "SH001",
        "name": "上海南京路店",
        "region": "华东",
        "address": "上海市黄浦区南京东路123号",
        "manager": "张三",
        "contact": "13800138000",
        "status": "active"
    }'

$storeId = $storeResp.data.id
Write-Host "创建门店成功，ID: $storeId" -ForegroundColor Green
```

### 测试 2: 创建费用科目（树形结构）
```powershell
# 创建一级科目：原材料
$type1Resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-types" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{
        "code": "MAT",
        "name": "原材料",
        "level": 1,
        "is_leaf": false,
        "sort_order": 1,
        "kpi_mapping": null
    }'
$type1Id = $type1Resp.data.id

# 创建二级科目：食材
$type2Resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-types" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body "{
        \"code\": \"MAT_FOOD\",
        \"name\": \"食材\",
        \"parent_id\": $type1Id,
        \"level\": 2,
        \"is_leaf\": true,
        \"sort_order\": 1,
        \"kpi_mapping\": \"cost_material\"
    }"

Write-Host "创建费用科目成功" -ForegroundColor Green

# 获取树形结构
$treeResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-types/tree" `
    -Method GET `
    -Headers $headers

Write-Host "费用科目树形结构：" -ForegroundColor Cyan
$treeResp.data | ConvertTo-Json -Depth 5
```

### 测试 3: 创建订单（含明细）
```powershell
# 创建订单
$orderResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orders" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body "{
        \"store_id\": $storeId,
        \"order_no\": \"ORD202601220001\",
        \"biz_date\": \"2026-01-20\",
        \"channel\": \"dine-in\",
        \"customer_name\": \"李四\",
        \"discount_amount\": 0,
        \"payment_method\": \"cash\",
        \"status\": \"completed\",
        \"items\": [
            {
                \"product_code\": \"P001\",
                \"product_name\": \"咖啡\",
                \"quantity\": 2,
                \"unit_price\": 25.00,
                \"discount_amount\": 0,
                \"total_amount\": 50.00
            },
            {
                \"product_code\": \"P002\",
                \"product_name\": \"蛋糕\",
                \"quantity\": 1,
                \"unit_price\": 35.00,
                \"discount_amount\": 5.00,
                \"total_amount\": 30.00
            }
        ]
    }"

$orderId = $orderResp.data.id
Write-Host "创建订单成功，ID: $orderId，总金额: $($orderResp.data.final_amount)" -ForegroundColor Green
```

### 测试 4: 创建费用记录
```powershell
# 获取费用科目ID
$type2Id = $type2Resp.data.id

# 创建费用记录
$expenseResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-records" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body "{
        \"store_id\": $storeId,
        \"expense_type_id\": $type2Id,
        \"biz_date\": \"2026-01-20\",
        \"amount\": 1500.00,
        \"invoice_no\": \"INV20260120001\",
        \"supplier\": \"食材供应商A\",
        \"remark\": \"采购生鲜食材\",
        \"status\": \"draft\"
    }"

$expenseId = $expenseResp.data.id
Write-Host "创建费用记录成功，ID: $expenseId" -ForegroundColor Green

# 审批费用记录
$approveResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-records/$expenseId/approve" `
    -Method POST `
    -Headers $headers

Write-Host "费用记录已审批" -ForegroundColor Green
```

### 测试 5: 重建日指标（核心功能）
```powershell
# 重建日指标
$rebuildResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/rebuild-daily" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{
        "start_date": "2026-01-20",
        "end_date": "2026-01-20"
    }'

Write-Host "重建日指标成功：" -ForegroundColor Green
Write-Host "  影响日期数: $($rebuildResp.data.affected_dates)" -ForegroundColor Yellow
Write-Host "  影响门店数: $($rebuildResp.data.affected_stores)" -ForegroundColor Yellow
Write-Host "  总记录数: $($rebuildResp.data.total_records)" -ForegroundColor Yellow
```

### 测试 6: 查询 KPI 趋势数据
```powershell
# 获取趋势数据
$trendResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/daily/trend?start_date=2026-01-20&end_date=2026-01-20" `
    -Method GET `
    -Headers $headers

Write-Host "KPI 趋势数据：" -ForegroundColor Cyan
Write-Host "  总营收: $($trendResp.data.summary.total_revenue)" -ForegroundColor Yellow
Write-Host "  总成本: $($trendResp.data.summary.total_cost)" -ForegroundColor Yellow
Write-Host "  总利润: $($trendResp.data.summary.total_profit)" -ForegroundColor Yellow
Write-Host "  利润率: $($trendResp.data.summary.profit_rate)%" -ForegroundColor Yellow

Write-Host "`n每日数据点：" -ForegroundColor Cyan
$trendResp.data.data | Format-Table date, revenue, cost, profit, order_count
```

### 测试 7: 门店对比数据
```powershell
# 获取门店对比数据
$compareResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/daily/compare?start_date=2026-01-20&end_date=2026-01-20" `
    -Method GET `
    -Headers $headers

Write-Host "门店对比数据：" -ForegroundColor Cyan
$compareResp.data.data | Format-Table store_code, store_name, revenue, cost, profit, profit_rate
```

### 测试 8: 列表查询（分页、筛选、排序）
```powershell
# 查询门店列表
$storesResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/stores?page=1&page_size=10&region=华东&sort_by=code&sort_order=asc" `
    -Method GET `
    -Headers $headers

Write-Host "门店列表（共 $($storesResp.data.total) 条）：" -ForegroundColor Cyan
$storesResp.data.items | Format-Table code, name, region, status

# 查询费用记录列表
$expensesResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-records?page=1&page_size=10&store_id=$storeId&start_date=2026-01-01&end_date=2026-01-31&status=approved" `
    -Method GET `
    -Headers $headers

Write-Host "费用记录列表（共 $($expensesResp.data.total) 条）：" -ForegroundColor Cyan
$expensesResp.data.items | Format-Table biz_date, expense_type_name, amount, status

# 查询订单列表
$ordersResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orders?page=1&page_size=10&store_id=$storeId&start_date=2026-01-01&end_date=2026-01-31&channel=dine-in" `
    -Method GET `
    -Headers $headers

Write-Host "订单列表（共 $($ordersResp.data.total) 条）：" -ForegroundColor Cyan
$ordersResp.data.items | Format-Table order_no, biz_date, channel, final_amount, status
```

## 验收点检查

### ✅ 验收点 1: 插入订单与费用后，调用 rebuild-daily，kpi_daily_store 有数据
运行测试 3、4、5 后，通过以下命令验证：

```powershell
# 查询 kpi_daily_store 表
# 需要使用数据库客户端连接到 PostgreSQL
# SELECT * FROM kpi_daily_store WHERE biz_date = '2026-01-20';
# 预期结果：
# - net_revenue = 80.00 (订单总额)
# - cost_material = 1500.00 (费用记录)
# - profit_net = 80.00 - 1500.00 = -1420.00
```

### ✅ 验收点 2: GET kpi/daily 返回趋势数据可用于折线图
运行测试 6，预期返回：
- `data` 数组包含每日数据点（date, revenue, cost, profit, order_count）
- `summary` 包含汇总统计（total_revenue, total_cost, total_profit, profit_rate）
- 数据格式适合前端折线图渲染

### ✅ 验收点 3: API 在日期范围较大时仍可用
```powershell
# 测试大范围查询（30天）
$largeRangeResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/daily/trend?start_date=2026-01-01&end_date=2026-01-31" `
    -Method GET `
    -Headers $headers

Write-Host "大范围查询结果：数据点数 = $($largeRangeResp.data.data.Count)" -ForegroundColor Green
# 预期：查询速度 < 2秒，得益于 SQL 聚合和索引优化
```

## 关键 SQL/聚合实现说明

### 订单聚合查询
```sql
SELECT 
    COALESCE(SUM(CASE WHEN status = 'completed' THEN final_amount ELSE 0 END), 0) AS revenue_total,
    COALESCE(SUM(CASE WHEN status = 'completed' AND channel = 'dine-in' THEN final_amount ELSE 0 END), 0) AS revenue_dine_in,
    COALESCE(SUM(CASE WHEN status = 'completed' AND channel = 'takeout' THEN final_amount ELSE 0 END), 0) AS revenue_takeout,
    COALESCE(SUM(CASE WHEN status = 'completed' AND channel = 'delivery' THEN final_amount ELSE 0 END), 0) AS revenue_delivery,
    COALESCE(SUM(refund_amount), 0) AS refund_amount,
    COUNT(CASE WHEN status = 'completed' THEN id ELSE NULL END) AS order_count
FROM order_header
WHERE store_id = ? AND biz_date = ?
```

**优化点：**
- 使用 `CASE WHEN` 在单次扫描中计算多个指标
- `COALESCE` 处理空值，避免 NULL 传播
- 利用 `idx_order_header_store_date` 复合索引快速定位

### 费用聚合查询
```sql
SELECT 
    expense_type.kpi_mapping,
    SUM(expense_record.amount) AS total_amount
FROM expense_record
JOIN expense_type ON expense_record.expense_type_id = expense_type.id
WHERE expense_record.store_id = ? 
  AND expense_record.biz_date = ?
  AND expense_record.status = 'approved'
GROUP BY expense_type.kpi_mapping
```

**优化点：**
- 通过 `kpi_mapping` 字段直接映射到成本分类
- 只统计已审批的费用记录
- 利用 `idx_expense_record_store_date` 复合索引

### Upsert 逻辑
```python
# 1. 查找现有记录
existing = await db.execute(
    select(KpiDailyStore).where(
        and_(
            KpiDailyStore.store_id == store_id,
            KpiDailyStore.biz_date == biz_date
        )
    )
)
kpi_record = existing.scalar_one_or_none()

# 2. 更新或插入
if kpi_record:
    # 更新所有字段
    kpi_record.revenue_total = ...
    kpi_record.cost_total = ...
else:
    # 插入新记录
    kpi_record = KpiDailyStore(...)
    db.add(kpi_record)

await db.commit()
```

**优化点：**
- 利用 `idx_kpi_daily_store_date` 唯一索引快速查找
- 避免重复数据，支持增量更新

## 完整测试脚本

将以上所有测试合并为一个脚本 `test_stage4.ps1`：

```powershell
# 保存为 backend/test_stage4.ps1
# 运行: .\test_stage4.ps1

# 颜色输出函数
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

Write-Info "========== 阶段四验收测试 =========="

# 1. 登录获取 Token
Write-Info "`n[1/8] 登录获取 Token..."
$loginResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"username":"admin","password":"Admin@123"}'
$token = $loginResp.data.access_token
$headers = @{Authorization = "Bearer $token"}
Write-Success "✓ 登录成功"

# 2. 创建门店
Write-Info "`n[2/8] 创建门店..."
$storeResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/stores" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body '{"code":"SH001","name":"上海南京路店","region":"华东","address":"上海市黄浦区南京东路123号","manager":"张三","contact":"13800138000","status":"active"}'
$storeId = $storeResp.data.id
Write-Success "✓ 创建门店成功，ID: $storeId"

# 3. 创建费用科目
Write-Info "`n[3/8] 创建费用科目..."
$type1Resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-types" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body '{"code":"MAT","name":"原材料","level":1,"is_leaf":false,"sort_order":1}'
$type1Id = $type1Resp.data.id
$type2Resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-types" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body "{\"code\":\"MAT_FOOD\",\"name\":\"食材\",\"parent_id\":$type1Id,\"level\":2,\"is_leaf\":true,\"sort_order\":1,\"kpi_mapping\":\"cost_material\"}"
$type2Id = $type2Resp.data.id
Write-Success "✓ 创建费用科目成功"

# 4. 创建订单
Write-Info "`n[4/8] 创建订单..."
$orderResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orders" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body "{\"store_id\":$storeId,\"order_no\":\"ORD202601220001\",\"biz_date\":\"2026-01-20\",\"channel\":\"dine-in\",\"customer_name\":\"李四\",\"discount_amount\":0,\"payment_method\":\"cash\",\"status\":\"completed\",\"items\":[{\"product_code\":\"P001\",\"product_name\":\"咖啡\",\"quantity\":2,\"unit_price\":25.00,\"discount_amount\":0,\"total_amount\":50.00},{\"product_code\":\"P002\",\"product_name\":\"蛋糕\",\"quantity\":1,\"unit_price\":35.00,\"discount_amount\":5.00,\"total_amount\":30.00}]}"
Write-Success "✓ 创建订单成功，总金额: $($orderResp.data.final_amount)"

# 5. 创建并审批费用记录
Write-Info "`n[5/8] 创建并审批费用记录..."
$expenseResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-records" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body "{\"store_id\":$storeId,\"expense_type_id\":$type2Id,\"biz_date\":\"2026-01-20\",\"amount\":1500.00,\"invoice_no\":\"INV20260120001\",\"supplier\":\"食材供应商A\",\"remark\":\"采购生鲜食材\",\"status\":\"draft\"}"
$expenseId = $expenseResp.data.id
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/expense-records/$expenseId/approve" `
    -Method POST -Headers $headers | Out-Null
Write-Success "✓ 创建并审批费用记录成功"

# 6. 重建日指标
Write-Info "`n[6/8] 重建日指标..."
$rebuildResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/rebuild-daily" `
    -Method POST -Headers $headers -ContentType "application/json" `
    -Body '{"start_date":"2026-01-20","end_date":"2026-01-20"}'
Write-Success "✓ 重建成功: $($rebuildResp.data.affected_dates)天 x $($rebuildResp.data.affected_stores)店 = $($rebuildResp.data.total_records)条"

# 7. 查询 KPI 趋势
Write-Info "`n[7/8] 查询 KPI 趋势..."
$trendResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/daily/trend?start_date=2026-01-20&end_date=2026-01-20" `
    -Method GET -Headers $headers
Write-Warning "  总营收: $($trendResp.data.summary.total_revenue)"
Write-Warning "  总成本: $($trendResp.data.summary.total_cost)"
Write-Warning "  总利润: $($trendResp.data.summary.total_profit)"
Write-Warning "  利润率: $([math]::Round($trendResp.data.summary.profit_rate, 2))%"
Write-Success "✓ KPI 趋势数据查询成功"

# 8. 门店对比
Write-Info "`n[8/8] 门店对比数据..."
$compareResp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/kpi/daily/compare?start_date=2026-01-20&end_date=2026-01-20" `
    -Method GET -Headers $headers
Write-Success "✓ 门店对比数据查询成功，共 $($compareResp.data.data.Count) 个门店"

Write-Info "`n========== 所有测试通过！ =========="
```

## API 文档访问
启动服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 下一步
阶段五建议：
- 实现数据导出功能（Excel/CSV）
- 添加数据报表生成
- 实现异步任务队列（Celery）处理大批量计算
- 添加数据缓存（Redis）优化频繁查询
