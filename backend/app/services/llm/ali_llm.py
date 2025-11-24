"""
阿里通义千问LLM客户端
"""

import logging
from typing import Dict, List, Generator, Any
from http import HTTPStatus
from dashscope import Generation
from app.services.llm.base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class AliLLMClient(BaseLLMClient):
    """阿里通义千问LLM客户端"""
    
    def __init__(self):
        """初始化阿里客户端"""
        import dashscope
        dashscope.api_key = settings.ali_api_key
        logger.info(f"✅ 阿里通义千问客户端初始化完成")
    
    @property
    def provider_name(self) -> str:
        """提供商名称"""
        return "ali"
    
    def supports_thinking(self, model: str) -> bool:
        """
        检查模型是否支持thinking模式
        
        Args:
            model: 模型名称
        
        Returns:
            是否支持thinking
        """
        # Qwen3 及以上版本的主流模型都支持思考模式
        thinking_models = ["qwen-max", "qwen-plus", "qwen-turbo", "qwen3"]
        return any(thinking_model in model.lower() for thinking_model in thinking_models)
    
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
            model: 模型名称（如"qwen-max"）
            **kwargs: 其他参数，包括：
                - enable_thinking: 是否启用思考模式（默认True）
                - thinking_budget: 最大推理过程Token数
        
        Returns:
            包含content、usage、reasoning_content等信息的字典
        """
        try:
            # 准备API调用参数
            api_params = {
                "model": model,
                "messages": messages,
                "result_format": "message",
                "stream": False,
            }
            
            # 如果模型支持思考模式且未显式设置，默认启用
            enable_thinking = False
            if self.supports_thinking(model):
                enable_thinking = kwargs.pop('enable_thinking', True)
                if enable_thinking:
                    api_params['enable_thinking'] = True
                    # 如果有thinking_budget参数，也传递
                    if 'thinking_budget' in kwargs:
                        api_params['thinking_budget'] = kwargs.pop('thinking_budget')
            
            # 添加其他参数
            api_params.update(kwargs)
            
            logger.info(f"📤 调用阿里通义千问模型: {model} (思考模式: {enable_thinking})")
            
            # 调用DashScope API
            response = Generation.call(**api_params)
            
            # 检查响应状态
            if response.status_code != HTTPStatus.OK:
                error_msg = f"阿里API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 提取响应内容
            choice = response.output.choices[0]
            message = choice.message
            content = message.content
            
            # 提取思考内容（如果启用了思考模式）
            reasoning_content = None
            if enable_thinking:
                try:
                    # 使用 getattr 安全获取，避免属性不存在时抛出异常
                    reasoning_content = getattr(message, 'reasoning_content', None)
                    if reasoning_content:
                        logger.info(f"🧠 获取到思考内容: {len(reasoning_content)} 字符")
                except Exception as e:
                    logger.warning(f"获取思考内容时出错: {e}")
            
            # 提取token使用统计
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            result = {
                "content": content,
                "usage": usage,
                "finish_reason": choice.finish_reason,
            }
            
            # 如果有思考内容，添加到结果中
            if reasoning_content:
                result["reasoning_content"] = reasoning_content
            
            logger.info(f"✅ 阿里API调用成功，生成 {len(content)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"❌ 阿里API调用失败: {e}")
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
            **kwargs: 其他参数，包括：
                - enable_thinking: 是否启用思考模式（默认True）
                - thinking_budget: 最大推理过程Token数
        
        Yields:
            包含增量内容和思考内容的字典
        """
        try:
            # 准备API调用参数
            api_params = {
                "model": model,
                "messages": messages,
                "result_format": "message",
                "stream": True,
                "incremental_output": True,  # 增量输出
            }
            
            # 如果模型支持思考模式且未显式设置，默认启用
            enable_thinking = False
            if self.supports_thinking(model):
                enable_thinking = kwargs.pop('enable_thinking', True)
                if enable_thinking:
                    api_params['enable_thinking'] = True
                    # 如果有thinking_budget参数，也传递
                    if 'thinking_budget' in kwargs:
                        api_params['thinking_budget'] = kwargs.pop('thinking_budget')
            
            # 添加其他参数
            api_params.update(kwargs)
            
            logger.info(f"📤 调用阿里通义千问模型（流式）: {model} (思考模式: {enable_thinking})")
            
            # 调用DashScope API（流式）
            responses = Generation.call(**api_params)
            
            # 流式处理响应
            for response in responses:
                try:
                    if response.status_code != HTTPStatus.OK:
                        error_msg = f"阿里API流式调用失败: {response.code} - {response.message}"
                        logger.error(error_msg)
                        yield {
                            "content": "",
                            "error": error_msg,
                            "finish_reason": "error"
                        }
                        break
                    
                    # 提取增量内容
                    chunk_data = {
                        "content": "",
                        "reasoning_content": None,
                        "usage": None,
                        "finish_reason": None,
                    }
                    
                    # 获取增量文本
                    if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                        choice = response.output.choices[0]
                        message = choice.message
                        
                        # 获取正常内容
                        if hasattr(message, 'content'):
                            chunk_data["content"] = message.content or ""
                        
                        # 获取思考内容（如果启用了思考模式）
                        if enable_thinking:
                            try:
                                # 使用 getattr 安全获取，避免属性不存在时抛出异常
                                reasoning = getattr(message, 'reasoning_content', None)
                                if reasoning:
                                    chunk_data["reasoning_content"] = reasoning
                                    logger.debug(f"🧠 流式思考内容: {len(reasoning)} 字符")
                            except AttributeError as ae:
                                # 属性不存在或访问失败，继续处理正常内容
                                logger.debug(f"思考内容字段不存在: {ae}")
                            except Exception as te:
                                # 其他异常也捕获，避免中断流式输出
                                logger.warning(f"获取思考内容时出错: {te}")
                        
                        # 检查是否结束
                        if hasattr(choice, 'finish_reason') and choice.finish_reason:
                            chunk_data["finish_reason"] = choice.finish_reason
                            
                            # 在最后一个chunk中返回token统计
                            if hasattr(response, 'usage') and response.usage:
                                chunk_data["usage"] = {
                                    "prompt_tokens": response.usage.input_tokens,
                                    "completion_tokens": response.usage.output_tokens,
                                    "total_tokens": response.usage.total_tokens,
                                }
                    
                    yield chunk_data
                    
                except Exception as chunk_error:
                    # 单个chunk处理错误不应该中断整个流
                    logger.warning(f"处理chunk时出错: {chunk_error}, 继续处理...")
                    continue
            
            logger.info(f"✅ 阿里流式API调用完成")
            
        except Exception as e:
            logger.error(f"❌ 阿里流式API调用失败: {e}")
            yield {
                "content": "",
                "error": str(e),
                "finish_reason": "error"
            }

