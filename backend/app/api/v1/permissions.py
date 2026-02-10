"""
权限管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response, PaginatedResponse
from app.schemas.permission import PermissionSchema, PermissionListItem
from app.services.permission_service import PermissionService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[List[PermissionListItem]])
async def get_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=1000, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    resource: Optional[str] = Query(None, description="资源类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取权限列表
    """
    await check_permission(current_user, "permission:view", db)

    skip = (page - 1) * page_size
    permissions, total = await PermissionService.get_list(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        resource=resource
    )

    # 获取每个权限的统计信息
    result_items = []
    for perm in permissions:
        stats = await PermissionService.get_permission_stats(db, perm.id)
        result_items.append({
            "id": perm.id,
            "code": perm.code,
            "name": perm.name,
            "resource": perm.resource,
            "action": perm.action,
            "description": perm.description,
            "role_count": stats["role_count"],
            "created_at": perm.created_at
        })

    return PaginatedResponse(
        code=200,
        message="查询成功",
        data=result_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/all", response_model=Response[List[PermissionSchema]])
async def get_all_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有权限（不分页，用于下拉选择）
    """
    await check_permission(current_user, "permission:view", db)

    permissions = await PermissionService.get_all(db)

    return Response(
        code=200,
        message="查询成功",
        data=permissions
    )


@router.get("/resources", response_model=Response[List[str]])
async def get_resources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有资源类型
    """
    await check_permission(current_user, "permission:view", db)

    resources = await PermissionService.get_resources(db)

    return Response(
        code=200,
        message="查询成功",
        data=resources
    )


@router.get("/{permission_id}", response_model=Response[PermissionSchema])
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取权限详情
    """
    await check_permission(current_user, "permission:view", db)

    permission = await PermissionService.get_by_id(db, permission_id)

    return Response(
        code=200,
        message="查询成功",
        data=permission
    )
