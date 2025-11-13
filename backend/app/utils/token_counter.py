"""
Token计数器

使用tiktoken库精确计算Token数量
"""

import logging
from typing import List, Dict, Optional
import tiktoken

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token计数器"""
    
    def __init__(self):
        """初始化Token计数器"""
        # 智谱AI使用的tokenizer（与OpenAI兼容）
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.info("✅ Token计数器初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ tiktoken初始化失败，使用估算方法: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """
        计算单个文本的Token数量
        
        Args:
            text: 文本内容
        
        Returns:
            int: Token数量
        """
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.warning(f"⚠️ Token计数失败，使用估算: {e}")
        
        # 备用估算方法：中文约0.5 token/字，英文约0.25 token/字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 0.5 + other_chars * 0.25)
    
    def count_messages_tokens(
        self,
        messages: List[Dict[str, str]],
        model: str = "glm-4"
    ) -> int:
        """
        计算消息列表的Token数量（Chat API格式）
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
        
        Returns:
            int: Token数量
        """
        total_tokens = 0
        
        # 每条消息的固定开销（角色标记等）
        tokens_per_message = 3
        tokens_per_name = 1
        
        for message in messages:
            total_tokens += tokens_per_message
            
            for key, value in message.items():
                if isinstance(value, str):
                    total_tokens += self.count_tokens(value)
                    if key == "name":
                        total_tokens += tokens_per_name
        
        # API调用的固定开销
        total_tokens += 3
        
        return total_tokens
    
    def estimate_embedding_tokens(self, texts: List[str]) -> int:
        """
        估算向量化的Token消耗
        
        Args:
            texts: 文本列表
        
        Returns:
            int: 总Token数量
        """
        return sum(self.count_tokens(text) for text in texts)
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "GLM-4.5-Air"
    ) -> float:
        """
        计算Token成本（元）
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            model: 模型名称
        
        Returns:
            float: 成本（元）
        """
        from app.core.config import settings
        
        # 获取模型价格
        model_meta = settings.model_metadata.get(model, {})
        price_input = model_meta.get('price_input', 0.001)  # 默认0.001元/1K tokens
        price_output = model_meta.get('price_output', 0.001)
        
        # 计算成本（价格是每1000 tokens）
        cost = (input_tokens * price_input + output_tokens * price_output) / 1000.0
        
        return cost
    
    def get_token_stats_summary(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "GLM-4.5-Air"
    ) -> Dict:
        """
        获取Token统计摘要
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            model: 模型名称
        
        Returns:
            Dict: 包含total_tokens、cost等信息的摘要
        """
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'cost': round(cost, 6),
            'model': model
        }


# 全局实例
_token_counter: Optional[TokenCounter] = None


def get_token_counter() -> TokenCounter:
    """获取全局Token计数器实例（单例）"""
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter()
    return _token_counter


def count_tokens(text: str) -> int:
    """
    便捷方法：计算文本Token数量
    
    Args:
        text: 文本内容
    
    Returns:
        int: Token数量
    """
    counter = get_token_counter()
    return counter.count_tokens(text)
