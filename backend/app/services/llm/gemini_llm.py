"""
Gemini LLM客户端实现
"""

import logging
from typing import Dict, List, Generator, Any
from google import genai
from google.genai import types
from app.services.llm.base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiLLMClient(BaseLLMClient):
    """Gemini LLM客户端"""
    
    def __init__(self):
        """初始化Gemini客户端"""
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        logger.info(f"✅ Gemini客户端初始化完成")
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    def _convert_messages_to_contents(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        将OpenAI格式的messages转换为Gemini的contents格式
        
        Args:
            messages: OpenAI格式的消息列表
        
        Returns:
            Gemini格式的contents
        """
        # Gemini API简化格式：直接使用最后一条用户消息
        # 或者将多轮对话合并为一个提示
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system" or role == "developer":
                # 系统消息作为system_instruction
                system_instruction = content
            elif role == "user":
                contents.append(content)
            elif role == "assistant":
                # 将助手消息也加入上下文
                contents.append(f"[Previous response]: {content}")
        
        return contents, system_instruction
    
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
            model: 模型名称（如"gemini-1.5-pro"）
            **kwargs: 其他参数
        
        Returns:
            包含content和usage的字典
        """
        try:
            contents, system_instruction = self._convert_messages_to_contents(messages)
            
            # 构建配置
            config_params = {}
            if system_instruction:
                config_params["system_instruction"] = system_instruction
            
            # 添加其他配置参数
            if "temperature" in kwargs:
                config_params["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                config_params["max_output_tokens"] = kwargs["max_tokens"]
            
            config = types.GenerateContentConfig(**config_params) if config_params else None
            
            # 调用API
            response = self.client.models.generate_content(
                model=model,
                contents="\n\n".join(contents),
                config=config
            )
            
            result = {
                "content": response.text or "",
                "finish_reason": "stop",  # Gemini不返回finish_reason，默认为stop
            }
            
            # 添加token使用统计（如果有）
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                result["usage"] = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Gemini对话生成失败: {e}")
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
            contents, system_instruction = self._convert_messages_to_contents(messages)
            
            # 构建配置
            config_params = {}
            if system_instruction:
                config_params["system_instruction"] = system_instruction
            
            if "temperature" in kwargs:
                config_params["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                config_params["max_output_tokens"] = kwargs["max_tokens"]
            
            config = types.GenerateContentConfig(**config_params) if config_params else None
            
            # 流式调用
            stream = self.client.models.generate_content_stream(
                model=model,
                contents="\n\n".join(contents),
                config=config
            )
            
            total_prompt_tokens = 0
            total_completion_tokens = 0
            
            for chunk in stream:
                result = {}
                
                # 内容增量
                if hasattr(chunk, 'text') and chunk.text:
                    result["content"] = chunk.text
                
                # Token统计（通常在最后一个chunk）
                if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                    total_prompt_tokens = chunk.usage_metadata.prompt_token_count
                    total_completion_tokens = chunk.usage_metadata.candidates_token_count
                    
                    result["usage"] = {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens,
                    }
                
                if result:
                    yield result
            
            # 流式结束，发送finish_reason
            yield {
                "finish_reason": "stop",
            }
                    
        except Exception as e:
            logger.error(f"❌ Gemini流式生成失败: {e}")
            raise
    
    def supports_thinking(self, model: str) -> bool:
        """Gemini标准模型不支持thinking模式"""
        return False

