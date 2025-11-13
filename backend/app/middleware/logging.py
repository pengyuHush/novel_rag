"""
请求日志中间件
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求并记录日志"""
        # 记录请求开始
        start_time = time.time()
        
        # 提取请求信息
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        logger.info(f"➡️ {method} {url} from {client_host}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应
            status_code = response.status_code
            log_message = f"⬅️ {method} {url} - {status_code} ({process_time:.3f}s)"
            
            # 根据状态码选择日志级别
            if status_code >= 500:
                logger.error(log_message)
            elif status_code >= 400:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录异常
            logger.error(f"❌ {method} {url} - Exception: {str(e)} ({process_time:.3f}s)")
            raise

