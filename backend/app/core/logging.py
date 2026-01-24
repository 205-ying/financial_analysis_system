"""
日志配置模块

使用 loguru 库配置应用日志，
支持控制台输出、文件输出、日志轮转等功能。
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    """
    配置应用日志
    
    根据配置设置日志级别、输出格式、文件轮转等。
    """
    # 移除默认的控制台处理器
    logger.remove()
    
    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # 如果配置了日志文件，添加文件处理器
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            settings.log_file,
            format=log_format,
            level=settings.log_level,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
    
    # 配置第三方库日志级别
    configure_third_party_logging()


def configure_third_party_logging() -> None:
    """
    配置第三方库的日志级别
    
    避免第三方库的日志过于冗余。
    """
    import logging
    
    # SQLAlchemy 日志配置
    if not settings.database_echo:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # uvicorn 日志配置
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # httpx 日志配置
    logging.getLogger("httpx").setLevel(logging.WARNING)


class StructuredLogger:
    """
    结构化日志记录器
    
    提供统一的日志记录接口，支持结构化日志输出。
    """
    
    @staticmethod
    def log_request(
        method: str,
        url: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None,
    ) -> None:
        """
        记录 HTTP 请求日志
        
        Args:
            method: HTTP 方法
            url: 请求 URL
            status_code: 响应状态码
            duration: 请求处理时间（秒）
            user_id: 用户 ID（可选）
        """
        logger.info(
            "HTTP Request",
            extra={
                "type": "http_request",
                "method": method,
                "url": url,
                "status_code": status_code,
                "duration": duration,
                "user_id": user_id,
            }
        )
    
    @staticmethod
    def log_database_operation(
        operation: str,
        table: str,
        duration: float,
        affected_rows: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        记录数据库操作日志
        
        Args:
            operation: 操作类型（SELECT, INSERT, UPDATE, DELETE）
            table: 表名
            duration: 操作耗时（秒）
            affected_rows: 影响的行数
            user_id: 用户 ID（可选）
        """
        logger.info(
            "Database Operation",
            extra={
                "type": "database_operation",
                "operation": operation,
                "table": table,
                "duration": duration,
                "affected_rows": affected_rows,
                "user_id": user_id,
            }
        )
    
    @staticmethod
    def log_business_event(
        event: str,
        details: dict,
        user_id: Optional[str] = None,
    ) -> None:
        """
        记录业务事件日志
        
        Args:
            event: 事件名称
            details: 事件详情
            user_id: 用户 ID（可选）
        """
        logger.info(
            f"Business Event: {event}",
            extra={
                "type": "business_event",
                "event": event,
                "details": details,
                "user_id": user_id,
            }
        )
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[dict] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            user_id: 用户 ID（可选）
        """
        logger.error(
            f"Error: {str(error)}",
            extra={
                "type": "error",
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "context": context or {},
                "user_id": user_id,
            }
        )


# 导出结构化日志记录器实例
structured_logger = StructuredLogger()