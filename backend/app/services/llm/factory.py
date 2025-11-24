"""
LLM客户端工厂
"""

import logging
from typing import Optional
from app.services.llm.base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# 全局客户端缓存
_client_cache: dict = {}


def get_llm_client(provider: str) -> BaseLLMClient:
    """
    获取指定提供商的LLM客户端实例（单例模式）
    
    Args:
        provider: 提供商名称（zhipu/openai/deepseek/gemini）
    
    Returns:
        LLM客户端实例
    
    Raises:
        ValueError: 不支持的提供商或API密钥未配置
    """
    # 检查缓存
    if provider in _client_cache:
        return _client_cache[provider]
    
    # 检查API密钥是否已配置
    if not settings.is_provider_available(provider):
        raise ValueError(
            f"提供商 '{provider}' 的API密钥未配置，请在.env文件中设置对应的API_KEY"
        )
    
    # 延迟导入，避免循环依赖
    if provider == "zhipu":
        from app.services.llm.zhipu_llm import ZhipuLLMClient
        client = ZhipuLLMClient()
    elif provider == "openai":
        from app.services.llm.openai_llm import OpenAILLMClient
        client = OpenAILLMClient()
    elif provider == "deepseek":
        from app.services.llm.deepseek_llm import DeepSeekLLMClient
        client = DeepSeekLLMClient()
    elif provider == "gemini":
        from app.services.llm.gemini_llm import GeminiLLMClient
        client = GeminiLLMClient()
    elif provider == "ali":
        from app.services.llm.ali_llm import AliLLMClient
        client = AliLLMClient()
    else:
        raise ValueError(f"不支持的提供商: {provider}")
    
    # 缓存客户端
    _client_cache[provider] = client
    logger.info(f"✅ 初始化LLM客户端: {provider}")
    
    return client


def parse_model_string(model: str) -> tuple[str, str]:
    """
    解析模型字符串，提取provider和model_name
    
    Args:
        model: 模型字符串，格式：provider/model_name
    
    Returns:
        (provider, model_name) 元组
    
    Examples:
        >>> parse_model_string("openai/gpt-4o")
        ("openai", "gpt-4o")
        
        >>> parse_model_string("zhipu/GLM-4.5-Flash")
        ("zhipu", "GLM-4.5-Flash")
    """
    if "/" not in model:
        raise ValueError(f"无效的模型格式: {model}，应为 'provider/model_name'")
    
    parts = model.split("/", 1)
    return parts[0], parts[1]


def get_llm_client_for_model(model: str) -> tuple[BaseLLMClient, str]:
    """
    根据完整模型字符串获取客户端和模型名称
    
    Args:
        model: 完整模型字符串（如"openai/gpt-4o"）
    
    Returns:
        (客户端实例, 纯模型名称) 元组
    """
    provider, model_name = parse_model_string(model)
    client = get_llm_client(provider)
    return client, model_name

