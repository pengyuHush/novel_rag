"""
自适应Prompt构建器 - Adaptive Prompt Builder

根据查询类型定制不同的Prompt模板，提升答案质量：
- 对话类：强调引用原文对话并标注章节
- 分析类：引导逐步推理，添加Chain of Thought
- 事实类：强调准确性和简洁性

包含Few-shot示例和CoT引导，预留扩展接口
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.services.query_router import QueryType, query_router
from app.models.database import Novel
from app.core.trace_logger import get_trace_logger

logger = logging.getLogger(__name__)
trace_logger = get_trace_logger()


class AdaptivePromptBuilder:
    """自适应Prompt构建器"""
    
    # Few-shot示例（硬编码，预留从数据库加载的扩展接口）
    FEW_SHOT_EXAMPLES = {
        QueryType.DIALOGUE: """
示例问答：
问题：萧峰在聚贤庄说了什么？
回答：萧峰在聚贤庄大声说道："我萧峰大好男儿，何惧于死？今日既然来到聚贤庄，便是来赴死的！"（第42章）他还说："诸位英雄，萧峰平生不敢做之事，便是对不起朋友。"（第42章）这些话表达了他宁死不屈的决心和重情重义的品格。
""",
        QueryType.ANALYSIS: """
示例问答：
问题：令狐冲为何被逐出华山派？
回答：令狐冲被逐出华山派主要有三个原因：

第一，在思过崖学习了"吸星大法"等魔教武功（第13章）。令狐冲因伤被困思过崖时，无意中发现了魔教长老留下的武功秘籍，出于好奇和求生本能学习了这些武功。

第二，与魔教长老向问天结交，被怀疑投靠魔教（第18章）。令狐冲救了向问天一命，两人结为好友，这让岳不群更加怀疑他与魔教有染。

第三，与小师妹岳灵珊的感情破裂，失去了师门庇护（第21章）。岳灵珊移情别恋林平之后，岳不群借机清理门户，以"行为不端、私学魔功"为由将令狐冲逐出师门。

综合以上因素，岳不群的野心和猜忌是令狐冲被逐的根本原因。
""",
        QueryType.FACT: """
示例问答：
问题：张三丰活了多少岁？
回答：张三丰活了至少200岁以上。在《倚天屠龙记》中，张三丰创立武当派时已是百岁高龄，到张无忌时代仍然健在（第1章、第24章），是武林中德高望重的宗师级人物。
"""
    }
    
    def __init__(self):
        """初始化自适应Prompt构建器"""
        logger.info("✅ 自适应Prompt构建器初始化完成")
    
    def build_prompt(
        self,
        db: Session,
        novel_id: int,
        query: str,
        context_chunks: List[Dict],
        max_chunks: int = 10,
        query_type: Optional[QueryType] = None,
        include_few_shot: bool = True,
        query_id: Optional[int] = None,
        novel_ids: Optional[List[int]] = None
    ) -> str:
        """
        构建自适应RAG Prompt
        
        Args:
            db: 数据库会话
            novel_id: 小说ID（主小说ID，向后兼容）
            query: 查询文本
            context_chunks: 上下文块列表
            max_chunks: 最大使用的上下文块数量
            query_type: 查询类型（如不提供则自动检测）
            include_few_shot: 是否包含Few-shot示例
            query_id: 查询ID（用于日志记录）
            novel_ids: 多个小说ID（用于多小说查询）
        
        Returns:
            str: 构建好的Prompt
        """
        # 自动检测查询类型
        if query_type is None:
            query_type = query_router.classify_query(query)
        
        logger.info(f"🎯 构建 {query_type.value} 类型的Prompt")
        
        # 获取小说信息
        if novel_ids and len(novel_ids) > 1:
            # 多小说查询
            novels = db.query(Novel).filter(Novel.id.in_(novel_ids)).all()
            novel_info = ", ".join([f"《{n.title}》" for n in novels])
            novel_title = f"{len(novels)}本小说（{novel_info}）"
            novel_author = "多位作者"
            is_multi_novel = True
        else:
            # 单小说查询
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            novel_title = novel.title if novel else "未知"
            novel_author = novel.author if novel and novel.author else "未知"
            is_multi_novel = False
        
        # 限制上下文块数量
        limited_chunks = context_chunks[:max_chunks]
        
        # 构建上下文
        context_text = self._format_context(limited_chunks, db)
        
        # 根据查询类型选择Prompt模板
        if query_type == QueryType.DIALOGUE:
            prompt = self._build_dialogue_prompt(
                novel_title, novel_author, context_text, query, include_few_shot, is_multi_novel
            )
        elif query_type == QueryType.ANALYSIS:
            prompt = self._build_analysis_prompt(
                novel_title, novel_author, context_text, query, include_few_shot, is_multi_novel
            )
        else:  # FACT
            prompt = self._build_fact_prompt(
                novel_title, novel_author, context_text, query, include_few_shot, is_multi_novel
            )
        
        # 详细日志
        if query_id:
            trace_logger.trace_step(
                query_id=query_id,
                step_name="Prompt构建",
                emoji="📝",
                input_data={
                    "查询": query,
                    "查询类型": query_type.value,
                    "小说": f"{novel_title}（{novel_author}）",
                    "上下文块数量": len(limited_chunks),
                    "包含Few-shot": include_few_shot
                },
                output_data=prompt,
                status="success"
            )
        
        return prompt
    
    def _format_context(self, chunks: List[Dict], db: Session = None) -> str:
        """
        格式化上下文片段
        
        Args:
            chunks: 上下文块列表
            db: 数据库会话（用于查询小说标题）
        
        Returns:
            str: 格式化后的上下文文本
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            chapter_num = metadata.get('chapter_num', '?')
            chapter_title = metadata.get('chapter_title', '')
            source_novel_id = metadata.get('source_novel_id')
            content = chunk['content']
            
            # 如果有来源小说ID，查询小说标题
            novel_prefix = ""
            if source_novel_id and db:
                try:
                    novel = db.query(Novel).filter(Novel.id == source_novel_id).first()
                    if novel:
                        novel_prefix = f"《{novel.title}》 - "
                except:
                    pass
            
            context_parts.append(
                f"[片段{i} - {novel_prefix}第{chapter_num}章 {chapter_title}]\n{content}"
            )
        
        return "\n\n".join(context_parts)
    
    def _build_dialogue_prompt(
        self,
        novel_title: str,
        novel_author: str,
        context_text: str,
        query: str,
        include_few_shot: bool,
        is_multi_novel: bool = False
    ) -> str:
        """
        构建对话类查询的Prompt
        
        特点：
        - 强调直接引用原文对话
        - 要求使用引号标注
        - 标注说话者和章节
        """
        few_shot = ""
        if include_few_shot:
            few_shot = self.FEW_SHOT_EXAMPLES[QueryType.DIALOGUE]
        
        multi_novel_note = ""
        if is_multi_novel:
            multi_novel_note = "\n**注意**: 以下片段来自多本小说，请在回答时明确标注每段对话来自哪本小说和哪一章。"
        
        prompt = f"""你是小说对话分析专家。请从以下片段中提取与问题相关的对话内容。

**小说信息**
- 标题: {novel_title}
- 作者: {novel_author}{multi_novel_note}

**相关片段**
{context_text}

**用户问题**
{query}

**回答要求**
1. **直接引用原文对话**，使用引号标注（如："张无忌说道：'……'"）
2. 标注说话者和对话所在的章节号{' 以及小说名称（多本小说时）' if is_multi_novel else ''}
3. 如有必要，简要说明对话发生的背景或场景
4. 如果片段中没有相关对话，请明确说明
5. 保持对话的完整性，不要断章取义
6. {'综合多本小说的内容，给出全面完整的回答' if is_multi_novel else '基于小说内容给出完整的回答'}

{few_shot}

**你的回答**:"""
        
        return prompt
    
    def _build_analysis_prompt(
        self,
        novel_title: str,
        novel_author: str,
        context_text: str,
        query: str,
        include_few_shot: bool,
        is_multi_novel: bool = False
    ) -> str:
        """
        构建分析类查询的Prompt
        
        特点：
        - 引导逐步推理
        - 添加Chain of Thought
        - 要求综合多个片段
        """
        few_shot = ""
        if include_few_shot:
            few_shot = self.FEW_SHOT_EXAMPLES[QueryType.ANALYSIS]
        
        multi_novel_note = ""
        if is_multi_novel:
            multi_novel_note = "\n**注意**: 以下片段来自多本小说，请综合分析不同小说中的相关内容，并在回答时标注来源。"
        
        prompt = f"""你是小说情节分析专家。请基于以下片段进行深度分析。

**小说信息**
- 标题: {novel_title}
- 作者: {novel_author}{multi_novel_note}

**相关片段**
{context_text}

**用户问题**
{query}

**回答要求**
1. 首先梳理关键情节和时间线
2. 分析因果关系和人物动机
3. 综合多个片段，形成连贯的解释
4. 标注引用的章节范围{' 和小说名称（多本小说时）' if is_multi_novel else ''}
5. 如果信息不足以完整回答，请说明缺失的信息
6. {'对比分析不同小说中的相关内容，给出全面深入的分析' if is_multi_novel else '基于小说内容给出深入的分析'}

**思考步骤**（请按此步骤组织回答）：
第1步：识别问题中的关键要素（人物、事件、时间）
第2步：从提供的片段中定位相关信息
第3步：建立信息之间的因果关系或时序关系
第4步：形成连贯的解释和结论

{few_shot}

**你的回答**:"""
        
        return prompt
    
    def _build_fact_prompt(
        self,
        novel_title: str,
        novel_author: str,
        context_text: str,
        query: str,
        include_few_shot: bool,
        is_multi_novel: bool = False
    ) -> str:
        """
        构建事实类查询的Prompt
        
        特点：
        - 强调准确性
        - 要求简洁明确
        - 明确信息来源
        """
        few_shot = ""
        if include_few_shot:
            few_shot = self.FEW_SHOT_EXAMPLES[QueryType.FACT]
        
        multi_novel_note = ""
        if is_multi_novel:
            multi_novel_note = "\n**注意**: 以下片段来自多本小说，请在回答时明确标注信息来自哪本小说。"
        
        prompt = f"""你是小说内容助手。请准确回答用户的事实性问题。

**小说信息**
- 标题: {novel_title}
- 作者: {novel_author}{multi_novel_note}

**相关片段**
{context_text}

**用户问题**
{query}

**回答要求**
1. 回答必须基于提供的片段内容
2. 如片段内容不足以回答，明确说明缺少哪些信息
3. 标注信息来源章节{' 和小说名称（多本小说时）' if is_multi_novel else ''}
4. 回答要简洁明确，直击要点
5. 不要添加推测或编造信息
6. {'综合多本小说的信息，给出完整准确的回答' if is_multi_novel else '基于小说内容给出准确的回答'}

{few_shot}

**你的回答**:"""
        
        return prompt
    
    # 预留扩展接口：从数据库加载Few-shot示例
    def load_few_shot_from_db(
        self,
        db: Session,
        query_type: QueryType,
        limit: int = 3
    ) -> str:
        """
        从数据库加载Few-shot示例（预留接口）
        
        未来可以实现：
        - 从高质量的历史查询记录中选择示例
        - 动态更新示例库
        - 根据小说类型选择示例
        
        Args:
            db: 数据库会话
            query_type: 查询类型
            limit: 加载示例数量
        
        Returns:
            str: 格式化的Few-shot示例
        """
        # TODO: 实现从数据库加载逻辑
        # 目前返回硬编码的示例
        return self.FEW_SHOT_EXAMPLES.get(query_type, "")
    
    # 预留扩展接口：添加自定义Few-shot示例
    def add_custom_example(
        self,
        query_type: QueryType,
        question: str,
        answer: str
    ) -> None:
        """
        添加自定义Few-shot示例（预留接口）
        
        未来可以实现：
        - 管理员添加高质量示例
        - 用户标注的优质回答
        - 自动从反馈中学习
        
        Args:
            query_type: 查询类型
            question: 问题
            answer: 答案
        """
        # TODO: 实现自定义示例添加逻辑
        logger.info(f"预留功能：添加 {query_type.value} 类型的自定义示例")
        pass


# 全局自适应Prompt构建器实例
_adaptive_prompt_builder: Optional[AdaptivePromptBuilder] = None


def get_adaptive_prompt_builder() -> AdaptivePromptBuilder:
    """获取全局自适应Prompt构建器实例（单例）"""
    global _adaptive_prompt_builder
    if _adaptive_prompt_builder is None:
        _adaptive_prompt_builder = AdaptivePromptBuilder()
    return _adaptive_prompt_builder

