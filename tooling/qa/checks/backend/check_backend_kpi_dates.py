"""检查KPI数据的日期范围"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = PROJECT_ROOT / "services" / "api"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.kpi import KpiDailyStore

async def check_kpi_dates():
    async with AsyncSessionLocal() as db:
        # 获取KPI日期范围
        result = await db.execute(
            select(
                func.min(KpiDailyStore.biz_date).label('earliest'),
                func.max(KpiDailyStore.biz_date).label('latest'),
                func.count(KpiDailyStore.id).label('total')
            )
        )
        row = result.one()
        
        print(f"📅 KPI数据日期范围:")
        print(f"   最早日期: {row.earliest}")
        print(f"   最晚日期: {row.latest}")
        print(f"   总记录数: {row.total}")
        print()
        
        # 检查2026年2月的数据
        from datetime import date
        feb_start = date(2026, 2, 1)
        feb_end = date(2026, 2, 10)
        
        feb_count = await db.execute(
            select(func.count(KpiDailyStore.id))
            .where(KpiDailyStore.biz_date >= feb_start)
            .where(KpiDailyStore.biz_date <= feb_end)
        )
        feb_num = feb_count.scalar()
        
        print(f"🔍 2026年2月1-10日 KPI数据:")
        print(f"   记录数: {feb_num}")
        print()
        
        if feb_num == 0:
            print("⚠️  当前月份(2026-02)无KPI数据!")
            print("   解决方案:")
            print("   1. 访问 http://localhost:5174/dashboard")
            print("   2. 确保日期选择'本月'")
            print("   3. 点击'重建KPI'按钮")
            print("   4. 确认后等待完成")
        else:
            print("✅ 当前月份有数据，请:")
            print("   1. 访问 http://localhost:5174/dashboard (注意是5174端口)")
            print("   2. 按 Ctrl+Shift+R 强制刷新")
            print("   3. 点击'查询'按钮")

if __name__ == "__main__":
    asyncio.run(check_kpi_dates())
