"""重建历史 KPI 数据以修复渠道分布统计缺失。"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
BACKEND_DIR = project_root / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import AsyncSessionLocal
from app.services.kpi_calculator import KpiCalculator


async def main() -> None:
    print("🚀 开始修复 KPI 渠道分布数据...")
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    print(f"📅 重建范围: {start_date} 至 {end_date}")

    async with AsyncSessionLocal() as session:
        calculator = KpiCalculator(session)
        days, stores, records = await calculator.rebuild_daily_kpi(start_date, end_date)

    print("✅ 修复完成")
    print(f"   - 覆盖天数: {days}")
    print(f"   - 涉及门店: {stores}")
    print(f"   - 更新记录: {records}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

