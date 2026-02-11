"""
预算测试数据生成脚本
用于生成预算管理功能的测试数据

使用方法:
    python scripts/generate_budget_test_data.py

生成内容:
    - 10个门店的预算设置
    - 覆盖2026年1-12月
    - 包含实际费用记录（用于差异分析）
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta
import random

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session
from app.models.budget import Budget
from app.models.store import Store
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.user import User


async def get_or_create_data(db: AsyncSession):
    """获取或验证基础数据"""
    print("检查基础数据...")
    
    # 获取门店
    result = await db.execute(select(Store).where(Store.is_active == True).limit(10))
    stores = result.scalars().all()
    if not stores:
        print("❌ 错误：系统中没有可用的门店，请先运行 seed_data.py")
        return None, None, None
    print(f"✓ 找到 {len(stores)} 个门店")
    
    # 获取费用科目
    result = await db.execute(select(ExpenseType))
    expense_types = result.scalars().all()
    if not expense_types:
        print("❌ 错误：系统中没有费用科目，请先运行 seed_data.py")
        return None, None, None
    print(f"✓ 找到 {len(expense_types)} 个费用科目")
    
    # 获取admin用户
    result = await db.execute(select(User).where(User.username == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        print("❌ 错误：找不到admin用户，请先运行 seed_data.py")
        return None, None, None
    print(f"✓ 找到admin用户")
    
    return stores, expense_types, admin


async def clear_existing_budget_data(db: AsyncSession):
    """清理现有测试数据"""
    print("\n清理现有预算测试数据...")
    
    # 删除2026年的预算数据
    result = await db.execute(
        select(Budget).where(Budget.year == 2026)
    )
    budgets = result.scalars().all()
    for budget in budgets:
        await db.delete(budget)
    
    await db.commit()
    print(f"✓ 清理了 {len(budgets)} 条预算记录")


async def generate_budgets(db: AsyncSession, stores, expense_types, admin):
    """生成预算数据"""
    print("\n生成预算数据...")
    
    budget_count = 0
    
    for store in stores:
        print(f"  生成门店 [{store.name}] 的预算...")
        
        # 为每个月生成预算
        for month in range(1, 13):  # 1-12月
            # 为每个费用科目设置预算
            for expense_type in expense_types:
                # 根据费用科目生成合理的预算金额
                base_amount = {
                    "食材采购": 50000,
                    "房租": 20000,
                    "人工工资": 30000,
                    "水电费": 5000,
                    "物料采购": 10000,
                    "设备维修": 3000,
                    "营销推广": 8000,
                    "清洁卫生": 2000,
                }.get(expense_type.name, 5000)
                
                # 添加一些随机波动（±20%）
                amount = Decimal(str(base_amount * (0.8 + random.random() * 0.4)))
                
                budget = Budget(
                    store_id=store.id,
                    expense_type_id=expense_type.id,
                    year=2026,
                    month=month,
                    amount=amount.quantize(Decimal('0.01')),
                    created_by_id=admin.id,
                    updated_by_id=admin.id
                )
                db.add(budget)
                budget_count += 1
    
    await db.commit()
    print(f"✓ 生成了 {budget_count} 条预算记录")
    return budget_count


async def generate_expense_records(db: AsyncSession, stores, expense_types):
    """生成实际费用记录（用于差异分析测试）"""
    print("\n生成实际费用记录...")
    
    expense_count = 0
    
    for store in stores:
        print(f"  生成门店 [{store.name}] 的费用记录...")
        
        # 为前3个月生成费用记录
        for month in range(1, 4):
            # 每个月生成10-20笔费用
            num_expenses = random.randint(10, 20)
            
            for _ in range(num_expenses):
                # 随机选择费用科目
                expense_type = random.choice(expense_types)
                
                # 生成日期（该月的随机一天）
                day = random.randint(1, 28)
                biz_date = date(2026, month, day)
                
                # 生成金额（基于科目类型）
                base_amount = {
                    "食材采购": 2000,
                    "房租": 20000,
                    "人工工资": 3000,
                    "水电费": 500,
                    "物料采购": 800,
                    "设备维修": 1200,
                    "营销推广": 1500,
                    "清洁卫生": 300,
                }.get(expense_type.name, 500)
                
                amount = Decimal(str(base_amount * (0.5 + random.random())))
                
                # 随机状态（大部分为已审批）
                status = random.choices(
                    ['pending', 'approved', 'paid', 'rejected'],
                    weights=[0.1, 0.5, 0.3, 0.1]
                )[0]
                
                expense = ExpenseRecord(
                    store_id=store.id,
                    expense_type_id=expense_type.id,
                    biz_date=biz_date,
                    amount=amount.quantize(Decimal('0.01')),
                    description=f"{expense_type.name} - {month}月",
                    status=status,
                    is_deleted=False
                )
                db.add(expense)
                expense_count += 1
    
    await db.commit()
    print(f"✓ 生成了 {expense_count} 条费用记录")
    return expense_count


async def generate_test_scenarios(db: AsyncSession, stores, expense_types, admin):
    """生成特定测试场景的数据"""
    print("\n生成特定测试场景...")
    
    if not stores or not expense_types:
        print("⚠ 跳过场景数据生成")
        return
    
    store = stores[0]  # 使用第一个门店
    food_type = next((et for et in expense_types if "食材" in et.name), expense_types[0])
    rent_type = next((et for et in expense_types if "房租" in et.name), expense_types[1] if len(expense_types) > 1 else expense_types[0])
    
    # 场景1：明显超支的情况（2月）
    print("  场景1: 超支预警测试...")
    budget1 = Budget(
        store_id=store.id,
        expense_type_id=food_type.id,
        year=2026,
        month=2,
        amount=Decimal('30000.00'),
        created_by_id=admin.id,
        updated_by_id=admin.id
    )
    db.add(budget1)
    
    # 生成超支的费用
    for i, amount in enumerate([15000, 12000, 8000], 1):
        expense = ExpenseRecord(
            store_id=store.id,
            expense_type_id=food_type.id,
            biz_date=date(2026, 2, i * 7),
            amount=Decimal(str(amount)),
            description=f"食材采购 - 第{i}次（测试超支）",
            status='approved',
            is_deleted=False
        )
        db.add(expense)
    
    # 场景2：完全节约的情况（3月）
    print("  场景2: 节余测试...")
    budget2 = Budget(
        store_id=store.id,
        expense_type_id=food_type.id,
        year=2026,
        month=3,
        amount=Decimal('50000.00'),
        created_by_id=admin.id,
        updated_by_id=admin.id
    )
    db.add(budget2)
    
    expense = ExpenseRecord(
        store_id=store.id,
        expense_type_id=food_type.id,
        biz_date=date(2026, 3, 15),
        amount=Decimal('35000.00'),
        description="食材采购 - 节约（测试节余）",
        status='approved',
        is_deleted=False
    )
    db.add(expense)
    
    # 场景3：无预算有费用（4月）
    print("  场景3: 无预算测试...")
    expense = ExpenseRecord(
        store_id=store.id,
        expense_type_id=food_type.id,
        biz_date=date(2026, 4, 10),
        amount=Decimal('25000.00'),
        description="食材采购 - 无预算（测试无预算）",
        status='approved',
        is_deleted=False
    )
    db.add(expense)
    
    # 场景4：有预算无费用（5月）
    print("  场景4: 有预算无费用测试...")
    budget3 = Budget(
        store_id=store.id,
        expense_type_id=rent_type.id,
        year=2026,
        month=5,
        amount=Decimal('20000.00'),
        created_by_id=admin.id,
        updated_by_id=admin.id
    )
    db.add(budget3)
    # 不添加费用记录
    
    await db.commit()
    print("✓ 场景数据生成完成")


async def print_summary(db: AsyncSession):
    """打印数据摘要"""
    print("\n" + "="*60)
    print("数据生成摘要")
    print("="*60)
    
    # 统计预算数据
    result = await db.execute(select(Budget).where(Budget.year == 2026))
    budget_count = len(result.scalars().all())
    
    # 统计费用数据
    result = await db.execute(
        select(ExpenseRecord).where(
            ExpenseRecord.biz_date >= date(2026, 1, 1),
            ExpenseRecord.biz_date < date(2027, 1, 1)
        )
    )
    expense_count = len(result.scalars().all())
    
    print(f"\n预算记录总数: {budget_count}")
    print(f"费用记录总数: {expense_count}")
    
    # 按月统计
    print("\n按月统计:")
    for month in range(1, 13):
        result = await db.execute(
            select(Budget).where(Budget.year == 2026, Budget.month == month)
        )
        month_budgets = len(result.scalars().all())
        
        result = await db.execute(
            select(ExpenseRecord).where(
                ExpenseRecord.biz_date >= date(2026, month, 1),
                ExpenseRecord.biz_date < date(2026, month + 1 if month < 12 else 12, 31 if month == 12 else 1)
            )
        )
        month_expenses = len(result.scalars().all())
        
        if month_budgets > 0 or month_expenses > 0:
            print(f"  {month}月: {month_budgets} 条预算, {month_expenses} 条费用")
    
    print("\n特殊测试场景:")
    print("  ✓ 2月: 超支场景（预算30,000，实际35,000）")
    print("  ✓ 3月: 节余场景（预算50,000，实际35,000）")
    print("  ✓ 4月: 无预算场景（无预算，有费用25,000）")
    print("  ✓ 5月: 无费用场景（预算20,000，无费用）")
    
    print("\n" + "="*60)
    print("数据生成完成！")
    print("="*60)
    
    print("\n下一步:")
    print("  1. 运行测试: pytest tests/test_budget.py -v")
    print("  2. 手动测试: 访问前端预算管理模块")
    print("  3. API测试: 查看 docs/budget_testing_guide.md")


async def main():
    """主函数"""
    print("="*60)
    print("预算测试数据生成工具")
    print("="*60)
    
    try:
        async for db in get_async_session():
            # 1. 检查基础数据
            stores, expense_types, admin = await get_or_create_data(db)
            if not stores or not expense_types or not admin:
                return
            
            # 2. 清理现有数据
            await clear_existing_budget_data(db)
            
            # 3. 生成预算数据
            await generate_budgets(db, stores, expense_types, admin)
            
            # 4. 生成费用记录
            await generate_expense_records(db, stores, expense_types)
            
            # 5. 生成特定测试场景
            await generate_test_scenarios(db, stores, expense_types, admin)
            
            # 6. 打印摘要
            await print_summary(db)
            
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
