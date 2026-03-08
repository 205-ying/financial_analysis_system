"""
容器初始化默认数据脚本。

用途：
- 在全新数据库中创建可登录的默认账号
- 初始化最小可用的角色、权限和基础业务数据
- 保持幂等，重复执行不会创建重复数据
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.expense import ExpenseType
from app.models.store import Product, ProductCategory, Store
from app.models.user import Permission, Role, User, role_permission, user_role
from app.models.user_store import UserStorePermission

PERMISSIONS = [
    ("dashboard:view", "查看经营看板", "dashboard", "view"),
    ("store:view", "查看门店", "store", "view"),
    ("store:create", "创建门店", "store", "create"),
    ("store:edit", "编辑门店", "store", "edit"),
    ("store:delete", "删除门店", "store", "delete"),
    ("order:view", "查看订单", "order", "view"),
    ("order:create", "创建订单", "order", "create"),
    ("order:update", "编辑订单", "order", "update"),
    ("order:delete", "删除订单", "order", "delete"),
    ("order:export", "导出订单", "order", "export"),
    ("expense:view", "查看费用", "expense", "view"),
    ("expense:create", "创建费用", "expense", "create"),
    ("expense:update", "编辑费用", "expense", "update"),
    ("expense:delete", "删除费用", "expense", "delete"),
    ("expense:export", "导出费用", "expense", "export"),
    ("budget:view", "查看预算", "budget", "view"),
    ("budget:manage", "管理预算", "budget", "manage"),
    ("decision:cvp", "本量利分析", "decision", "cvp"),
    ("kpi:view", "查看KPI", "kpi", "view"),
    ("kpi:rebuild", "重建KPI", "kpi", "rebuild"),
    ("report:view", "查看报表", "report", "view"),
    ("report:export", "导出报表", "report", "export"),
    ("audit:view", "查看审计日志", "audit", "view"),
    ("import_job:create", "创建导入任务", "import_job", "create"),
    ("import_job:view", "查看导入任务", "import_job", "view"),
    ("import_job:run", "执行导入任务", "import_job", "run"),
    ("import_job:download", "下载导入报告", "import_job", "download"),
    ("product_analysis:view", "查看菜品分析", "product_analysis", "view"),
    ("user:view", "查看用户", "user", "view"),
    ("user:create", "创建用户", "user", "create"),
    ("user:edit", "编辑用户", "user", "edit"),
    ("role:view", "查看角色", "role", "view"),
    ("role:create", "创建角色", "role", "create"),
    ("role:edit", "编辑角色", "role", "edit"),
    ("role:delete", "删除角色", "role", "delete"),
    ("role:assign-permission", "分配角色权限", "role", "assign-permission"),
]

MANAGER_PERMISSION_CODES = {
    "dashboard:view",
    "store:view",
    "order:view",
    "order:create",
    "expense:view",
    "expense:create",
    "budget:view",
    "kpi:view",
    "report:view",
    "product_analysis:view",
    "import_job:view",
}

CASHIER_PERMISSION_CODES = {
    "dashboard:view",
    "order:view",
    "order:create",
    "store:view",
}


async def get_or_create_permission(
    session: AsyncSession, code: str, name: str, resource: str, action: str
) -> Permission:
    result = await session.execute(select(Permission).where(Permission.code == code))
    permission = result.scalar_one_or_none()
    if permission is not None:
        return permission

    permission = Permission(
        code=code,
        name=name,
        resource=resource,
        action=action,
        description=name,
    )
    session.add(permission)
    await session.flush()
    return permission


async def get_or_create_role(
    session: AsyncSession, code: str, name: str, description: str
) -> Role:
    result = await session.execute(select(Role).where(Role.code == code))
    role = result.scalar_one_or_none()
    if role is not None:
        return role

    role = Role(code=code, name=name, description=description, is_active=True)
    session.add(role)
    await session.flush()
    return role


async def ensure_role_permission(
    session: AsyncSession, role_id: int, permission_id: int
) -> None:
    result = await session.execute(
        select(role_permission).where(
            role_permission.c.role_id == role_id,
            role_permission.c.permission_id == permission_id,
        )
    )
    if result.first() is None:
        await session.execute(
            role_permission.insert().values(role_id=role_id, permission_id=permission_id)
        )


async def get_or_create_user(
    session: AsyncSession,
    username: str,
    password: str,
    email: str,
    full_name: str,
    phone: str,
    is_superuser: bool,
) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        phone=phone,
        is_active=True,
        is_superuser=is_superuser,
    )
    session.add(user)
    await session.flush()
    return user


async def ensure_user_role(session: AsyncSession, user_id: int, role_id: int) -> None:
    result = await session.execute(
        select(user_role).where(
            user_role.c.user_id == user_id,
            user_role.c.role_id == role_id,
        )
    )
    if result.first() is None:
        await session.execute(user_role.insert().values(user_id=user_id, role_id=role_id))


async def get_or_create_store(session: AsyncSession) -> Store:
    result = await session.execute(select(Store).where(Store.code == "STORE001"))
    store = result.scalar_one_or_none()
    if store is not None:
        return store

    store = Store(
        code="STORE001",
        name="默认示例门店",
        address="示例地址 1 号",
        phone="13800000000",
        contact_person="系统初始化",
        business_hours="09:00-21:00",
        area_sqm=Decimal("120.00"),
        is_active=True,
        sort_order=1,
        remark="容器初始化自动创建",
        is_deleted=False,
    )
    session.add(store)
    await session.flush()
    return store


async def ensure_user_store_permission(
    session: AsyncSession, user_id: int, store_id: int
) -> None:
    result = await session.execute(
        select(UserStorePermission).where(
            UserStorePermission.user_id == user_id,
            UserStorePermission.store_id == store_id,
        )
    )
    if result.scalar_one_or_none() is None:
        session.add(UserStorePermission(user_id=user_id, store_id=store_id))
        await session.flush()


async def get_or_create_product_category(session: AsyncSession) -> ProductCategory:
    result = await session.execute(
        select(ProductCategory).where(ProductCategory.code == "CAT001")
    )
    category = result.scalar_one_or_none()
    if category is not None:
        return category

    category = ProductCategory(
        code="CAT001",
        name="招牌菜",
        level=1,
        description="容器初始化默认分类",
        is_active=True,
        sort_order=1,
    )
    session.add(category)
    await session.flush()
    return category


async def get_or_create_product(session: AsyncSession, category_id: int) -> Product:
    result = await session.execute(select(Product).where(Product.sku_code == "SKU001"))
    product = result.scalar_one_or_none()
    if product is not None:
        return product

    product = Product(
        sku_code="SKU001",
        name="示例红烧牛肉面",
        category_id=category_id,
        unit_price=Decimal("28.00"),
        cost_price=Decimal("12.00"),
        unit="份",
        description="容器初始化默认菜品",
        is_active=True,
        is_featured=True,
        sort_order=1,
        is_deleted=False,
    )
    session.add(product)
    await session.flush()
    return product


async def get_or_create_expense_type(session: AsyncSession) -> ExpenseType:
    result = await session.execute(
        select(ExpenseType).where(ExpenseType.type_code == "EXP001")
    )
    expense_type = result.scalar_one_or_none()
    if expense_type is not None:
        return expense_type

    expense_type = ExpenseType(
        type_code="EXP001",
        name="房租",
        level=1,
        category="operating",
        description="容器初始化默认费用科目",
        is_active=True,
        sort_order=1,
        cost_behavior="fixed",
    )
    session.add(expense_type)
    await session.flush()
    return expense_type


async def seed_default_data() -> None:
    async with AsyncSessionLocal() as session:
        permissions: dict[str, Permission] = {}
        for code, name, resource, action in PERMISSIONS:
            permissions[code] = await get_or_create_permission(
                session, code, name, resource, action
            )

        admin_role = await get_or_create_role(
            session, "admin", "系统管理员", "拥有全部系统权限"
        )
        manager_role = await get_or_create_role(
            session, "manager", "门店经理", "负责门店日常运营"
        )
        cashier_role = await get_or_create_role(
            session, "cashier", "收银员", "负责订单与收银"
        )

        for permission in permissions.values():
            await ensure_role_permission(session, admin_role.id, permission.id)

        for code in MANAGER_PERMISSION_CODES:
            await ensure_role_permission(session, manager_role.id, permissions[code].id)

        for code in CASHIER_PERMISSION_CODES:
            await ensure_role_permission(session, cashier_role.id, permissions[code].id)

        admin = await get_or_create_user(
            session,
            username="admin",
            password="Admin@123",
            email="admin@example.com",
            full_name="系统管理员",
            phone="13800138000",
            is_superuser=True,
        )
        manager = await get_or_create_user(
            session,
            username="manager",
            password="Manager@123",
            email="manager@example.com",
            full_name="门店经理",
            phone="13800138001",
            is_superuser=False,
        )
        cashier = await get_or_create_user(
            session,
            username="cashier",
            password="Cashier@123",
            email="cashier@example.com",
            full_name="收银员",
            phone="13800138002",
            is_superuser=False,
        )

        await ensure_user_role(session, admin.id, admin_role.id)
        await ensure_user_role(session, manager.id, manager_role.id)
        await ensure_user_role(session, cashier.id, cashier_role.id)

        store = await get_or_create_store(session)
        category = await get_or_create_product_category(session)
        await get_or_create_product(session, category.id)
        await get_or_create_expense_type(session)
        await ensure_user_store_permission(session, manager.id, store.id)
        await ensure_user_store_permission(session, cashier.id, store.id)

        await session.commit()

        print("默认数据初始化完成")
        print("可用账号：admin / Admin@123")
        print("可用账号：manager / Manager@123")
        print("可用账号：cashier / Cashier@123")


if __name__ == "__main__":
    asyncio.run(seed_default_data())
