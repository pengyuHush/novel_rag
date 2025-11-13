"""
证据质量评分器

三维评分：时效性、具体性、权威性
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.database import Chapter, Novel

logger = logging.getLogger(__name__)


class EvidenceScorer:
    """证据质量评分器"""
    
    def __init__(self):
        """初始化证据评分器"""
        logger.info("✅ 证据评分器初始化完成")
    
    def score_evidence(
        self,
        db: Session,
        novel_id: int,
        evidence: Dict,
        query_context: Optional[Dict] = None
    ) -> Dict:
        """
        对单条证据进行三维评分
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            evidence: 证据字典
            query_context: 查询上下文（可选）
        
        Returns:
            Dict: 评分结果
                - timeliness: 时效性评分 (0-1)
                - specificity: 具体性评分 (0-1)
                - authority: 权威性评分 (0-1)
                - overall: 综合评分 (0-1)
        """
        # 1. 时效性评分
        timeliness = self._score_timeliness(
            db, novel_id, evidence, query_context
        )
        
        # 2. 具体性评分
        specificity = self._score_specificity(evidence)
        
        # 3. 权威性评分
        authority = self._score_authority(
            db, novel_id, evidence
        )
        
        # 综合评分（加权平均）
        overall = (
            0.3 * timeliness +
            0.4 * specificity +
            0.3 * authority
        )
        
        scores = {
            'timeliness': timeliness,
            'specificity': specificity,
            'authority': authority,
            'overall': overall
        }
        
        logger.debug(f"📊 证据评分: {scores}")
        
        return scores
    
    def _score_timeliness(
        self,
        db: Session,
        novel_id: int,
        evidence: Dict,
        query_context: Optional[Dict]
    ) -> float:
        """
        时效性评分
        
        证据距离查询时间点的远近
        - 如果查询指定了章节，距离该章节越近分数越高
        - 否则，优先近期章节
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            evidence: 证据
            query_context: 查询上下文
        
        Returns:
            float: 时效性分数 (0-1)
        """
        chapter_num = evidence.get('chapter_num')
        if chapter_num is None:
            return 0.5  # 默认中等分数
        
        # 获取小说总章节数
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return 0.5
        
        total_chapters = novel.total_chapters
        
        # 如果查询指定了章节范围
        if query_context and query_context.get('target_chapter'):
            target_chapter = query_context['target_chapter']
            distance = abs(chapter_num - target_chapter)
            
            # 距离越近分数越高
            if distance == 0:
                return 1.0
            elif distance <= 10:
                return 0.8
            elif distance <= 50:
                return 0.6
            elif distance <= 100:
                return 0.4
            else:
                return 0.2
        
        # 否则，按在小说中的位置评分
        # 优先中后期章节（通常更重要）
        position = chapter_num / total_chapters
        
        if 0.4 <= position <= 0.8:  # 中期章节
            return 0.8
        elif 0.8 < position:  # 后期章节
            return 0.9
        else:  # 前期章节
            return 0.6
    
    def _score_specificity(self, evidence: Dict) -> float:
        """
        具体性评分
        
        证据的详细程度和明确性
        - 包含具体细节（数字、名称、引号）
        - 内容长度适中
        - 信息密度高
        
        Args:
            evidence: 证据
        
        Returns:
            float: 具体性分数 (0-1)
        """
        content = evidence.get('content', '')
        score = 0.5  # 基础分数
        
        # 长度评分
        length = len(content)
        if 100 <= length <= 500:
            score += 0.2
        elif length < 50 or length > 1000:
            score -= 0.1
        
        # 包含具体数字
        import re
        if re.search(r'\d+', content):
            score += 0.1
        
        # 包含引号（对话通常更具体）
        quote_count = content.count('"') + content.count('"') + content.count("'")
        if quote_count > 0:
            score += 0.15
        
        # 包含关键细节词
        detail_keywords = ['具体', '详细', '明确', '清楚', '确实', '确定']
        for keyword in detail_keywords:
            if keyword in content:
                score += 0.05
                break
        
        # 限制在0-1范围
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _score_authority(
        self,
        db: Session,
        novel_id: int,
        evidence: Dict
    ) -> float:
        """
        权威性评分
        
        基于来源章节的重要性和可信度
        - 章节重要性评分（importance_score）
        - 来源类型（向量/关键词/图谱）
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            evidence: 证据
        
        Returns:
            float: 权威性分数 (0-1)
        """
        chapter_num = evidence.get('chapter_num')
        source = evidence.get('source', 'vector')
        
        score = 0.5  # 基础分数
        
        # 来源类型权重
        source_weights = {
            'vector': 0.7,    # 向量检索：标准权威性
            'keyword': 0.8,   # 关键词检索：精确匹配，权威性较高
            'graph': 0.9,     # 图谱检索：结构化知识，权威性最高
        }
        source_score = source_weights.get(source, 0.7)
        score = score * 0.4 + source_score * 0.6
        
        # 章节重要性
        if chapter_num is not None:
            try:
                chapter = db.query(Chapter).filter(
                    Chapter.novel_id == novel_id,
                    Chapter.chapter_num == chapter_num
                ).first()
                
                if chapter and chapter.importance_score:
                    # 重要章节提升权威性
                    importance = chapter.importance_score
                    score = score * 0.6 + importance * 0.4
            except Exception as e:
                logger.debug(f"查询章节重要性失败: {e}")
        
        return score
    
    def batch_score(
        self,
        db: Session,
        novel_id: int,
        evidence_list: List[Dict],
        query_context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        批量评分
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            evidence_list: 证据列表
            query_context: 查询上下文
        
        Returns:
            List[Dict]: 带评分的证据列表
        """
        scored_evidence = []
        
        for evidence in evidence_list:
            scores = self.score_evidence(
                db, novel_id, evidence, query_context
            )
            
            # 合并评分到证据
            evidence_with_score = {**evidence, **scores}
            scored_evidence.append(evidence_with_score)
        
        # 按综合分数排序
        scored_evidence.sort(key=lambda x: -x.get('overall', 0))
        
        logger.info(f"✅ 批量评分完成: {len(scored_evidence)} 条证据")
        
        return scored_evidence


# 全局实例
_evidence_scorer: Optional[EvidenceScorer] = None


def get_evidence_scorer() -> EvidenceScorer:
    """获取全局证据评分器实例（单例）"""
    global _evidence_scorer
    if _evidence_scorer is None:
        _evidence_scorer = EvidenceScorer()
    return _evidence_scorer

