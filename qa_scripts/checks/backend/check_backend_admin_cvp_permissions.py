"""检查 admin 用户的 CVP/预算权限是否就绪。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User


async def main() -> None:
    async for db in get_db():
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload("permissions"))
            .where(User.username == "admin")
        )
        user = result.scalar_one_or_none()

        if user is None:
            print("❌ 未找到 admin 用户")
            return

        permissions: set[str] = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(f"{permission.resource}:{permission.action}")

        print("admin 用户权限列表：")
        for item in sorted(permissions):
            print(f"  - {item}")

        print(f"\n包含 decision:cvp 权限: {'✅' if 'decision:cvp' in permissions else '❌'}")
        print(f"包含 budget:view 权限: {'✅' if 'budget:view' in permissions else '❌'}")
        print(f"包含 budget:manage 权限: {'✅' if 'budget:manage' in permissions else '❌'}")
        return


if __name__ == "__main__":
    asyncio.run(main())
