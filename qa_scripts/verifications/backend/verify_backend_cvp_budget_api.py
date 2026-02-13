"""验证 CVP 与预算管理核心服务调用链。"""

import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.expense import ExpenseType
from app.models.store import Store
from app.models.user import User
from app.schemas.budget import BudgetItemCreate
from app.services import budget_service, cvp_service


async def verify_budget_service() -> bool:
    print("\n" + "=" * 60)
    print("验证预算管理服务")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        store = (await db.execute(select(Store).limit(1))).scalar_one_or_none()
        if store is None:
            print("✗ 未找到门店数据，请先运行 seed_data.py")
            return False

        expense_types = (await db.execute(select(ExpenseType).limit(3))).scalars().all()
        if not expense_types:
            print("✗ 未找到费用类型数据")
            return False

        user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if user is None:
            print("✗ 未找到用户数据")
            return False

        items = [BudgetItemCreate(expense_type_id=item.id, amount=Decimal("10000.00")) for item in expense_types]

        try:
            await budget_service.batch_save_budgets(
                db=db,
                store_id=store.id,
                year=date.today().year,
                month=date.today().month,
                items=items,
                user=user,
            )
            analysis = await budget_service.get_budget_analysis(
                db=db,
                store_id=store.id,
                year=date.today().year,
                month=date.today().month,
            )
            print(f"✓ 预算分析记录数: {len(analysis.items)}")
            return True
        except Exception as error:
            print(f"✗ 预算服务验证失败: {error}")
            return False


async def verify_cvp_service() -> bool:
    print("\n" + "=" * 60)
    print("验证 CVP 服务")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        store = (await db.execute(select(Store).limit(1))).scalar_one_or_none()
        if store is None:
            print("✗ 未找到门店数据")
            return False

        expense_types = (await db.execute(select(ExpenseType).limit(2))).scalars().all()
        if len(expense_types) < 2:
            print("✗ 费用类型不足，至少需要2条")
            return False

        try:
            await cvp_service.update_cost_behavior(db=db, expense_type_id=expense_types[0].id, cost_behavior="fixed")
            await cvp_service.update_cost_behavior(db=db, expense_type_id=expense_types[1].id, cost_behavior="variable")

            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            result = await cvp_service.calculate_cvp(
                db=db,
                store_id=store.id,
                start_date=start_date,
                end_date=end_date,
            )
            print(f"✓ CVP 收入: {result.total_revenue}")
            print(f"✓ CVP 盈亏平衡点: {result.break_even_point}")
            return True
        except Exception as error:
            print(f"✗ CVP 服务验证失败: {error}")
            return False


async def main() -> int:
    budget_ok = await verify_budget_service()
    cvp_ok = await verify_cvp_service()

    print("\n" + "=" * 60)
    print("验证汇总")
    print("=" * 60)
    print(f"预算服务: {'✓ 通过' if budget_ok else '✗ 失败'}")
    print(f"CVP 服务: {'✓ 通过' if cvp_ok else '✗ 失败'}")

    return 0 if budget_ok and cvp_ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
