"""
智能查询路由模块

根据查询类型自动选择最佳的RAG策略：
- 对话类查询：优先短块+引号权重
- 分析类查询：合并相邻块
- 事实类查询：标准RAG流程
"""

from typing import Literal
from enum import Enum
import re


class QueryType(str, Enum):
    """查询类型枚举"""
    DIALOGUE = "dialogue"      # 对话类："XX说了什么"
    ANALYSIS = "analysis"      # 分析类："XX为什么要YY"，"XX如何演变"
    FACT = "fact"             # 事实类："XX是谁"，"XX在哪"


class QueryRouter:
    """智能查询路由器"""
    
    # 对话类查询关键词
    DIALOGUE_KEYWORDS = [
        "说", "讲", "提到", "回答", "问", "告诉", "谈",
        "说话", "对话", "聊天", "交流", "沟通", "说道",
        "问道", "答道", "喊道", "叫道", "笑道", "哭着说"
    ]
    
    # 分析类查询关键词
    ANALYSIS_KEYWORDS = [
        "为什么", "怎么", "如何", "原因", "动机", "目的",
        "演变", "变化", "发展", "转变", "改变", "成长",
        "分析", "解释", "理解", "探讨", "研究",
        "关系", "影响", "意义", "作用", "价值"
    ]
    
    # 演变分析关键词（分析类的子集）
    EVOLUTION_KEYWORDS = [
        "演变", "变化", "发展", "转变", "改变", "成长",
        "从...到", "前期", "中期", "后期", "早期", "晚期",
        "最初", "最后", "开始", "结束", "经历", "历程"
    ]
    
    def __init__(self):
        pass
    
    def classify_query(self, query: str) -> QueryType:
        """
        分类查询类型
        
        Args:
            query: 用户查询文本
            
        Returns:
            QueryType: 查询类型枚举
        """
        query_lower = query.lower()
        
        # 1. 检测对话类查询
        if self._is_dialogue_query(query_lower):
            return QueryType.DIALOGUE
        
        # 2. 检测分析类查询
        if self._is_analysis_query(query_lower):
            return QueryType.ANALYSIS
        
        # 3. 默认事实类查询
        return QueryType.FACT
    
    def _is_dialogue_query(self, query: str) -> bool:
        """
        判断是否为对话类查询
        
        对话类查询特征：
        - 包含对话关键词："说"、"讲"、"提到"等
        - 通常询问具体的对话内容
        - 答案通常包含引号或对话标记
        """
        for keyword in self.DIALOGUE_KEYWORDS:
            if keyword in query:
                return True
        
        # 检测特殊模式："XXX对YYY说"，"XXX跟YYY讲"
        dialogue_patterns = [
            r'对.{0,5}说',
            r'跟.{0,5}讲',
            r'向.{0,5}提',
            r'告诉.{0,5}',
        ]
        for pattern in dialogue_patterns:
            if re.search(pattern, query):
                return True
        
        return False
    
    def _is_analysis_query(self, query: str) -> bool:
        """
        判断是否为分析类查询
        
        分析类查询特征：
        - 包含分析关键词："为什么"、"如何"、"演变"等
        - 需要推理和综合多个信息
        - 答案通常跨越多个章节
        """
        for keyword in self.ANALYSIS_KEYWORDS:
            if keyword in query:
                return True
        
        # 检测疑问句模式
        question_patterns = [
            r'为何',
            r'缘何',
            r'因何',
            r'凭什么',
        ]
        for pattern in question_patterns:
            if re.search(pattern, query):
                return True
        
        return False
    
    def is_evolution_query(self, query: str) -> bool:
        """
        判断是否为演变分析类查询（分析类的特殊情况）
        
        演变类查询特征：
        - 关注时间线变化
        - 需要时序分段检索
        - 答案需要按时间顺序组织
        """
        query_lower = query.lower()
        
        for keyword in self.EVOLUTION_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # 检测时序模式
        temporal_patterns = [
            r'从.+到.+',
            r'(前|中|后|早|晚)期',
            r'(最初|开始).+(最后|结束)',
            r'(如何|怎么).+(变|转|改)',
        ]
        for pattern in temporal_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def get_retrieval_strategy(self, query_type: QueryType) -> dict:
        """
        根据查询类型返回推荐的检索策略参数
        
        Args:
            query_type: 查询类型
            
        Returns:
            dict: 策略参数
                - top_k: 检索的文档数量
                - chunk_merge: 是否合并相邻块
                - quote_weight: 引号内容权重加成
                - prefer_dialogue: 是否优先对话块
        """
        if query_type == QueryType.DIALOGUE:
            return {
                "top_k": 15,              # 对话块较短，增加检索数量
                "chunk_merge": False,     # 不合并，保留对话完整性
                "quote_weight": 1.5,      # 引号内容权重x1.5
                "prefer_dialogue": True,  # 优先对话块
                "filter_metadata": {"has_dialogue": True},  # 过滤对话块
            }
        
        elif query_type == QueryType.ANALYSIS:
            return {
                "top_k": 20,              # 分析需要更多上下文
                "chunk_merge": True,      # 合并相邻块获取完整语境
                "quote_weight": 1.0,      # 无特殊权重
                "prefer_dialogue": False,
                "filter_metadata": None,
            }
        
        else:  # FACT
            return {
                "top_k": 10,              # 标准检索数量
                "chunk_merge": False,     # 标准块大小
                "quote_weight": 1.0,
                "prefer_dialogue": False,
                "filter_metadata": None,
            }


# 全局路由器实例
query_router = QueryRouter()


def classify_query(query: str) -> QueryType:
    """便捷函数：分类查询"""
    return query_router.classify_query(query)


def get_retrieval_strategy(query_type: QueryType) -> dict:
    """便捷函数：获取检索策略"""
    return query_router.get_retrieval_strategy(query_type)


def is_evolution_query(query: str) -> bool:
    """便捷函数：判断是否为演变查询"""
    return query_router.is_evolution_query(query)

