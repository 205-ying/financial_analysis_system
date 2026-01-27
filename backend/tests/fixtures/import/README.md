# 数据导入测试文件说明

## 文件列表

### 1. 订单数据 (orders_import_test)
- **用途**: 测试订单导入功能
- **记录数**: 50条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `order_no`: 订单号（唯一）
  - `biz_date`: 业务日期 (格式: YYYY-MM-DD)
  - `gross_amount`: 总金额
  - `discount_amount`: 折扣金额
  - `net_amount`: 实收金额
- **可选字段**: channel, payment_method, customer_name, customer_phone, table_no
- **导入要求**: 需要指定门店ID

### 2. 费用记录 (expense_records_import_test)
- **用途**: 测试费用记录导入功能
- **记录数**: 30条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `expense_type_code`: 费用科目编码（需在系统中存在）
  - `biz_date`: 业务日期 (格式: YYYY-MM-DD)
  - `amount`: 金额
- **可选字段**: payment_method, vendor, description, invoice_no
- **导入要求**: 需要指定门店ID
- **注意**: 费用科目编码必须与系统中的数据匹配，参考：
  - EXP_MATERIAL_FOOD (食材采购)
  - EXP_MATERIAL_BEV (饮料采购)
  - EXP_LABOR_SALARY (员工工资)
  - EXP_RENT (租金)
  - EXP_UTILITIES_ELEC (电费)
  - EXP_UTILITIES_WATER (水费)
  - EXP_MARKETING_AD (广告费用)

### 3. 门店信息 (stores_import_test)
- **用途**: 测试门店导入功能
- **记录数**: 5条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `code`: 门店编码（唯一）
  - `name`: 门店名称
- **可选字段**: address, phone, contact_person, business_hours, area_sqm, is_active
- **注意**: 门店编码不能与现有门店重复

### 4. 费用科目 (expense_types_import_test)
- **用途**: 测试费用科目导入功能
- **记录数**: 10条（5个一级科目，5个二级科目）
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `type_code`: 科目编码（唯一）
  - `name`: 科目名称
  - `level`: 层级 (1 或 2)
  - `category`: 分类 (cost|expense|tax)
- **可选字段**: parent_code, description, is_active, sort_order
- **注意**: 
  - 二级科目的 parent_code 必须指向已存在的一级科目
  - 科目编码不能与现有科目重复

## 使用方法

### 通过前端页面导入
1. 登录系统
2. 进入"数据导入"页面
3. 选择导入类型（订单数据、费用记录、门店信息、费用科目）
4. 选择对应的测试文件（.xlsx 或 .csv）
5. 如果是订单或费用记录，需要选择门店
6. 点击"导入数据"按钮
7. 等待处理完成，查看导入结果

### 通过API导入
```bash
# 1. 登录获取token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123"}'

# 2. 创建导入任务（上传文件）
curl -X POST "http://localhost:8000/api/v1/import-jobs" \
  -H "Authorization: Bearer <token>" \
  -F "file=@backend/test_data/orders_import_test.xlsx" \
  -F "target_type=orders" \
  -F "store_id=1" \
  -F "job_name=测试订单导入"

# 3. 执行导入任务
curl -X POST "http://localhost:8000/api/v1/import-jobs/{job_id}/run" \
  -H "Authorization: Bearer <token>"

# 4. 查看任务结果
curl -X GET "http://localhost:8000/api/v1/import-jobs/{job_id}" \
  -H "Authorization: Bearer <token>"
```

## 测试建议

### 正常流程测试
1. 先导入"门店信息"，创建测试门店
2. 再导入"费用科目"（可选，系统已有默认科目）
3. 使用新创建的门店ID导入"订单数据"
4. 使用新创建的门店ID导入"费用记录"

### 异常情况测试
1. **重复导入**: 尝试导入相同订单号的订单，验证幂等性
2. **缺少必填字段**: 删除某些必填列后导入，验证校验逻辑
3. **错误格式**: 修改日期或金额格式，验证数据转换
4. **不存在的关联数据**: 使用不存在的费用科目编码，验证关联校验
5. **大数据量**: 生成更多数据（修改脚本中的count参数），验证性能

## 生成新数据

如需生成新的测试数据，运行：
```bash
cd backend
python scripts/generate_import_test_data.py
```

可修改脚本中的参数：
- `generate_orders_data(count=50)` - 订单数量
- `generate_expense_records_data(count=30)` - 费用记录数量
- `generate_stores_data(count=5)` - 门店数量
- `generate_expense_types_data(count=10)` - 费用科目数量
