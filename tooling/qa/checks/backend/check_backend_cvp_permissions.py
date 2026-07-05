"""检查数据库中的 CVP/预算权限及其角色分配关系。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
BACKEND_DIR = ROOT_DIR / "services" / "api"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text

from app.core.database import AsyncSessionLocal


async def main() -> None:
    print("🔍 检查 CVP/预算权限...")

    async with AsyncSessionLocal() as session:
        permissions_result = await session.execute(
            text(
                """
                SELECT id, code, name, resource, action
                FROM permissions
                WHERE code LIKE '%cvp%' OR code LIKE '%budget%'
                ORDER BY code
                """
            )
        )
        permissions = permissions_result.fetchall()

        if not permissions:
            print("❌ 未找到 CVP/预算相关权限")
            return

        print("✅ 权限清单：")
        for permission in permissions:
            print(
                f"   - {permission[1]}: {permission[2]} "
                + f"(resource={permission[3]}, action={permission[4]})"
            )

        role_result = await session.execute(
            text(
                """
                SELECT r.name AS role_name, p.code, p.name
                FROM roles r
                JOIN role_permission rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE p.code LIKE '%cvp%' OR p.code LIKE '%budget%'
                ORDER BY r.name, p.code
                """
            )
        )
        role_permissions = role_result.fetchall()

        print("\n✅ 角色分配：" if role_permissions else "\n❌ 未找到角色分配")
        for item in role_permissions:
            print(f"   - {item[0]}: {item[1]} ({item[2]})")

        admin_result = await session.execute(
            text(
                """
                SELECT u.username, p.code, p.name
                FROM users u
                JOIN user_role ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                JOIN role_permission rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.username = 'admin' AND (p.code LIKE '%cvp%' OR p.code LIKE '%budget%')
                ORDER BY p.code
                """
            )
        )
        admin_permissions = admin_result.fetchall()

        print("\n✅ admin 权限：" if admin_permissions else "\n❌ admin 未分配到 CVP/预算权限")
        for item in admin_permissions:
            print(f"   - {item[1]}: {item[2]}")

        print("\n📊 汇总：")
        print(f"   权限数: {len(permissions)}")
        print(f"   角色分配数: {len(role_permissions)}")
        print(f"   admin权限数: {len(admin_permissions)}")


if __name__ == "__main__":
    asyncio.run(main())
