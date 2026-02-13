"""
费用记录业务服务
"""

from datetime import date
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ExpenseRecord, ExpenseType
from app.models.store import Store
from app.models.user import User
from app.services.data_scope_service import filter_stores_by_access


def _build_expense_conditions(
    accessible_store_ids: list[int] | None,
    expense_type_id: int | None,
    start_date: date | None,
    end_date: date | None,
) -> list[Any]:
    conditions = []
    if accessible_store_ids is not None:
        conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))
    if expense_type_id:
        conditions.append(ExpenseRecord.expense_type_id == expense_type_id)
    if start_date:
        conditions.append(ExpenseRecord.biz_date >= start_date)
    if end_date:
        conditions.append(ExpenseRecord.biz_date <= end_date)
    return conditions


async def get_expense_record_list(
    db: AsyncSession,
    current_user: User,
    store_id: int | None,
    expense_type_id: int | None,
    start_date: date | None,
    end_date: date | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    """获取费用记录列表（含分页）"""
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    conditions = _build_expense_conditions(
        accessible_store_ids=accessible_store_ids,
        expense_type_id=expense_type_id,
        start_date=start_date,
        end_date=end_date,
    )

    query = (
        select(
            ExpenseRecord,
            Store.name.label("store_name"),
            ExpenseType.name.label("expense_type_name"),
        )
        .join(Store, ExpenseRecord.store_id == Store.id, isouter=True)
        .join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id, isouter=True)
    )

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(ExpenseRecord)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(ExpenseRecord.biz_date.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        {
            "id": row.ExpenseRecord.id,
            "store_id": row.ExpenseRecord.store_id,
            "store_name": row.store_name or "未知门店",
            "expense_type_id": row.ExpenseRecord.expense_type_id,
            "expense_type_name": row.expense_type_name or "未知类型",
            "expense_date": row.ExpenseRecord.biz_date.isoformat() if row.ExpenseRecord.biz_date else "",
            "amount": float(row.ExpenseRecord.amount or 0),
            "remark": row.ExpenseRecord.remark or "",
            "created_at": row.ExpenseRecord.created_at.isoformat() if row.ExpenseRecord.created_at else "",
        }
        for row in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_expense_record_export_rows(
    db: AsyncSession,
    current_user: User,
    store_id: int | None,
    expense_type_id: int | None,
    start_date: date | None,
    end_date: date | None,
) -> list[Any]:
    """获取费用记录导出数据（最多10000条）"""
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    conditions = _build_expense_conditions(
        accessible_store_ids=accessible_store_ids,
        expense_type_id=expense_type_id,
        start_date=start_date,
        end_date=end_date,
    )

    query = (
        select(
            ExpenseRecord,
            Store.name.label("store_name"),
            ExpenseType.name.label("expense_type_name"),
            ExpenseType.category.label("expense_type_category"),
        )
        .join(Store, ExpenseRecord.store_id == Store.id, isouter=True)
        .join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id, isouter=True)
    )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(ExpenseRecord.biz_date.desc()).limit(10000)
    result = await db.execute(query)
    return result.all()
