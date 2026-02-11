"""
添加CVP和预算管理相关权限到数据库

使用方法:
cd backend
python scripts/add_cvp_budget_permissions.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, AsyncSessionLocal
from app.models.user import Permission, Role


async def add_permissions():
    """添加权限到数据库"""
    async with AsyncSessionLocal() as db:
        # 定义要添加的权限
        permissions_to_add = [
            {
                "code": "budget:view",
                "name": "查看预算",
                "description": "查看预算数据的权限",
                "resource": "budget",
                "action": "view"
            },
            {
                "code": "budget:manage",
                "name": "管理预算",
                "description": "编制和修改预算的权限",
                "resource": "budget",
                "action": "manage"
            },
            {
                "code": "decision:cvp",
                "name": "本量利分析",
                "description": "访问本量利(CVP)分析功能的权限",
                "resource": "decision",
                "action": "cvp"
            }
        ]

        added_count = 0
        existing_count = 0

        for perm_data in permissions_to_add:
            # 检查权限是否已存在
            result = await db.execute(
                select(Permission).where(Permission.code == perm_data["code"])
            )
            existing_perm = result.scalar_one_or_none()

            if existing_perm:
                print(f"✓ 权限已存在: {perm_data['code']} - {perm_data['name']}")
                existing_count += 1
            else:
                # 创建新权限
                new_perm = Permission(
                    code=perm_data["code"],
                    name=perm_data["name"],
                    description=perm_data["description"],
                    resource=perm_data["resource"],
                    action=perm_data["action"]
                )
                db.add(new_perm)
                print(f"+ 添加权限: {perm_data['code']} - {perm_data['name']}")
                added_count += 1

        # 提交所有更改
        await db.commit()

        print(f"\n总计: 添加 {added_count} 个权限, {existing_count} 个已存在")

        # 可选：将权限分配给管理员角色
        print("\n--- 分配权限给管理员角色 ---")
        result = await db.execute(
            select(Role).where(Role.name == "系统管理员")
        )
        admin_role = result.scalar_one_or_none()

        if admin_role:
            # 获取所有权限
            result = await db.execute(
                select(Permission).where(
                    Permission.code.in_(["budget:view", "budget:manage", "decision:cvp"])
                )
            )
            permissions = result.scalars().all()

            # 检查哪些权限还未分配
            existing_perm_ids = {p.id for p in admin_role.permissions}
            new_perms = [p for p in permissions if p.id not in existing_perm_ids]

            if new_perms:
                admin_role.permissions.extend(new_perms)
                await db.commit()
                print(f"✓ 为管理员角色添加了 {len(new_perms)} 个新权限")
            else:
                print("✓ 管理员角色已拥有所有权限")
        else:
            print("⚠ 未找到'系统管理员'角色")


async def main():
    """主函数"""
    print("=" * 50)
    print("添加CVP和预算管理权限")
    print("=" * 50)
    print()

    try:
        await add_permissions()
        print("\n✓ 权限添加完成!")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
