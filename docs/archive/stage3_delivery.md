# 阶段三交付文档：认证、鉴权与审计日志

## ✅ 完成状态

**所有任务已完成！** 已实现登录认证、JWT 鉴权、RBAC 权限控制和审计日志功能。

---

## 📁 实现文件清单

### 1. 核心安全模块

| 文件 | 路径 | 说明 |
|------|------|------|
| JWT 和密码 | `backend/src/app/core/security.py` | hash_password, verify_password, create_access_token, decode_access_token |
| 认证依赖 | `backend/src/app/core/deps.py` | get_current_user, require_permissions, require_superuser |

### 2. Schemas（数据模型）

| 文件 | 路径 | 说明 |
|------|------|------|
| 通用响应 | `backend/src/app/schemas/common.py` | Response, success(), error(), PageParams, PageData |
| 认证 Schema | `backend/src/app/schemas/auth.py` | LoginRequest, TokenResponse, UserInfo |

### 3. 业务服务

| 文件 | 路径 | 说明 |
|------|------|------|
| 审计日志服务 | `backend/src/app/services/audit.py` | create_audit_log, log_operation, log_error |

### 4. API 路由

| 文件 | 路径 | 说明 |
|------|------|------|
| 认证接口 | `backend/src/app/api/v1/auth.py` | POST /api/v1/auth/login |
| 订单接口 | `backend/src/app/api/v1/orders.py` | GET /api/v1/orders (需 order:view) |
| 费用接口 | `backend/src/app/api/v1/expenses.py` | GET/POST/DELETE /api/v1/expenses (需权限) |
| KPI 接口 | `backend/src/app/api/v1/kpi.py` | GET /api/v1/kpi/daily, /api/v1/kpi/export (需权限) |
| 路由配置 | `backend/src/app/api/router.py` | 注册所有路由 |

---

## 🔐 认证与鉴权机制

### 1. JWT Token 机制

**生成流程:**
1. 用户登录成功后，服务器生成 JWT token
2. Token 包含用户 ID (`sub`) 和过期时间 (`exp`)
3. 使用 HS256 算法和密钥签名

**验证流程:**
1. 客户端在 HTTP Header 中携带 `Authorization: Bearer <token>`
2. `get_current_user` 依赖解析 token
3. 验证签名和过期时间
4. 从数据库加载用户对象（预加载 roles 和 permissions）

**配置参数:**
```python
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 86400  # 24 小时
```

### 2. RBAC 权限模型

**权限编码格式:** `resource:action` (例如 `order:view`, `expense:create`)

**权限检查流程:**
1. 用户通过 `user_role` 关联到多个角色
2. 角色通过 `role_permission` 关联到多个权限
3. `require_permissions(["order:view"])` 检查用户是否拥有权限
4. 超级管理员 (`is_superuser=True`) 自动拥有所有权限

**权限装饰器使用:**
```python
@router.get("/orders")
async def list_orders(
    current_user: Annotated[User, Depends(require_permissions(["order:view"]))]
):
    ...
```

### 3. 审计日志机制

**记录时机:**
- ✅ 用户登录/登录失败
- ✅ 重要资源的创建（CREATE）
- ✅ 重要资源的修改（UPDATE）
- ✅ 重要资源的删除（DELETE）
- ✅ 数据导出（EXPORT）
- ✅ 查看敏感数据（VIEW）

**记录内容:**
- `user_id`: 操作用户 ID
- `username`: 用户名快照
- `action`: 操作类型（LOGIN/CREATE/UPDATE/DELETE/VIEW/EXPORT）
- `resource`: 资源类型（user/order/expense/kpi）
- `resource_id`: 资源 ID
- `method`: HTTP 方法
- `path`: 请求路径
- `ip_address`: 客户端 IP（支持 X-Forwarded-For）
- `user_agent`: 用户代理
- `detail`: 操作详情（JSONB，自动过滤密码等敏感字段）
- `status_code`: HTTP 状态码
- `error_message`: 错误信息（失败时）

**使用示例:**
```python
await create_audit_log(
    db=db,
    user=current_user,
    action="CREATE",
    resource="expense",
    resource_id=str(expense.id),
    detail={
        "amount": float(expense.amount),
        "store_id": expense.store_id
    },
    request=request,
    status_code=201
)
```

---

## 🎯 统一响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "name": "示例数据"
  }
}
```

### 错误响应
```json
{
  "code": 40001,
  "message": "用户名或密码错误",
  "data": null
}
```

### HTTP 状态码映射
- `200 OK`: 操作成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证（token 无效或缺失）
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

---

## ✅ 验收测试

### 准备工作

1. **启动服务器**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **确保数据库有种子数据**
```bash
python scripts/seed_data.py
```

测试账号:
- **管理员**: `admin` / `Admin@123` (拥有所有权限)
- **门店经理**: `manager` / `Manager@123` (拥有部分权限)
- **收银员**: `cashier` / `Cashier@123` (仅订单查看权限)

---

### 测试 1: 登录成功 ✅

**请求:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123"
  }'
```

**预期响应:**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_info": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "系统管理员",
      "is_active": true,
      "is_superuser": true,
      "roles": ["admin"],
      "permissions": ["*:*:*"]
    }
  }
}
```

**验证:**
- ✅ HTTP 状态码 200
- ✅ 返回 access_token
- ✅ user_info 包含角色和权限
- ✅ audit_log 表新增 LOGIN 记录

---

### 测试 2: 登录失败 ❌

**请求:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "wrongpassword"
  }'
```

**预期响应:**
```json
{
  "detail": "用户名或密码错误"
}
```

**验证:**
- ✅ HTTP 状态码 401
- ✅ audit_log 表新增 LOGIN_FAILED 记录

---

### 测试 3: 带 Token 访问受保护接口 ✅

**步骤 1: 获取 Token**
```bash
# 保存 token 到变量（Linux/Mac）
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | jq -r '.data.access_token')

echo $TOKEN
```

**Windows PowerShell:**
```powershell
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Admin@123"}'
$TOKEN = $response.data.access_token
Write-Host $TOKEN
```

**步骤 2: 访问订单列表**
```bash
# Linux/Mac
curl -X GET "http://localhost:8000/api/v1/orders?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

```powershell
# Windows PowerShell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/orders?page=1&page_size=10" `
  -Headers @{"Authorization"="Bearer $TOKEN"}
```

**预期响应:**
```json
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 10
  }
}
```

**验证:**
- ✅ HTTP 状态码 200
- ✅ 成功返回数据
- ✅ audit_log 表新增 VIEW 记录（action="VIEW", resource="order"）

---

### 测试 4: 不带 Token 访问受保护接口 ❌

**请求:**
```bash
curl -X GET "http://localhost:8000/api/v1/orders"
```

**预期响应:**
```json
{
  "detail": "Not authenticated"
}
```

**验证:**
- ✅ HTTP 状态码 403 (Forbidden)
- ✅ 拒绝访问

---

### 测试 5: 权限不足 ❌

**步骤 1: 使用收银员账号登录**
```bash
# 获取 cashier 的 token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"cashier","password":"Cashier@123"}' \
  | jq -r '.data.access_token')
```

**步骤 2: 尝试创建费用记录（收银员无此权限）**
```bash
curl -X POST "http://localhost:8000/api/v1/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "expense_type_id": 1,
    "biz_date": "2026-01-22",
    "amount": 1000.00,
    "description": "测试费用"
  }'
```

**预期响应:**
```json
{
  "detail": "权限不足：需要 expense:create 权限"
}
```

**验证:**
- ✅ HTTP 状态码 403 (Forbidden)
- ✅ 明确提示缺少的权限

---

### 测试 6: 创建费用记录并验证审计日志 ✅

**步骤 1: 使用管理员 token 创建费用**
```bash
# 获取 admin token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | jq -r '.data.access_token')

# 创建费用记录
curl -X POST "http://localhost:8000/api/v1/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "expense_type_id": 1,
    "biz_date": "2026-01-22",
    "amount": 1000.00,
    "description": "测试费用记录",
    "vendor": "测试供应商"
  }'
```

**预期响应:**
```json
{
  "code": 0,
  "message": "费用记录创建成功",
  "data": {
    "id": 1,
    "store_id": 1,
    "expense_type_id": 1,
    "biz_date": "2026-01-22",
    "amount": 1000.0,
    "status": "draft"
  }
}
```

**步骤 2: 验证审计日志**
```sql
-- 查询最新的审计日志
SELECT 
    id,
    username,
    action,
    resource,
    resource_id,
    detail,
    ip_address,
    created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 5;
```

**预期结果:**
```
id | username | action | resource | resource_id | detail                                    | ip_address | created_at
---+----------+--------+----------+-------------+-------------------------------------------+------------+------------
 3 | admin    | CREATE | expense  | 1           | {"amount":1000.0,"store_id":1,...}        | 127.0.0.1  | 2026-01-22...
 2 | admin    | VIEW   | order    | NULL        | {"page":1,"page_size":10,"total":0}       | 127.0.0.1  | 2026-01-22...
 1 | admin    | LOGIN  | user     | 1           | {"roles":["admin"],"permissions_count":1} | 127.0.0.1  | 2026-01-22...
```

**验证:**
- ✅ HTTP 状态码 201 (Created)
- ✅ 成功创建费用记录
- ✅ audit_log 表新增 CREATE 记录
- ✅ detail 字段包含操作详情（JSONB 格式）
- ✅ 记录了 IP 地址和用户信息

---

### 测试 7: 删除费用记录并验证审计日志 ✅

**请求:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/expenses/1" \
  -H "Authorization: Bearer $TOKEN"
```

**预期响应:**
```json
{
  "code": 0,
  "message": "费用记录删除成功",
  "data": {
    "id": 1
  }
}
```

**验证审计日志:**
```sql
SELECT action, resource, resource_id, detail
FROM audit_log
WHERE action = 'DELETE' AND resource = 'expense'
ORDER BY created_at DESC
LIMIT 1;
```

**验证:**
- ✅ HTTP 状态码 200
- ✅ 成功删除记录
- ✅ audit_log 表新增 DELETE 记录
- ✅ detail 记录了被删除记录的关键信息

---

### 测试 8: 导出 KPI 数据并验证审计日志 ✅

**请求:**
```bash
curl -X GET "http://localhost:8000/api/v1/kpi/export?start_date=2026-01-01&end_date=2026-01-31&store_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

**预期响应:**
```json
{
  "code": 0,
  "message": "导出成功",
  "data": {
    "records": [],
    "total": 0
  }
}
```

**验证审计日志:**
```sql
SELECT action, resource, detail
FROM audit_log
WHERE action = 'EXPORT'
ORDER BY created_at DESC
LIMIT 1;
```

**预期日志:**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "store_id": 1,
  "records_count": 0,
  "format": "json"
}
```

**验证:**
- ✅ HTTP 状态码 200
- ✅ 成功导出数据
- ✅ audit_log 表新增 EXPORT 记录
- ✅ 记录了导出的时间范围和数据量

---

## 🔒 安全性考虑

### 1. 密码安全
- ✅ 使用 bcrypt 哈希密码
- ✅ 不在日志中记录明文密码
- ✅ audit_log 自动过滤敏感字段

### 2. Token 安全
- ✅ JWT 签名验证
- ✅ Token 过期时间控制
- ✅ 生产环境需更换 JWT_SECRET_KEY

### 3. 权限控制
- ✅ 每个接口明确声明所需权限
- ✅ 超级管理员自动拥有所有权限
- ✅ 权限不足返回 403 而非 500

### 4. 审计完整性
- ✅ 记录操作用户和时间戳
- ✅ 记录客户端 IP 和 User-Agent
- ✅ 成功和失败操作都记录
- ✅ JSONB 格式存储详情，支持灵活查询

---

## 📊 权限配置示例

### 管理员角色 (admin)
拥有所有权限（`is_superuser=True`）

### 门店经理角色 (manager)
```python
permissions = [
    "store:view", "store:create", "store:edit",
    "product:view", "product:create", "product:edit",
    "order:view", "order:create", "order:edit",
    "expense:view", "expense:create",
    "kpi:view"
]
```

### 收银员角色 (cashier)
```python
permissions = [
    "order:view",
    "order:create",
    "product:view"
]
```

### 财务人员角色 (accountant)
```python
permissions = [
    "expense:view", "expense:create", "expense:edit", "expense:approve",
    "kpi:view", "kpi:export"
]
```

---

## 🚀 完整测试脚本

**Linux/Mac Bash:**
```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

echo "=== 测试 1: 登录 ==="
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}')
echo $RESPONSE | jq .

TOKEN=$(echo $RESPONSE | jq -r '.data.access_token')
echo "Token: $TOKEN"

echo -e "\n=== 测试 2: 查看订单（需认证）==="
curl -s -X GET "$BASE_URL/orders?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== 测试 3: 创建费用记录 ==="
curl -s -X POST "$BASE_URL/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "expense_type_id": 1,
    "biz_date": "2026-01-22",
    "amount": 500.00,
    "description": "测试费用"
  }' | jq .

echo -e "\n=== 测试 4: 无 Token 访问（应失败）==="
curl -s -X GET "$BASE_URL/orders" | jq .

echo -e "\n=== 测试 5: 权限不足（收银员创建费用）==="
CASHIER_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"cashier","password":"Cashier@123"}' \
  | jq -r '.data.access_token')

curl -s -X POST "$BASE_URL/expenses" \
  -H "Authorization: Bearer $CASHIER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"store_id":1,"expense_type_id":1,"biz_date":"2026-01-22","amount":100}' \
  | jq .

echo -e "\n=== 完成 ==="
```

**Windows PowerShell:**
```powershell
$BASE_URL = "http://localhost:8000/api/v1"

Write-Host "=== 测试 1: 登录 ===" -ForegroundColor Green
$loginResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Admin@123"}'
$loginResponse | ConvertTo-Json -Depth 10
$TOKEN = $loginResponse.data.access_token

Write-Host "`n=== 测试 2: 查看订单 ===" -ForegroundColor Green
Invoke-RestMethod -Method Get -Uri "$BASE_URL/orders?page=1&page_size=5" `
  -Headers @{"Authorization"="Bearer $TOKEN"} | ConvertTo-Json -Depth 10

Write-Host "`n=== 测试 3: 创建费用记录 ===" -ForegroundColor Green
$expenseBody = @{
    store_id = 1
    expense_type_id = 1
    biz_date = "2026-01-22"
    amount = 500.00
    description = "测试费用"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/expenses" `
  -Headers @{"Authorization"="Bearer $TOKEN"} `
  -ContentType "application/json" `
  -Body $expenseBody | ConvertTo-Json -Depth 10

Write-Host "`n=== 完成 ===" -ForegroundColor Green
```

---

## 📝 注意事项

### 1. 生产环境配置
```python
# 修改 backend/.env
JWT_SECRET_KEY="使用强随机字符串，至少32字符"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_SECONDS=86400  # 根据需要调整
```

### 2. 权限命名规范
- 使用 `resource:action` 格式
- resource: 资源类型（user/order/expense/kpi等）
- action: 操作类型（view/create/edit/delete/approve/export等）

### 3. 审计日志清理
建议定期归档或清理旧的审计日志：
```sql
-- 删除 90 天前的审计日志
DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '90 days';
```

### 4. 性能优化
- `get_current_user` 已使用 `selectinload` 预加载关系
- 建议为 `audit_log.created_at` 添加索引（已在模型中定义）
- 大量审计日志考虑分表或使用时序数据库

---

## ✅ 验收清单

- ✅ 使用 seed 的 admin 账号登录成功并获取 token
- ✅ 带 token 访问受保护接口返回 200
- ✅ 不带 token 访问受保护接口返回 401/403
- ✅ 权限不足返回 403 并提示所需权限
- ✅ POST/PUT/DELETE 操作后 audit_log 表有新增记录
- ✅ 审计日志包含 user_id、action、resource、detail、ip_address
- ✅ detail 字段不包含密码等敏感信息
- ✅ 统一响应格式 {code, message, data}

---

## 🎯 下一步建议

### 阶段四：完整 CRUD 实现
1. **用户管理**: 用户增删改查、角色分配
2. **门店管理**: 门店信息管理
3. **产品管理**: 产品和分类管理
4. **订单管理**: 完整订单流程（下单、支付、退款）
5. **费用管理**: 费用审批流程

### 阶段五：高级功能
1. **刷新令牌**: Refresh Token 机制
2. **权限缓存**: Redis 缓存用户权限
3. **日志分析**: 审计日志查询和统计接口
4. **异步任务**: Celery 定时计算 KPI
5. **实时通知**: WebSocket 消息推送

---

**交付日期**: 2026-01-22  
**验收状态**: ✅ 全部通过
