"""
Token计数工具
用于估算文本的Token数量
"""

import tiktoken
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token计数器"""
    
    def __init__(self, model: str = "gpt-4"):
        """
        初始化Token计数器
        
        Args:
            model: 模型名称（用于选择tokenizer）
        """
        try:
            # 智谱AI的GLM系列模型使用类似GPT-4的tokenizer
            self.encoding = tiktoken.encoding_for_model(model)
            logger.debug(f"✅ Token计数器初始化完成 (model: {model})")
        except KeyError:
            # 如果模型不支持，使用cl100k_base编码（GPT-4默认）
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"⚠️ 模型 '{model}' 不支持，使用默认编码")
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的Token数量
        
        Args:
            text: 文本内容
        
        Returns:
            int: Token数量
        """
        if not text:
            return 0
        
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"❌ Token计数失败: {e}")
            # 回退到简单估算：平均每个中文字符约1.5 token
            return int(len(text) * 1.5)
    
    def count_messages_tokens(self, messages: List[dict]) -> int:
        """
        计算消息列表的Token数量（包含格式化开销）
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
        
        Returns:
            int: Token数量
        """
        num_tokens = 0
        
        for message in messages:
            # 每条消息的基础开销（role、content等）
            num_tokens += 4  # 每条消息约4个token的格式化开销
            
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += self.count_tokens(value)
                # role字段约1个token
                if key == "role":
                    num_tokens += 1
        
        # 对话的整体开销
        num_tokens += 2
        
        return num_tokens
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "glm-4"
    ) -> float:
        """
        估算API调用成本（人民币）
        
        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            model: 模型名称
        
        Returns:
            float: 估算成本（元）
        """
        # 智谱AI定价（2024年）
        pricing = {
            "glm-4-flash": {"input": 0.1, "output": 0.1},
            "glm-4": {"input": 5.0, "output": 5.0},
            "glm-4-plus": {"input": 50.0, "output": 50.0},
            "glm-4-5": {"input": 10.0, "output": 10.0},
            "glm-4-6": {"input": 15.0, "output": 15.0},
            "embedding-3": {"input": 0.5, "output": 0}
        }
        
        model_pricing = pricing.get(model, pricing["glm-4"])
        
        input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def split_text_by_tokens(
        self,
        text: str,
        max_tokens: int,
        overlap: int = 0
    ) -> List[str]:
        """
        按Token数分割文本
        
        Args:
            text: 文本内容
            max_tokens: 每块最大token数
            overlap: 重叠token数
        
        Returns:
            List[str]: 分割后的文本块
        """
        if not text:
            return []
        
        try:
            # 编码文本
            tokens = self.encoding.encode(text)
            
            # 分块
            chunks = []
            start = 0
            
            while start < len(tokens):
                # 确定结束位置
                end = min(start + max_tokens, len(tokens))
                
                # 解码当前块
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoding.decode(chunk_tokens)
                chunks.append(chunk_text)
                
                # 移动到下一块（考虑重叠）
                start = end - overlap
                if start >= len(tokens):
                    break
            
            logger.debug(f"✅ 文本分块完成: {len(chunks)} 块")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ 文本分块失败: {e}")
            # 回退到简单分割
            chunk_size = int(max_tokens / 1.5)  # 估算字符数
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# 全局Token计数器实例
_token_counter: Optional[TokenCounter] = None


def get_token_counter(model: str = "gpt-4") -> TokenCounter:
    """获取全局Token计数器实例（单例）"""
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter(model=model)
    return _token_counter

