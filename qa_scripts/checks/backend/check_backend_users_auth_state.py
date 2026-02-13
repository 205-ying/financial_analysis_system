"""检查用户基础状态与默认口令匹配情况（只读）。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import verify_password
from app.models.user import User


DEFAULT_PASSWORD_CANDIDATES = ["Admin@123", "Manager@123", "Cashier@123", "Test@123"]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).order_by(User.id))
        users = result.scalars().all()

        if not users:
            print("❌ 数据库中没有用户")
            return

        print(f"📊 用户总数: {len(users)}")
        print("\n用户状态概览：")
        for user in users:
            matched = [
                password
                for password in DEFAULT_PASSWORD_CANDIDATES
                if verify_password(password, user.password_hash)
            ]
            matched_text = ", ".join(matched) if matched else "无默认口令匹配"
            print(
                f"- {user.username:<20} 激活={'是' if user.is_active else '否'} "
                f"超管={'是' if user.is_superuser else '否'} | {matched_text}"
            )


if __name__ == "__main__":
    asyncio.run(main())
