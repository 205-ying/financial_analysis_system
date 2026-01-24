"""
统一异常处理模块

定义自定义异常类和全局异常处理器，
确保 API 返回统一的错误响应格式。
"""

from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """标准错误响应模型"""
    
    code: int
    message: str
    detail: Optional[str] = None
    timestamp: str


class BaseAPIException(HTTPException):
    """
    API 基础异常类
    
    所有自定义异常都应该继承此类
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.message = message
        self.detail = detail


class ValidationException(BaseAPIException):
    """数据验证异常"""
    
    def __init__(
        self,
        message: str = "数据验证失败",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            detail=detail,
        )


class AuthenticationException(BaseAPIException):
    """认证异常"""
    
    def __init__(
        self,
        message: str = "认证失败",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(BaseAPIException):
    """授权异常"""
    
    def __init__(
        self,
        message: str = "权限不足",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail,
        )


class NotFoundException(BaseAPIException):
    """资源不存在异常"""
    
    def __init__(
        self,
        message: str = "资源不存在",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail,
        )


class ConflictException(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(
        self,
        message: str = "资源冲突",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            detail=detail,
        )


class BusinessException(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(
        self,
        message: str = "业务处理失败",
        detail: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(
            status_code=status_code,
            message=message,
            detail=detail,
        )


class DatabaseException(BaseAPIException):
    """数据库操作异常"""
    
    def __init__(
        self,
        message: str = "数据库操作失败",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail,
        )


class ExternalServiceException(BaseAPIException):
    """外部服务异常"""
    
    def __init__(
        self,
        message: str = "外部服务调用失败",
        detail: Optional[str] = None,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ):
        super().__init__(
            status_code=status_code,
            message=message,
            detail=detail,
        )


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    自定义异常处理器
    
    Args:
        request: FastAPI 请求对象
        exc: 自定义异常实例
        
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    from datetime import datetime
    
    # 记录异常日志
    logger.error(
        "API Exception: {}".format(exc.message),
        extra={
            "type": "api_exception",
            "status_code": exc.status_code,
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.message,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 异常处理器
    
    Args:
        request: FastAPI 请求对象
        exc: HTTP 异常实例
        
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    from datetime import datetime
    
    # 记录异常日志
    logger.warning(
        "HTTP Exception: {}".format(exc.detail),
        extra={
            "type": "http_exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": "请求处理失败",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    数据验证异常处理器
    
    Args:
        request: FastAPI 请求对象
        exc: 验证异常实例
        
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    from datetime import datetime
    
    # 记录异常日志
    try:
        logger.warning(
            "Validation Exception: {error}",
            error=str(exc),
            extra={
                "exception_type": "validation_exception",
                "path": request.url.path,
                "method": request.method,
            }
        )
    except Exception:
        # 如果日志记录失败，使用简单格式
        logger.warning(f"Validation Exception at {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "数据验证失败",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    
    处理所有未被其他处理器捕获的异常
    
    Args:
        request: FastAPI 请求对象
        exc: 异常实例
        
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    from datetime import datetime
    
    # 记录异常日志（避免使用format以防止KeyError）
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "exception_type": "unhandled_exception",
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "服务器内部错误",
            "detail": "请联系系统管理员",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )