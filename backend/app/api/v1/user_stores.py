"""
用户门店权限管理 API
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.api.deps import get_current_user, check_permission
from app.models.user import User
from app.models.user_store import UserStorePermission
from app.models.store import Store
from app.schemas.common import Response, success
from app.schemas.user_store import UserStoreAssignRequest
from app.services.audit import create_audit_log

router = APIRouter()


@router.get(
    "",
    response_model=Response[Dict[str, Any]],
    summary="查询用户的门店权限",
    description="查询指定用户被分配的门店权限"
)
async def get_user_stores(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查询用户的门店权限"""
    # 权限检查：需要 user:assign-store 权限
    await check_permission(current_user, "user:assign-store", db)
    
    # 验证用户存在
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询用户的门店权限
    query = select(
        UserStorePermission.store_id,
        Store.name.label('store_name'),
        UserStorePermission.created_at
    ).join(
        Store, UserStorePermission.store_id == Store.id, isouter=True
    ).where(
        UserStorePermission.user_id == user_id
    ).order_by(
        UserStorePermission.created_at.desc()
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    stores = [{
        "store_id": row.store_id,
        "store_name": row.store_name or '未知门店',
        "assigned_at": row.created_at.isoformat() if row.created_at else ''
    } for row in rows]
    
    return success(
        data={
            "user_id": user_id,
            "username": user.username,
            "stores": stores,
            "total": len(stores)
        }
    )


@router.post(
    "/assign",
    response_model=Response[dict],
    summary="分配门店权限",
    description="为用户分配门店权限（覆盖式更新）"
)
async def assign_user_stores(
    data: UserStoreAssignRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    分配门店权限
    
    采用覆盖式更新：先删除该用户的所有门店权限，再添加新的权限。
    """
    # 权限检查：需要 user:assign-store 权限
    await check_permission(current_user, "user:assign-store", db)
    
    # 验证用户存在
    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证所有门店存在
    if data.store_ids:
        store_result = await db.execute(
            select(Store.id).where(Store.id.in_(data.store_ids))
        )
        existing_store_ids = {row[0] for row in store_result.all()}
        
        invalid_store_ids = set(data.store_ids) - existing_store_ids
        if invalid_store_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"门店不存在: {list(invalid_store_ids)}"
            )
    
    # 删除用户的所有门店权限
    await db.execute(
        delete(UserStorePermission).where(UserStorePermission.user_id == data.user_id)
    )
    
    # 添加新的门店权限
    for store_id in data.store_ids:
        permission = UserStorePermission(
            user_id=data.user_id,
            store_id=store_id
        )
        db.add(permission)
    
    await db.commit()
    
    # 记录审计日志
    await create_audit_log(
        db=db,
        user=current_user,
        action="ASSIGN_STORE",
        resource="user",
        resource_id=str(data.user_id),
        detail={
            "user_id": data.user_id,
            "username": user.username,
            "store_ids": data.store_ids,
            "store_count": len(data.store_ids)
        },
        request=request,
        status_code=200
    )
    await db.commit()
    
    return success(
        data={
            "user_id": data.user_id,
            "username": user.username,
            "assigned_stores": data.store_ids,
            "total_stores": len(data.store_ids)
        }
    )


@router.delete(
    "",
    response_model=Response[dict],
    summary="删除用户的所有门店权限",
    description="删除指定用户的所有门店权限"
)
async def delete_user_stores(
    request: Request,
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除用户的所有门店权限"""
    # 权限检查：需要 user:assign-store 权限
    await check_permission(current_user, "user:assign-store", db)
    
    # 验证用户存在
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户的所有门店权限
    result = await db.execute(
        delete(UserStorePermission).where(UserStorePermission.user_id == user_id)
    )
    deleted_count = result.rowcount
    
    await db.commit()
    
    # 记录审计日志
    await create_audit_log(
        db=db,
        user=current_user,
        action="CLEAR_STORE",
        resource="user",
        resource_id=str(user_id),
        detail={
            "user_id": user_id,
            "username": user.username,
            "deleted_count": deleted_count
        },
        request=request,
        status_code=200
    )
    await db.commit()
    
    return success(
        data={
            "user_id": user_id,
            "username": user.username,
            "deleted_count": deleted_count
        }
    )
