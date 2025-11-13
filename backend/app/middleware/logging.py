"""
请求日志中间件
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求并记录日志"""
        # 记录请求开始
        start_time = time.time()
        
        # 提取请求信息
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # 使用结构化日志记录请求
        logger.info(
            f"Request started: {method} {path}",
            method=method,
            path=path,
            url=url,
            client_ip=client_host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间（毫秒）
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录响应
            status_code = response.status_code
            
            # 根据状态码选择日志级别
            if status_code >= 500:
                logger.error(
                    f"Request completed: {method} {path} - {status_code}",
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    client_ip=client_host
                )
            elif status_code >= 400:
                logger.warning(
                    f"Request completed: {method} {path} - {status_code}",
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    client_ip=client_host
                )
            else:
                logger.info(
                    f"Request completed: {method} {path} - {status_code}",
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    client_ip=client_host
                )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(duration_ms)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录异常
            logger.exception(
                f"Request failed: {method} {path} - {type(e).__name__}",
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                client_ip=client_host,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise

