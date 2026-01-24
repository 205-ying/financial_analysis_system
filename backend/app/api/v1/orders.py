"""
订单管理 API
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.order import OrderHeader
from app.models.store import Store
from app.schemas.common import Response, success

router = APIRouter()


@router.get(
    "",
    response_model=Response[Dict[str, Any]],
    summary="获取订单列表",
    description="获取订单列表"
)
async def list_orders(
    store_id: int = Query(None, description="门店ID"),
    channel: str = Query(None, description="渠道"),
    order_no: str = Query(None, description="订单号"),
    start_date: date = Query(None, description="开始日期"),
    end_date: date = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表"""
    # 构建查询
    query = select(OrderHeader, Store.name.label('store_name')).join(
        Store, OrderHeader.store_id == Store.id, isouter=True
    )
    
    # 应用筛选条件
    conditions = []
    if store_id:
        conditions.append(OrderHeader.store_id == store_id)
    if channel:
        conditions.append(OrderHeader.channel == channel)
    if order_no:
        conditions.append(OrderHeader.order_no.ilike(f'%{order_no}%'))
    if start_date:
        conditions.append(func.date(OrderHeader.order_time) >= start_date)
    if end_date:
        conditions.append(func.date(OrderHeader.order_time) <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # 获取总数
    count_query = select(func.count()).select_from(OrderHeader)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 应用分页
    offset = (page - 1) * page_size
    query = query.order_by(OrderHeader.order_time.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    items = [{
        "id": row.OrderHeader.id,
        "order_no": row.OrderHeader.order_no,
        "store_id": row.OrderHeader.store_id,
        "store_name": row.store_name or '未知门店',
        "channel": row.OrderHeader.channel or '未知',
        "amount": float(row.OrderHeader.net_amount or 0),
        "order_time": row.OrderHeader.order_time.isoformat() if row.OrderHeader.order_time else '',
        "remark": row.OrderHeader.remark or '',
        "status": row.OrderHeader.status or 'completed'
    } for row in rows]
    
    return success(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get(
    "/{order_id}",
    response_model=Response[dict],
    summary="获取订单详情",
    description="获取订单详情"
)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    result = await db.execute(select(OrderHeader).where(OrderHeader.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return success(
        data={
            "id": order.id,
            "order_no": order.order_no,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.isoformat()
        }
    )