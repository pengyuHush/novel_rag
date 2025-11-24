"""
LLM提供商配置状态API
用于前端动态显示/隐藏模型选项
"""

from fastapi import APIRouter
from typing import Dict
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/providers",
    tags=["提供商配置"]
)


@router.get("/status")
async def get_providers_status() -> Dict[str, Dict[str, bool]]:
    """
    获取所有LLM提供商的配置状态
    
    Returns:
        返回各提供商的API Key配置状态（仅返回布尔值，不返回敏感信息）
        
    Example:
        {
            "providers": {
                "zhipu": true,
                "openai": false,
                "deepseek": false,
                "gemini": false,
                "ali": true
            }
        }
    """
    try:
        # 获取所有提供商的配置状态
        providers_status = {
            "zhipu": settings.is_provider_available("zhipu"),
            "openai": settings.is_provider_available("openai"),
            "deepseek": settings.is_provider_available("deepseek"),
            "gemini": settings.is_provider_available("gemini"),
            "ali": settings.is_provider_available("ali"),
        }
        
        logger.info(f"📊 提供商状态: {providers_status}")
        
        return {
            "providers": providers_status
        }
    
    except Exception as e:
        logger.error(f"❌ 获取提供商状态失败: {e}")
        # 发生错误时返回默认状态（全部不可用）
        return {
            "providers": {
                "zhipu": False,
                "openai": False,
                "deepseek": False,
                "gemini": False,
                "ali": False,
            }
        }

