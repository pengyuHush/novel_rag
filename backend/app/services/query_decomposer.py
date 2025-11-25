"""
查询分解服务

负责将复杂查询智能分解为多个子查询，提升检索覆盖率
"""

import logging
import json
import re
from typing import List, Optional, Dict, Tuple
from app.services.zhipu_client import ZhipuAIClient
from app.core.trace_logger import get_trace_logger

logger = logging.getLogger(__name__)
trace_logger = get_trace_logger()


class QueryDecomposer:
    """
    查询分解器
    
    功能：
    1. 判断查询是否需要分解（复杂度检测）
    2. 使用LLM智能分解查询为多个子查询
    3. 验证和清理子查询
    """
    
    # 枚举关键词（提示查询包含多个信息维度）
    ENUMERATION_KEYWORDS = [
        "包含", "包括", "以及", "和", "还有", "另外",
        "、", "，", "；", "等", "等等"
    ]
    
    # 多问句标记
    QUESTION_MARKERS = [
        "是谁", "是什么", "在哪里", "怎么样", "为什么",
        "如何", "哪些", "多少", "几个", "什么时候"
    ]
    
    def __init__(
        self,
        zhipu_client: ZhipuAIClient,
        max_subqueries: int = 5,
        complexity_threshold: int = 30,
        model: str = "glm-4-flash"
    ):
        """
        初始化查询分解器
        
        Args:
            zhipu_client: 智谱AI客户端
            max_subqueries: 最多分解为几个子查询
            complexity_threshold: 查询字数阈值
            model: 使用的LLM模型
        """
        self.zhipu_client = zhipu_client
        self.max_subqueries = max_subqueries
        self.complexity_threshold = complexity_threshold
        self.model = model
    
    def should_decompose(self, query: str) -> Tuple[bool, str]:
        """
        判断查询是否需要分解
        
        Args:
            query: 查询文本
            
        Returns:
            Tuple[bool, str]: (是否需要分解, 判断原因)
        """
        logger.info(f"🔧 [DEBUG] should_decompose被调用: query='{query}', threshold={self.complexity_threshold}")
        
        # 1. 检查查询长度
        query_length = len(query)
        logger.info(f"🔧 [DEBUG] 检查1 - 查询长度: {query_length} (阈值={self.complexity_threshold})")
        if query_length > self.complexity_threshold:
            reason = f"查询字数超过阈值（{query_length} > {self.complexity_threshold}）"
            logger.info(f"✅ [DEBUG] 触发分解: {reason}")
            return True, reason
        
        # 2. 检查枚举关键词
        enumeration_count = sum(1 for kw in self.ENUMERATION_KEYWORDS if kw in query)
        logger.info(f"🔧 [DEBUG] 检查2 - 枚举关键词数量: {enumeration_count} (需要>=2)")
        if enumeration_count >= 2:
            reason = f"包含{enumeration_count}个枚举关键词"
            logger.info(f"✅ [DEBUG] 触发分解: {reason}")
            return True, reason
        
        # 3. 检查多个问句
        question_count = sum(1 for marker in self.QUESTION_MARKERS if marker in query)
        logger.info(f"🔧 [DEBUG] 检查3 - 疑问词数量: {question_count} (需要>=2)")
        if question_count >= 2:
            reason = f"包含{question_count}个不同的疑问词"
            logger.info(f"✅ [DEBUG] 触发分解: {reason}")
            return True, reason
        
        # 4. 检查是否包含明确的列举结构
        has_list_structure = bool(re.search(r'[，、；].{2,}[，、；].{2,}', query))
        logger.info(f"🔧 [DEBUG] 检查4 - 列举结构: {has_list_structure}")
        if has_list_structure:
            reason = "包含明确的列举结构"
            logger.info(f"✅ [DEBUG] 触发分解: {reason}")
            return True, reason
        
        reason = "查询相对简单"
        logger.info(f"❌ [DEBUG] 不触发分解: {reason}")
        return False, reason
    
    def decompose_query(
        self,
        query: str,
        query_id: Optional[int] = None
    ) -> List[str]:
        """
        使用LLM分解查询为多个子查询
        
        Args:
            query: 原始查询
            query_id: 查询ID（用于日志）
            
        Returns:
            List[str]: 子查询列表（如果不需要分解或失败，返回空列表）
        """
        # 先判断是否需要分解
        should_decompose, reason = self.should_decompose(query)
        
        if not should_decompose:
            logger.info(f"🔍 查询无需分解: {reason}")
            if query_id:
                trace_logger.trace_step(
                    query_id=query_id,
                    step_name="查询分解",
                    emoji="🔍",
                    input_data=query,
                    output_data=f"无需分解: {reason}",
                    status="skipped"
                )
            return []
        
        logger.info(f"🔨 查询需要分解: {reason}")
        
        # 构建LLM Prompt
        prompt = self._build_decomposition_prompt(query)
        
        try:
            # 调用LLM
            response = self.zhipu_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )
            
            content = response["content"].strip()
            logger.debug(f"LLM分解结果: {content}")
            
            # 解析JSON结果
            sub_queries = self._parse_subqueries(content)
            
            # 验证和清理
            sub_queries = self._validate_subqueries(sub_queries, query)
            
            if len(sub_queries) > 1:
                logger.info(f"✅ 查询分解成功: {len(sub_queries)}个子查询")
                logger.info(f"   子查询: {sub_queries}")
                
                # 记录详细日志
                if query_id:
                    trace_logger.trace_step(
                        query_id=query_id,
                        step_name="查询分解",
                        emoji="🔨",
                        input_data={
                            "原始查询": query,
                            "判断依据": reason,
                            "使用模型": self.model
                        },
                        output_data={
                            "子查询数量": len(sub_queries),
                            "子查询列表": sub_queries
                        },
                        status="success"
                    )
                
                return sub_queries
            else:
                logger.info("ℹ️ LLM判断查询无需分解")
                if query_id:
                    trace_logger.trace_step(
                        query_id=query_id,
                        step_name="查询分解",
                        emoji="ℹ️",
                        input_data=query,
                        output_data="LLM判断无需分解",
                        status="skipped"
                    )
                return []
        
        except Exception as e:
            logger.error(f"❌ 查询分解失败: {e}")
            if query_id:
                trace_logger.trace_step(
                    query_id=query_id,
                    step_name="查询分解",
                    emoji="❌",
                    input_data=query,
                    output_data=f"分解失败: {str(e)}",
                    status="failed"
                )
            return []
    
    def _build_decomposition_prompt(self, query: str) -> str:
        """构建查询分解的Prompt"""
        prompt = f"""你是查询分解专家。请将复杂查询拆分为多个独立的子查询。

原始查询：{query}

要求：
1. 每个子查询应该独立、明确、可单独回答
2. 保留原查询的核心实体和上下文
3. 最多拆分为{self.max_subqueries}个子查询
4. 如果查询本身已经足够简单（只包含单一信息维度），返回空列表
5. 子查询应该覆盖原查询的所有信息维度
6. 输出纯JSON格式的字符串数组，不要有其他文字

输出格式（纯JSON）：
["子查询1", "子查询2", "子查询3"]

示例1：
原始查询："介绍李凡的身世，包含他的父母、家族、师傅、师门以及现在的状况"
输出：["李凡的父母是谁", "李凡的家族背景", "李凡的师傅和师门", "李凡现在的状况"]

示例2：
原始查询："李凡的母亲是谁"
输出：[]

示例3：
原始查询："描述张三丰的武功和他与张无忌的关系"
输出：["张三丰的武功实力", "张三丰和张无忌的关系"]

请直接输出JSON格式的子查询数组："""
        
        return prompt
    
    def _parse_subqueries(self, content: str) -> List[str]:
        """
        解析LLM返回的子查询列表
        
        支持多种格式：
        - 纯JSON数组：["查询1", "查询2"]
        - 带代码块的JSON：```json\n["查询1", "查询2"]\n```
        - 带序号的列表：1. 查询1\n2. 查询2
        """
        # 尝试提取JSON内容
        json_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if json_match:
            try:
                sub_queries = json.loads(json_match.group())
                if isinstance(sub_queries, list):
                    return [str(q).strip() for q in sub_queries if q]
            except json.JSONDecodeError:
                pass
        
        # 尝试解析带序号的列表格式
        lines = content.split('\n')
        sub_queries = []
        for line in lines:
            line = line.strip()
            # 匹配 "1. 查询" 或 "- 查询" 格式
            match = re.match(r'^[\d\-\*]+[\.\)]\s*(.+)$', line)
            if match:
                sub_queries.append(match.group(1).strip())
        
        if sub_queries:
            return sub_queries
        
        # 如果都失败了，尝试按逗号分割（最后的fallback）
        if ',' in content or '，' in content:
            parts = re.split(r'[,，]', content)
            return [p.strip().strip('"\'') for p in parts if p.strip()]
        
        logger.warning(f"无法解析子查询: {content}")
        return []
    
    def _validate_subqueries(self, sub_queries: List[str], original_query: str) -> List[str]:
        """
        验证和清理子查询
        
        1. 去除空字符串
        2. 去重
        3. 限制最大数量
        4. 过滤过短或无意义的查询
        """
        # 去除空字符串和过短的查询
        valid_queries = []
        for q in sub_queries:
            q = q.strip().strip('"\'')
            if len(q) >= 3 and q not in valid_queries:  # 至少3个字符且不重复
                valid_queries.append(q)
        
        # 限制最大数量
        if len(valid_queries) > self.max_subqueries:
            logger.warning(f"子查询数量超过限制，截断为前{self.max_subqueries}个")
            valid_queries = valid_queries[:self.max_subqueries]
        
        # 如果所有子查询都与原查询相同，返回空（说明无需分解）
        if len(valid_queries) == 1 and valid_queries[0] == original_query:
            return []
        
        return valid_queries

