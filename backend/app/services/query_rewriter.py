"""
查询改写服务 - Query Rewriting Service

基于LLM的智能查询改写，提升检索召回率和精度
- 对话类：添加"说""道""台词"等关键词
- 分析类：添加"原因""过程""影响"等关键词，明确因果关系
- 事实类：添加同义词，明确查询意图
"""

import logging
from typing import Optional, Dict
from app.services.zhipu_client import get_zhipu_client
from app.services.query_router import QueryType, query_router
from app.core.trace_logger import get_trace_logger

logger = logging.getLogger(__name__)
trace_logger = get_trace_logger()


class QueryRewriter:
    """查询改写器"""
    
    def __init__(self):
        """初始化查询改写器"""
        self.zhipu_client = get_zhipu_client()
        # 使用免费模型GLM-4-Flash进行查询改写
        self.rewrite_model = "GLM-4.5-Flash"
        logger.info("✅ 查询改写器初始化完成")
    
    def rewrite_query(
        self,
        original_query: str,
        query_type: Optional[QueryType] = None,
        enable: bool = True,
        query_id: Optional[int] = None
    ) -> Dict[str, str]:
        """
        改写查询以提升检索效果
        
        Args:
            original_query: 原始查询文本
            query_type: 查询类型（如不提供则自动检测）
            enable: 是否启用查询改写
            query_id: 查询ID（用于日志记录）
        
        Returns:
            Dict: {
                "original": 原始查询,
                "rewritten": 改写后的查询,
                "query_type": 查询类型,
                "rewrite_applied": 是否应用了改写
            }
        """
        result = {
            "original": original_query,
            "rewritten": original_query,
            "query_type": None,
            "rewrite_applied": False
        }
        
        # 如果未启用改写，直接返回原始查询
        if not enable:
            logger.info("🔄 查询改写未启用，使用原始查询")
            trace_logger.trace_step(
                query_id=query_id,
                step_name="查询改写",
                emoji="🔄",
                input_data=original_query,
                output_data="改写功能未启用",
                status="skipped"
            )
            return result
        
        # 检测查询类型
        if query_type is None:
            query_type = query_router.classify_query(original_query)
        
        result["query_type"] = query_type.value
        
        try:
            # 根据查询类型选择改写策略
            rewritten = self._rewrite_by_type(original_query, query_type)
            
            # 如果改写成功且与原查询不同
            if rewritten and rewritten.strip() != original_query.strip():
                result["rewritten"] = rewritten.strip()
                result["rewrite_applied"] = True
                logger.info(f"✅ 查询改写成功 [{query_type.value}]")
                logger.info(f"   原始: {original_query}")
                logger.info(f"   改写: {rewritten.strip()}")
                
                # 详细日志
                trace_logger.trace_step(
                    query_id=query_id,
                    step_name="查询改写",
                    emoji="🔄",
                    input_data={
                        "原始查询": original_query,
                        "查询类型": query_type.value,
                        "使用模型": self.rewrite_model
                    },
                    output_data={
                        "改写后查询": rewritten.strip(),
                        "改写策略": self._get_strategy_description(query_type)
                    },
                    status="success"
                )
            else:
                logger.info(f"ℹ️ 查询无需改写或改写失败，使用原始查询")
                
                # 详细日志
                trace_logger.trace_step(
                    query_id=query_id,
                    step_name="查询改写",
                    emoji="🔄",
                    input_data={
                        "原始查询": original_query,
                        "查询类型": query_type.value
                    },
                    output_data="改写后与原查询相同，跳过改写",
                    status="skipped"
                )
        
        except Exception as e:
            logger.warning(f"⚠️ 查询改写失败，使用原始查询: {e}")
            
            # 详细日志
            trace_logger.trace_step(
                query_id=query_id,
                step_name="查询改写",
                emoji="🔄",
                input_data=original_query,
                output_data=f"改写失败: {str(e)}",
                status="failed"
            )
            # 降级处理：返回原始查询
        
        return result
    
    def _get_strategy_description(self, query_type: QueryType) -> str:
        """获取改写策略描述"""
        descriptions = {
            QueryType.DIALOGUE: '对话类：添加"说""道""台词"等关键词',
            QueryType.ANALYSIS: '分析类：添加"原因""过程""影响"等关键词，明确因果关系',
            QueryType.FACT: "事实类：添加同义词，明确查询意图"
        }
        return descriptions.get(query_type, "未知策略")
    
    def _rewrite_by_type(self, query: str, query_type: QueryType) -> str:
        """
        根据查询类型改写查询
        
        Args:
            query: 原始查询
            query_type: 查询类型
        
        Returns:
            str: 改写后的查询
        """
        if query_type == QueryType.DIALOGUE:
            return self._rewrite_dialogue_query(query)
        elif query_type == QueryType.ANALYSIS:
            return self._rewrite_analysis_query(query)
        else:  # FACT
            return self._rewrite_fact_query(query)
    
    def _rewrite_dialogue_query(self, query: str) -> str:
        """
        改写对话类查询
        
        策略：
        - 添加"说""道""台词"等关键词
        - 明确对话场景和说话者
        - 保留核心语义
        """
        prompt = f"""你是查询优化专家。请将用户的对话类查询改写为更利于检索小说对话内容的形式。

查询类型：对话类（询问角色的对话、台词）

原始查询：{query}

改写要求：
1. 保留核心语义和关键信息（人物、场景）
2. 添加对话相关的关键词，如："说"、"道"、"回答"、"讲"、"台词"、"对话"等
3. 明确对话的上下文（如果原查询有提及）
4. 改写后的查询应该更容易匹配小说中的对话场景
5. 保持查询简洁，不要过度扩展

示例1：
原始："张无忌和赵敏怎么认识的"
改写："张无忌和赵敏初次见面时说了什么 两人的对话"

示例2：
原始："令狐冲在思过崖学到了什么武功"
改写："令狐冲在思过崖提到学了什么武功 说过的话"

请直接输出改写后的查询，不要有其他解释："""

        try:
            response = self.zhipu_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.rewrite_model,
                temperature=0.3,  # 较低温度保证稳定性
                max_tokens=200
            )
            
            rewritten = response["content"].strip()
            # 移除可能的引号包装
            rewritten = rewritten.strip('"\'')
            return rewritten
        
        except Exception as e:
            logger.error(f"❌ 对话类查询改写失败: {e}")
            return query
    
    def _rewrite_analysis_query(self, query: str) -> str:
        """
        改写分析类查询
        
        策略：
        - 添加"原因""过程""影响"等关键词
        - 明确时间、因果关系
        - 扩展同义词和相关概念
        """
        prompt = f"""你是查询优化专家。请将用户的分析类查询改写为更利于检索小说情节和因果关系的形式。

查询类型：分析类（需要综合分析、推理的问题）

原始查询：{query}

改写要求：
1. 保留核心语义和关键信息（人物、事件）
2. 添加分析相关的关键词，如："原因"、"过程"、"结果"、"影响"、"变化"、"发展"等
3. 明确因果关系和时间顺序（如果原查询有提及）
4. 可以适当添加同义词或相关概念
5. 改写后的查询应该更容易匹配小说中的情节分析和因果描述
6. 保持查询相对简洁

示例1：
原始："为什么张无忌成为明教教主"
改写："张无忌成为明教教主的原因和过程 如何当上教主的经过"

示例2：
原始："令狐冲和岳灵珊的感情"
改写："令狐冲和岳灵珊感情发展变化过程 从相爱到分离的原因"

请直接输出改写后的查询，不要有其他解释："""

        try:
            response = self.zhipu_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.rewrite_model,
                temperature=0.3,
                max_tokens=200
            )
            
            rewritten = response["content"].strip()
            rewritten = rewritten.strip('"\'')
            return rewritten
        
        except Exception as e:
            logger.error(f"❌ 分析类查询改写失败: {e}")
            return query
    
    def _rewrite_fact_query(self, query: str) -> str:
        """
        改写事实类查询
        
        策略：
        - 添加同义词
        - 明确查询意图
        - 补充相关上下文
        """
        prompt = f"""你是查询优化专家。请将用户的事实类查询改写为更利于检索小说具体信息的形式。

查询类型：事实类（询问具体事实、情节细节）

原始查询：{query}

改写要求：
1. 保留核心语义和关键信息
2. 添加同义词或相关表达方式
3. 明确查询对象（人物、地点、事件等）
4. 改写后的查询应该更容易匹配小说中的具体描述
5. 保持查询简洁明确

示例1：
原始："张三丰的武功"
改写："张三丰的武功实力 会什么武学招式"

示例2：
原始："华山派在哪里"
改写："华山派的地点位置 山门所在"

请直接输出改写后的查询，不要有其他解释："""

        try:
            response = self.zhipu_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.rewrite_model,
                temperature=0.3,
                max_tokens=200
            )
            
            rewritten = response["content"].strip()
            rewritten = rewritten.strip('"\'')
            return rewritten
        
        except Exception as e:
            logger.error(f"❌ 事实类查询改写失败: {e}")
            return query


# 全局查询改写器实例
_query_rewriter: Optional[QueryRewriter] = None


def get_query_rewriter() -> QueryRewriter:
    """获取全局查询改写器实例（单例）"""
    global _query_rewriter
    if _query_rewriter is None:
        _query_rewriter = QueryRewriter()
    return _query_rewriter

