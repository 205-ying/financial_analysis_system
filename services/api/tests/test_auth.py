"""
认证模块测试
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
class TestAuth:
    """认证相关测试"""
    
    async def test_login_success(self, client: AsyncClient, admin_user: User):
        """测试登录成功"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "user_info" in data["data"]
        assert data["data"]["user_info"]["username"] == "admin"
    
    async def test_login_wrong_password(self, client: AsyncClient, admin_user: User):
        """测试登录失败 - 密码错误"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "用户名或密码错误" in data["detail"]
    
    async def test_login_user_not_exist(self, client: AsyncClient):
        """测试登录失败 - 用户不存在"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "用户名或密码错误" in data["detail"]
    
    async def test_get_user_info(self, client: AsyncClient, auth_headers: dict):
        """测试获取用户信息"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "admin"
        assert "permissions" in data["data"]
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
