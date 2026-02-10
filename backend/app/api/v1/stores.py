"""
门店管理 API

提供门店的 CRUD 操作接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.store import Store
from app.schemas.common import Response, success, PageData
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreInDB,
    StoreListQuery
)

router = APIRouter()


@router.get(
    "/all",
    response_model=Response[List[StoreInDB]],
    summary="获取所有门店",
    description="获取所有激活的门店（不分页）"
)
async def get_all_stores(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有激活的门店"""
    result = await db.execute(
        select(Store).where(Store.is_active == True).order_by(Store.name)
    )
    stores = result.scalars().all()
    
    return success(
        data=[StoreInDB.model_validate(store) for store in stores]
    )


@router.get(
    "",
    response_model=Response[PageData[StoreInDB]],
    summary="获取门店列表",
    description="获取门店列表，支持分页和筛选"
)
async def list_stores(
    query_params: StoreListQuery = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取门店列表"""
    # 构建查询
    query = select(Store)
    
    # 应用筛选条件
    conditions = []
    if query_params.name:
        conditions.append(Store.name.ilike(f"%{query_params.name}%"))
    if query_params.city:
        conditions.append(Store.city == query_params.city)
    if query_params.is_active is not None:
        conditions.append(Store.is_active == query_params.is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # 应用排序
    if query_params.order_by:
        if query_params.order_by == "name":
            query = query.order_by(Store.name.desc() if query_params.desc else Store.name.asc())
        elif query_params.order_by == "created_at":
            query = query.order_by(Store.created_at.desc() if query_params.desc else Store.created_at.asc())
    else:
        query = query.order_by(Store.created_at.desc())
    
    # 获取总数
    from sqlalchemy import func
    count_query = select(func.count()).select_from(Store)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # 应用分页
    offset = (query_params.page - 1) * query_params.page_size
    query = query.offset(offset).limit(query_params.page_size)
    
    # 执行查询
    result = await db.execute(query)
    stores = result.scalars().all()
    
    # 转换为字典列表
    store_items = [StoreInDB.model_validate(store).model_dump() for store in stores]
    
    return success(
        data={
            "items": store_items,
            "total": total,
            "page": query_params.page,
            "page_size": query_params.page_size,
            "pages": (total + query_params.page_size - 1) // query_params.page_size
        }
    )


@router.post(
    "",
    response_model=Response[StoreInDB],
    status_code=status.HTTP_201_CREATED,
    summary="创建门店",
    description="创建新的门店"
)
async def create_store(
    store_data: StoreCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建门店"""
    # 检查名称是否已存在
    existing = await db.execute(
        select(Store).where(Store.name == store_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="门店名称已存在"
        )
    
    # 创建门店
    store = Store(**store_data.dict())
    db.add(store)
    await db.commit()
    await db.refresh(store)
    
    return success(
        data=StoreInDB.model_validate(store),
        message="门店创建成功"
    )


@router.get(
    "/{store_id}",
    response_model=Response[StoreInDB],
    summary="获取门店详情",
    description="根据ID获取门店详情"
)
async def get_store(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取门店详情"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="门店不存在"
        )
    
    return success(data=StoreInDB.model_validate(store))


@router.put(
    "/{store_id}",
    response_model=Response[StoreInDB],
    summary="更新门店",
    description="更新门店信息"
)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新门店"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="门店不存在"
        )
    
    # 如果更新名称，检查是否与其他门店重复
    if store_data.name and store_data.name != store.name:
        existing = await db.execute(
            select(Store).where(
                and_(Store.name == store_data.name, Store.id != store_id)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="门店名称已存在"
            )
    
    # 更新字段
    update_data = store_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    await db.commit()
    await db.refresh(store)
    
    return success(
        data=StoreInDB.model_validate(store),
        message="门店更新成功"
    )


@router.delete(
    "/{store_id}",
    response_model=Response[None],
    summary="删除门店",
    description="删除门店（软删除）"
)
async def delete_store(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除门店"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="门店不存在"
        )
    
    # 软删除
    store.is_active = False
    await db.commit()
    
    return success(message="门店删除成功")