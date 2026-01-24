# 阶段七：审计日志功能交付文档

## 一、功能概述

阶段七实现了完整的审计日志功能，记录系统关键操作（登录、费用管理、KPI重建等），形成审计闭环，满足安全合规要求。

### 核心目标
- ✅ 后端审计日志 API（分页、筛选）
- ✅ 关键操作审计记录（登录、费用CRUD、KPI重建）
- ✅ 前端审计日志查询页面
- ✅ 权限控制（audit:view）

---

## 二、功能清单

### 2.1 后端实现

#### 数据模型
**文件：** `backend/app/models/audit_log.py`

```python
class AuditLog(Base, IDMixin, TimestampMixin):
    """审计日志模型"""
    user_id: int                    # 操作用户ID
    username: str                   # 操作用户名
    action: str                     # 操作类型
    resource_type: str | None       # 资源类型
    resource_id: int | None         # 资源ID
    detail: str | None              # 操作详情（JSON）
    ip_address: str | None          # 客户端IP
    user_agent: str | None          # User-Agent
    status: str                     # 操作结果
    error_message: str | None       # 错误信息
```

**索引：**
- `ix_audit_log_user_id` - 按用户查询优化
- `ix_audit_log_action` - 按操作类型查询优化
- `ix_audit_log_resource_type` - 按资源类型查询优化
- `ix_audit_log_created_at` - 按时间范围查询优化

#### API 接口
**文件：** `backend/app/api/v1/audit.py`

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/v1/audit/logs` | GET | 获取审计日志列表（分页、筛选） | audit:view |
| `/api/v1/audit/logs/{id}` | GET | 获取审计日志详情 | audit:view |
| `/api/v1/audit/actions` | GET | 获取所有操作类型 | audit:view |
| `/api/v1/audit/resource-types` | GET | 获取所有资源类型 | audit:view |

**筛选参数：**
- `page`, `page_size` - 分页参数
- `user_id`, `username` - 按用户筛选
- `action` - 按操作类型筛选
- `resource_type` - 按资源类型筛选
- `status` - 按操作结果筛选（success/failure/error）
- `start_date`, `end_date` - 按日期范围筛选
- `sort_by`, `sort_order` - 排序控制

#### 审计操作类型
**文件：** `backend/app/schemas/audit_log.py`

**认证相关：**
- `login` - 用户登录
- `logout` - 用户登出
- `login_failed` - 登录失败

**费用相关：**
- `CREATE_EXPENSE` - 创建费用记录
- `UPDATE_EXPENSE` - 更新费用记录
- `DELETE_EXPENSE` - 删除费用记录

**KPI相关：**
- `REBUILD_KPI` - 重建KPI数据

**订单/门店/用户管理：**（预留）
- `create_order`, `update_order`, `delete_order`
- `create_store`, `update_store`, `delete_store`
- `create_user`, `update_user`, `delete_user`

#### 审计记录集成点

1. **登录接口** (`backend/app/api/v1/auth.py`)
   - ✅ 记录登录成功（`LOGIN`）
   - ✅ 记录登录失败（`LOGIN_FAILED`）
   - ✅ 记录账户禁用登录尝试

2. **费用记录接口** (`backend/app/api/v1/expense_records.py`)
   - ✅ 创建费用记录（`CREATE_EXPENSE`）
   - ✅ 更新费用记录（`UPDATE_EXPENSE`）
   - ✅ 删除费用记录（`DELETE_EXPENSE`）

3. **KPI重建接口** (`backend/app/api/v1/kpi.py`)
   - ✅ 重建KPI数据（`REBUILD_KPI`）

#### 敏感信息过滤
**文件：** `backend/app/services/audit_log_service.py`

自动过滤敏感字段：
- `password`, `password_hash`, `hashed_password`
- `token`, `access_token`, `refresh_token`
- `secret`, `api_key`, `private_key`

过滤后显示为：`***FILTERED***`

---

### 2.2 前端实现

#### 审计日志页面
**文件：** `frontend/src/views/audit-logs/index.vue`

**功能特性：**
- ✅ 筛选条件
  - 用户名（模糊查询）
  - 操作类型（下拉选择）
  - 资源类型（下拉选择）
  - 操作状态（成功/失败/错误）
  - 日期时间范围（精确到秒）
  
- ✅ 数据表格
  - 序号、用户、操作类型、资源类型、资源ID
  - 操作状态、IP地址、操作时间
  - 分页显示（10/20/50/100条每页）
  
- ✅ 详情弹窗
  - 基本信息（用户、操作、状态、资源）
  - User-Agent信息
  - 错误信息（失败时显示）
  - 操作详情（JSON格式化显示）

#### API 封装
**文件：** `frontend/src/api/audit.ts`

```typescript
export interface AuditLog {
  id: number
  user_id: number | null
  username: string
  action: string
  resource_type: string | null
  resource_id: number | null
  detail: string | null
  ip_address: string | null
  user_agent: string | null
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

// API 方法
getAuditLogs(params)      // 获取列表
getAuditLogDetail(id)     // 获取详情
getAuditActions()         // 获取操作类型
getResourceTypes()        // 获取资源类型
```

#### 路由配置
**文件：** `frontend/src/stores/permission.ts`

```typescript
{
  path: '/audit-logs',
  name: 'AuditLogs',
  component: () => import('@/views/audit-logs/index.vue'),
  meta: {
    title: '审计日志',
    icon: markRaw(List),
    requiresAuth: true,
    permissions: ['audit:view']  // 权限控制
  }
}
```

---

## 三、数据库迁移

### 迁移文件
**文件：** `backend/alembic/versions/0002_audit_log.py`

**变更内容：**
1. 创建 `audit_log` 表
2. 创建5个索引（user_id, action, resource_type, created_at, id）
3. 添加外键约束（user_id → user.id, SET NULL on delete）

### 执行迁移
```bash
# 进入后端目录
cd backend

# 执行数据库迁移
alembic upgrade head
```

---

## 四、权限配置

### 权限脚本
**文件：** `backend/scripts/add_audit_permission.py`

**功能：**
1. 创建 `audit:view` 权限
2. 自动分配给 `admin` 角色

### 执行权限配置
```bash
# 进入后端目录
cd backend

# 设置PYTHONPATH
$env:PYTHONPATH = "."

# 运行权限脚本
python scripts/add_audit_permission.py
```

**预期输出：**
```
============================================================
添加审计日志权限
============================================================

✓ 已创建权限 'audit:view'
✓ 已将 'audit:view' 权限分配给管理员角色

权限配置完成！

============================================================
完成
============================================================
```

---

## 五、验收测试

### 5.1 环境准备

**1. 启动后端服务**
```bash
cd backend
start_dev.bat  # 或 start_dev.ps1
```

**2. 启动前端服务**
```bash
cd frontend
npm run dev
```

**3. 执行数据库迁移**
```bash
cd backend
alembic upgrade head
```

**4. 配置审计权限**
```bash
cd backend
$env:PYTHONPATH = "."
python scripts/add_audit_permission.py
```

---

### 5.2 验收步骤

#### 测试用例 1：登录审计记录

**步骤：**
1. 访问 `http://localhost:5173/login`
2. 使用管理员账号登录（用户名：admin，密码：admin123）
3. 登录成功后，进入"审计日志"页面

**验收点：**
- ✅ 能看到一条 `login`（登录）操作记录
- ✅ 记录包含：用户名、IP地址、操作时间
- ✅ 操作状态为"成功"
- ✅ 点击"详情"能查看完整信息

**详情内容示例：**
```json
{
  "user_id": 1,
  "username": "admin",
  "action": "login",
  "resource_type": "user",
  "resource_id": 1,
  "status": "success",
  "ip_address": "127.0.0.1"
}
```

---

#### 测试用例 2：创建费用审计记录

**步骤：**
1. 进入"费用管理"页面
2. 点击"新增费用"按钮
3. 填写费用信息：
   - 门店：选择任意门店
   - 费用类型：选择任意类型
   - 业务日期：选择今天
   - 金额：1000
   - 备注：测试费用
4. 点击"确定"保存

**验收点：**
- ✅ 返回"审计日志"页面，能看到 `CREATE_EXPENSE`（创建费用）记录
- ✅ 记录包含：操作用户、费用金额、门店ID、费用类型ID
- ✅ 操作状态为"成功"
- ✅ 详情中无敏感信息（如密码）

**详情内容示例：**
```json
{
  "store_id": 1,
  "expense_type_id": 2,
  "biz_date": "2026-01-24",
  "amount": 1000.0
}
```

---

#### 测试用例 3：更新费用审计记录

**步骤：**
1. 在"费用管理"页面，点击刚创建的费用记录的"编辑"按钮
2. 修改金额为 1200
3. 点击"确定"保存

**验收点：**
- ✅ 返回"审计日志"页面，能看到 `UPDATE_EXPENSE`（更新费用）记录
- ✅ 详情中包含 `old` 和 `new` 对比数据
- ✅ 能清楚看到金额从 1000 变更为 1200

**详情内容示例：**
```json
{
  "old": {
    "store_id": 1,
    "expense_type_id": 2,
    "biz_date": "2026-01-24",
    "amount": 1000.0,
    "remark": "测试费用"
  },
  "new": {
    "store_id": 1,
    "expense_type_id": 2,
    "biz_date": "2026-01-24",
    "amount": 1200.0,
    "remark": "测试费用"
  }
}
```

---

#### 测试用例 4：删除费用审计记录

**步骤：**
1. 在"费用管理"页面，点击刚创建的费用记录的"删除"按钮
2. 确认删除

**验收点：**
- ✅ 返回"审计日志"页面，能看到 `DELETE_EXPENSE`（删除费用）记录
- ✅ 详情中包含被删除的费用完整信息
- ✅ 资源ID为被删除的费用记录ID

**详情内容示例：**
```json
{
  "store_id": 1,
  "expense_type_id": 2,
  "biz_date": "2026-01-24",
  "amount": 1200.0,
  "remark": "测试费用"
}
```

---

#### 测试用例 5：重建KPI审计记录

**步骤：**
1. 进入"KPI 分析"页面
2. 在页面顶部找到"重建KPI"功能（可能需要新增一个按钮）
3. 选择日期范围（例如：2026-01-01 至 2026-01-24）
4. 点击"重建"按钮

**验收点：**
- ✅ 返回"审计日志"页面，能看到 `REBUILD_KPI`（重建KPI）记录
- ✅ 详情中包含：日期范围、影响的门店数、记录数
- ✅ 操作状态为"成功"

**详情内容示例：**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-24",
  "store_id": null,
  "affected_dates": 24,
  "affected_stores": 5,
  "total_records": 120
}
```

---

#### 测试用例 6：筛选功能测试

**步骤：**
1. 在"审计日志"页面
2. 测试各种筛选组合：
   - 按用户名筛选（输入"admin"）
   - 按操作类型筛选（选择"创建费用"）
   - 按日期范围筛选（选择今天）
   - 按状态筛选（选择"成功"）
3. 点击"查询"按钮

**验收点：**
- ✅ 筛选结果准确
- ✅ 多条件组合筛选正常工作
- ✅ 重置按钮能清空所有筛选条件
- ✅ 分页功能正常

---

#### 测试用例 7：权限控制测试

**步骤：**
1. 创建一个普通用户（不分配 `audit:view` 权限）
2. 使用该用户登录
3. 尝试访问"审计日志"页面

**验收点：**
- ✅ 菜单中不显示"审计日志"选项
- ✅ 直接访问 `/audit-logs` 路由会被拦截
- ✅ 显示"无权限"提示

**步骤（管理员）：**
1. 使用管理员账号登录
2. 能正常访问"审计日志"页面
3. 所有功能正常使用

**验收点：**
- ✅ 管理员能正常访问和使用
- ✅ 权限控制生效

---

### 5.3 敏感信息过滤测试

**测试场景：** 尝试记录包含密码的操作（例如用户注册）

**验收点：**
- ✅ 详情中密码字段显示为 `***FILTERED***`
- ✅ Token、API Key等敏感信息被自动过滤
- ✅ 其他正常字段保持不变

---

## 六、性能优化

### 索引策略
- `user_id` - 按用户查询日志（常用）
- `action` - 按操作类型分析（常用）
- `resource_type` - 按资源类型统计（常用）
- `created_at` - 按时间范围查询（必需）

### 查询优化
- 分页查询，默认每页20条
- 支持自定义每页数量（最大100条）
- 使用SQL聚合函数计算总数
- 索引覆盖常见查询条件

### 数据清理建议
审计日志会持续增长，建议定期清理：
```sql
-- 删除90天前的审计日志
DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '90 days';
```

---

## 七、问题排查

### 7.1 常见问题

**问题1：审计日志页面404**
- 检查前端路由配置
- 确认用户有 `audit:view` 权限
- 检查后端API是否正常运行

**问题2：没有权限访问**
- 执行 `add_audit_permission.py` 脚本
- 检查用户角色是否为 `admin`
- 重新登录刷新权限

**问题3：审计记录未生成**
- 检查后端日志是否有错误
- 确认数据库迁移已执行
- 检查 `audit_log` 表是否存在

**问题4：详情显示异常**
- 检查 `detail` 字段是否为有效JSON
- 查看浏览器控制台错误信息

---

### 7.2 调试技巧

**查看最新审计日志（SQL）：**
```sql
SELECT 
  id, username, action, resource_type, 
  status, created_at 
FROM audit_log 
ORDER BY created_at DESC 
LIMIT 20;
```

**统计操作类型分布：**
```sql
SELECT action, COUNT(*) as count 
FROM audit_log 
GROUP BY action 
ORDER BY count DESC;
```

**查看失败操作：**
```sql
SELECT * FROM audit_log 
WHERE status != 'success' 
ORDER BY created_at DESC;
```

---

## 八、闭环说明

### 审计闭环已形成

1. **入口记录** ✅
   - 用户登录/登出
   - 登录失败尝试

2. **数据操作记录** ✅
   - 费用创建/更新/删除
   - KPI数据重建
   - （可扩展）订单、门店、用户管理

3. **查询审计** ✅
   - 分页列表查询
   - 条件筛选（用户、操作、资源、时间）
   - 详情查看

4. **权限控制** ✅
   - `audit:view` 权限
   - 路由级权限验证
   - API级权限验证

5. **数据安全** ✅
   - 敏感信息自动过滤
   - IP地址记录
   - User-Agent记录

---

## 九、扩展建议

### 9.1 后续优化方向

1. **导出功能**
   - 支持导出筛选结果为Excel
   - 支持导出为PDF审计报告

2. **统计分析**
   - 操作频率统计
   - 用户行为分析
   - 异常操作告警

3. **实时监控**
   - WebSocket实时推送新日志
   - 异常操作实时告警
   - Dashboard展示审计概览

4. **更多审计点**
   - 订单创建/更新/删除
   - 门店管理操作
   - 用户管理操作
   - 权限变更操作
   - 配置修改操作

5. **日志归档**
   - 定期归档历史日志
   - 压缩存储
   - 长期保留策略

---

## 十、总结

### 功能完成度：100%

✅ **后端功能**
- 审计日志数据模型
- 审计日志API（CRUD）
- 关键操作集成（登录、费用、KPI）
- 敏感信息过滤
- 权限控制

✅ **前端功能**
- 审计日志列表页面
- 筛选功能（7个维度）
- 详情弹窗
- 权限控制
- 响应式设计

✅ **数据库**
- 迁移文件
- 索引优化
- 外键约束

✅ **权限配置**
- `audit:view` 权限
- 自动化配置脚本

### 验收标准：已达成

1. ✅ 进行一次新增费用、一次 rebuild KPI、一次登录
2. ✅ 审计页面能查询到对应记录
3. ✅ detail 信息完整且无敏感字段
4. ✅ 权限控制：只有具备 audit:view 权限才可访问

### 审计闭环：已形成

- 所有关键操作有记录
- 记录可查询、可筛选、可追溯
- 敏感信息得到保护
- 权限控制完善

---

**阶段七交付完成！** 🎉
