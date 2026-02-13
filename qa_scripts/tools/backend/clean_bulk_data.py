"""
清理所有测试数据脚本

删除数据库中的所有测试数据，保留基础配置数据
包括：订单、费用、KPI、产品、门店、用户等

使用方法：
python qa_scripts/tools/backend/clean_bulk_data.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User, Role, user_role
from app.models.store import Store, ProductCategory, Product
from app.models.order import OrderHeader, OrderItem
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.kpi import KpiDailyStore


async def clean_data():
    """清理所有业务数据"""
    print("\n" + "="*70)
    print("🗑️  开始清理数据库...")
    print("="*70 + "\n")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. 清理订单明细
            print("📋 清理订单明细...")
            result = await session.execute(select(func.count(OrderItem.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(OrderItem))
                print(f"  ✅ 删除了 {count} 条订单明细")
            else:
                print(f"  ℹ️  没有订单明细需要清理")
            
            # 2. 清理订单
            print("📋 清理订单...")
            result = await session.execute(select(func.count(OrderHeader.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(OrderHeader))
                print(f"  ✅ 删除了 {count} 条订单")
            else:
                print(f"  ℹ️  没有订单需要清理")
            
            # 3. 清理KPI
            print("📊 清理KPI数据...")
            result = await session.execute(select(func.count(KpiDailyStore.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(KpiDailyStore))
                print(f"  ✅ 删除了 {count} 条KPI记录")
            else:
                print(f"  ℹ️  没有KPI记录需要清理")
            
            # 4. 清理费用记录
            print("💰 清理费用记录...")
            result = await session.execute(select(func.count(ExpenseRecord.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(ExpenseRecord))
                print(f"  ✅ 删除了 {count} 条费用记录")
            else:
                print(f"  ℹ️  没有费用记录需要清理")
            
            # 5. 清理产品
            print("🍱 清理产品...")
            result = await session.execute(select(func.count(Product.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(Product))
                print(f"  ✅ 删除了 {count} 个产品")
            else:
                print(f"  ℹ️  没有产品需要清理")
            
            # 6. 清理门店
            print("🏪 清理门店...")
            result = await session.execute(select(func.count(Store.id)))
            count = result.scalar()
            if count > 0:
                await session.execute(delete(Store))
                print(f"  ✅ 删除了 {count} 个门店")
            else:
                print(f"  ℹ️  没有门店需要清理")
            
            # 7. 清理用户（保留admin）
            print("👤 清理用户（保留admin）...")
            result = await session.execute(
                select(func.count(User.id)).filter(User.username != "admin")
            )
            count = result.scalar()
            if count > 0:
                # 先删除用户角色关联
                result = await session.execute(
                    select(User.id).filter(User.username != "admin")
                )
                user_ids = [row[0] for row in result.all()]
                if user_ids:
                    await session.execute(
                        delete(user_role).where(user_role.c.user_id.in_(user_ids))
                    )
                
                # 再删除用户
                await session.execute(
                    delete(User).filter(User.username != "admin")
                )
                print(f"  ✅ 删除了 {count} 个用户")
            else:
                print(f"  ℹ️  没有用户需要清理")
            
            await session.commit()
            
            print("\n" + "="*70)
            print("✅ 数据清理完成！")
            print("="*70)
            print("\n💡 提示：admin用户和基础配置数据（角色、产品类别、费用类型）已保留\n")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 清理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """主函数"""
    try:
        await clean_data()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户取消")
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

