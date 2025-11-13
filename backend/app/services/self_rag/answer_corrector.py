"""
答案修正器

基于矛盾检测修正答案或标注不确定性
"""

import logging
from typing import List, Dict, Optional

from app.models.schemas import Contradiction

logger = logging.getLogger(__name__)


class AnswerCorrector:
    """答案修正器"""
    
    def __init__(self):
        """初始化答案修正器"""
        logger.info("✅ 答案修正器初始化完成")
    
    def correct_answer(
        self,
        original_answer: str,
        contradictions: List[Contradiction],
        confidence: str = "high"
    ) -> Dict:
        """
        修正答案
        
        策略：
        1. 如果没有矛盾，直接返回原答案
        2. 如果有低置信度矛盾，添加警告但保留答案
        3. 如果有高置信度矛盾，修改答案或标注不确定性
        
        Args:
            original_answer: 原始答案
            contradictions: 矛盾列表
            confidence: 答案置信度
        
        Returns:
            Dict: 修正结果
                - corrected_answer: 修正后的答案
                - original_answer: 原始答案
                - modifications: 修改说明列表
                - final_confidence: 最终置信度
        """
        if not contradictions:
            # 无矛盾，直接返回
            return {
                'corrected_answer': original_answer,
                'original_answer': original_answer,
                'modifications': [],
                'final_confidence': confidence,
                'has_contradictions': False
            }
        
        # 按严重程度分类矛盾
        high_contradictions = [c for c in contradictions if c.confidence == 'high']
        medium_contradictions = [c for c in contradictions if c.confidence == 'medium']
        low_contradictions = [c for c in contradictions if c.confidence == 'low']
        
        modifications = []
        corrected_answer = original_answer
        final_confidence = confidence
        
        # 处理高置信度矛盾
        if high_contradictions:
            correction = self._handle_high_confidence_contradictions(
                original_answer, high_contradictions
            )
            corrected_answer = correction['answer']
            modifications.extend(correction['modifications'])
            final_confidence = 'low'  # 存在高置信度矛盾，降低整体置信度
        
        # 处理中等置信度矛盾
        if medium_contradictions:
            correction = self._handle_medium_confidence_contradictions(
                corrected_answer, medium_contradictions
            )
            corrected_answer = correction['answer']
            modifications.extend(correction['modifications'])
            if final_confidence == 'high':
                final_confidence = 'medium'
        
        # 处理低置信度矛盾（仅警告）
        if low_contradictions:
            for contradiction in low_contradictions:
                modifications.append({
                    'type': 'warning',
                    'description': f"注意：{contradiction.analysis}"
                })
        
        logger.info(f"✅ 答案修正: {len(modifications)} 处修改")
        
        return {
            'corrected_answer': corrected_answer,
            'original_answer': original_answer,
            'modifications': modifications,
            'final_confidence': final_confidence,
            'has_contradictions': len(contradictions) > 0
        }
    
    def _handle_high_confidence_contradictions(
        self,
        answer: str,
        contradictions: List[Contradiction]
    ) -> Dict:
        """
        处理高置信度矛盾
        
        在答案中添加矛盾说明和不确定性标注
        
        Args:
            answer: 原始答案
            contradictions: 高置信度矛盾列表
        
        Returns:
            Dict: 修正结果
        """
        modifications = []
        corrected_answer = answer
        
        # 在答案末尾添加矛盾说明
        contradiction_notes = []
        
        for idx, contradiction in enumerate(contradictions, 1):
            note = f"\n\n**矛盾提示 {idx}**：{contradiction.analysis}\n"
            note += f"- 第{contradiction.early_chapter}章：{contradiction.early_description}\n"
            note += f"- 第{contradiction.late_chapter}章：{contradiction.late_description}"
            
            contradiction_notes.append(note)
            modifications.append({
                'type': 'contradiction_note',
                'contradiction_index': idx,
                'description': contradiction.analysis
            })
        
        # 添加总体警告
        if contradiction_notes:
            warning = "\n\n⚠️ **注意**：以上答案存在以下矛盾，请结合原文仔细判断："
            corrected_answer = answer + warning + "".join(contradiction_notes)
        
        return {
            'answer': corrected_answer,
            'modifications': modifications
        }
    
    def _handle_medium_confidence_contradictions(
        self,
        answer: str,
        contradictions: List[Contradiction]
    ) -> Dict:
        """
        处理中等置信度矛盾
        
        添加轻量级提示
        
        Args:
            answer: 原始答案
            contradictions: 中等置信度矛盾列表
        
        Returns:
            Dict: 修正结果
        """
        modifications = []
        
        if contradictions:
            note = "\n\n💡 **提示**：答案涉及以下可能存在不一致的内容：\n"
            for contradiction in contradictions:
                note += f"- {contradiction.analysis}\n"
            
            corrected_answer = answer + note
            
            modifications.append({
                'type': 'hint',
                'description': '添加了潜在不一致性提示'
            })
        else:
            corrected_answer = answer
        
        return {
            'answer': corrected_answer,
            'modifications': modifications
        }
    
    def generate_confidence_explanation(
        self,
        confidence: str,
        contradictions: List[Contradiction]
    ) -> str:
        """
        生成置信度解释
        
        Args:
            confidence: 置信度等级
            contradictions: 矛盾列表
        
        Returns:
            str: 解释文本
        """
        if confidence == 'high' and not contradictions:
            return "答案具有高置信度，证据充分且无矛盾。"
        elif confidence == 'high' and contradictions:
            return f"答案基于证据，但存在{len(contradictions)}处潜在矛盾，建议参考原文验证。"
        elif confidence == 'medium':
            return f"答案具有中等置信度，可能存在{len(contradictions)}处不确定性或矛盾。"
        elif confidence == 'low':
            return f"答案置信度较低，存在{len(contradictions)}处明显矛盾，请谨慎参考。"
        else:
            return "置信度未知。"


# 全局实例
_answer_corrector: Optional[AnswerCorrector] = None


def get_answer_corrector() -> AnswerCorrector:
    """获取全局答案修正器实例（单例）"""
    global _answer_corrector
    if _answer_corrector is None:
        _answer_corrector = AnswerCorrector()
    return _answer_corrector

