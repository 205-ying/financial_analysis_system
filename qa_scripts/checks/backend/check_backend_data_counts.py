"""快速检查数据库数据量"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.order import OrderHeader
from app.models.kpi import KpiDailyStore
from app.models.store import Store

async def check_data():
    async with AsyncSessionLocal() as db:
        # 检查订单数量
        order_count = await db.execute(select(func.count(OrderHeader.id)))
        order_num = order_count.scalar()
        
        # 检查KPI数量  
        kpi_count = await db.execute(select(func.count(KpiDailyStore.id)))
        kpi_num = kpi_count.scalar()
        
        # 检查门店数量
        store_count = await db.execute(select(func.count(Store.id)))
        store_num = store_count.scalar()
        
        print(f"📊 数据库数据统计:")
        print(f"   门店数量: {store_num}")
        print(f"   订单数量: {order_num}")
        print(f"   KPI记录数: {kpi_num}")
        print()
        
        if order_num == 0:
            print("⚠️  订单表为空！需要先生成测试数据:")
            print("   python qa_scripts/tools/backend/seed_data.py")
        elif kpi_num == 0:
            print("⚠️  KPI表为空！需要重建KPI:")
            print("   在看板页面点击'重建KPI'按钮")
        else:
            print("✅ 数据正常，如果看板显示0，请检查查询日期范围")

if __name__ == "__main__":
    asyncio.run(check_data())
