"""
角色管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.core.exceptions import AuthorizationException, ValidationException
from app.models.user import User
from app.schemas.common import Response, PaginatedResponse
from app.schemas.role import (
    RoleSchema,
    RoleCreate,
    RoleUpdate,
    RoleListItem,
    AssignPermissionsRequest,
    UserRoleListItem,
    UserWithRoles,
    AssignUserRolesRequest,
    UserCreateRequest,
    UserUpdateRequest,
    UpdateUserStatusRequest,
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


@router.get("/users", response_model=PaginatedResponse[List[UserRoleListItem]])
async def get_users_with_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名/姓名/手机号）"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户列表（含角色）"""
    try:
        await check_permission(current_user, "role:view", db)
    except AuthorizationException:
        await check_permission(current_user, "user:view", db)

    skip = (page - 1) * page_size
    users, total = await RoleService.get_user_list(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        is_active=is_active,
    )

    items = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "phone": user.phone,
            "email": user.email,
            "is_active": user.is_active,
            "roles": [
                {"id": role.id, "code": role.code, "name": role.name}
                for role in user.roles
            ],
            "updated_at": user.updated_at,
        }
        for user in users
    ]

    return PaginatedResponse(
        code=200,
        message="查询成功",
        data=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/users/{user_id}/roles", response_model=Response[UserWithRoles])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户角色详情"""
    try:
        await check_permission(current_user, "role:view", db)
    except AuthorizationException:
        await check_permission(current_user, "user:view", db)

    user = await RoleService.get_user_with_roles(db, user_id)
    data = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [{"id": role.id, "code": role.code, "name": role.name} for role in user.roles],
    }

    return Response(code=200, message="查询成功", data=data)


@router.put("/users/{user_id}/roles", response_model=Response[UserWithRoles])
async def assign_user_roles(
    request: Request,
    user_id: int,
    data: AssignUserRolesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分配用户角色（覆盖式保存）"""
    await check_permission(current_user, "role:assign-permission", db)

    before_user = await RoleService.get_user_with_roles(db, user_id)
    before_roles = [
        {"id": role.id, "code": role.code, "name": role.name}
        for role in before_user.roles
    ]

    updated_user = await RoleService.assign_roles_to_user(db, user_id, data.role_ids)
    after_roles = [
        {"id": role.id, "code": role.code, "name": role.name}
        for role in updated_user.roles
    ]

    await log_audit(
        db=db,
        user=current_user,
        request=request,
        action="assign_user_roles",
        resource_type="user",
        resource_id=updated_user.id,
        detail={
            "target_user": updated_user.username,
            "before_roles": before_roles,
            "after_roles": after_roles,
        },
    )

    result = {
        "id": updated_user.id,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "email": updated_user.email,
        "is_active": updated_user.is_active,
        "roles": after_roles,
    }

    return Response(code=200, message="角色分配成功", data=result)


@router.post("/users", response_model=Response[UserWithRoles])
async def create_user(
    request: Request,
    data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建用户"""
    try:
        await check_permission(current_user, "role:edit", db)
    except AuthorizationException:
        await check_permission(current_user, "user:create", db)

    created_user = await RoleService.create_user(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        phone=data.phone,
        is_active=data.is_active,
    )

    await log_audit(
        db=db,
        user=current_user,
        request=request,
        action="create_user",
        resource_type="user",
        resource_id=created_user.id,
        detail={
            "username": created_user.username,
            "email": created_user.email,
            "is_active": created_user.is_active,
        },
    )

    result = {
        "id": created_user.id,
        "username": created_user.username,
        "full_name": created_user.full_name,
        "phone": created_user.phone,
        "email": created_user.email,
        "is_active": created_user.is_active,
        "roles": [
            {"id": role.id, "code": role.code, "name": role.name}
            for role in created_user.roles
        ],
    }

    return Response(code=200, message="用户创建成功", data=result)


@router.put("/users/{user_id}", response_model=Response[UserWithRoles])
async def update_user(
    request: Request,
    user_id: int,
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户基础信息"""
    try:
        await check_permission(current_user, "role:edit", db)
    except AuthorizationException:
        await check_permission(current_user, "user:edit", db)

    before_user = await RoleService.get_user_with_roles(db, user_id)
    before_data = {
        "full_name": before_user.full_name,
        "phone": before_user.phone,
        "email": before_user.email,
    }

    updated_user = await RoleService.update_user_basic_info(
        db=db,
        user_id=user_id,
        email=data.email,
        full_name=data.full_name,
        phone=data.phone,
    )

    after_data = {
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "email": updated_user.email,
    }

    await log_audit(
        db=db,
        user=current_user,
        request=request,
        action="update_user",
        resource_type="user",
        resource_id=updated_user.id,
        detail={
            "username": updated_user.username,
            "before": before_data,
            "after": after_data,
        },
    )

    result = {
        "id": updated_user.id,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "email": updated_user.email,
        "is_active": updated_user.is_active,
        "roles": [
            {"id": role.id, "code": role.code, "name": role.name}
            for role in updated_user.roles
        ],
    }

    return Response(code=200, message="用户更新成功", data=result)


@router.put("/users/{user_id}/status", response_model=Response[UserWithRoles])
async def update_user_status(
    request: Request,
    user_id: int,
    data: UpdateUserStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户启用状态"""
    try:
        await check_permission(current_user, "role:edit", db)
    except AuthorizationException:
        await check_permission(current_user, "user:edit", db)

    if current_user.id == user_id and not data.is_active:
        raise ValidationException("不能禁用当前登录用户")

    before_user = await RoleService.get_user_with_roles(db, user_id)
    before_status = before_user.is_active

    updated_user = await RoleService.update_user_status(
        db=db,
        user_id=user_id,
        is_active=data.is_active,
    )

    await log_audit(
        db=db,
        user=current_user,
        request=request,
        action="update_user_status",
        resource_type="user",
        resource_id=updated_user.id,
        detail={
            "username": updated_user.username,
            "before": before_status,
            "after": updated_user.is_active,
        },
    )

    result = {
        "id": updated_user.id,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "email": updated_user.email,
        "is_active": updated_user.is_active,
        "roles": [
            {"id": role.id, "code": role.code, "name": role.name}
            for role in updated_user.roles
        ],
    }

    return Response(code=200, message="用户状态更新成功", data=result)


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
