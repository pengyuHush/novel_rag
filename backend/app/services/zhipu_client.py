"""
智谱AI客户端封装
支持GLM-4系列模型和Embedding-3向量化
"""

import time
import logging
from typing import List, Dict, Optional, Iterator, Any
from zhipuai import ZhipuAI
import asyncio
from functools import wraps

from app.core.config import settings
from app.core.error_handlers import ZhipuAPIError

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    API调用失败重试装饰器（指数退避）
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"❌ API调用失败，已达最大重试次数: {e}")
                        raise
                    
                    logger.warning(f"⚠️ API调用失败，{current_delay}秒后重试 ({retries}/{max_retries}): {e}")
                    time.sleep(current_delay)
                    current_delay *= 2  # 指数退避
            
            return None
        return wrapper
    return decorator


class ZhipuAIClient:
    """智谱AI客户端封装类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱AI客户端
        
        Args:
            api_key: API密钥，如不提供则从配置读取
        """
        self.api_key = api_key or settings.zhipu_api_key
        
        if not self.api_key or self.api_key == "your_zhipuai_api_key_here":
            raise ValueError("智谱AI API Key未配置，请在.env文件中设置ZHIPU_API_KEY")
        
        self.client = ZhipuAI(api_key=self.api_key)
        self.default_model = settings.zhipu_default_model
        
        logger.info(f"✅ 智谱AI客户端初始化成功 (默认模型: {self.default_model})")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def embed_texts(
        self,
        texts: List[str],
        model: str = "embedding-3"
    ) -> List[List[float]]:
        """
        文本向量化（Embedding-3）
        
        Args:
            texts: 文本列表
            model: Embedding模型名称
        
        Returns:
            List[List[float]]: 向量列表
        """
        try:
            logger.debug(f"🔄 正在向量化 {len(texts)} 个文本...")
            
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"✅ 向量化完成: {len(embeddings)} 个向量")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ 向量化失败: {e}")
            raise ZhipuAPIError(str(e))
    
    def embed_text(self, text: str, model: str = "embedding-3") -> List[float]:
        """
        单个文本向量化
        
        Args:
            text: 文本
            model: Embedding模型名称
        
        Returns:
            List[float]: 向量
        """
        embeddings = self.embed_texts([text], model=model)
        return embeddings[0]
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天补全（同步）
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称（默认使用配置的默认模型）
            temperature: 温度参数 (0.0-1.0)
            top_p: Top-p采样参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        
        Returns:
            Dict: 响应数据
        """
        model = model or self.default_model
        
        try:
            logger.debug(f"🔄 调用 {model}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 提取响应数据
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"✅ {model} 调用成功 (tokens: {result['usage']['total_tokens']})")
            return result
            
        except Exception as e:
            logger.error(f"❌ {model} 调用失败: {e}")
            raise ZhipuAPIError(str(e))
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        聊天补全（流式）
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            top_p: Top-p采样参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        
        Yields:
            Dict: 流式响应数据
        """
        model = model or self.default_model
        
        try:
            logger.debug(f"🔄 调用 {model} (流式)...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            total_tokens = 0
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    # 提取内容
                    content = delta.content if hasattr(delta, 'content') else ""
                    
                    # 提取Token使用情况（如果有）
                    usage = None
                    if hasattr(chunk, 'usage') and chunk.usage:
                        usage = {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        }
                        total_tokens = chunk.usage.total_tokens
                    
                    yield {
                        "content": content,
                        "model": model,
                        "usage": usage,
                        "finish_reason": chunk.choices[0].finish_reason if hasattr(chunk.choices[0], 'finish_reason') else None
                    }
            
            logger.info(f"✅ {model} 流式调用完成 (tokens: {total_tokens})")
            
        except Exception as e:
            logger.error(f"❌ {model} 流式调用失败: {e}")
            raise ZhipuAPIError(str(e))
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model: 模型名称
        
        Returns:
            Dict: 模型信息
        """
        # 智谱AI模型信息（2024年数据）
        model_info = {
            "glm-4-flash": {
                "name": "GLM-4-Flash",
                "description": "最快速、最经济的模型",
                "max_tokens": 128000,
                "price_per_million_tokens": {
                    "input": 0.1,
                    "output": 0.1
                }
            },
            "glm-4": {
                "name": "GLM-4",
                "description": "平衡性能和成本",
                "max_tokens": 128000,
                "price_per_million_tokens": {
                    "input": 5.0,
                    "output": 5.0
                }
            },
            "glm-4-plus": {
                "name": "GLM-4-Plus",
                "description": "最强推理能力",
                "max_tokens": 128000,
                "price_per_million_tokens": {
                    "input": 50.0,
                    "output": 50.0
                }
            },
            "glm-4-5": {
                "name": "GLM-4.5",
                "description": "增强版本",
                "max_tokens": 128000,
                "price_per_million_tokens": {
                    "input": 10.0,
                    "output": 10.0
                }
            },
            "glm-4-6": {
                "name": "GLM-4.6",
                "description": "最新版本",
                "max_tokens": 128000,
                "price_per_million_tokens": {
                    "input": 15.0,
                    "output": 15.0
                }
            },
            "embedding-3": {
                "name": "Embedding-3",
                "description": "文本向量化模型",
                "dimensions": 1024,
                "price_per_million_tokens": {
                    "input": 0.5,
                    "output": 0
                }
            }
        }
        
        return model_info.get(model, {
            "name": model,
            "description": "未知模型",
            "max_tokens": 128000
        })
    
    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int = 0
    ) -> float:
        """
        估算API调用成本（人民币）
        
        Args:
            model: 模型名称
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
        
        Returns:
            float: 估算成本（元）
        """
        model_info = self.get_model_info(model)
        pricing = model_info.get("price_per_million_tokens", {"input": 0, "output": 0})
        
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost


# 全局智谱AI客户端实例
_zhipu_client: Optional[ZhipuAIClient] = None


def get_zhipu_client() -> ZhipuAIClient:
    """获取全局智谱AI客户端实例（单例）"""
    global _zhipu_client
    if _zhipu_client is None:
        _zhipu_client = ZhipuAIClient()
    return _zhipu_client

