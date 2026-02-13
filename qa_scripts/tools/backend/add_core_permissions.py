"""统一补充核心权限（预算/CVP/数据权限/菜品分析/角色用户/审计）。

用法：
    cd backend
    python qa_scripts/tools/backend/add_core_permissions.py
    python qa_scripts/tools/backend/add_core_permissions.py --setup-data-scope-demo
"""

import argparse
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, OperationalError

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.store import Store
from app.models.user import Permission, Role, User, role_permission
from app.models.user_store import UserStorePermission


PERMISSION_DEFINITIONS = [
    {
        "code": "budget:view",
        "name": "预算查看",
        "resource": "budget",
        "action": "view",
        "description": "查看预算数据和差异分析",
    },
    {
        "code": "budget:manage",
        "name": "预算管理",
        "resource": "budget",
        "action": "manage",
        "description": "创建和修改预算设置",
    },
    {
        "code": "decision:cvp",
        "name": "本量利分析",
        "resource": "decision",
        "action": "cvp",
        "description": "访问本量利(CVP)分析功能",
    },
    {
        "code": "user:assign-store",
        "name": "分配门店权限",
        "resource": "user",
        "action": "assign-store",
        "description": "为用户分配门店数据权限",
    },
    {
        "code": "product_analysis:view",
        "name": "查看菜品分析",
        "resource": "product_analysis",
        "action": "view",
        "description": "查看菜品销售分析报表",
    },
    {
        "code": "user:view",
        "name": "查看用户",
        "resource": "user",
        "action": "view",
        "description": "查看用户列表和详情",
    },
    {
        "code": "user:create",
        "name": "创建用户",
        "resource": "user",
        "action": "create",
        "description": "创建新用户",
    },
    {
        "code": "user:edit",
        "name": "编辑用户",
        "resource": "user",
        "action": "edit",
        "description": "编辑用户信息",
    },
    {
        "code": "role:view",
        "name": "查看角色",
        "resource": "role",
        "action": "view",
        "description": "查看角色列表和详情",
    },
    {
        "code": "role:create",
        "name": "创建角色",
        "resource": "role",
        "action": "create",
        "description": "创建新角色",
    },
    {
        "code": "role:edit",
        "name": "编辑角色",
        "resource": "role",
        "action": "edit",
        "description": "编辑角色信息",
    },
    {
        "code": "role:delete",
        "name": "删除角色",
        "resource": "role",
        "action": "delete",
        "description": "删除角色",
    },
    {
        "code": "role:assign-permission",
        "name": "分配角色权限",
        "resource": "role",
        "action": "assign-permission",
        "description": "为角色分配权限并为用户分配角色",
    },
    {
        "code": "audit:view",
        "name": "审计日志查看",
        "resource": "audit",
        "action": "view",
        "description": "查看审计日志列表和详情",
    },
]


async def setup_data_scope_demo(session) -> None:
    manager_result = await session.execute(select(User).where(User.username == "manager003"))
    manager = manager_result.scalar_one_or_none()

    if manager is None:
        manager = User(
            username="manager003",
            email="manager003@example.com",
            password_hash=hash_password("Manager@123"),
            full_name="门店经理003",
            is_active=True,
            is_superuser=False,
        )
        session.add(manager)
        await session.flush()
        print("+ 已创建演示用户: manager003")

    stores_result = await session.execute(select(Store).order_by(Store.id))
    stores = stores_result.scalars().all()
    if not stores:
        print("! 无门店数据，跳过门店权限演示初始化")
        return

    first_store = stores[0]
    exists_result = await session.execute(
        select(UserStorePermission).where(
            UserStorePermission.user_id == manager.id,
            UserStorePermission.store_id == first_store.id,
        )
    )
    if exists_result.scalar_one_or_none() is None:
        session.add(UserStorePermission(user_id=manager.id, store_id=first_store.id))
        print(f"+ 已分配门店权限: manager003 -> {first_store.name}(ID={first_store.id})")
    else:
        print("= manager003 门店权限已存在")


async def run_once(setup_demo: bool) -> int:
    async with AsyncSessionLocal() as session:
        created_count = 0

        admin_role_result = await session.execute(select(Role).where(Role.code == "admin"))
        admin_role = admin_role_result.scalar_one_or_none()
        if admin_role is None:
            print("! 未找到 admin 角色，权限将仅创建不分配")

        for item in PERMISSION_DEFINITIONS:
            existing = await session.execute(select(Permission).where(Permission.code == item["code"]))
            permission = existing.scalar_one_or_none()

            if permission is None:
                permission = Permission(**item)
                session.add(permission)
                await session.flush()
                created_count += 1
                print(f"+ 新增权限: {item['code']}")
            else:
                print(f"= 已存在权限: {item['code']}")

            if admin_role is not None:
                relation_exists = await session.execute(
                    select(role_permission).where(
                        role_permission.c.role_id == admin_role.id,
                        role_permission.c.permission_id == permission.id,
                    )
                )
                if relation_exists.first() is None:
                    await session.execute(
                        role_permission.insert().values(
                            role_id=admin_role.id,
                            permission_id=permission.id,
                        )
                    )
                    print(f"  -> 已分配给 admin: {item['code']}")

        if setup_demo:
            await setup_data_scope_demo(session)

        await session.commit()
        print(f"\n完成：新增 {created_count} 个权限")
        return created_count


async def main() -> None:
    parser = argparse.ArgumentParser(description="统一补充核心权限")
    parser.add_argument(
        "--setup-data-scope-demo",
        action="store_true",
        help="同时初始化 data scope 演示用户和门店权限",
    )
    args = parser.parse_args()

    max_retries = 3
    delay_seconds = 1.5

    for attempt in range(1, max_retries + 1):
        try:
            await run_once(args.setup_data_scope_demo)
            return
        except (ConnectionResetError, OSError, DBAPIError, OperationalError, Exception) as exc:
            if attempt == max_retries:
                print(f"\n❌ 执行失败（已重试 {max_retries} 次）：{exc}")
                raise

            print(f"\n⚠️ 数据库连接中断（第 {attempt}/{max_retries} 次）：{exc}")
            print(f"   {delay_seconds:.1f}s 后自动重试...")
            await asyncio.sleep(delay_seconds)
            delay_seconds *= 2


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        sys.exit(1)

