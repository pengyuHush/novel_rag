"""
OpenAI LLM客户端实现
"""

import logging
from typing import Dict, List, Generator, Any
from openai import OpenAI
from app.services.llm.base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAILLMClient(BaseLLMClient):
    """OpenAI LLM客户端"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        logger.info(f"✅ OpenAI客户端初始化完成")
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
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
            model: 模型名称（如"gpt-4o"）
            **kwargs: 其他参数
        
        Returns:
            包含content和usage的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                **kwargs
            )
            
            result = {
                "content": response.choices[0].message.content or "",
                "finish_reason": response.choices[0].finish_reason,
            }
            
            # 添加token使用统计
            if response.usage:
                result["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ OpenAI对话生成失败: {e}")
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
            包含content增量的字典
        """
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},  # 请求返回usage
                **kwargs
            )
            
            for chunk in stream:
                if not chunk.choices:
                    # 某些chunk可能只包含usage信息
                    if hasattr(chunk, 'usage') and chunk.usage:
                        yield {
                            "usage": {
                                "prompt_tokens": chunk.usage.prompt_tokens,
                                "completion_tokens": chunk.usage.completion_tokens,
                                "total_tokens": chunk.usage.total_tokens,
                            }
                        }
                    continue
                
                choice = chunk.choices[0]
                result = {}
                
                # 内容增量
                if choice.delta.content:
                    result["content"] = choice.delta.content
                
                # 结束原因
                if choice.finish_reason:
                    result["finish_reason"] = choice.finish_reason
                
                # Token使用统计（通常在最后一个chunk）
                if hasattr(chunk, 'usage') and chunk.usage:
                    result["usage"] = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                
                if result:
                    yield result
                    
        except Exception as e:
            logger.error(f"❌ OpenAI流式生成失败: {e}")
            raise
    
    def supports_thinking(self, model: str) -> bool:
        """OpenAI标准模型不支持thinking模式"""
        return False

