"""检查OrderHeader字段和channel值"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = PROJECT_ROOT / "services" / "api"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, func, distinct
from app.core.database import AsyncSessionLocal
from app.models.order import OrderHeader

async def check_order_schema():
    async with AsyncSessionLocal() as db:
        # 检查不同的channel值
        result = await db.execute(
            select(distinct(OrderHeader.channel), func.count(OrderHeader.id))
            .group_by(OrderHeader.channel)
            .limit(10)
        )
        channels = result.all()
        
        print("📊 订单渠道统计:")
        for ch, count in channels:
            print(f"   {ch}: {count} 条订单")
        print()
        
        # 检查不同的status值
        result2 = await db.execute(
            select(distinct(OrderHeader.status), func.count(OrderHeader.id))
            .group_by(OrderHeader.status)
            .limit(10)
        )
        statuses = result2.all()
        
        print("📊 订单状态统计:")
        for st, count in statuses:
            print(f"   {st}: {count} 条订单")
        print()
        
        # 检查一条样例订单的金额字段
        sample = await db.execute(select(OrderHeader).limit(1))
        order = sample.scalar_one_or_none()
        
        if order:
            print("📋 样例订单金额字段:")
            print(f"   gross_amount: {order.gross_amount}")
            print(f"   discount_amount: {order.discount_amount}")
            print(f"   service_charge: {order.service_charge}")
            print(f"   delivery_fee: {order.delivery_fee}")
            print(f"   net_amount: {order.net_amount}")

if __name__ == "__main__":
    asyncio.run(check_order_schema())
