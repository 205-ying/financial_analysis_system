"""检查默认账户口令哈希验证结果。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select

from app.core.database import get_session
from app.core.security import verify_password
from app.models.user import User


async def main() -> None:
    print("=== 默认账户口令验证 ===\n")
    test_users = [
        {"username": "admin", "password": "Admin@123"},
        {"username": "manager", "password": "Manager@123"},
        {"username": "cashier", "password": "Cashier@123"},
    ]

    async for session in get_session():
        for item in test_users:
            username = item["username"]
            password = item["password"]
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

            if user is None:
                print(f"❌ {username}: 用户不存在")
                continue

            is_valid = verify_password(password, user.password_hash)
            print(f"{'✅' if is_valid else '❌'} {username}: {'口令匹配' if is_valid else '口令不匹配'}")
        break


if __name__ == "__main__":
    asyncio.run(main())
