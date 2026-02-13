"""导入功能端到端验证（服务层）。"""

import asyncio
import sys
from io import BytesIO
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, OperationalError

from app.core.database import AsyncSessionLocal
from app.models.store import Store
from app.models.user import User
from app.models.import_job import ImportTargetType
from app.services.import_service import ImportService


class MockUploadFile:
    def __init__(self, filename: str, content: BytesIO):
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content.getvalue()

    async def seek(self, position: int) -> None:
        self._content.seek(position)


async def ensure_test_context(session):
    user = (await session.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
    if user is None:
        print("❌ 找不到 admin 用户，请先运行 seed_data.py")
        return None, None

    store = (await session.execute(select(Store).where(Store.code == "TEST001"))).scalar_one_or_none()
    if store is None:
        store = Store(
            code="TEST001",
            name="测试门店",
            address="测试地址",
            contact_person="测试联系人",
            phone="13800138000",
            is_active=True,
        )
        session.add(store)
        await session.commit()
        await session.refresh(store)
    return user, store


async def main() -> int:
    print("=" * 60)
    print("数据导入功能端到端验证")
    print("=" * 60)

    max_retries = 3
    delay_seconds = 1.5

    for attempt in range(1, max_retries + 1):
        try:
            async with AsyncSessionLocal() as session:
                user, store = await ensure_test_context(session)
                if user is None or store is None:
                    return 1

                csv_content = f"""order_no,biz_date,gross_amount,net_amount
TEST{user.id}001,2024-01-01,1000.50,950.50
TEST{user.id}002,2024-01-02,2000.00,2000.00
TEST{user.id}001,2024-01-03,1500.00,1400.00
TEST{user.id}003,2024-01-03,500.00,500.00
"""

                upload_file = MockUploadFile("test_orders.csv", BytesIO(csv_content.encode("utf-8")))

                job = await ImportService.create_job(
                    db=session,
                    user=user,
                    upload_file=upload_file,
                    target_type=ImportTargetType.ORDERS,
                    job_name="E2E 导入验证任务",
                    store_id=store.id,
                )
                job = await ImportService.run_job(session, job.id, user)

                ok = True
                if job.status.value != "partial_fail":
                    print(f"❌ 状态异常，预期 partial_fail，实际 {job.status.value}")
                    ok = False
                if not (job.total_rows == 4 and job.success_rows == 3 and job.fail_rows == 1):
                    print(f"❌ 行数统计异常: total={job.total_rows}, success={job.success_rows}, fail={job.fail_rows}")
                    ok = False
                if not job.error_report_path or not Path(job.error_report_path).exists():
                    print("❌ 错误报告未生成")
                    ok = False

                if ok:
                    print("✅ 导入 E2E 验证通过")
                    return 0

                return 1
        except (ConnectionResetError, OSError, DBAPIError, OperationalError, Exception) as exc:
            if attempt == max_retries:
                print(f"\n❌ 执行失败（已重试 {max_retries} 次）：{exc}")
                raise

            print(f"\n⚠️ 数据库连接中断（第 {attempt}/{max_retries} 次）：{exc}")
            print(f"   {delay_seconds:.1f}s 后自动重试...")
            await asyncio.sleep(delay_seconds)
            delay_seconds *= 2

    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
