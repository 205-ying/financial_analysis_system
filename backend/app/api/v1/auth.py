"""
认证相关接口
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User, Role
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.common import success
from app.services.audit import create_audit_log


router = APIRouter()


@router.post(
    "/login",
    response_model=dict,
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT 访问令牌"
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回:
    - **access_token**: JWT 访问令牌
    - **token_type**: 令牌类型（bearer）
    - **expires_in**: 令牌过期时间（秒）
    - **user_info**: 用户信息（包含角色和权限）
    """
    # DEBUG: 打印接收到的登录信息
    print(f"[DEBUG] 登录请求 - 用户名: {login_data.username}, 密码长度: {len(login_data.password)}")
    
    # 查询用户（预加载 roles 和 permissions）
    stmt = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(User.username == login_data.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # DEBUG: 打印查询结果
    print(f"[DEBUG] 数据库查询结果 - 用户存在: {user is not None}")
    if user:
        print(f"[DEBUG] 用户信息 - ID: {user.id}, 用户名: {user.username}, 激活状态: {user.is_active}")
        print(f"[DEBUG] 密码哈希: {user.password_hash[:50]}...")
        password_valid = verify_password(login_data.password, user.password_hash)
        print(f"[DEBUG] 密码验证结果: {password_valid}")
    
    # 验证用户存在性和密码
    if not user or not verify_password(login_data.password, user.password_hash):
        # 记录失败的登录尝试
        await create_audit_log(
            db=db,
            user=None,
            action="LOGIN_FAILED",
            resource="user",
            detail={"username": login_data.username},
            request=request,
            status_code=401,
            error_message="用户名或密码错误"
        )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        # 记录被禁用用户的登录尝试
        await create_audit_log(
            db=db,
            user=user,
            action="LOGIN_FAILED",
            resource="user",
            resource_id=str(user.id),
            detail={"reason": "用户已被禁用"},
            request=request,
            status_code=403,
            error_message="用户已被禁用"
        )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 生成 JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)},  # sub必须是字符串
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
    )
    
    # 构建用户信息
    roles = [role.code for role in user.roles]
    permissions = []
    
    # 超级用户拥有所有权限
    if user.is_superuser:
        permissions = ["*:*:*"]
    else:
        # 收集用户所有权限
        perm_set = set()
        for role in user.roles:
            for perm in role.permissions:
                perm_set.add(perm.code)
        permissions = sorted(perm_set)
    
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=roles,
        permissions=permissions
    )
    
    # 记录成功的登录
    await create_audit_log(
        db=db,
        user=user,
        action="LOGIN",
        resource="user",
        resource_id=str(user.id),
        detail={
            "roles": roles,
            "permissions_count": len(permissions)
        },
        request=request,
        status_code=200
    )
    await db.commit()
    
    # 构建响应
    token_response = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,  # 转换为秒
        user_info=user_info
    )
    
    return success(
        data=token_response.model_dump(),
        message="登录成功"
    )


@router.get(
    "/me",
    response_model=dict,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息，包含角色、权限和可访问门店"
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    获取当前用户信息
    
    返回:
    - **id**: 用户 ID
    - **username**: 用户名
    - **email**: 邮箱
    - **full_name**: 全名
    - **is_active**: 是否激活
    - **is_superuser**: 是否超级用户
    - **roles**: 角色列表
    - **permissions**: 权限列表
    - **accessible_stores**: 可访问门店列表（None表示全部，[]表示无权限，[id1,id2]表示限定门店）
    """
    # 构建角色列表
    roles = [role.code for role in current_user.roles]
    
    # 构建权限列表
    permissions = []
    if current_user.is_superuser:
        permissions = ["*:*:*"]
    else:
        perm_set = set()
        for role in current_user.roles:
            for perm in role.permissions:
                perm_set.add(perm.code)
        permissions = sorted(perm_set)
    
    # 获取可访问门店列表
    from app.services.data_scope_service import get_accessible_store_ids
    accessible_store_ids = await get_accessible_store_ids(db, current_user)
    
    user_info = UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        roles=roles,
        permissions=permissions
    )
    
    # 将用户信息转为字典并添加门店信息
    user_data = user_info.model_dump()
    user_data["accessible_stores"] = accessible_store_ids  # None表示全部，[]表示无权限，[id1,id2]表示限定门店
    
    return success(
        data=user_data,
        message="获取用户信息成功"
    )


@router.post(
    "/logout",
    response_model=dict,
    summary="用户登出",
    description="用户登出（前端需清除 token）"
)
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    用户登出
    
    由于使用 JWT，服务端无状态，登出主要在客户端清除 token
    这里记录登出日志
    """
    # 记录审计日志
    await create_audit_log(
        db=db,
        user=current_user,
        action="logout",
        resource="auth",
        detail={"ip": request.client.host if request.client else "unknown"},
        request=request,
    )
    
    return success(message="登出成功")
