"""
订单业务服务
"""

from datetime import date
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderHeader
from app.models.store import Store
from app.models.user import User
from app.services.data_scope_service import filter_stores_by_access


def _build_order_conditions(
    accessible_store_ids: list[int] | None,
    channel: str | None,
    order_no: str | None,
    start_date: date | None,
    end_date: date | None,
) -> list[Any]:
    conditions = []
    if accessible_store_ids is not None:
        conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
    if channel:
        conditions.append(OrderHeader.channel == channel)
    if order_no:
        conditions.append(OrderHeader.order_no.ilike(f"%{order_no}%"))
    if start_date:
        conditions.append(func.date(OrderHeader.order_time) >= start_date)
    if end_date:
        conditions.append(func.date(OrderHeader.order_time) <= end_date)
    return conditions


async def get_order_list(
    db: AsyncSession,
    current_user: User,
    store_id: int | None,
    channel: str | None,
    order_no: str | None,
    start_date: date | None,
    end_date: date | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    """获取订单列表（含分页）"""
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    conditions = _build_order_conditions(
        accessible_store_ids=accessible_store_ids,
        channel=channel,
        order_no=order_no,
        start_date=start_date,
        end_date=end_date,
    )

    query = select(OrderHeader, Store.name.label("store_name")).join(
        Store, OrderHeader.store_id == Store.id, isouter=True
    )

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(OrderHeader)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(OrderHeader.order_time.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    items = [
        {
            "id": row.OrderHeader.id,
            "order_no": row.OrderHeader.order_no,
            "store_id": row.OrderHeader.store_id,
            "store_name": row.store_name or "未知门店",
            "channel": row.OrderHeader.channel or "未知",
            "amount": float(row.OrderHeader.net_amount or 0),
            "order_time": row.OrderHeader.order_time.isoformat() if row.OrderHeader.order_time else "",
            "remark": row.OrderHeader.remark or "",
            "status": row.OrderHeader.status or "completed",
        }
        for row in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_order_export_rows(
    db: AsyncSession,
    current_user: User,
    store_id: int | None,
    channel: str | None,
    order_no: str | None,
    start_date: date | None,
    end_date: date | None,
) -> list[Any]:
    """获取订单导出数据（最多10000条）"""
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    conditions = _build_order_conditions(
        accessible_store_ids=accessible_store_ids,
        channel=channel,
        order_no=order_no,
        start_date=start_date,
        end_date=end_date,
    )

    query = select(OrderHeader, Store.name.label("store_name")).join(
        Store, OrderHeader.store_id == Store.id, isouter=True
    )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(OrderHeader.order_time.desc()).limit(10000)
    result = await db.execute(query)
    return result.all()
