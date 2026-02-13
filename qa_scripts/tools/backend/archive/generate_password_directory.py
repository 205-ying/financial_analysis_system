"""
生成密码目录文档

生成包含所有用户账号和密码信息的Markdown文档

使用方法：
python qa_scripts/tools/backend/archive/generate_password_directory.py
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User, Role, user_role


async def generate_password_directory():
    """生成密码目录文档"""
    print("=" * 70)
    print("📝 正在生成密码目录文档...")
    print("=" * 70)
    print()
    
    async with AsyncSessionLocal() as session:
        # 获取所有用户
        result = await session.execute(
            select(User).order_by(User.username)
        )
        users = result.scalars().all()
        
        if not users:
            print("❌ 没有找到任何用户")
            return
        
        # 分类用户
        admin_users = []
        cashier_users = []
        manager_users = []
        accountant_users = []
        other_users = []
        
        for user in users:
            if user.is_superuser or user.username == "admin":
                admin_users.append(user)
            elif "cashier" in user.username:
                cashier_users.append(user)
            elif "manager" in user.username:
                manager_users.append(user)
            elif "accountant" in user.username:
                accountant_users.append(user)
            else:
                other_users.append(user)
        
        # 生成Markdown文档
        md_content = generate_markdown(
            admin_users, cashier_users, manager_users, 
            accountant_users, other_users
        )
        
        # 保存文档
        output_file = Path(__file__).resolve().parents[1] / "用户密码目录.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"✅ 文档已生成：{output_file}")
        print()
        print("📊 用户统计：")
        print(f"  - 管理员：{len(admin_users)} 个")
        print(f"  - 收银员：{len(cashier_users)} 个")
        print(f"  - 门店经理：{len(manager_users)} 个")
        print(f"  - 财务人员：{len(accountant_users)} 个")
        if other_users:
            print(f"  - 其他用户：{len(other_users)} 个")
        print(f"  - 总计：{len(users)} 个")
        print()


def generate_markdown(admin_users, cashier_users, manager_users, accountant_users, other_users):
    """生成Markdown文档内容"""
    now = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    content = f"""# 餐饮财务分析系统 - 用户密码目录

> 📅 生成时间：{now}  
> 🔐 安全提示：本文档包含敏感信息，请妥善保管，切勿外泄！

---

## 📋 密码规则说明

本系统所有用户密码遵循以下规则：

| 用户类型 | 密码格式 | 示例 |
|---------|---------|-----|
| **超级管理员** | `Admin@123` | admin 用户 |
| **初始测试用户** | `角色名@123` | Manager@123, Cashier@123 |
| **批量测试用户** | `Test@123` | 所有编号测试用户统一密码 |

**密码特点**：
- ✅ 包含大小写字母、数字和特殊字符
- ✅ 长度8-20位，符合安全标准
- ✅ 所有测试用户使用统一密码便于测试

---

## 👤 用户账号列表

### 🔑 超级管理员 ({len(admin_users)} 个)

拥有系统所有权限，可以管理用户、角色、权限等。

| 用户名 | 密码 | 邮箱 | 姓名 | 状态 |
|--------|-----|------|-----|------|
"""
    
    # 管理员用户
    for user in admin_users:
        status = "✅ 启用" if user.is_active else "❌ 禁用"
        content += f"| **{user.username}** | `Admin@123` | {user.email} | {user.full_name or '-'} | {status} |\n"
    
    # 收银员
    content += f"""
---

### 💰 收银员 ({len(cashier_users)} 个)

处理订单和收款，查看产品信息。

**统一密码**：`Test@123`

<details>
<summary>点击展开查看完整列表（{len(cashier_users)} 个账号）</summary>

| 用户名 | 邮箱 | 姓名 | 状态 |
|--------|------|-----|------|
"""
    
    for user in cashier_users[:50]:  # 显示前50个
        status = "✅" if user.is_active else "❌"
        content += f"| {user.username} | {user.email} | {user.full_name or '-'} | {status} |\n"
    
    if len(cashier_users) > 50:
        content += f"| ... | ... | ... | ... |\n"
        content += f"| *(还有 {len(cashier_users) - 50} 个用户)* | | | |\n"
    
    content += "\n</details>\n"
    
    # 门店经理
    content += f"""
---

### 🏪 门店经理 ({len(manager_users)} 个)

管理门店日常运营，处理订单、费用和查看报表。

**统一密码**：`Test@123`

<details>
<summary>点击展开查看完整列表（{len(manager_users)} 个账号）</summary>

| 用户名 | 邮箱 | 姓名 | 状态 |
|--------|------|-----|------|
"""
    
    for user in manager_users[:50]:
        status = "✅" if user.is_active else "❌"
        content += f"| {user.username} | {user.email} | {user.full_name or '-'} | {status} |\n"
    
    if len(manager_users) > 50:
        content += f"| ... | ... | ... | ... |\n"
        content += f"| *(还有 {len(manager_users) - 50} 个用户)* | | | |\n"
    
    content += "\n</details>\n"
    
    # 财务人员
    content += f"""
---

### 💼 财务人员 ({len(accountant_users)} 个)

管理费用记录，查看财务报表和KPI数据。

**统一密码**：`Test@123`

| 用户名 | 邮箱 | 姓名 | 状态 |
|--------|------|-----|------|
"""
    
    for user in accountant_users:
        status = "✅" if user.is_active else "❌"
        content += f"| {user.username} | {user.email} | {user.full_name or '-'} | {status} |\n"
    
    # 其他用户（如果有）
    if other_users:
        content += f"""
---

### 👥 其他用户 ({len(other_users)} 个)

| 用户名 | 密码 | 邮箱 | 姓名 | 状态 |
|--------|-----|------|-----|------|
"""
        for user in other_users:
            status = "✅" if user.is_active else "❌"
            password = "Admin@123" if user.is_superuser else "Test@123"
            content += f"| {user.username} | `{password}` | {user.email} | {user.full_name or '-'} | {status} |\n"
    
    # 快速参考
    content += f"""
---

## 🚀 快速参考

### 登录示例

**Web登录地址**：`http://localhost:3000`

**推荐测试账号**：

| 场景 | 用户名 | 密码 | 说明 |
|-----|--------|-----|------|
| 系统管理 | admin | `Admin@123` | 所有权限 |
| 门店管理 | manager006 | `Test@123` | 运营权限 |
| 收银测试 | cashier002 | `Test@123` | 基本权限 |
| 财务查看 | accountant015 | `Test@123` | 财务权限 |

### API测试

使用 Postman 或 curl 测试登录：

```bash
# 登录获取token
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "admin", "password": "Admin@123"}}'

# 返回示例
{{
  "code": 200,
  "data": {{
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "user": {{...}}
  }}
}}
```

---

## 🔒 安全建议

⚠️ **重要安全提示**：

1. **开发环境专用** - 这些密码仅用于开发和测试环境
2. **生产环境修改** - 部署到生产环境前必须修改所有默认密码
3. **定期更换** - 建议每3个月更换一次密码
4. **权限控制** - 根据实际需求分配最小必要权限
5. **文档保管** - 本文档包含敏感信息，请勿提交到公开仓库

### 重置密码

使用密码重置脚本：

```bash
cd backend

# 重置admin密码
python qa_scripts/tools/backend/reset_passwords.py

# 重置所有测试用户
python qa_scripts/tools/backend/reset_passwords.py --all-test-users

# 重置指定用户
python qa_scripts/tools/backend/reset_passwords.py --user username --password NewPassword@123
```

---

## 📞 技术支持

如有问题，请联系系统管理员或查看项目文档：
- 项目文档：`docs/`
- 开发指南：`docs/development_guide.md`
- API文档：`http://localhost:8000/docs`

---

> 🔐 **请妥善保管本文档，切勿外泄！**  
> 📅 文档生成时间：{now}
"""
    
    return content


async def main():
    """主函数"""
    try:
        await generate_password_directory()
        print("=" * 70)
        print("✅ 密码目录文档生成完成！")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

