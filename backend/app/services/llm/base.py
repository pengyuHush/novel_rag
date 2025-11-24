"""
LLM客户端抽象基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Generator, Any


class BaseLLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        非流式对话生成
        
        Args:
            messages: 对话消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称（不含provider前缀，如"gpt-4o"）
            **kwargs: 其他参数
        
        Returns:
            Dict包含：
            - content: 生成的文本内容
            - reasoning_content: 思考过程（可选，仅支持thinking的模型）
            - usage: token使用统计
            - finish_reason: 结束原因
        """
        pass
    
    @abstractmethod
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
            model: 模型名称（不含provider前缀）
            **kwargs: 其他参数
        
        Yields:
            Dict包含：
            - content: 生成的文本内容增量
            - reasoning_content: 思考过程增量（可选）
            - usage: token使用统计（流式结束时返回）
            - finish_reason: 结束原因（流式结束时返回）
        """
        pass
    
    def embed_text(self, text: str) -> List[float]:
        """
        文本向量化（可选实现）
        
        默认不支持，由智谱客户端处理embedding
        
        Args:
            text: 待向量化的文本
        
        Returns:
            向量列表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support embedding")
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass
    
    def supports_thinking(self, model: str) -> bool:
        """
        检查模型是否支持thinking模式
        
        Args:
            model: 模型名称
        
        Returns:
            是否支持thinking
        """
        return False

