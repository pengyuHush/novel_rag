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


def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
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
                    
                    # 429错误（并发限制）时增加等待时间
                    if "429" in str(e) or "1302" in str(e):
                        current_delay = max(current_delay, 5.0)  # 至少等5秒
                        logger.warning(f"⚠️ 并发限制错误，{current_delay}秒后重试 ({retries}/{max_retries}): {e}")
                    else:
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
            message = response.choices[0].message
            
            # GLM-4.5-Flash思考模式：内容可能在reasoning_content中
            content = message.content or ""
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                # 如果有推理内容但没有普通内容，使用推理内容
                if not content:
                    content = message.reasoning_content
                    logger.debug(f"使用reasoning_content作为响应内容（长度: {len(content)}）")
            
            result = {
                "content": content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"✅ {model} 调用成功 (tokens: {result['usage']['total_tokens']}, 内容长度: {len(content)})")
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
            chunk_count = 0
            first_chunk_logged = False
            
            for chunk in response:
                chunk_count += 1
                
                # 🔍 只打印第1个chunk的详细结构
                if chunk_count == 1:
                    logger.info(f"📦 第1个Chunk结构: {chunk}")
                    if hasattr(chunk, 'choices') and chunk.choices:
                        logger.info(f"   - delta: {chunk.choices[0].delta}")
                        delta_attrs = [attr for attr in dir(chunk.choices[0].delta) if not attr.startswith('_')]
                        logger.info(f"   - delta公共属性: {delta_attrs}")
                    first_chunk_logged = True
                
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    choice = chunk.choices[0]
                    
                    # 提取内容（可能在content字段）
                    content = delta.content if hasattr(delta, 'content') and delta.content else ""
                    
                    # 🤔 提取thinking模式的推理内容
                    reasoning_content = None
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        reasoning_content = delta.reasoning_content
                        if chunk_count <= 3:
                            logger.info(f"🤔 Chunk #{chunk_count} 有reasoning_content (前20字符): {reasoning_content[:20]}...")
                    
                    # 提取Token使用情况（如果有）
                    usage = None
                    if hasattr(chunk, 'usage') and chunk.usage:
                        usage = {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        }
                        total_tokens = chunk.usage.total_tokens
                        logger.info(f"📊 Chunk #{chunk_count} 收到usage: {usage}")
                    
                    # 获取finish_reason
                    finish_reason = choice.finish_reason if hasattr(choice, 'finish_reason') else None
                    if finish_reason:
                        logger.info(f"🏁 Chunk #{chunk_count} finish_reason: {finish_reason}")
                    
                    # 只yield有内容、thinking内容、usage或finish_reason的chunk
                    if content or reasoning_content or usage or finish_reason:
                        yield {
                            "content": content,
                            "reasoning_content": reasoning_content,
                            "model": model,
                            "usage": usage,
                            "finish_reason": finish_reason
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
        # 智谱AI模型信息 - 基于官方文档
        # 参考: https://docs.bigmodel.cn/cn/guide/start/model-overview
        model_info = {
            # 免费模型
            "GLM-4.5-Flash": {
                "name": "GLM-4.5-Flash",
                "description": "免费模型 - 最新基座模型的普惠版本",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 0.0, "output": 0.0}
            },
            "GLM-4-Flash-250414": {
                "name": "GLM-4-Flash",
                "description": "免费模型 - 超长上下文处理能力、多语言支持",
                "max_tokens": 128000,
                "max_output": 16000,
                "price_per_million_tokens": {"input": 0.0, "output": 0.0}
            },
            # 高性价比模型
            "GLM-4.5-Air": {
                "name": "GLM-4.5-Air",
                "description": "高性价比 - 在推理、编码和智能体任务上表现强劲",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 1.0, "output": 1.0}
            },
            "GLM-4.5-AirX": {
                "name": "GLM-4.5-AirX",
                "description": "高性价比-极速版 - 推理速度快，且价格适中",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 1.0, "output": 1.0}
            },
            "GLM-4-Air-250414": {
                "name": "GLM-4-Air",
                "description": "高性价比 - 快速执行复杂任务、擅长工具调用",
                "max_tokens": 128000,
                "max_output": 16000,
                "price_per_million_tokens": {"input": 1.0, "output": 1.0}
            },
            # 极速模型
            "GLM-4.5-X": {
                "name": "GLM-4.5-X",
                "description": "超强性能-极速版 - 推理速度更快",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 5.0, "output": 5.0}
            },
            "GLM-4-AirX": {
                "name": "GLM-4-AirX",
                "description": "极速推理 - 超快的推理速度",
                "max_tokens": 8000,
                "max_output": 4000,
                "price_per_million_tokens": {"input": 1.0, "output": 1.0}
            },
            "GLM-4-FlashX-250414": {
                "name": "GLM-4-FlashX",
                "description": "高速低价 - Flash增强版本、超快推理速度",
                "max_tokens": 128000,
                "max_output": 16000,
                "price_per_million_tokens": {"input": 0.1, "output": 0.1}
            },
            # 高性能模型
            "GLM-4.5": {
                "name": "GLM-4.5",
                "description": "超强性能 - 强大的推理能力、代码生成能力",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 5.0, "output": 5.0}
            },
            "GLM-4-Plus": {
                "name": "GLM-4-Plus",
                "description": "性能优秀 - 语言理解、逻辑推理、指令遵循效果领先",
                "max_tokens": 128000,
                "max_output": 4000,
                "price_per_million_tokens": {"input": 50.0, "output": 50.0}
            },
            "GLM-4.6": {
                "name": "GLM-4.6",
                "description": "高智能旗舰 - 智谱最强性能、高级编码能力",
                "max_tokens": 200000,
                "max_output": 128000,
                "price_per_million_tokens": {"input": 10.0, "output": 10.0}
            },
            # 超长上下文
            "GLM-4-Long": {
                "name": "GLM-4-Long",
                "description": "超长输入 - 支持高达1M的上下文长度",
                "max_tokens": 1000000,
                "max_output": 4000,
                "price_per_million_tokens": {"input": 100.0, "output": 100.0}
            },
            # 视觉模型
            "GLM-4.5V": {
                "name": "GLM-4.5V",
                "description": "旗舰视觉推理模型 - 视频、图片、图表解析",
                "max_tokens": 128000,
                "max_output": 96000,
                "price_per_million_tokens": {"input": 10.0, "output": 10.0}
            },
            "GLM-4V": {
                "name": "GLM-4V",
                "description": "视觉理解模型 - 图文混合理解",
                "max_tokens": 128000,
                "max_output": 4000,
                "price_per_million_tokens": {"input": 10.0, "output": 10.0}
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

