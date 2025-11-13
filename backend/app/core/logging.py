"""
结构化日志配置模块
提供统一的日志记录接口和格式化
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义JSON日志格式化器"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """添加自定义字段到日志记录"""
        super().add_fields(log_record, record, message_dict)
        
        # 添加时间戳
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # 添加日志级别
        log_record['level'] = record.levelname
        
        # 添加模块信息
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # 添加进程和线程信息
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # 如果有异常信息，添加完整的堆栈跟踪
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._extra: Dict[str, Any] = {}
    
    def with_context(self, **kwargs) -> 'StructuredLogger':
        """添加上下文信息"""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.logger = self.logger
        new_logger._extra = {**self._extra, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, **kwargs):
        """内部日志记录方法"""
        extra = {**self._extra, **kwargs}
        self.logger.log(level, message, extra={'props': extra})
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """异常日志（自动包含堆栈信息）"""
        extra = {**self._extra, **kwargs}
        self.logger.exception(message, extra={'props': extra})


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = True
) -> None:
    """
    配置应用日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        json_format: 是否使用JSON格式
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 配置格式化器
    if json_format:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)


def get_logger(name: str) -> StructuredLogger:
    """
    获取结构化日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
    
    Returns:
        结构化日志记录器实例
    """
    return StructuredLogger(name)


# 便捷的日志记录函数
def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None
):
    """记录HTTP请求日志"""
    logger = get_logger('api.request')
    logger.info(
        f"{method} {path} - {status_code}",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id
    )


def log_llm_call(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    success: bool = True,
    error: Optional[str] = None
):
    """记录LLM调用日志"""
    logger = get_logger('llm.call')
    logger.info(
        f"LLM call to {model}",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        duration_ms=duration_ms,
        success=success,
        error=error
    )


def log_db_query(
    operation: str,
    collection: str,
    duration_ms: float,
    result_count: Optional[int] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """记录数据库查询日志"""
    logger = get_logger('db.query')
    logger.info(
        f"{operation} on {collection}",
        operation=operation,
        collection=collection,
        duration_ms=duration_ms,
        result_count=result_count,
        success=success,
        error=error
    )


def log_cache_operation(
    operation: str,
    key: str,
    hit: bool,
    duration_ms: Optional[float] = None
):
    """记录缓存操作日志"""
    logger = get_logger('cache.operation')
    logger.info(
        f"Cache {operation}: {key}",
        operation=operation,
        key=key,
        hit=hit,
        duration_ms=duration_ms
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    **tags
):
    """记录性能指标"""
    logger = get_logger('performance.metric')
    logger.info(
        f"Performance metric: {metric_name}",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **tags
    )

