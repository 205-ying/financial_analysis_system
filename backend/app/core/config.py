"""
应用配置管理模块

使用 pydantic-settings 管理应用配置
支持从环境变量、.env 文件等多种方式读取配置
"""

from functools import lru_cache
from typing import List, Optional
import json

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = Field(default="餐饮企业财务分析系统", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")
    
    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/financial_analysis",
        description="数据库连接字符串"
    )
    database_echo: bool = Field(default=False, description="是否打印 SQL 语句")
    
    # JWT 认证配置
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production",
        description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT 过期时间（分钟）")
    jwt_refresh_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
    
    # CORS 配置
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://localhost:5174",
            "http://127.0.0.1:5174"
        ],
        description="允许跨域的源地址列表"
    )
    cors_allow_credentials: bool = Field(default=True, description="是否允许携带认证信息")
    cors_allow_methods: List[str] = Field(
        default=["*"], 
        description="允许的 HTTP 方法"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], 
        description="允许的 HTTP 请求头"
    )
    
    # API 配置
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 路径前缀")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_rotation: str = Field(default="1 day", description="日志文件轮转周期")
    log_retention: str = Field(default="30 days", description="日志文件保留时间")
    
    # Redis 配置（可选）
    redis_url: Optional[str] = Field(default=None, description="Redis 连接地址")
    
    # 分页配置
    default_page_size: int = Field(default=20, description="默认分页大小")
    max_page_size: int = Field(default=100, description="最大分页大小")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('cors_allow_methods', pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [method.strip() for method in v.split(',')]
        return v
    
    @validator('cors_allow_headers', pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [header.strip() for header in v.split(',')]
        return v
    
    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置实例
    
    使用 lru_cache 装饰器确保配置只被实例化一次
    提高性能并确保配置的一致性
    
    Returns:
        Settings: 应用配置实例
    """
    return Settings()


# 导出配置实例
settings = get_settings()