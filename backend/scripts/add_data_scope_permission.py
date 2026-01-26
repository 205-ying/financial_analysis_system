"""
添加 user:assign-store 权限的脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, Role, Permission, role_permission


async def add_assign_store_permission():
    """添加门店权限分配的权限"""
    async with AsyncSessionLocal() as session:
        try:
            # 检查权限是否已存在
            result = await session.execute(
                select(Permission).where(Permission.code == "user:assign-store")
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✅ 权限已存在: user:assign-store")
                return
            
            # 创建新权限
            new_permission = Permission(
                code="user:assign-store",
                name="分配门店权限",
                resource="user",
                action="assign-store",
                description="为用户分配门店数据权限"
            )
            session.add(new_permission)
            await session.flush()
            
            # 将权限分配给admin角色
            admin_role_result = await session.execute(
                select(Role).where(Role.code == "admin")
            )
            admin_role = admin_role_result.scalar_one_or_none()
            
            if admin_role:
                await session.execute(
                    role_permission.insert().values(
                        role_id=admin_role.id,
                        permission_id=new_permission.id
                    )
                )
                print(f"✅ 已将权限分配给 admin 角色")
            
            await session.commit()
            print("✅ 成功添加权限: user:assign-store")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 添加权限失败: {str(e)}")
            raise


async def add_user_store_permissions():
    """为manager用户添加门店权限"""
    async with AsyncSessionLocal() as session:
        try:
            from app.models.store import Store
            from app.models.user_store import UserStorePermission
            
            # 获取manager用户（使用manager003）
            manager_result = await session.execute(
                select(User).where(User.username == "manager003")
            )
            manager = manager_result.scalar_one_or_none()
            
            if not manager:
                print("⚠️  manager003 用户不存在，尝试创建...")
                from app.core.security import get_password_hash
                
                # 创建manager测试用户
                manager = User(
                    username="manager",
                    email="manager@example.com",
                    password_hash=get_password_hash("Manager@123"),
                    full_name="门店经理",
                    is_active=True,
                    is_superuser=False
                )
                session.add(manager)
                await session.flush()
                print("✅ 已创建 manager 用户")
            
            # 获取第一个门店
            stores_result = await session.execute(select(Store).order_by(Store.id))
            stores = stores_result.scalars().all()
            
            if not stores:
                print("⚠️  没有门店数据")
                return
            
            first_store = stores[0]
            
            # 检查是否已有权限
            existing_result = await session.execute(
                select(UserStorePermission).where(
                    UserStorePermission.user_id == manager.id,
                    UserStorePermission.store_id == first_store.id
                )
            )
            if existing_result.scalar_one_or_none():
                print(f"✅ manager 用户已有门店权限: {first_store.name}")
                return
            
            # 添加门店权限
            permission = UserStorePermission(
                user_id=manager.id,
                store_id=first_store.id
            )
            session.add(permission)
            await session.commit()
            
            print(f"✅ 为 manager (ID={manager.id}) 分配门店权限: {first_store.name} (ID={first_store.id})")
            print(f"ℹ️  测试提示: manager/Manager@123 用户只能访问 {first_store.name} 的数据")
            print(f"ℹ️  测试提示: admin/Admin@123 用户可以访问所有门店的数据")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 添加门店权限失败: {str(e)}")
            raise


async def main():
    print("\n" + "="*60)
    print("🔧 补充权限和测试数据...")
    print("="*60 + "\n")
    
    await add_assign_store_permission()
    print()
    await add_user_store_permissions()
    
    print("\n" + "="*60)
    print("✅ 完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
