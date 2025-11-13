"""
全局异常处理器
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """自定义异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NovelNotFoundError(CustomException):
    """小说未找到"""
    def __init__(self, novel_id: int):
        super().__init__(
            message=f"小说 ID={novel_id} 未找到",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOVEL_NOT_FOUND"
        )


class ChapterNotFoundError(CustomException):
    """章节未找到"""
    def __init__(self, novel_id: int, chapter_num: int):
        super().__init__(
            message=f"小说 ID={novel_id} 的第 {chapter_num} 章未找到",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CHAPTER_NOT_FOUND"
        )


class FileUploadError(CustomException):
    """文件上传错误"""
    def __init__(self, message: str):
        super().__init__(
            message=f"文件上传失败: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR"
        )


class IndexingError(CustomException):
    """索引构建错误"""
    def __init__(self, message: str):
        super().__init__(
            message=f"索引构建失败: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INDEXING_ERROR"
        )


class ZhipuAPIError(CustomException):
    """智谱AI API错误"""
    def __init__(self, message: str):
        super().__init__(
            message=f"智谱AI API调用失败: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="ZHIPU_API_ERROR"
        )


class ChromaDBError(CustomException):
    """ChromaDB错误"""
    def __init__(self, message: str):
        super().__init__(
            message=f"ChromaDB操作失败: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CHROMADB_ERROR"
        )


class RateLimitError(CustomException):
    """频率限制错误"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"请求过于频繁，请在 {retry_after} 秒后重试",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class TokenLimitError(CustomException):
    """Token限制错误"""
    def __init__(self, current: int, limit: int):
        super().__init__(
            message=f"Token数量超出限制: 当前{current}, 限制{limit}",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code="TOKEN_LIMIT_EXCEEDED"
        )


class ModelNotFoundError(CustomException):
    """模型未找到"""
    def __init__(self, model_name: str):
        super().__init__(
            message=f"模型 '{model_name}' 不存在或不支持",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="MODEL_NOT_FOUND"
        )


class ConfigurationError(CustomException):
    """配置错误"""
    def __init__(self, message: str):
        super().__init__(
            message=f"配置错误: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CONFIGURATION_ERROR"
        )


async def custom_exception_handler(request: Request, exc: CustomException):
    """自定义异常处理器"""
    logger.error(f"自定义异常: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(f"验证异常: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未捕获的异常: {type(exc).__name__}")
    logger.error(f"异常详情: {str(exc)}")
    logger.error(f"异常追踪:\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "detail": str(exc) if logger.level == logging.DEBUG else "请联系管理员",
            "path": str(request.url.path)
        }
    )


def register_exception_handlers(app):
    """注册所有异常处理器到FastAPI应用"""
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("✅ 异常处理器已注册")

