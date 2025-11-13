"""
Self-RAG模块

增强版Self-RAG，包含：
- 断言提取
- 多源证据收集
- 证据质量评分
- 一致性检查
- 矛盾检测
- 答案修正
"""

from .assertion_extractor import AssertionExtractor, get_assertion_extractor
from .evidence_collector import EvidenceCollector, get_evidence_collector
from .evidence_scorer import EvidenceScorer, get_evidence_scorer
from .consistency_checker import ConsistencyChecker, get_consistency_checker
from .contradiction_detector import ContradictionDetector, get_contradiction_detector
from .answer_corrector import AnswerCorrector, get_answer_corrector

__all__ = [
    'AssertionExtractor',
    'get_assertion_extractor',
    'EvidenceCollector',
    'get_evidence_collector',
    'EvidenceScorer',
    'get_evidence_scorer',
    'ConsistencyChecker',
    'get_consistency_checker',
    'ContradictionDetector',
    'get_contradiction_detector',
    'AnswerCorrector',
    'get_answer_corrector',
]

