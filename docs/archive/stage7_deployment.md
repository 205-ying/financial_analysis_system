# 阶段七部署和运行指南

## 快速启动（5分钟）

### 步骤1：数据库迁移（1分钟）

```bash
# 进入后端目录
cd backend

# 执行迁移（创建audit_log表）
alembic upgrade head
```

**预期输出：**
```
INFO  [alembic.runtime.migration] Running upgrade 0001_initial -> 0002_audit_log, add audit_log table
```

---

### 步骤2：配置审计权限（1分钟）

```bash
# 设置PYTHONPATH
$env:PYTHONPATH = "."

# 运行权限配置脚本
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
```

---

### 步骤3：启动后端服务（1分钟）

**Windows（PowerShell）：**
```bash
cd backend
start_dev.ps1
```

**Windows（CMD）：**
```bash
cd backend
start_dev.bat
```

**预期输出：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### 步骤4：启动前端服务（1分钟）

```bash
cd frontend
npm run dev
```

**预期输出：**
```
VITE v5.4.21  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

### 步骤5：访问系统（1分钟）

1. 打开浏览器访问：http://localhost:5173
2. 登录（admin / admin123）
3. 点击左侧菜单"审计日志"
4. **验证成功：** 能看到审计日志页面 ✅

---

## 完整部署检查清单

### 环境检查

- [ ] Python 3.11+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] PostgreSQL 数据库已运行
- [ ] 数据库连接配置正确（`.env`文件）

### 后端检查

- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 数据库迁移已执行（`alembic upgrade head`）
- [ ] 审计权限已配置（`python scripts/add_audit_permission.py`）
- [ ] 后端服务正常启动（http://localhost:8000）
- [ ] API文档可访问（http://localhost:8000/docs）

### 前端检查

- [ ] 依赖已安装（`npm install`）
- [ ] 环境变量配置正确（`.env.development`）
- [ ] 前端服务正常启动（http://localhost:5173）
- [ ] 登录功能正常
- [ ] 审计日志菜单可见（管理员用户）

---

## 验证审计功能

### 快速验证命令

**1. 检查audit_log表是否存在：**
```sql
-- 连接PostgreSQL
psql -U postgres -d financial_analysis

-- 查看表结构
\d audit_log

-- 查看最新记录
SELECT id, username, action, status, created_at 
FROM audit_log 
ORDER BY created_at DESC 
LIMIT 5;
```

**2. 检查权限是否配置：**
```sql
-- 查看audit:view权限
SELECT * FROM permission WHERE code = 'audit:view';

-- 查看管理员角色权限
SELECT r.code, p.code 
FROM role r
JOIN role_permission rp ON r.id = rp.role_id
JOIN permission p ON rp.permission_id = p.id
WHERE r.code = 'admin' AND p.code = 'audit:view';
```

**3. 测试API：**
```bash
# 获取Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 查询审计日志（使用上面获取的token）
curl -X GET "http://localhost:8000/api/v1/audit/logs?page=1&page_size=10" \
  -H "Authorization: Bearer <your_token>"
```

---

## 常见问题排查

### 问题1：数据库迁移失败

**错误：** `sqlalchemy.exc.OperationalError: could not connect to server`

**解决：**
```bash
# 检查PostgreSQL服务是否运行
# Windows:
services.msc  # 查看 PostgreSQL 服务状态

# 检查数据库连接配置
cat backend/.env  # 确认DATABASE_URL正确
```

---

### 问题2：权限脚本执行失败

**错误：** `ModuleNotFoundError: No module named 'app'`

**解决：**
```bash
# 确保在backend目录
cd backend

# 设置PYTHONPATH
$env:PYTHONPATH = "."

# 重新运行
python scripts/add_audit_permission.py
```

---

### 问题3：后端启动失败

**错误：** `ModuleNotFoundError: No module named 'src'`

**解决：**
```bash
# 使用项目提供的启动脚本
cd backend
start_dev.bat  # 或 start_dev.ps1

# 脚本会自动设置PYTHONPATH
```

---

### 问题4：前端看不到审计日志菜单

**原因：** 用户没有 `audit:view` 权限

**解决：**
```bash
# 1. 确认权限已配置
python scripts/add_audit_permission.py

# 2. 重新登录刷新权限
# 登出 → 重新登录

# 3. 检查用户角色
# 确保用户是管理员角色
```

---

### 问题5：审计记录没有生成

**排查步骤：**

1. **检查表是否存在：**
```sql
\d audit_log
```

2. **检查后端日志：**
```bash
# 查看控制台输出，是否有错误信息
```

3. **手动测试记录：**
```python
# backend/test_audit.py
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.audit_log import AuditLog

async def test():
    async with AsyncSessionLocal() as db:
        log = AuditLog(
            username="test",
            action="test",
            status="success"
        )
        db.add(log)
        await db.commit()
        print("✓ 测试记录创建成功")

asyncio.run(test())
```

---

## 生产环境部署建议

### 1. 环境变量配置

**backend/.env.production：**
```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# JWT
JWT_SECRET_KEY=<生产环境强密钥>
JWT_EXPIRE_MINUTES=1440

# 日志
LOG_LEVEL=INFO

# CORS（根据实际域名配置）
CORS_ORIGINS=["https://yourdomain.com"]
```

### 2. 数据库备份策略

```bash
# 定期备份审计日志
pg_dump -U postgres -t audit_log financial_analysis > audit_log_backup.sql

# 定期清理旧日志（保留90天）
DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '90 days';
```

### 3. 监控和告警

**关键指标：**
- 审计日志写入速率
- 审计日志查询响应时间
- 失败操作统计
- 异常IP访问

**告警规则：**
- 连续登录失败超过5次
- 同一IP短时间内大量操作
- 批量删除操作

### 4. 性能优化

**索引维护：**
```sql
-- 定期重建索引
REINDEX TABLE audit_log;

-- 分析查询计划
EXPLAIN ANALYZE 
SELECT * FROM audit_log 
WHERE action = 'login' 
AND created_at > NOW() - INTERVAL '7 days';
```

**分区表（数据量大时）：**
```sql
-- 按月分区
CREATE TABLE audit_log_2026_01 PARTITION OF audit_log
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## 维护操作

### 日常维护

**1. 查看审计统计：**
```sql
-- 今天的操作统计
SELECT action, COUNT(*) as count
FROM audit_log
WHERE created_at::date = CURRENT_DATE
GROUP BY action
ORDER BY count DESC;

-- 失败操作
SELECT username, action, error_message, created_at
FROM audit_log
WHERE status != 'success'
ORDER BY created_at DESC
LIMIT 20;
```

**2. 清理测试数据：**
```sql
-- 删除测试用户的审计记录
DELETE FROM audit_log WHERE username = 'testuser';
```

**3. 导出审计报告：**
```bash
# 导出最近30天的审计日志
psql -U postgres -d financial_analysis -c "
COPY (
  SELECT * FROM audit_log 
  WHERE created_at > NOW() - INTERVAL '30 days'
  ORDER BY created_at DESC
) TO '/tmp/audit_report.csv' CSV HEADER;
"
```

---

## 回滚方案

如果需要回滚审计功能：

```bash
# 1. 回滚数据库迁移
cd backend
alembic downgrade -1

# 2. 移除审计权限
# 连接PostgreSQL
DELETE FROM role_permission 
WHERE permission_id = (SELECT id FROM permission WHERE code = 'audit:view');

DELETE FROM permission WHERE code = 'audit:view';

# 3. 重启服务
# 重新启动后端和前端服务
```

---

## 成功验证标准

✅ 所有检查项通过后，系统即可正常使用：

- [x] 数据库迁移成功
- [x] 审计权限配置成功
- [x] 后端服务正常启动
- [x] 前端服务正常启动
- [x] 登录操作产生审计记录
- [x] 审计日志页面可访问
- [x] 筛选功能正常工作
- [x] 详情查看正常显示
- [x] 权限控制生效

---

**部署完成！** 🎉

如有问题，请参考：
- 完整文档：`docs/stage7_delivery.md`
- 测试指南：`docs/stage7_test.md`
- 功能总结：`docs/stage7_summary.md`
