"""
添加预算管理权限到数据库

使用方法:
    python scripts/add_budget_permissions.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session
from app.models.user import Permission, Role


async def main():
    """主函数"""
    print("=" * 60)
    print("添加预算管理权限")
    print("=" * 60)
    
    try:
        async for db in get_async_session():
            # 1. 检查权限是否已存在
            result = await db.execute(
                select(Permission).where(Permission.code == 'budget:view')
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("\n✓ 预算管理权限已存在，跳过创建")
            else:
                # 2. 创建预算相关权限
                print("\n创建预算管理权限...")
                
                permissions = [
                    Permission(
                        code='budget:view',
                        name='预算查看',
                        description='查看预算数据和差异分析'
                    ),
                    Permission(
                        code='budget:manage',
                        name='预算管理',
                        description='创建和修改预算设置'
                    )
                ]
                
                for perm in permissions:
                    db.add(perm)
                    print(f"  ✓ 创建权限: {perm.code} - {perm.name}")
                
                await db.commit()
                
                # 刷新以获取ID
                for perm in permissions:
                    await db.refresh(perm)
                
                # 3. 给管理员角色添加这些权限
                print("\n给管理员角色添加预算权限...")
                
                result = await db.execute(
                    select(Role).where(Role.code == 'admin')
                )
                admin_role = result.scalar_one_or_none()
                
                if admin_role:
                    for perm in permissions:
                        if perm not in admin_role.permissions:
                            admin_role.permissions.append(perm)
                    
                    await db.commit()
                    print("  ✓ 已将预算权限添加到管理员角色")
                else:
                    print("  ⚠ 警告: 未找到admin角色，请手动分配权限")
                
                print("\n" + "=" * 60)
                print("预算管理权限添加完成！")
                print("=" * 60)
                
                print("\n下一步:")
                print("  1. 重启后端服务")
                print("  2. 重新登录系统")
                print("  3. 在左侧菜单中可以看到'预算管理'菜单")
            
            break  # 只需要一个session
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
