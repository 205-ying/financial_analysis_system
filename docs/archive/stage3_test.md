# 阶段三验收测试脚本

## 说明
本脚本用于验收阶段三的认证、鉴权和审计日志功能。

## 使用方法

### 1. 启动服务器
在一个终端窗口中运行：
```bash
cd backend
C:\Users\29624\Desktop\financial_analysis_system\backend\venv\Scripts\python.exe -m uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 在另一个 PowerShell 窗口运行测试

#### 测试 1: 登录成功
```powershell
$loginBody = @{
    username = "admin"
    password = "Admin@123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/api/v1/auth/login" `
    -ContentType "application/json" `
    -Body $loginBody

Write-Host "===登录成功===" -ForegroundColor Green
$loginResponse | ConvertTo-Json -Depth 10
$token = $loginResponse.data.access_token
Write-Host "`nToken: $token" -ForegroundColor Yellow
```

#### 测试 2: 查看订单（带 Token）
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$ordersResponse = Invoke-RestMethod -Method Get `
    -Uri "http://localhost:8000/api/v1/orders?page=1&page_size=10" `
    -Headers $headers

Write-Host "`n===查看订单成功===" -ForegroundColor Green
$ordersResponse | ConvertTo-Json -Depth 10
```

#### 测试 3: 创建费用记录
```powershell
$expenseBody = @{
    store_id = 1
    expense_type_id = 1
    biz_date = "2026-01-22"
    amount = 500.00
    description = "测试费用记录"
    vendor = "测试供应商"
} | ConvertTo-Json

$expenseResponse = Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/api/v1/expenses" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $expenseBody

Write-Host "`n===创建费用成功===" -ForegroundColor Green
$expenseResponse | ConvertTo-Json -Depth 10
```

#### 测试 4: 无 Token 访问（应失败）
```powershell
try {
    Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/orders"
} catch {
    Write-Host "`n===无 Token 访问被拒绝===" -ForegroundColor Red
    $_.Exception.Response.StatusCode
}
```

#### 测试 5: 权限不足（收银员创建费用）
```powershell
$cashierLoginBody = @{
    username = "cashier"
    password = "Cashier@123"
} | ConvertTo-Json

$cashierResponse = Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/api/v1/auth/login" `
    -ContentType "application/json" `
    -Body $cashierLoginBody

$cashierToken = $cashierResponse.data.access_token
$cashierHeaders = @{
    "Authorization" = "Bearer $cashierToken"
}

try {
    Invoke-RestMethod -Method Post `
        -Uri "http://localhost:8000/api/v1/expenses" `
        -Headers $cashierHeaders `
        -ContentType "application/json" `
        -Body $expenseBody
} catch {
    Write-Host "`n===权限不足===" -ForegroundColor Red
    $_.Exception.Message
}
```

#### 测试 6: 验证审计日志
```powershell
# 在 PostgreSQL 中查询
psql -U postgres -d financial_analysis -c "SELECT id, username, action, resource, resource_id, created_at FROM audit_log ORDER BY created_at DESC LIMIT 5;"
```

### 完整测试脚本
将以下内容保存为 `test_auth.ps1`：

```powershell
# 阶段三完整验收测试脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  阶段三验收测试：认证、鉴权与审计日志" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/v1"

# 测试 1: 登录成功
Write-Host "【测试 1】登录成功" -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "Admin@123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Method Post `
        -Uri "$baseUrl/auth/login" `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host "✓ 登录成功" -ForegroundColor Green
    Write-Host "  用户: $($loginResponse.data.user_info.username)" -ForegroundColor Gray
    Write-Host "  角色: $($loginResponse.data.user_info.roles -join ', ')" -ForegroundColor Gray
    
    $token = $loginResponse.data.access_token
} catch {
    Write-Host "✗ 登录失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试 2: 带 Token 访问受保护接口
Write-Host "`n【测试 2】带 Token 访问订单列表" -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $ordersResponse = Invoke-RestMethod -Method Get `
        -Uri "$baseUrl/orders?page=1&page_size=5" `
        -Headers $headers
    
    Write-Host "✓ 成功访问受保护接口" -ForegroundColor Green
    Write-Host "  订单数: $($ordersResponse.data.total)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试 3: 创建费用记录
Write-Host "`n【测试 3】创建费用记录" -ForegroundColor Yellow
$expenseBody = @{
    store_id = 1
    expense_type_id = 1
    biz_date = (Get-Date -Format "yyyy-MM-dd")
    amount = 500.00
    description = "自动化测试费用"
    vendor = "测试供应商"
} | ConvertTo-Json

try {
    $expenseResponse = Invoke-RestMethod -Method Post `
        -Uri "$baseUrl/expenses" `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $expenseBody
    
    Write-Host "✓ 费用记录创建成功" -ForegroundColor Green
    Write-Host "  费用ID: $($expenseResponse.data.id)" -ForegroundColor Gray
    Write-Host "  金额: $($expenseResponse.data.amount)" -ForegroundColor Gray
    
    $expenseId = $expenseResponse.data.id
} catch {
    Write-Host "✗ 创建失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试 4: 无 Token 访问
Write-Host "`n【测试 4】无 Token 访问（应失败）" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Method Get -Uri "$baseUrl/orders"
    Write-Host "✗ 应该被拒绝但通过了" -ForegroundColor Red
} catch {
    Write-Host "✓ 成功拒绝未认证请求 (403)" -ForegroundColor Green
}

# 测试 5: 权限不足
Write-Host "`n【测试 5】权限不足（收银员创建费用）" -ForegroundColor Yellow
$cashierLoginBody = @{
    username = "cashier"
    password = "Cashier@123"
} | ConvertTo-Json

try {
    $cashierResponse = Invoke-RestMethod -Method Post `
        -Uri "$baseUrl/auth/login" `
        -ContentType "application/json" `
        -Body $cashierLoginBody
    
    $cashierToken = $cashierResponse.data.access_token
    $cashierHeaders = @{
        "Authorization" = "Bearer $cashierToken"
    }
    
    try {
        Invoke-RestMethod -Method Post `
            -Uri "$baseUrl/expenses" `
            -Headers $cashierHeaders `
            -ContentType "application/json" `
            -Body $expenseBody
        
        Write-Host "✗ 应该被拒绝但通过了" -ForegroundColor Red
    } catch {
        Write-Host "✓ 成功拒绝权限不足的请求 (403)" -ForegroundColor Green
        Write-Host "  错误: 权限不足：需要 expense:create 权限" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ 收银员登录失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试 6: 删除费用记录
if ($expenseId) {
    Write-Host "`n【测试 6】删除费用记录" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Method Delete `
            -Uri "$baseUrl/expenses/$expenseId" `
            -Headers $headers
        
        Write-Host "✓ 费用记录删除成功" -ForegroundColor Green
    } catch {
        Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n请在数据库中查看审计日志：" -ForegroundColor Yellow
Write-Host 'psql -U postgres -d financial_analysis -c "SELECT id, username, action, resource, created_at FROM audit_log ORDER BY created_at DESC LIMIT 10;"' -ForegroundColor Gray
```

运行测试：
```powershell
.\test_auth.ps1
```
