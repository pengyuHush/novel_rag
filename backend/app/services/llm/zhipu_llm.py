"""
智谱AI LLM客户端实现（适配新接口）
"""

import logging
from typing import Dict, List, Generator, Any
from app.services.llm.base import BaseLLMClient
from app.services.zhipu_client import ZhipuAIClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class ZhipuLLMClient(BaseLLMClient):
    """智谱AI LLM客户端（复用现有ZhipuAIClient）"""
    
    def __init__(self):
        """初始化智谱LLM客户端"""
        # 复用现有的智谱客户端
        self.zhipu_client = ZhipuAIClient()
        logger.info(f"✅ 智谱LLM客户端初始化完成")
    
    @property
    def provider_name(self) -> str:
        return "zhipu"
    
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
            model: 模型名称（如"GLM-4.5-Flash"）
            **kwargs: 其他参数
        
        Returns:
            包含content、reasoning_content(可选)和usage的字典
        """
        try:
            # 调用现有的智谱客户端
            response = self.zhipu_client.chat_completion(
                messages=messages,
                model=model,
                **kwargs
            )
            
            # 统一返回格式
            result = {
                "content": response.get("content", ""),
                "finish_reason": response.get("finish_reason", "stop"),
            }
            
            # 智谱模型可能返回reasoning_content
            if "reasoning_content" in response:
                result["reasoning_content"] = response["reasoning_content"]
            
            # Token统计
            if "usage" in response:
                result["usage"] = response["usage"]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 智谱对话生成失败: {e}")
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
            # 调用现有的智谱客户端流式方法
            for chunk_data in self.zhipu_client.chat_completion_stream(
                messages=messages,
                model=model,
                **kwargs
            ):
                # chunk_data已经是标准格式，直接yield
                # 格式：{"content": "...", "reasoning_content": "...", "usage": {...}, "finish_reason": "..."}
                yield chunk_data
                    
        except Exception as e:
            logger.error(f"❌ 智谱流式生成失败: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        文本向量化（复用现有embedding功能）
        
        Args:
            text: 待向量化的文本
        
        Returns:
            向量列表
        """
        return self.zhipu_client.embed_text(text)
    
    def supports_thinking(self, model: str) -> bool:
        """检查模型是否支持thinking模式"""
        # 智谱的GLM-4.5-Flash等模型支持thinking模式（reasoning_content）
        # 但这不是专门的reasoning模型，所以返回False
        return False

