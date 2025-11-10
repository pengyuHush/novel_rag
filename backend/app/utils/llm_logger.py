"""LLM API调用日志工具 - 统一记录所有智谱AI API的入参和出参."""

from __future__ import annotations

import json
import time
from functools import wraps
from typing import Any, Callable, Optional

from loguru import logger


class LLMCallLogger:
    """LLM API调用日志记录器."""
    
    @staticmethod
    def log_api_call(
        api_type: str,
        model: str,
        request_params: dict,
        response: Any = None,
        error: Optional[Exception] = None,
        duration: Optional[float] = None,
        stream_accumulated_content: Optional[str] = None
    ):
        """记录API调用详情.
        
        Args:
            api_type: API类型 (embeddings/chat/chat_stream)
            model: 模型名称
            request_params: 请求参数
            response: API响应对象
            error: 异常信息（如果有）
            duration: 调用耗时（秒）
            stream_accumulated_content: 流式输出累积的完整内容
        """
        log_data = {
            "api_type": api_type,
            "model": model,
            "timestamp": time.time(),
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
        
        # 记录请求参数（敏感信息脱敏）
        safe_params = LLMCallLogger._sanitize_params(request_params)
        log_data["request"] = safe_params
        
        # 记录响应或错误
        if error:
            log_data["status"] = "error"
            log_data["error"] = str(error)
            logger.error(f"[LLM API ERROR] {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        else:
            log_data["status"] = "success"
            
            # 提取响应信息
            if response:
                response_info = LLMCallLogger._extract_response_info(
                    response, 
                    api_type, 
                    stream_accumulated_content
                )
                log_data["response"] = response_info
            
            logger.info(f"[LLM API CALL] {json.dumps(log_data, ensure_ascii=False, indent=2)}")
    
    @staticmethod
    def _sanitize_params(params: dict) -> dict:
        """脱敏处理请求参数."""
        safe_params = params.copy()
        
        # 截断过长的input/messages
        if "input" in safe_params:
            if isinstance(safe_params["input"], list):
                safe_params["input"] = [
                    text[:100] + "..." if len(text) > 100 else text
                    for text in safe_params["input"][:3]  # 只显示前3条
                ]
                if len(params.get("input", [])) > 3:
                    safe_params["input"].append(f"... and {len(params['input']) - 3} more")
            elif isinstance(safe_params["input"], str):
                if len(safe_params["input"]) > 200:
                    safe_params["input"] = safe_params["input"][:200] + "..."
        
        if "messages" in safe_params:
            safe_messages = []
            for msg in safe_params["messages"][:5]:  # 只显示前5条消息
                safe_msg = msg.copy()
                if "content" in safe_msg and len(safe_msg["content"]) > 200:
                    safe_msg["content"] = safe_msg["content"][:200] + "..."
                safe_messages.append(safe_msg)
            
            if len(safe_params["messages"]) > 5:
                safe_messages.append(f"... and {len(safe_params['messages']) - 5} more messages")
            
            safe_params["messages"] = safe_messages
        
        return safe_params
    
    @staticmethod
    def _extract_response_info(response: Any, api_type: str, stream_content: Optional[str] = None) -> dict:
        """提取响应信息."""
        info = {}
        
        # 提取token使用情况
        if hasattr(response, 'usage') and response.usage:
            info["usage"] = {
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                "total_tokens": getattr(response.usage, 'total_tokens', 0),
            }
        
        # 根据API类型提取内容
        if api_type == "embeddings":
            if hasattr(response, 'data') and response.data:
                info["vector_count"] = len(response.data)
                info["vector_dimension"] = len(response.data[0].embedding) if response.data else 0
        
        elif api_type in ["chat", "chat_stream"]:
            # 对于流式输出，使用累积的内容
            if stream_content is not None:
                content = stream_content
            elif hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                content = message.content or getattr(message, 'reasoning_content', None) or ""
            else:
                content = ""
            
            # 截断过长的输出
            if len(content) > 500:
                info["content"] = content[:500] + f"... (total {len(content)} chars)"
            else:
                info["content"] = content
            
            info["content_length"] = len(content)
        
        return info


class StreamContentAccumulator:
    """流式内容累积器 - 用于收集流式API的完整输出."""
    
    def __init__(self):
        self.thinking_parts = []
        self.answer_parts = []
        self.total_chunks = 0
        self.start_time = time.time()
        self.usage = None
    
    def add_thinking_chunk(self, content: str):
        """添加思考过程片段."""
        self.thinking_parts.append(content)
        self.total_chunks += 1
    
    def add_answer_chunk(self, content: str):
        """添加答案片段."""
        self.answer_parts.append(content)
        self.total_chunks += 1
    
    def set_usage(self, usage: Any):
        """设置token使用信息."""
        self.usage = usage
    
    def get_full_thinking(self) -> str:
        """获取完整的思考过程."""
        return "".join(self.thinking_parts)
    
    def get_full_answer(self) -> str:
        """获取完整的答案."""
        return "".join(self.answer_parts)
    
    def get_full_content(self) -> str:
        """获取完整内容（思考+答案）."""
        parts = []
        if self.thinking_parts:
            parts.append("【思考过程】\n" + self.get_full_thinking())
        if self.answer_parts:
            parts.append("【答案】\n" + self.get_full_answer())
        return "\n\n".join(parts)
    
    def get_duration(self) -> float:
        """获取累积耗时."""
        return time.time() - self.start_time
    
    def log_summary(self, api_type: str, model: str, request_params: dict):
        """记录流式调用的汇总日志."""
        # 构建模拟的response对象用于统一日志格式
        class MockResponse:
            def __init__(self, usage):
                self.usage = usage
        
        mock_response = MockResponse(self.usage) if self.usage else None
        
        LLMCallLogger.log_api_call(
            api_type=api_type,
            model=model,
            request_params=request_params,
            response=mock_response,
            duration=self.get_duration(),
            stream_accumulated_content=self.get_full_content()
        )
        
        # 额外记录统计信息
        logger.info(
            f"[STREAM SUMMARY] chunks={self.total_chunks}, "
            f"thinking_length={len(self.get_full_thinking())}, "
            f"answer_length={len(self.get_full_answer())}, "
            f"duration={self.get_duration():.3f}s"
        )


def log_llm_call(api_type: str, model: str):
    """装饰器：自动记录LLM API调用的日志.
    
    用法:
        @log_llm_call("chat", "glm-4.5")
        async def my_api_call(...):
            return client.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            request_params = kwargs.copy()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                LLMCallLogger.log_api_call(
                    api_type=api_type,
                    model=model,
                    request_params=request_params,
                    response=result,
                    duration=duration
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                LLMCallLogger.log_api_call(
                    api_type=api_type,
                    model=model,
                    request_params=request_params,
                    error=e,
                    duration=duration
                )
                
                raise
        
        return wrapper
    return decorator


__all__ = [
    "LLMCallLogger",
    "StreamContentAccumulator",
    "log_llm_call"
]

