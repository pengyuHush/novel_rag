"""
置信度计算器
基于多个因素计算查询答案的置信度
"""

from typing import List, Dict, Optional
import re
from app.models.schemas import Confidence


class ConfidenceCalculator:
    """置信度计算器"""
    
    # 不确定词列表
    UNCERTAIN_WORDS = [
        '可能', '也许', '大概', '似乎', '好像', '应该',
        '或许', '估计', '猜测', '不确定', '不清楚', '未知'
    ]
    
    # 模糊词列表
    VAGUE_WORDS = [
        '一些', '某些', '若干', '多个', '少量', '大量',
        '很多', '不少', '较多', '较少'
    ]
    
    def calculate_confidence(
        self,
        answer: str,
        citations: List[Dict],
        reranked_chunks: List[Dict],
        retrieved_count: int = 0
    ) -> Confidence:
        """
        计算答案的置信度
        
        Args:
            answer: 生成的答案
            citations: 引用列表
            reranked_chunks: 重排后的文档块
            retrieved_count: 检索到的文档数量
            
        Returns:
            Confidence: 置信度等级（high/medium/low）
        """
        score = 0.0
        max_score = 10.0
        
        # 因素1: 引用质量（权重: 30%）
        citation_score = self._calculate_citation_score(citations, reranked_chunks)
        score += citation_score * 3.0
        
        # 因素2: 答案完整性（权重: 25%）
        answer_quality_score = self._calculate_answer_quality(answer)
        score += answer_quality_score * 2.5
        
        # 因素3: 检索召回率（权重: 20%）
        retrieval_score = self._calculate_retrieval_score(citations, retrieved_count)
        score += retrieval_score * 2.0
        
        # 因素4: 语言确定性（权重: 25%）
        certainty_score = self._calculate_certainty_score(answer)
        score += certainty_score * 2.5
        
        # 计算最终得分百分比
        confidence_percentage = (score / max_score) * 100
        
        # 转换为置信度等级
        if confidence_percentage >= 75:
            return Confidence.HIGH
        elif confidence_percentage >= 50:
            return Confidence.MEDIUM
        else:
            return Confidence.LOW
    
    def _calculate_citation_score(
        self,
        citations: List[Dict],
        reranked_chunks: List[Dict]
    ) -> float:
        """
        计算引用质量得分（0-1）
        
        基于：
        - 引用数量
        - 引用的相关性分数
        """
        if not citations:
            return 0.0
        
        score = 0.0
        
        # 引用数量得分（0-0.5）
        citation_count = len(citations)
        if citation_count >= 5:
            score += 0.5
        elif citation_count >= 3:
            score += 0.4
        elif citation_count >= 1:
            score += 0.3
        
        # 引用相关性得分（0-0.5）
        if reranked_chunks:
            # 取前5个chunk的平均分数
            top_chunks = reranked_chunks[:min(5, len(reranked_chunks))]
            scores = [chunk.get('score', 0.0) for chunk in top_chunks]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            # 归一化到0-0.5范围
            score += min(avg_score * 0.5, 0.5)
        
        return min(score, 1.0)
    
    def _calculate_answer_quality(self, answer: str) -> float:
        """
        计算答案质量得分（0-1）
        
        基于：
        - 答案长度（适中为好）
        - 结构完整性（有开头、正文、结尾）
        """
        if not answer:
            return 0.0
        
        score = 0.0
        length = len(answer)
        
        # 长度得分（0-0.6）
        if 100 <= length <= 1000:
            score += 0.6  # 理想长度
        elif 50 <= length < 100:
            score += 0.4  # 较短但可接受
        elif 1000 < length <= 2000:
            score += 0.5  # 较长但可接受
        elif length < 50:
            score += 0.2  # 过短
        else:
            score += 0.3  # 过长
        
        # 结构完整性得分（0-0.4）
        # 检查是否有合理的段落结构
        paragraphs = [p.strip() for p in answer.split('\n') if p.strip()]
        if len(paragraphs) >= 2:
            score += 0.2  # 有多个段落
        
        # 检查是否有结论性语句
        conclusion_patterns = [
            r'总之', r'综上', r'因此', r'所以', r'综合.*来看',
            r'可以.*得出', r'说明', r'表明'
        ]
        for pattern in conclusion_patterns:
            if re.search(pattern, answer):
                score += 0.2
                break
        
        return min(score, 1.0)
    
    def _calculate_retrieval_score(
        self,
        citations: List[Dict],
        retrieved_count: int
    ) -> float:
        """
        计算检索召回率得分（0-1）
        
        基于：
        - 检索到的文档数量
        - 引用占比
        """
        if retrieved_count == 0:
            return 0.5  # 默认中等
        
        score = 0.0
        
        # 检索数量得分（0-0.6）
        if retrieved_count >= 20:
            score += 0.6
        elif retrieved_count >= 10:
            score += 0.5
        elif retrieved_count >= 5:
            score += 0.4
        else:
            score += 0.3
        
        # 引用率得分（0-0.4）
        if citations and retrieved_count > 0:
            citation_rate = len(citations) / retrieved_count
            if citation_rate >= 0.3:
                score += 0.4
            elif citation_rate >= 0.2:
                score += 0.3
            elif citation_rate >= 0.1:
                score += 0.2
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_certainty_score(self, answer: str) -> float:
        """
        计算语言确定性得分（0-1）
        
        基于：
        - 不确定词的数量
        - 模糊词的数量
        - 明确性表达
        """
        if not answer:
            return 0.5
        
        score = 1.0
        
        # 检查不确定词（每个-0.2，最多-0.5）
        uncertain_count = 0
        for word in self.UNCERTAIN_WORDS:
            uncertain_count += answer.count(word)
        
        penalty = min(uncertain_count * 0.1, 0.5)
        score -= penalty
        
        # 检查模糊词（每个-0.1，最多-0.3）
        vague_count = 0
        for word in self.VAGUE_WORDS:
            vague_count += answer.count(word)
        
        penalty = min(vague_count * 0.05, 0.3)
        score -= penalty
        
        # 检查明确性表达（加分）
        definite_patterns = [
            r'确实', r'明确', r'清楚', r'显然', r'毫无疑问',
            r'事实上', r'实际上', r'具体来说'
        ]
        for pattern in definite_patterns:
            if re.search(pattern, answer):
                score += 0.1
                break
        
        return max(0.0, min(score, 1.0))
    
    def get_confidence_details(
        self,
        answer: str,
        citations: List[Dict],
        reranked_chunks: List[Dict],
        retrieved_count: int = 0
    ) -> Dict:
        """
        获取置信度计算的详细信息（用于调试）
        
        Returns:
            Dict: 包含各项得分的详细信息
        """
        citation_score = self._calculate_citation_score(citations, reranked_chunks)
        answer_quality_score = self._calculate_answer_quality(answer)
        retrieval_score = self._calculate_retrieval_score(citations, retrieved_count)
        certainty_score = self._calculate_certainty_score(answer)
        
        total_score = (
            citation_score * 3.0 +
            answer_quality_score * 2.5 +
            retrieval_score * 2.0 +
            certainty_score * 2.5
        )
        confidence_percentage = (total_score / 10.0) * 100
        
        return {
            'citation_score': citation_score,
            'answer_quality_score': answer_quality_score,
            'retrieval_score': retrieval_score,
            'certainty_score': certainty_score,
            'total_score': total_score,
            'confidence_percentage': confidence_percentage,
            'confidence_level': self.calculate_confidence(
                answer, citations, reranked_chunks, retrieved_count
            ).value
        }


# 全局实例
_confidence_calculator: Optional[ConfidenceCalculator] = None


def get_confidence_calculator() -> ConfidenceCalculator:
    """获取置信度计算器实例"""
    global _confidence_calculator
    if _confidence_calculator is None:
        _confidence_calculator = ConfidenceCalculator()
    return _confidence_calculator

