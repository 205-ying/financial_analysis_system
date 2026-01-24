# 阶段七快速测试指南

## 前置准备（5分钟）

### 1. 数据库迁移
```bash
cd backend
alembic upgrade head
```

### 2. 添加审计权限
```bash
cd backend
$env:PYTHONPATH = "."
python scripts/add_audit_permission.py
```

### 3. 启动服务

**后端：**
```bash
cd backend
start_dev.bat
```

**前端：**
```bash
cd frontend
npm run dev
```

---

## 快速验收（10分钟）

### 测试1：登录审计（2分钟）

1. 访问 http://localhost:5173/login
2. 登录（admin / admin123）
3. 进入"审计日志"页面
4. **验收：** 看到 `login`（登录）记录 ✅

---

### 测试2：创建费用审计（3分钟）

1. 进入"费用管理"
2. 点击"新增费用"
3. 填写：
   - 门店：任选
   - 费用类型：任选
   - 日期：今天
   - 金额：1000
   - 备注：测试
4. 保存
5. 返回"审计日志"
6. **验收：** 看到 `CREATE_EXPENSE`（创建费用）记录 ✅
7. 点击"详情"
8. **验收：** 看到费用金额、门店ID等信息 ✅

---

### 测试3：KPI重建审计（3分钟）

**注意：** 如果KPI页面没有"重建"按钮，可以直接通过API测试：

**使用Postman/cURL：**
```bash
# 获取Token
POST http://localhost:8000/api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# 重建KPI（使用上面获取的token）
POST http://localhost:8000/api/v1/kpi/rebuild
Authorization: Bearer <your_token>
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-24"
}
```

**或者在浏览器控制台：**
```javascript
// 在前端任意页面打开浏览器控制台（F12）
fetch('/api/v1/kpi/rebuild', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  },
  body: JSON.stringify({
    start_date: '2026-01-01',
    end_date: '2026-01-24'
  })
}).then(r => r.json()).then(console.log)
```

6. 返回"审计日志"页面
7. **验收：** 看到 `REBUILD_KPI`（重建KPI）记录 ✅
8. 点击"详情"
9. **验收：** 看到日期范围、影响的记录数 ✅

---

### 测试4：筛选功能（2分钟）

1. 在"审计日志"页面
2. 筛选操作类型：选择"创建费用"
3. 点击"查询"
4. **验收：** 只显示创建费用的记录 ✅
5. 点击"重置"
6. **验收：** 显示所有记录 ✅

---

### 测试5：权限控制（如果有时间）

**创建测试用户（后端）：**
```python
# backend/scripts/create_test_user.py
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def create_test_user():
    async with AsyncSessionLocal() as db:
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            full_name="测试用户",
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        await db.commit()
        print("测试用户创建成功")

import asyncio
asyncio.run(create_test_user())
```

**测试步骤：**
1. 登出
2. 用 testuser / test123 登录
3. **验收：** 菜单中没有"审计日志" ✅
4. 直接访问 http://localhost:5173/audit-logs
5. **验收：** 显示403或跳转到首页 ✅

---

## 验收通过标准

| 项目 | 状态 |
|------|------|
| 1. 登录操作有审计记录 | ✅ |
| 2. 创建费用有审计记录 | ✅ |
| 3. 重建KPI有审计记录 | ✅ |
| 4. 详情信息完整无敏感字段 | ✅ |
| 5. 筛选功能正常工作 | ✅ |
| 6. 权限控制生效 | ✅ |

---

## 快速检查SQL

**查看最新10条审计记录：**
```sql
SELECT 
  id, 
  username, 
  action, 
  resource_type, 
  status, 
  created_at 
FROM audit_log 
ORDER BY created_at DESC 
LIMIT 10;
```

**统计操作类型：**
```sql
SELECT 
  action, 
  COUNT(*) as count 
FROM audit_log 
GROUP BY action;
```

---

## 常见问题

**Q1: 审计日志页面显示"无权限"？**
A: 执行 `python scripts/add_audit_permission.py`，然后重新登录

**Q2: 没有看到审计记录？**
A: 检查：
1. 数据库迁移是否执行？`alembic current`
2. 后端是否有报错？查看控制台
3. 操作是否成功？检查其他页面功能

**Q3: KPI重建按钮在哪里？**
A: 目前可能没有UI按钮，使用API测试即可（见测试3）

**Q4: 详情里的JSON格式混乱？**
A: 这是正常的，系统会自动格式化显示

---

**全部测试完成预计时间：10-15分钟** ⏱️
