"""
DeepSeek LLM客户端实现
"""

import logging
from typing import Dict, List, Generator, Any
from openai import OpenAI
from app.services.llm.base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekLLMClient(BaseLLMClient):
    """DeepSeek LLM客户端（兼容OpenAI格式）"""
    
    def __init__(self):
        """初始化DeepSeek客户端"""
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        logger.info(f"✅ DeepSeek客户端初始化完成")
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        非流式对话生成
        
        Args:
            messages: 对话消息列表
            model: 模型名称（如"deepseek-chat", "deepseek-reasoner"）
            **kwargs: 其他参数
        
        Returns:
            包含content、reasoning_content(可选)和usage的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                **kwargs
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content or "",
                "finish_reason": response.choices[0].finish_reason,
            }
            
            # DeepSeek-Reasoner模型会返回reasoning_content
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                result["reasoning_content"] = message.reasoning_content
            
            # 添加token使用统计
            if response.usage:
                result["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                
                # DeepSeek特有的缓存命中统计
                if hasattr(response.usage, 'prompt_cache_hit_tokens'):
                    result["usage"]["prompt_cache_hit_tokens"] = response.usage.prompt_cache_hit_tokens
                if hasattr(response.usage, 'prompt_cache_miss_tokens'):
                    result["usage"]["prompt_cache_miss_tokens"] = response.usage.prompt_cache_miss_tokens
            
            return result
            
        except Exception as e:
            logger.error(f"❌ DeepSeek对话生成失败: {e}")
            raise
    
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式对话生成
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            **kwargs: 其他参数
        
        Yields:
            包含content和reasoning_content增量的字典
        """
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if not chunk.choices:
                    continue
                
                choice = chunk.choices[0]
                result = {}
                
                # 推理内容增量（DeepSeek-Reasoner专有）
                if hasattr(choice.delta, 'reasoning_content') and choice.delta.reasoning_content:
                    result["reasoning_content"] = choice.delta.reasoning_content
                
                # 回答内容增量
                if choice.delta.content:
                    result["content"] = choice.delta.content
                
                # 结束原因
                if choice.finish_reason:
                    result["finish_reason"] = choice.finish_reason
                
                # Token使用统计（DeepSeek在流式结束时返回）
                if hasattr(chunk, 'usage') and chunk.usage:
                    result["usage"] = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                    
                    # 缓存命中统计
                    if hasattr(chunk.usage, 'prompt_cache_hit_tokens'):
                        result["usage"]["prompt_cache_hit_tokens"] = chunk.usage.prompt_cache_hit_tokens
                    if hasattr(chunk.usage, 'prompt_cache_miss_tokens'):
                        result["usage"]["prompt_cache_miss_tokens"] = chunk.usage.prompt_cache_miss_tokens
                
                if result:
                    yield result
                    
        except Exception as e:
            logger.error(f"❌ DeepSeek流式生成失败: {e}")
            raise
    
    def supports_thinking(self, model: str) -> bool:
        """检查模型是否支持thinking模式"""
        # deepseek-reasoner支持thinking模式
        return "reasoner" in model.lower()

