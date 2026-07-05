"""
权限控制测试
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
class TestPermission:
    """权限控制测试"""
    
    async def test_admin_can_access_audit_logs(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        admin_user: User
    ):
        """测试管理员可以访问审计日志"""
        response = await client.get(
            "/api/v1/audit/logs",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
    
    async def test_normal_user_cannot_access_audit_logs(
        self, 
        client: AsyncClient,
        test_user: User
    ):
        """测试普通用户不能访问审计日志"""
        # 先登录获取token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "test123"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 尝试访问审计日志
        response = await client.get(
            "/api/v1/audit/logs",
            headers=headers
        )
        
        # 应该返回403禁止访问
        assert response.status_code == 403
    
    async def test_unauthenticated_cannot_access_protected_route(
        self, 
        client: AsyncClient
    ):
        """测试未认证用户不能访问受保护的路由"""
        response = await client.get("/api/v1/audit/logs")
        
        assert response.status_code == 403
    
    async def test_invalid_token(self, client: AsyncClient):
        """测试无效Token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == 401
