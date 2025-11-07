"""元数据提取服务 - 从文本chunk中提取丰富的元数据信息."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from typing import List, Optional

from loguru import logger
from zai import ZhipuAiClient

from app.core.config import settings


@dataclass
class ChunkMetadata:
    """文本块元数据."""
    
    characters: List[str]  # 角色列表
    keywords: List[str]    # 关键词列表
    summary: str           # 摘要
    scene_type: str        # 场景类型
    emotional_tone: str    # 情感基调


class MetadataExtractionService:
    """元数据提取服务 - 使用LLM提取文本语义特征."""
    
    # 场景类型枚举
    SCENE_TYPES = ["对话", "描述", "动作", "心理", "混合"]
    
    # 情感基调枚举
    EMOTIONAL_TONES = ["积极", "消极", "中性", "紧张", "温馨", "悲伤", "激动", "平静"]
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化元数据提取服务.
        
        Args:
            api_key: 智谱AI API密钥（如果为None，则从配置读取）
        """
        if api_key is None:
            api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        
        if not api_key:
            logger.warning("API key not configured; metadata extraction will be disabled")
            self.client = None
        else:
            self.client = ZhipuAiClient(api_key=api_key)
        
        # 是否启用元数据提取
        self.enabled = getattr(settings, 'ENABLE_METADATA_EXTRACTION', True)
        
        # 提取模型（使用快速模型降低成本）
        self.extraction_model = getattr(settings, 'METADATA_EXTRACTION_MODEL', 'glm-4-flash')
    
    async def extract_metadata(self, text: str) -> Optional[ChunkMetadata]:
        """从文本中提取元数据.
        
        Args:
            text: 待提取的文本内容
            
        Returns:
            ChunkMetadata: 提取的元数据，如果提取失败则返回None
        """
        if not self.enabled or not self.client:
            logger.debug("Metadata extraction disabled, skipping")
            return None
        
        if len(text) < 50:
            logger.debug(f"Text too short ({len(text)} chars), skipping metadata extraction")
            return None
        
        try:
            # 使用LLM提取元数据
            metadata = await self._extract_with_llm(text)
            return metadata
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return None
    
    async def extract_metadata_batch(
        self, 
        texts: List[str],
        batch_size: int = 5
    ) -> List[Optional[ChunkMetadata]]:
        """批量提取元数据（并发处理以提高效率）.
        
        Args:
            texts: 文本列表
            batch_size: 并发批次大小
            
        Returns:
            List[Optional[ChunkMetadata]]: 元数据列表（与texts一一对应）
        """
        if not self.enabled or not self.client:
            return [None] * len(texts)
        
        results: List[Optional[ChunkMetadata]] = []
        
        # 分批并发处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 并发提取
            tasks = [self.extract_metadata(text) for text in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.warning(f"Batch extraction error: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        logger.info(f"Batch extraction completed: {len(texts)} texts, {sum(1 for r in results if r)} succeeded")
        return results
    
    async def _extract_with_llm(self, text: str) -> ChunkMetadata:
        """使用LLM提取元数据.
        
        使用结构化输出格式确保JSON解析成功率。
        
        Args:
            text: 文本内容
            
        Returns:
            ChunkMetadata: 提取的元数据
        """
        # 截断过长文本（避免超出token限制）
        max_length = 800
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        prompt = f"""分析文本并直接输出JSON（不要任何解释）：

文本：
{text}

直接输出JSON：
{{
  "characters": ["角色1", "角色2"],
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "summary": "简短摘要20-30字",
  "scene_type": "{'/'.join(self.SCENE_TYPES)}之一",
  "emotional_tone": "{'/'.join(self.EMOTIONAL_TONES)}之一"
}}"""

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.extraction_model,
                messages=[
                    {
                        "role": "system",
                        "content": "直接输出JSON格式的结果，不要任何解释、推理过程或额外文字。只输出有效的JSON对象。"
                    },
                    {"role": "user", "content": prompt}
                ],
                thinking={
                    "type": "disable",  # 启用深度思考模式
                },
                temperature=0.1,  # 低温度保证稳定输出
                max_tokens=800,  # 增加token限制，确保能输出完整JSON（glm-4.5需要更多空间）
            ),
        )
        logger.debug(f"Response from server: {response}")  # 降低为debug级别，避免日志过多
        
        # 从响应中提取消息内容
        message = response.choices[0].message if response.choices else None
        if not message:
            raise ValueError("LLM returned empty response")
        
        # 优先读取 content 字段（JSON结果在这里），reasoning_content 是推理过程文本
        # 根据智谱AI官方文档和测试：无论 thinking 设置如何，JSON都在 content 字段
        content = message.content or getattr(message, 'reasoning_content', None) or ""
        if not content:
            raise ValueError("LLM returned empty response")
        
        # 解析JSON响应
        try:
            # 尝试提取JSON（有时LLM会在前后加其他文字）
            # 使用非贪婪匹配，找到最后一个完整的JSON对象
            json_matches = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL))
            
            if json_matches:
                # 尝试解析找到的每个JSON，从最后一个开始
                for match in reversed(json_matches):
                    try:
                        json_str = match.group()
                        data = json.loads(json_str)
                        # 如果成功解析且包含必要字段，使用这个
                        if 'characters' in data or 'keywords' in data:
                            break
                    except json.JSONDecodeError:
                        continue
                else:
                    # 如果所有匹配都失败，尝试直接解析整个内容
                    data = json.loads(content)
            else:
                data = json.loads(content)
            
            # 构建元数据对象
            metadata = ChunkMetadata(
                characters=data.get("characters", [])[:5],  # 最多5个角色
                keywords=data.get("keywords", [])[:5],      # 最多5个关键词
                summary=data.get("summary", "")[:100],       # 最多100字
                scene_type=self._validate_scene_type(data.get("scene_type", "混合")),
                emotional_tone=self._validate_emotional_tone(data.get("emotional_tone", "中性"))
            )
            
            logger.debug(
                f"Metadata extracted: characters={len(metadata.characters)}, "
                f"keywords={len(metadata.keywords)}, scene={metadata.scene_type}, "
                f"tone={metadata.emotional_tone}"
            )
            
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {content[:200]}")
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e
    
    def _validate_scene_type(self, scene_type: str) -> str:
        """验证并标准化场景类型."""
        if scene_type in self.SCENE_TYPES:
            return scene_type
        
        # 尝试模糊匹配
        for valid_type in self.SCENE_TYPES:
            if valid_type in scene_type or scene_type in valid_type:
                return valid_type
        
        return "混合"  # 默认值
    
    def _validate_emotional_tone(self, emotional_tone: str) -> str:
        """验证并标准化情感基调."""
        if emotional_tone in self.EMOTIONAL_TONES:
            return emotional_tone
        
        # 尝试模糊匹配
        for valid_tone in self.EMOTIONAL_TONES:
            if valid_tone in emotional_tone or emotional_tone in valid_tone:
                return valid_tone
        
        return "中性"  # 默认值
    
    async def extract_simple_metadata(self, text: str) -> ChunkMetadata:
        """使用规则提取简单元数据（不调用LLM，用于降级场景）.
        
        Args:
            text: 文本内容
            
        Returns:
            ChunkMetadata: 基于规则提取的元数据
        """
        # 1. 角色识别（简单规则：寻找常见姓名模式）
        characters = self._extract_characters_rule_based(text)
        
        # 2. 关键词（使用TF-IDF或简单的词频）
        keywords = self._extract_keywords_rule_based(text)
        
        # 3. 摘要（取前50字）
        summary = text[:50].strip() + "..." if len(text) > 50 else text.strip()
        
        # 4. 场景类型（基于标点符号和特征词）
        scene_type = self._detect_scene_type_rule_based(text)
        
        # 5. 情感基调（基于情感词典）
        emotional_tone = self._detect_emotional_tone_rule_based(text)
        
        return ChunkMetadata(
            characters=characters,
            keywords=keywords,
            summary=summary,
            scene_type=scene_type,
            emotional_tone=emotional_tone
        )
    
    def _extract_characters_rule_based(self, text: str) -> List[str]:
        """基于规则提取角色名称."""
        # 简单规则：识别2-4个字的中文词（可能是人名）
        # 这个可以根据实际情况优化
        pattern = r'["\']([^"\']{2,4})["\']|([，。！？：；""''（）、《》【】]{2,4})'
        matches = re.findall(pattern, text)
        
        characters = []
        for match in matches:
            name = match[0] or match[1]
            if name and len(name) >= 2 and name not in characters:
                characters.append(name)
                if len(characters) >= 5:
                    break
        
        return characters
    
    def _extract_keywords_rule_based(self, text: str) -> List[str]:
        """基于规则提取关键词（简单词频统计）."""
        # 移除标点符号和空白字符
        clean_text = re.sub(r'[，。！？：；""''（）、《》【】\t\n\r ]', '', text)
        
        # 简单的2-3字词提取
        words = []
        for i in range(len(clean_text) - 1):
            word2 = clean_text[i:i+2]
            word3 = clean_text[i:i+3] if i < len(clean_text) - 2 else None
            
            if word3 and len(word3) == 3:
                words.append(word3)
            words.append(word2)
        
        # 词频统计
        from collections import Counter
        word_freq = Counter(words)
        
        # 返回最常见的3-5个词
        keywords = [word for word, _ in word_freq.most_common(5)]
        return keywords[:5]
    
    def _detect_scene_type_rule_based(self, text: str) -> str:
        """基于规则检测场景类型."""
        # 对话特征：引号多
        quote_count = text.count('"') + text.count('"') + text.count('"')
        if quote_count >= 4:
            return "对话"
        
        # 动作特征：动词多
        action_keywords = ['走', '跑', '跳', '飞', '打', '击', '追', '逃', '抓', '扔']
        action_count = sum(1 for kw in action_keywords if kw in text)
        if action_count >= 3:
            return "动作"
        
        # 心理特征：心理动词
        mental_keywords = ['想', '思', '念', '忆', '感觉', '觉得', '认为', '以为']
        mental_count = sum(1 for kw in mental_keywords if kw in text)
        if mental_count >= 2:
            return "心理"
        
        # 描述特征：形容词多
        desc_keywords = ['美丽', '巨大', '明亮', '黑暗', '寒冷', '温暖', '高大', '宽阔']
        desc_count = sum(1 for kw in desc_keywords if kw in text)
        if desc_count >= 2:
            return "描述"
        
        return "混合"
    
    def _detect_emotional_tone_rule_based(self, text: str) -> str:
        """基于规则检测情感基调."""
        # 积极情感词
        positive_words = ['高兴', '快乐', '喜悦', '欢笑', '幸福', '美好', '温暖', '舒适']
        positive_count = sum(1 for word in positive_words if word in text)
        
        # 消极情感词
        negative_words = ['悲伤', '痛苦', '难过', '哭泣', '绝望', '恐惧', '害怕', '担心']
        negative_count = sum(1 for word in negative_words if word in text)
        
        # 紧张情感词
        tense_words = ['紧张', '危险', '急促', '焦虑', '匆忙', '惊慌', '冲突']
        tense_count = sum(1 for word in tense_words if word in text)
        
        # 根据词频判断
        if positive_count > negative_count and positive_count > tense_count:
            return "积极"
        elif negative_count > positive_count and negative_count > tense_count:
            return "消极"
        elif tense_count > 0:
            return "紧张"
        
        return "中性"


__all__ = ["MetadataExtractionService", "ChunkMetadata"]

