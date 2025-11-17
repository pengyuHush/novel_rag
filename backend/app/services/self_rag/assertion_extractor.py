"""
断言提取器

从LLM生成的答案中提取关键断言（可验证的陈述）
"""

import logging
import re
from typing import List, Dict, Optional
from app.core.trace_logger import get_trace_logger

logger = logging.getLogger(__name__)
trace_logger = get_trace_logger()


class AssertionExtractor:
    """断言提取器"""
    
    # 断言标识词
    ASSERTION_MARKERS = [
        # 明确陈述
        "是", "为", "在", "有", "没有", "属于", "来自",
        # 时间相关
        "发生在", "出现在", "始于", "终于", "持续",
        # 关系相关
        "认识", "结识", "成为", "变成", "喜欢", "讨厌",
        # 能力/状态
        "能够", "可以", "会", "拥有", "失去", "获得",
    ]
    
    def __init__(self):
        """初始化断言提取器"""
        logger.info("✅ 断言提取器初始化完成")
    
    def extract_assertions(
        self,
        answer: str,
        min_confidence: float = 0.5,
        query_id: Optional[int] = None
    ) -> List[Dict]:
        """
        从答案中提取断言
        
        断言是可验证的具体陈述，如：
        - "萧炎在第1章是三段斗之气"
        - "药老是萧炎的师傅"
        - "纳兰嫣然退婚发生在第3章"
        
        Args:
            answer: LLM生成的答案
            min_confidence: 最小置信度阈值
        
        Returns:
            List[Dict]: 断言列表
                - assertion: 断言文本
                - type: 断言类型（fact/relation/event）
                - confidence: 置信度
                - entities: 涉及的实体
                - chapter_ref: 章节引用（如果有）
        """
        assertions = []
        
        # 按句子分割
        sentences = self._split_into_sentences(answer)
        
        for sent_idx, sentence in enumerate(sentences):
            # 跳过太短的句子
            if len(sentence) < 5:
                continue
            
            # 检测断言类型
            assertion_type = self._detect_assertion_type(sentence)
            if assertion_type is None:
                continue
            
            # 提取实体
            entities = self._extract_entities(sentence)
            
            # 提取章节引用
            chapter_ref = self._extract_chapter_reference(sentence)
            
            # 计算置信度
            confidence = self._calculate_confidence(
                sentence, assertion_type, entities, chapter_ref
            )
            
            if confidence >= min_confidence:
                assertions.append({
                    'assertion': sentence.strip(),
                    'type': assertion_type,
                    'confidence': confidence,
                    'entities': entities,
                    'chapter_ref': chapter_ref,
                    'index': sent_idx
                })
        
        logger.info(f"✅ 提取断言: {len(assertions)} 个")
        
        # 详细日志
        if query_id:
            trace_logger.trace_step(
                query_id=query_id,
                step_name="Self-RAG: 断言提取",
                emoji="🔬",
                input_data={
                    "答案长度": len(answer),
                    "句子数量": len(sentences),
                    "最小置信度": min_confidence
                },
                output_data={
                    "提取的断言数量": len(assertions),
                    "断言列表": [
                        {
                            "断言": a["assertion"],
                            "类型": a["type"],
                            "置信度": f"{a['confidence']:.2f}",
                            "实体": a["entities"],
                            "章节": a.get("chapter_ref")
                        } for a in assertions
                    ]
                },
                status="success"
            )
        
        return assertions
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 文本
        
        Returns:
            List[str]: 句子列表
        """
        # 按标点符号分割
        sentences = re.split(r'[。！？\n；]', text)
        
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _detect_assertion_type(self, sentence: str) -> Optional[str]:
        """
        检测断言类型
        
        Args:
            sentence: 句子
        
        Returns:
            Optional[str]: fact/relation/event/None
        """
        # 事件类型关键词
        event_keywords = ["发生", "出现", "开始", "结束", "离开", "到达", "战斗", "死亡"]
        
        # 关系类型关键词
        relation_keywords = ["关系", "认识", "朋友", "敌人", "师傅", "徒弟", "父子", "母女"]
        
        # 检测事件
        for keyword in event_keywords:
            if keyword in sentence:
                return "event"
        
        # 检测关系
        for keyword in relation_keywords:
            if keyword in sentence:
                return "relation"
        
        # 检测事实（包含断言标识词）
        for marker in self.ASSERTION_MARKERS:
            if marker in sentence:
                return "fact"
        
        return None
    
    def _extract_entities(self, sentence: str) -> List[str]:
        """
        提取实体（简单版）
        
        使用正则匹配人名/组织名
        
        Args:
            sentence: 句子
        
        Returns:
            List[str]: 实体列表
        """
        entities = []
        
        # 匹配中文名字（2-4个字）
        name_pattern = r'[\u4e00-\u9fa5]{2,4}(?=[是为在有说讲提到])'
        matches = re.findall(name_pattern, sentence)
        
        for match in matches:
            # 过滤常见无效词
            if match not in ['他们', '我们', '大家', '所有', '这个', '那个', '什么', '如何']:
                entities.append(match)
        
        # 去重
        entities = list(set(entities))
        
        return entities
    
    def _extract_chapter_reference(self, sentence: str) -> Optional[int]:
        """
        提取章节引用
        
        Args:
            sentence: 句子
        
        Returns:
            Optional[int]: 章节号
        """
        # 匹配模式："第X章"，"第X回"，"在X章"
        patterns = [
            r'第(\d+)[章回]',
            r'在(\d+)章',
            r'(\d+)章节',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _calculate_confidence(
        self,
        sentence: str,
        assertion_type: str,
        entities: List[str],
        chapter_ref: Optional[int]
    ) -> float:
        """
        计算断言置信度
        
        基于以下因素：
        - 句子长度（太短或太长降低置信度）
        - 实体数量（有具体实体提高置信度）
        - 章节引用（有章节引用提高置信度）
        - 不确定词（"可能"、"也许"降低置信度）
        
        Args:
            sentence: 句子
            assertion_type: 断言类型
            entities: 实体列表
            chapter_ref: 章节引用
        
        Returns:
            float: 置信度 (0-1)
        """
        confidence = 0.7  # 基础置信度
        
        # 句子长度
        length = len(sentence)
        if 10 <= length <= 100:
            confidence += 0.1
        elif length < 5 or length > 200:
            confidence -= 0.2
        
        # 实体数量
        if len(entities) > 0:
            confidence += 0.1
        if len(entities) >= 2:
            confidence += 0.1
        
        # 章节引用
        if chapter_ref is not None:
            confidence += 0.2
        
        # 不确定词
        uncertain_words = ["可能", "也许", "大概", "似乎", "好像", "或许"]
        for word in uncertain_words:
            if word in sentence:
                confidence -= 0.3
                break
        
        # 限制在0-1范围
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence


# 全局实例
_assertion_extractor: Optional[AssertionExtractor] = None


def get_assertion_extractor() -> AssertionExtractor:
    """获取全局断言提取器实例（单例）"""
    global _assertion_extractor
    if _assertion_extractor is None:
        _assertion_extractor = AssertionExtractor()
    return _assertion_extractor

