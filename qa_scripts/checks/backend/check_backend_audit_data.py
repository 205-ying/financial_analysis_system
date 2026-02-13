"""检查审计日志表数据规模与最近记录。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import func, select, text

from app.core.database import AsyncSessionLocal, engine
from app.models.audit_log import AuditLog


async def main() -> None:
    print("检查 audit_log 表数据...")

    async with engine.begin() as conn:
        count_result = await conn.execute(text("SELECT COUNT(*) FROM audit_log"))
        total_count = count_result.scalar() or 0
        print(f"\n总记录数: {total_count}")

        if total_count > 0:
            recent_result = await conn.execute(
                text(
                    """
                    SELECT id, username, action, resource_type, status, created_at
                    FROM audit_log
                    ORDER BY created_at DESC
                    LIMIT 10
                    """
                )
            )
            print("\n最近10条记录：")
            for row in recent_result.fetchall():
                print(
                    f"  ID:{row[0]} | 用户:{row[1]} | 操作:{row[2]} | "
                    f"资源:{row[3]} | 状态:{row[4]} | 时间:{row[5]}"
                )

    print("\n使用 ORM 查询计数...")
    async with AsyncSessionLocal() as session:
        orm_count = await session.scalar(select(func.count()).select_from(AuditLog))
        print(f"ORM 查询记录数: {orm_count}")


if __name__ == "__main__":
    asyncio.run(main())
