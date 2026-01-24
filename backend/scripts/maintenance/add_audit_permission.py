"""
添加审计日志查看权限

该脚本用于向数据库中添加 audit:view 权限，并将其分配给管理员角色
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, AsyncSessionLocal
from app.models.user import Permission, Role


async def add_audit_permission():
    """添加审计日志权限"""
    async with AsyncSessionLocal() as db:
        try:
            # 1. 检查权限是否已存在
            result = await db.execute(
                select(Permission).where(Permission.code == "audit:view")
            )
            existing_perm = result.scalar_one_or_none()
            
            if existing_perm:
                print("✓ 权限 'audit:view' 已存在")
                permission = existing_perm
            else:
                # 2. 创建权限
                permission = Permission(
                    code="audit:view",
                    name="审计日志查看",
                    description="查看审计日志列表和详情"
                )
                db.add(permission)
                await db.flush()
                print("✓ 已创建权限 'audit:view'")
            
            # 3. 查找管理员角色
            result = await db.execute(
                select(Role).where(Role.code == "admin")
            )
            admin_role = result.scalar_one_or_none()
            
            if not admin_role:
                print("✗ 未找到管理员角色，跳过权限分配")
                await db.commit()
                return
            
            # 4. 检查角色是否已有该权限
            if permission in admin_role.permissions:
                print("✓ 管理员角色已拥有 'audit:view' 权限")
            else:
                # 5. 分配权限给管理员角色
                admin_role.permissions.append(permission)
                print("✓ 已将 'audit:view' 权限分配给管理员角色")
            
            await db.commit()
            print("\n权限配置完成！")
            
        except Exception as e:
            await db.rollback()
            print(f"✗ 错误: {str(e)}")
            raise


async def main():
    """主函数"""
    print("=" * 60)
    print("添加审计日志权限")
    print("=" * 60)
    print()
    
    await add_audit_permission()
    
    print()
    print("=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
