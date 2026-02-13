"""检查导入相关数据库对象（表、枚举类型）。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError

from app.core.database import AsyncSessionLocal


async def run_once() -> None:
    async with AsyncSessionLocal() as session:
        table_result = await session.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public' AND tablename LIKE '%import%'
                ORDER BY tablename
                """
            )
        )
        tables = [row[0] for row in table_result.fetchall()]
        print(f"✅ 导入相关表: {tables if tables else '无'}")

        enum_result = await session.execute(
            text(
                """
                SELECT typname
                FROM pg_type
                WHERE typname LIKE 'import%'
                ORDER BY typname
                """
            )
        )
        enums = [row[0] for row in enum_result.fetchall()]
        print(f"✅ 导入相关枚举: {enums if enums else '无'}")


async def main() -> None:
    max_retries = 3
    delay_seconds = 1.5

    for attempt in range(1, max_retries + 1):
        try:
            await run_once()
            return
        except (ConnectionResetError, OSError, DBAPIError, OperationalError, Exception) as exc:
            if attempt == max_retries:
                print(f"\n❌ 执行失败（已重试 {max_retries} 次）：{exc}")
                raise

            print(f"\n⚠️ 数据库连接中断（第 {attempt}/{max_retries} 次）：{exc}")
            print(f"   {delay_seconds:.1f}s 后自动重试...")
            await asyncio.sleep(delay_seconds)
            delay_seconds *= 2


if __name__ == "__main__":
    asyncio.run(main())
