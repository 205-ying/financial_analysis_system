"""
角色管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response, PaginatedResponse
from app.schemas.role import (
    RoleSchema,
    RoleCreate,
    RoleUpdate,
    RoleListItem,
    AssignPermissionsRequest
)
from app.services.role_service import RoleService
from app.services.audit_log_service import log_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[List[RoleListItem]])
async def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色列表
    """
    await check_permission(current_user, "role:view", db)

    skip = (page - 1) * page_size
    roles, total = await RoleService.get_list(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        is_active=is_active
    )

    # 获取每个角色的统计信息
    result_items = []
    for role in roles:
        stats = await RoleService.get_role_stats(db, role.id)
        result_items.append({
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "permission_count": stats["permission_count"],
            "user_count": stats["user_count"],
            "created_at": role.created_at,
            "updated_at": role.updated_at
        })

    return PaginatedResponse(
        code=200,
        message="查询成功",
        data=result_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{role_id}", response_model=Response[RoleSchema])
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色详情
    """
    await check_permission(current_user, "role:view", db)

    role = await RoleService.get_by_id(db, role_id)

    return Response(
        code=200,
        message="查询成功",
        data=role
    )


@router.post("", response_model=Response[RoleSchema])
async def create_role(
    request: Request,
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建角色
    """
    await check_permission(current_user, "role:create", db)

    role = await RoleService.create(db, data)

    # 记录审计日志
    await log_audit(
        db=db,
        user=current_user,
        action="create_role",
        request=request,
        resource_type="role",
        resource_id=role.id,
        detail={
            "role_code": role.code,
            "role_name": role.name,
            "permission_count": len(data.permission_ids)
        }
    )

    return Response(
        code=200,
        message="创建成功",
        data=role
    )


@router.put("/{role_id}", response_model=Response[RoleSchema])
async def update_role(
    request: Request,
    role_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新角色
    """
    await check_permission(current_user, "role:edit", db)

    role = await RoleService.update(db, role_id, data)

    # 记录审计日志
    await log_audit(
        db=db,
        user=current_user,
        action="update_role",
        request=request,
        resource_type="role",
        resource_id=role.id,
        detail={
            "role_code": role.code,
            "role_name": role.name,
            "updates": data.model_dump(exclude_unset=True)
        }
    )

    return Response(
        code=200,
        message="更新成功",
        data=role
    )


@router.delete("/{role_id}", response_model=Response[None])
async def delete_role(
    request: Request,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除角色
    """
    await check_permission(current_user, "role:delete", db)

    # 先获取角色信息用于审计
    role = await RoleService.get_by_id(db, role_id)
    role_info = {"code": role.code, "name": role.name}

    await RoleService.delete(db, role_id)

    # 记录审计日志
    await log_audit(
        db=db,
        user=current_user,
        action="delete_role",
        request=request,
        resource_type="role",
        resource_id=role_id,
        detail=role_info
    )

    return Response(
        code=200,
        message="删除成功",
        data=None
    )


@router.post("/{role_id}/permissions", response_model=Response[RoleSchema])
async def assign_permissions(
    request: Request,
    role_id: int,
    data: AssignPermissionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为角色分配权限
    """
    await check_permission(current_user, "role:assign-permission", db)

    role = await RoleService.assign_permissions(db, role_id, data.permission_ids)

    # 记录审计日志
    await log_audit(
        db=db,
        user=current_user,
        action="assign_role_permissions",
        request=request,
        resource_type="role",
        resource_id=role_id,
        detail={
            "role_code": role.code,
            "role_name": role.name,
            "permission_count": len(data.permission_ids),
            "permission_ids": data.permission_ids
        }
    )

    return Response(
        code=200,
        message="分配权限成功",
        data=role
    )
