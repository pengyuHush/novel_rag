"""
索引服务
整合文件解析、章节识别、文本分块、向量化等功能
"""

import logging
import asyncio
from typing import Dict, Optional, Callable, List
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.parser.txt_parser import TXTParser
from app.services.parser.epub_parser import EPUBParser
from app.services.parser.chapter_detector import ChapterDetector
from app.services.text_splitter import get_text_splitter
from app.services.embedding_service import get_embedding_service
from app.services.nlp.entity_extractor import EntityExtractor
from app.services.nlp.entity_merger import EntityMerger
from app.services.entity_service import EntityService
from app.services.graph.graph_builder import GraphBuilder
from app.services.graph.graph_analyzer import GraphAnalyzer
from app.services.graph.relation_classifier import RelationshipClassifier
from app.services.graph.evolution_tracker import RelationshipEvolutionTracker
from app.services.graph.attribute_extractor import EntityAttributeExtractor
from app.models.database import Novel, Chapter
from app.models.schemas import IndexStatus, FileFormat
from app.core.config import settings

logger = logging.getLogger(__name__)


def clamp_progress(value: float) -> float:
    """
    将进度值限制在0-1范围内，处理浮点数精度问题
    
    Args:
        value: 原始进度值
    
    Returns:
        限制后的进度值（0.0-1.0）
    """
    return max(0.0, min(value, 1.0))


class IndexingService:
    """索引服务"""
    
    def __init__(self):
        """初始化索引服务"""
        self.txt_parser = TXTParser()
        self.epub_parser = EPUBParser()
        self.chapter_detector = ChapterDetector()
        self.text_splitter = get_text_splitter()
        self.embedding_service = get_embedding_service()
        
        # Phase 5: 知识图谱相关服务
        self.entity_extractor = EntityExtractor()
        self.entity_merger = EntityMerger()
        self.entity_service = EntityService()
        self.graph_builder = GraphBuilder()
        self.graph_analyzer = GraphAnalyzer()
        
        logger.info("✅ 索引服务初始化完成（包含知识图谱功能）")
    
    async def index_novel(
        self,
        db: Session,
        novel_id: int,
        file_path: str,
        file_format: FileFormat,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        索引小说
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            file_path: 文件路径
            file_format: 文件格式
            progress_callback: 进度回调函数
        
        Returns:
            bool: 是否成功
        """
        try:
            # 更新状态为处理中
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            if not novel:
                raise ValueError(f"小说 ID={novel_id} 不存在")
            
            novel.index_status = IndexStatus.PROCESSING.value
            novel.index_progress = clamp_progress(0.0)
            db.commit()
            
            # 立即初始化进度追踪（估计章节数为0，后续更新）
            from app.services.indexing_progress_tracker import get_progress_tracker
            tracker = get_progress_tracker()
            tracker.init_progress(novel_id, 0)
            tracker.update_step(novel_id, 0, 'processing', 0.0, '开始解析文件...')
            
            if progress_callback:
                await progress_callback(novel_id, 0.0, "开始解析文件...")
            
            # 1. 解析文件
            logger.info(f"📖 开始解析文件: {file_path}")
            if file_format == FileFormat.TXT:
                content, metadata = self.txt_parser.parse_file(file_path)
                chapters_data = self.chapter_detector.detect(content)
            elif file_format == FileFormat.EPUB:
                content, metadata = self.epub_parser.parse_file(file_path)
                chapters_data = self.epub_parser.detect_chapters(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_format}")
            
            novel.total_chapters = len(chapters_data)
            novel.total_chars = metadata.get('total_chars', len(content))
            db.commit()
            
            # 更新进度追踪的总章节数
            tracker._details[novel_id]['steps'][3]['message'] = f'共{len(chapters_data)}章待处理'
            tracker.update_step(novel_id, 0, 'completed', 1.0, f'解析完成，共{len(chapters_data)}章')
            tracker.update_step(novel_id, 1, 'completed', 1.0, f'检测到{len(chapters_data)}个章节')
            tracker.update_step(novel_id, 2, 'processing', 0.0, '准备处理章节...')
            
            # 更新总进度：文件解析和章节检测完成（0%-5%）
            novel.index_progress = clamp_progress(0.05)
            db.commit()
            
            if progress_callback:
                await progress_callback(novel_id, 0.05, f"文件解析完成，检测到{len(chapters_data)}章")
            
            # 2. 创建ChromaDB集合
            collection_name = self.embedding_service.create_collection(novel_id)
            
            # 3. 处理每个章节（向量化并存储）
            total_chapters = len(chapters_data)
            total_chunks = 0
            total_embedding_tokens = 0  # 初始化token计数器
            
            # 更新步骤2为completed，步骤3为processing
            from app.services.indexing_progress_tracker import get_progress_tracker
            tracker = get_progress_tracker()
            tracker.update_step(novel_id, 2, 'completed', 1.0, f'准备处理{total_chapters}个章节')
            tracker.update_step(novel_id, 3, 'processing', 0.0, '开始处理章节...')
            
            # 检查是否使用 Batch API 进行向量化
            use_batch_api_for_embedding = settings.use_batch_api_for_embedding
            
            if use_batch_api_for_embedding:
                logger.info(f"🚀 启用向量化 Batch API 模式（实验性）")
                
                # 收集所有章节的分块数据
                all_chapters_chunks = []
                
                for i, chapter_data in enumerate(chapters_data):
                    chapter_num = chapter_data['chapter_num']
                    chapter_title = chapter_data.get('title', f"第{chapter_num}章")
                    
                    # 提取章节内容
                    chapter_content = self.chapter_detector.extract_chapter_content(
                        content,
                        chapter_data['start_pos'],
                        chapter_data['end_pos'],
                        include_title=True
                    )
                    
                    # 保存章节到数据库
                    chapter = Chapter(
                        novel_id=novel_id,
                        chapter_num=chapter_num,
                        chapter_title=chapter_title,
                        char_count=len(chapter_content),
                        start_pos=chapter_data['start_pos'],
                        end_pos=chapter_data['end_pos']
                    )
                    db.add(chapter)
                    db.commit()
                    
                    # 文本分块
                    chunks = self.text_splitter.split_chapter(
                        chapter_content,
                        novel_id,
                        chapter_num,
                        chapter_title
                    )
                    
                    chapter.chunk_count = len(chunks)
                    total_chunks += len(chunks)
                    
                    all_chapters_chunks.append({
                        'chapter_num': chapter_num,
                        'chapter_title': chapter_title,
                        'chunks': chunks
                    })
                
                db.commit()
                
                # 使用 Batch API 批量处理向量化
                success, total_embedding_tokens, failed_chapters = await self.embedding_service.process_novel_with_batch_api(
                    novel_id, all_chapters_chunks
                )
                
                if failed_chapters:
                    logger.warning(f"⚠️ {len(failed_chapters)} 个章节向量化失败: {failed_chapters}")
                    for failed_ch in failed_chapters:
                        tracker.add_failed_chapter(novel_id, failed_ch, f"第{failed_ch}章", "向量化处理失败")
                
                # 更新进度到80%
                novel.index_progress = clamp_progress(0.80)
                db.commit()
                
                if progress_callback:
                    token_stats = {
                        "embeddingTokens": total_embedding_tokens,
                        "totalTokens": total_embedding_tokens
                    }
                    await progress_callback(novel_id, 0.80, f"所有章节向量化完成", token_stats)
            else:
                # 原有的逐章节处理逻辑
                logger.info(f"⚡ 使用实时 API 模式处理向量化")
                
                for i, chapter_data in enumerate(chapters_data):
                    chapter_num = chapter_data['chapter_num']
                    chapter_title = chapter_data.get('title', f"第{chapter_num}章")
                    
                    logger.info(f"📝 处理章节 {chapter_num}/{total_chapters}: {chapter_title}")
                    
                    # 提取章节内容
                    chapter_content = self.chapter_detector.extract_chapter_content(
                        content,
                        chapter_data['start_pos'],
                        chapter_data['end_pos'],
                        include_title=True
                    )
                    
                    # 保存章节到数据库
                    chapter = Chapter(
                        novel_id=novel_id,
                        chapter_num=chapter_num,
                        chapter_title=chapter_title,
                        char_count=len(chapter_content),
                        start_pos=chapter_data['start_pos'],
                        end_pos=chapter_data['end_pos']
                    )
                    db.add(chapter)
                    db.commit()
                    
                    # 文本分块
                    chunks = self.text_splitter.split_chapter(
                        chapter_content,
                        novel_id,
                        chapter_num,
                        chapter_title
                    )
                    
                    chapter.chunk_count = len(chunks)
                    total_chunks += len(chunks)
                    
                    # 向量化并存储（获取token消耗）
                    success, chapter_tokens = self.embedding_service.process_chapter(
                        novel_id,
                        chapter_num,
                        chapter_title,
                        chunks
                    )
                    
                    # 累加token消耗
                    total_embedding_tokens += chapter_tokens
                    
                    if not success:
                        logger.warning(f"⚠️ 章节 {chapter_num} 处理失败")
                        # 记录失败章节
                        from app.services.indexing_progress_tracker import get_progress_tracker
                        tracker = get_progress_tracker()
                        tracker.add_failed_chapter(novel_id, chapter_num, chapter_title, "向量化处理失败")
                    
                    # 更新进度（章节处理占5%-80%，共75%）
                    progress = clamp_progress(0.05 + 0.75 * (i + 1) / total_chapters)
                    novel.index_progress = progress
                    db.commit()
                    
                    # 更新步骤3的进度
                    from app.services.indexing_progress_tracker import get_progress_tracker
                    tracker = get_progress_tracker()
                    step_progress = clamp_progress((i + 1) / total_chapters)
                    tracker.update_step(novel_id, 3, 'processing', step_progress, f'已完成 {i+1}/{total_chapters} 章')
                    
                    # 构建token统计信息
                    token_stats = {
                        "embeddingTokens": total_embedding_tokens,
                        "totalTokens": total_embedding_tokens
                    }
                    
                    if progress_callback:
                        await progress_callback(
                            novel_id,
                            progress,
                            f"已完成 {i+1}/{total_chapters} 章",
                            token_stats
                        )
            
            # 标记步骤3为完成，并记录总Token消耗
            from app.services.indexing_progress_tracker import get_progress_tracker
            from app.utils.token_counter import get_token_counter
            tracker = get_progress_tracker()
            tracker.update_step(novel_id, 3, 'completed', 1.0, f'所有章节处理完成（{total_chapters}章）')
            
            # 记录总的向量化Token消耗
            if total_embedding_tokens > 0:
                token_counter = get_token_counter()
                cost = token_counter.calculate_cost(total_embedding_tokens, 0, 'embedding-3')
                tracker.add_token_usage(
                    novel_id=novel_id,
                    step_name='生成嵌入向量',
                    model_name='embedding-3',
                    input_tokens=total_embedding_tokens,
                    output_tokens=0,
                    cost=cost
                )
            
            # 4. Phase 5: 构建知识图谱（占80%-100%，共20%）
            logger.info(f"🕸️ 开始构建知识图谱...")
            
            # 初始化图谱token统计变量
            graph_attribute_tokens = 0
            graph_relation_tokens = 0
            graph_evolution_tokens = 0
            
            # 更新步骤4为processing，并更新总进度到80%
            tracker.update_step(novel_id, 4, 'processing', 0.0, '开始构建知识图谱...')
            novel.index_progress = clamp_progress(0.80)
            db.commit()
            
            if progress_callback:
                await progress_callback(novel_id, 0.80, "开始构建知识图谱...")
            
            try:
                # 4.1 提取实体
                logger.info(f"📝 提取实体中...")
                
                # 检查 HanLP 是否可用
                if not self.entity_extractor.hanlp_client.is_available():
                    logger.warning(f"⚠️ HanLP 不可用，跳过知识图谱构建")
                    logger.warning(f"   提示: 如需使用知识图谱功能，请安装 HanLP:")
                    logger.warning(f"   pip install hanlp")
                    raise Exception("HanLP 不可用")  # 触发异常处理，跳过知识图谱
                
                chapters_for_extraction = [
                    (ch.chapter_num, self.chapter_detector.extract_chapter_content(
                        content, ch.start_pos, ch.end_pos, include_title=True
                    ))
                    for ch in db.query(Chapter).filter(Chapter.novel_id == novel_id).all()
                ]
                
                # 优化：一次遍历同时完成实体提取、频率统计和章节范围计算（性能提升50%）
                logger.info(f"📝 提取实体中（共{len(chapters_for_extraction)}章）...")
                from collections import Counter
                
                entity_counters = {
                    'characters': Counter(),
                    'locations': Counter(),
                    'organizations': Counter()
                }
                chapter_ranges = {}
                chapter_entity_map = {}  # 记录每章的实体列表（用于构建共现关系）
                
                for chapter_num, chapter_text in chapters_for_extraction:
                    # 只调用一次 HanLP
                    chapter_entities = self.entity_extractor.extract_from_chapter(chapter_text, chapter_num)
                    
                    # 记录本章出现的所有角色实体（仅角色参与关系图）
                    chapter_entity_map[chapter_num] = set(chapter_entities.get('characters', []))
                    
                    # 同时完成频率统计和章节范围计算
                    for entity_type in ['characters', 'locations', 'organizations']:
                        for entity_name in chapter_entities.get(entity_type, []):
                            # 任务1: 统计频率
                            entity_counters[entity_type][entity_name] += 1
                            
                            # 任务2: 记录章节范围
                            if entity_name not in chapter_ranges:
                                chapter_ranges[entity_name] = [chapter_num, chapter_num]
                            else:
                                chapter_ranges[entity_name][1] = chapter_num
                
                # 转换为元组
                chapter_ranges = {name: tuple(range_list) for name, range_list in chapter_ranges.items()}
                
                # 检查是否提取到实体
                total_entities = sum(len(counter) for counter in entity_counters.values())
                if total_entities == 0:
                    logger.warning(f"⚠️ 未提取到任何实体，跳过知识图谱构建")
                    logger.warning(f"   可能原因:")
                    logger.warning(f"   1. HanLP 模型未正确加载")
                    logger.warning(f"   2. 文本内容不适合实体识别")
                    logger.warning(f"   3. 文本格式问题")
                    raise Exception("未提取到任何实体")  # 触发异常处理，跳过知识图谱
                
                logger.info(f"✅ 实体提取完成: 角色{len(entity_counters['characters'])} "
                           f"地点{len(entity_counters['locations'])} "
                           f"组织{len(entity_counters['organizations'])}")
                
                # 更新进度：实体提取完成（80%-85%）
                novel.index_progress = clamp_progress(0.85)
                db.commit()
                tracker.update_step(novel_id, 4, 'processing', 0.25, f'实体提取完成')
                if progress_callback:
                    await progress_callback(novel_id, 0.85, "实体提取完成")
                
                # 4.2 实体去重与合并
                logger.info(f"🔀 实体去重与合并中...")
                merged_entities = {}
                merged_chapter_ranges = {}
                alias_mapping = {}  # ✅ 新增：同时保存别名映射
                
                for entity_type in ['characters', 'locations', 'organizations']:
                    # 获取该类型的所有实体
                    entity_list = list(entity_counters.get(entity_type, {}).keys())
                    
                    # ✅ 只调用一次 merge_entities
                    merge_mapping = self.entity_merger.merge_entities(entity_list)
                    
                    # ✅ 立即保存别名映射（供后续使用）
                    alias_mapping[entity_type] = merge_mapping
                    
                    # 更新计数和章节范围
                    from collections import Counter
                    merged_counter = Counter()
                    for main_name, aliases in merge_mapping.items():
                        # 合并计数
                        total_count = sum(entity_counters[entity_type].get(alias, 0) for alias in aliases)
                        merged_counter[main_name] = total_count
                        
                        # 合并章节范围（取最小和最大）
                        min_chapter = min(chapter_ranges.get(alias, (9999, 9999))[0] for alias in aliases)
                        max_chapter = max(chapter_ranges.get(alias, (0, 0))[1] for alias in aliases)
                        merged_chapter_ranges[main_name] = (min_chapter, max_chapter)
                    
                    merged_entities[entity_type] = merged_counter
                
                # 4.3 存储实体到数据库
                logger.info(f"💾 保存实体到数据库...")
                entity_count = self.entity_service.save_entities(
                    db, novel_id, merged_entities, merged_chapter_ranges
                )
                logger.info(f"✅ 保存了 {entity_count} 个实体")
                
                # 更新进度：实体保存完成（85%-87%）
                novel.index_progress = clamp_progress(0.87)
                db.commit()
                tracker.update_step(novel_id, 4, 'processing', 0.35, f'保存了{entity_count}个实体')
                if progress_callback:
                    await progress_callback(novel_id, 0.87, f"保存了{entity_count}个实体")
                
                # 4.3.5 存储实体别名映射 - ✅ 使用已有的 alias_mapping
                logger.info(f"🔗 保存实体别名映射...")
                alias_count = self.entity_service.save_entity_aliases(
                    db, novel_id, alias_mapping  # 直接使用缓存的结果
                )
                logger.info(f"✅ 保存了 {alias_count} 个实体别名")
                
                # 4.4 构建知识图谱
                logger.info(f"🕸️ 构建知识图谱...")
                
                # 更新进度：开始构建图谱（87%-89%）
                novel.index_progress = clamp_progress(0.89)
                db.commit()
                tracker.update_step(novel_id, 4, 'processing', 0.45, '构建图谱结构中...')
                if progress_callback:
                    await progress_callback(novel_id, 0.89, "构建图谱结构中...")
                
                graph = self.graph_builder.create_graph(novel_id)
                
                # 准备属性提取任务（仅对主要角色，出现≥10次）
                attribute_extractor = EntityAttributeExtractor()
                attribute_tasks = []
                entity_list = []  # 记录实体信息，用于后续添加
                
                # 根据章节数动态调整属性提取阈值
                # 短篇（<20章）：出现3次以上
                # 中篇（20-50章）：出现5次以上
                # 长篇（>50章）：出现10次以上
                if total_chapters < 20:
                    attribute_threshold = 3
                elif total_chapters < 50:
                    attribute_threshold = 5
                else:
                    attribute_threshold = 10
                
                logger.info(f"📊 属性提取阈值: {attribute_threshold}次（基于{total_chapters}章）")
                
                for entity_type in ['characters', 'locations', 'organizations']:
                    for entity_name, count in merged_entities.get(entity_type, {}).items():
                        first_ch, last_ch = merged_chapter_ranges.get(entity_name, (1, total_chapters))
                        entity_list.append((entity_name, entity_type, first_ch, last_ch, count))
                        
                        # 主要角色需要提取属性（使用动态阈值）
                        if entity_type == 'characters' and count >= attribute_threshold:
                            attribute_tasks.append((entity_name, entity_type))
                
                # 批量提取属性
                logger.info(f"📊 提取 {len(attribute_tasks)} 个主要角色的属性...")
                attributes_map = {}
                tasks_with_contexts = []  # 初始化，避免后续访问时变量未定义
                
                if attribute_tasks:
                    # 为每个实体提取上下文
                    # 注意：这里使用已经读取的content变量（来自向量化阶段）
                    for entity_name, entity_type in attribute_tasks:
                        # 获取实体出现的前3个章节的上下文
                        entity_chapters = []
                        for chapter_num, entities in chapter_entity_map.items():
                            if entity_name in entities:
                                entity_chapters.append(chapter_num)
                        
                        if entity_chapters:
                            # 取前3个章节
                            sampled_chapters = sorted(entity_chapters)[:3]
                            contexts = []
                            
                            for ch_num in sampled_chapters:
                                try:
                                    chapter = db.query(Chapter).filter(
                                        Chapter.novel_id == novel.id,
                                        Chapter.chapter_num == ch_num
                                    ).first()
                                    
                                    if chapter:
                                        # 使用字符位置切片（与向量化阶段一致，避免编码问题）
                                        # content变量在index_novel开头已读取
                                        chapter_content = content[chapter.start_pos:chapter.end_pos]
                                        
                                        if not chapter_content:
                                            continue
                                        
                                        # 只取前1000字符（避免过长）
                                        chapter_content = chapter_content[:1000]
                                        
                                        # 查找包含实体的段落
                                        if entity_name in chapter_content:
                                            idx = chapter_content.find(entity_name)
                                            start = max(0, idx - 100)
                                            end = min(len(chapter_content), idx + 200)
                                            context_snippet = chapter_content[start:end]
                                            contexts.append(f"[第{ch_num}章] {context_snippet}")
                                except Exception as e:
                                    logger.warning(f"提取{entity_name}上下文失败: {e}")
                            
                            if contexts:
                                tasks_with_contexts.append((entity_name, entity_type, contexts))
                    
                # 批量提取属性（根据配置选择Batch API或实时API）
                graph_attribute_tokens = 0
                if tasks_with_contexts:
                    use_batch = settings.use_batch_api_for_graph
                    if use_batch:
                        logger.info(f"🚀 启用Batch API模式：无并发限制，完全免费，需等待处理完成")
                    else:
                        logger.info(f"⚡ 使用实时API模式：并发限制3，立即返回")
                    
                    attributes_list, attr_token_stats = await attribute_extractor.extract_batch(
                        tasks_with_contexts,
                        use_batch_api=use_batch
                    )
                    
                    # 记录属性提取的token消耗
                    graph_attribute_tokens = attr_token_stats.get('total_tokens', 0)
                    
                    # 构建属性映射
                    for i, (entity_name, _, _) in enumerate(tasks_with_contexts):
                        if attributes_list[i]:
                            attributes_map[entity_name] = attributes_list[i]
                
                # 添加实体节点（带属性）
                logger.info(f"📝 添加 {len(entity_list)} 个实体节点...")
                for entity_name, entity_type, first_ch, last_ch, count in entity_list:
                    attributes = attributes_map.get(entity_name, {})
                    
                    self.graph_builder.add_entity(
                        graph,
                        entity_name=entity_name,
                        entity_type=entity_type,
                        first_chapter=first_ch,
                        last_chapter=last_ch,
                        mention_count=count,
                        attributes=attributes  # 添加属性
                    )
                
                # 添加角色间的共现关系边
                logger.info(f"🔗 构建角色关系...")
                cooccurrence_count = {}  # (entity1, entity2) -> count
                cooccurrence_chapters = {}  # (entity1, entity2) -> [chapter_nums]
                
                for chapter_num, entities in chapter_entity_map.items():
                    entity_list = list(entities)
                    # 对该章节的任意两个角色建立共现关系
                    for i in range(len(entity_list)):
                        for j in range(i + 1, len(entity_list)):
                            entity1, entity2 = sorted([entity_list[i], entity_list[j]])
                            pair = (entity1, entity2)
                            
                            if pair not in cooccurrence_count:
                                cooccurrence_count[pair] = 0
                                cooccurrence_chapters[pair] = []
                            
                            cooccurrence_count[pair] += 1
                            cooccurrence_chapters[pair].append(chapter_num)
                
                # 根据章节数动态调整关系分类阈值
                # 短篇（<20章）：共现2次即分类，1次为弱关系
                # 中篇（20-50章）：共现3次即分类，2次为弱关系
                # 长篇（>50章）：共现5次即分类，3次为弱关系
                if total_chapters < 20:
                    min_cooccurrence_for_classification = 2
                    min_cooccurrence_for_weak = 1
                elif total_chapters < 50:
                    min_cooccurrence_for_classification = 3
                    min_cooccurrence_for_weak = 2
                else:
                    min_cooccurrence_for_classification = 5
                    min_cooccurrence_for_weak = 3
                
                logger.info(f"📊 关系分类阈值: {min_cooccurrence_for_classification}次（基于{total_chapters}章）")
                
                classification_tasks = []
                weak_relations = []  # 低频关系，不分类直接标记为"共现"
                
                for (entity1, entity2), count in cooccurrence_count.items():
                    chapters = cooccurrence_chapters[(entity1, entity2)]
                    
                    if count >= min_cooccurrence_for_classification:
                        # 高频关系，需要LLM分类
                        classification_tasks.append((entity1, entity2, chapters, count))
                    elif count >= min_cooccurrence_for_weak:
                        # 低频关系，直接标记为"共现"
                        weak_relations.append((entity1, entity2, chapters, count))
                
                logger.info(f"📊 发现 {len(classification_tasks)} 对高频关系需要分类，{len(weak_relations)} 对低频关系")
                
                # 并发分类高频关系
                relation_classifier = RelationshipClassifier()
                classifications = []
                tasks_with_contexts = []  # 初始化，避免后续访问时变量未定义
                
                if classification_tasks:
                    # 提取上下文并准备分类任务
                    logger.info(f"🔍 提取上下文片段...")
                    
                    for entity1, entity2, chapters, count in classification_tasks:
                        # 智能采样章节（早期+中期+后期+均匀分布）
                        sampled_chapters = relation_classifier._smart_chapter_sampling(chapters, max_samples=5)
                        
                        # 提取上下文
                        contexts = await self._extract_cooccurrence_contexts(
                            entity1, entity2, sampled_chapters, novel, db
                        )
                        
                        if contexts:
                            tasks_with_contexts.append((entity1, entity2, contexts, count, chapters))
                        else:
                            # 如果无法提取上下文，降级为"共现"
                            weak_relations.append((entity1, entity2, chapters, count))
                    
                    logger.info(f"✅ 成功提取 {len(tasks_with_contexts)} 对关系的上下文")
                    
                # 批量分类（根据配置选择Batch API或实时API）
                graph_relation_tokens = 0
                if tasks_with_contexts:
                    use_batch = settings.use_batch_api_for_graph
                    if use_batch:
                        logger.info(f"🚀 启用Batch API模式：无并发限制，完全免费，需等待处理完成")
                    else:
                        logger.info(f"⚡ 使用实时API模式：并发限制5，立即返回")
                    
                    classifications, rel_token_stats = await relation_classifier.classify_batch(
                        tasks_with_contexts,
                        use_batch_api=use_batch
                    )
                    
                    # 记录关系分类的token消耗
                    graph_relation_tokens = rel_token_stats.get('total_tokens', 0)
                
                # 根据章节数动态调整演变追踪阈值
                # 短篇（<20章）：共现4次以上
                # 中篇（20-50章）：共现6次以上
                # 长篇（>50章）：共现10次以上
                if total_chapters < 20:
                    evolution_threshold = 4
                elif total_chapters < 50:
                    evolution_threshold = 6
                else:
                    evolution_threshold = 10
                
                evolution_tracker = RelationshipEvolutionTracker()
                evolution_tasks = []
                
                for i, (entity1, entity2, contexts, count, chapters) in enumerate(tasks_with_contexts):
                    if count >= evolution_threshold:  # 高频关系才追踪演变
                        evolution_tasks.append((entity1, entity2, chapters))
                
                logger.info(f"🔄 追踪 {len(evolution_tasks)} 对高频关系的演变（阈值: {evolution_threshold}次）...")
                evolutions = {}
                graph_evolution_tokens = 0
                
                if evolution_tasks:
                    evolutions, evo_token_stats = await evolution_tracker.track_batch(
                        evolution_tasks, novel, db
                    )
                    # 演变追踪的token已在关系分类中统计，这里不重复计数
                    graph_evolution_tokens = evo_token_stats.get('total_tokens', 0)
                
                # 添加分类后的关系边
                relation_count = 0
                
                for i, (entity1, entity2, contexts, count, chapters) in enumerate(tasks_with_contexts):
                    classification = classifications[i]
                    start_chapter = min(chapters)
                    end_chapter = max(chapters)
                    strength = min(count / 20.0, 1.0)
                    
                    # 获取演变轨迹（如果有）
                    evolution = evolutions.get((entity1, entity2), [])
                    
                    # 如果有演变，使用最后一个时期的关系类型
                    final_relation_type = evolution[-1]['type'] if evolution else classification['relation_type']
                    
                    # 添加双向边
                    self.graph_builder.add_relation(
                        graph,
                        source=entity1,
                        target=entity2,
                        relation_type=final_relation_type,
                        start_chapter=start_chapter,
                        end_chapter=end_chapter,
                        strength=strength,
                        confidence=classification['confidence'],
                        cooccurrence_count=count,
                        evolution=evolution  # 添加演变轨迹
                    )
                    
                    self.graph_builder.add_relation(
                        graph,
                        source=entity2,
                        target=entity1,
                        relation_type=final_relation_type,
                        start_chapter=start_chapter,
                        end_chapter=end_chapter,
                        strength=strength,
                        confidence=classification['confidence'],
                        cooccurrence_count=count,
                        evolution=evolution  # 添加演变轨迹
                    )
                    
                    relation_count += 1
                
                # 添加低频"共现"关系边
                for entity1, entity2, chapters, count in weak_relations:
                    start_chapter = min(chapters)
                    end_chapter = max(chapters)
                    strength = min(count / 20.0, 1.0)
                    
                    self.graph_builder.add_relation(
                        graph,
                        source=entity1,
                        target=entity2,
                        relation_type='共现',
                        start_chapter=start_chapter,
                        end_chapter=end_chapter,
                        strength=strength,
                        confidence=0.5,
                        cooccurrence_count=count
                    )
                    
                    self.graph_builder.add_relation(
                        graph,
                        source=entity2,
                        target=entity1,
                        relation_type='共现',
                        start_chapter=start_chapter,
                        end_chapter=end_chapter,
                        strength=strength,
                        confidence=0.5,
                        cooccurrence_count=count
                    )
                    
                    relation_count += 1
                
                logger.info(f"✅ 添加了 {relation_count} 对双向关系（共 {relation_count * 2} 条边）")
                
                # 4.5 计算 PageRank 重要性
                logger.info(f"📊 计算 PageRank 重要性...")
                if graph.number_of_nodes() > 0:
                    pagerank = self.graph_analyzer.compute_pagerank(graph)
                    self.graph_analyzer.update_node_importance(graph, pagerank)
                
                # 更新进度：PageRank计算完成（89%-93%）
                novel.index_progress = clamp_progress(0.93)
                db.commit()
                tracker.update_step(novel_id, 4, 'processing', 0.65, 'PageRank计算完成')
                if progress_callback:
                    await progress_callback(novel_id, 0.93, "PageRank计算完成")
                
                # 4.6 计算章节重要性
                logger.info(f"📈 计算章节重要性...")
                if graph.number_of_nodes() > 0:
                    # 为每个章节计算重要性
                    for chapter in db.query(Chapter).filter(Chapter.novel_id == novel_id).all():
                        importance = self.graph_analyzer.compute_chapter_importance(graph, chapter.chapter_num)
                        chapter.importance_score = importance
                    db.commit()
                    logger.info(f"✅ 章节重要性计算完成")
                else:
                    logger.warning(f"⚠️ 图谱为空，跳过章节重要性计算")
                
                # 更新进度：章节重要性计算完成（93%-96%）
                novel.index_progress = clamp_progress(0.96)
                db.commit()
                tracker.update_step(novel_id, 4, 'processing', 0.80, '章节重要性计算完成')
                if progress_callback:
                    await progress_callback(novel_id, 0.96, "章节重要性计算完成")
                
                # 4.7 保存知识图谱
                logger.info(f"💾 保存知识图谱...")
                self.graph_builder.save_graph(graph, novel_id)
                
                logger.info(f"✅ 知识图谱构建完成: {graph.number_of_nodes()}节点, {graph.number_of_edges()}边")
                
                # 更新进度：知识图谱保存完成（96%-98%）
                novel.index_progress = clamp_progress(0.98)
                db.commit()
                
                # 更新步骤4为完成
                from app.services.indexing_progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                tracker.update_step(novel_id, 4, 'completed', 1.0, f"知识图谱构建完成({graph.number_of_nodes()}节点)")
                
                if progress_callback:
                    await progress_callback(novel_id, 0.98, f"知识图谱构建完成({graph.number_of_nodes()}节点)")
                
            except Exception as e:
                logger.error(f"⚠️ 知识图谱构建失败: {e}")
                logger.exception(e)
                # 知识图谱构建失败不影响整体索引流程
                
                # 更新步骤4为失败，并将进度设置为98%（跳过图谱构建）
                from app.services.indexing_progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                tracker.update_step(novel_id, 4, 'failed', 0.0, "知识图谱构建失败", error=str(e))
                tracker.add_warning(novel_id, f"知识图谱构建失败: {str(e)}")
                
                # 即使图谱失败，也将进度推进到98%
                novel.index_progress = clamp_progress(0.98)
                db.commit()
                
                if progress_callback:
                    await progress_callback(novel_id, 0.98, "知识图谱构建失败，继续完成索引")
            
            # 记录图谱构建阶段的Token消耗（无论成功还是失败都记录）
            from app.services.indexing_progress_tracker import get_progress_tracker
            from app.utils.token_counter import get_token_counter
            tracker = get_progress_tracker()
            token_counter = get_token_counter()
            
            # 记录属性提取的token（即使为0也记录，显示完整流程）
            attr_cost = token_counter.calculate_cost(graph_attribute_tokens, 0, 'glm-4-flash')
            tracker.add_token_usage(
                novel_id=novel_id,
                step_name='图谱-属性提取',
                model_name='glm-4-flash',
                input_tokens=graph_attribute_tokens,
                output_tokens=0,
                cost=attr_cost
            )
            logger.info(f"📊 属性提取Token: {graph_attribute_tokens}")
            
            # 记录关系分类的token（即使为0也记录，显示完整流程）
            rel_cost = token_counter.calculate_cost(graph_relation_tokens, 0, 'glm-4-flash')
            tracker.add_token_usage(
                novel_id=novel_id,
                step_name='图谱-关系分类',
                model_name='glm-4-flash',
                input_tokens=graph_relation_tokens,
                output_tokens=0,
                cost=rel_cost
            )
            logger.info(f"📊 关系分类Token: {graph_relation_tokens}")
            
            # 5. 更新小说统计信息并保存token统计
            novel.total_chunks = total_chunks
            novel.embedding_tokens = total_embedding_tokens  # 保存embedding token消耗
            novel.index_status = IndexStatus.COMPLETED.value
            novel.index_progress = clamp_progress(1.0)  # 确保精确为1.0
            novel.indexed_date = novel.updated_at
            db.commit()
            
            # 计算图谱构建总token
            total_graph_tokens = graph_attribute_tokens + graph_relation_tokens + graph_evolution_tokens
            
            # 保存token统计到token_stats表
            try:
                from app.services.token_stats_service import get_token_stats_service
                token_stats_service = get_token_stats_service()
                
                # 记录Embedding-3模型的token使用
                token_stats_service.record_token_usage(
                    db=db,
                    operation_type='index',
                    operation_id=novel_id,
                    model_name='embedding-3',
                    input_tokens=total_embedding_tokens,
                    output_tokens=0
                )
                
                # 记录GLM-4-Flash图谱构建的token使用
                if total_graph_tokens > 0:
                    token_stats_service.record_token_usage(
                        db=db,
                        operation_type='index',
                        operation_id=novel_id,
                        model_name='glm-4-flash',
                        input_tokens=total_graph_tokens,
                        output_tokens=0
                    )
                
                logger.info(f"✅ Token统计已保存: embedding={total_embedding_tokens}, graph={total_graph_tokens} tokens")
            except Exception as e:
                logger.warning(f"⚠️ Token统计保存失败（不影响索引）: {e}")
            
            # 发送最终进度（包含完整的token统计）
            final_token_stats = {
                "embeddingTokens": total_embedding_tokens,
                "graphAttributeTokens": graph_attribute_tokens,
                "graphRelationTokens": graph_relation_tokens,
                "graphEvolutionTokens": graph_evolution_tokens,
                "graphTotalTokens": total_graph_tokens,
                "totalTokens": total_embedding_tokens + total_graph_tokens
            }
            
            logger.info(f"📊 最终Token统计: embedding={total_embedding_tokens}, graph={total_graph_tokens}, total={final_token_stats['totalTokens']}")
            
            if progress_callback:
                await progress_callback(novel_id, 1.0, "索引完成!", final_token_stats)
            
            logger.info(f"✅ 小说 ID={novel_id} 索引完成: {total_chapters}章, {total_chunks}块, {total_embedding_tokens} tokens")
            return True
            
        except Exception as e:
            logger.error(f"❌ 索引失败: {e}")
            
            # 更新状态为失败
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            if novel:
                novel.index_status = IndexStatus.FAILED.value
                db.commit()
            
            if progress_callback:
                await progress_callback(novel_id, 0.0, f"索引失败: {str(e)}")
            
            return False
    
    def get_indexing_progress(
        self,
        db: Session,
        novel_id: int
    ) -> Dict:
        """
        获取索引进度（包含详细信息）
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
        
        Returns:
            Dict: 进度信息
        """
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return {
                'found': False,
                'message': f'小说 ID={novel_id} 不存在'
            }
        
        # 统计已完成的章节
        completed_chapters = db.query(Chapter).filter(
            Chapter.novel_id == novel_id
        ).count()
        
        # 获取详细信息（如果有）
        from app.services.indexing_progress_tracker import get_progress_tracker
        tracker = get_progress_tracker()
        detail = tracker.get_detail(novel_id)
        
        return {
            'found': True,
            'novel_id': novel_id,
            'status': novel.index_status,
            'progress': novel.index_progress,
            'total_chapters': novel.total_chapters,
            'total_chars': novel.total_chars,
            'completed_chapters': completed_chapters,
            'total_chunks': novel.total_chunks,
            'message': self._get_status_message(novel.index_status, novel.index_progress),
            'detail': detail  # 添加详细信息
        }
    
    async def _extract_cooccurrence_contexts(
        self,
        entity1: str,
        entity2: str,
        chapter_nums: List[int],
        novel: Novel,
        db: Session
    ) -> List[str]:
        """
        提取两个实体共现的上下文片段
        
        Args:
            entity1: 实体1名称
            entity2: 实体2名称
            chapter_nums: 章节号列表
            novel: 小说对象
            db: 数据库会话
        
        Returns:
            上下文片段列表
        """
        contexts = []
        relation_classifier = RelationshipClassifier()
        
        # 读取完整文件内容（使用parser，避免编码问题）
        file_path = Path(novel.file_path)
        if not file_path.exists():
            logger.warning(f"小说文件不存在: {file_path}")
            return contexts
        
        try:
            # 使用与向量化阶段相同的parser读取文件
            if novel.file_format == 'txt':
                full_content, _ = self.txt_parser.parse_file(str(file_path))
            elif novel.file_format == 'epub':
                full_content, _ = self.epub_parser.parse_file(str(file_path))
            else:
                logger.error(f"不支持的文件格式: {novel.file_format}")
                return contexts
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return contexts
        
        for chapter_num in chapter_nums:
            try:
                # 查询章节记录
                chapter = db.query(Chapter).filter(
                    Chapter.novel_id == novel.id,
                    Chapter.chapter_num == chapter_num
                ).first()
                
                if not chapter:
                    continue
                
                # 使用字符位置切片（与向量化阶段一致，避免编码问题）
                content = full_content[chapter.start_pos:chapter.end_pos]
                
                if not content:
                    logger.warning(f"章节{chapter_num}内容为空")
                    continue
                
                # 提取包含两个实体的段落
                paragraph = relation_classifier._extract_paragraph_with_entities(
                    content, entity1, entity2, chapter_num
                )
                
                if paragraph:
                    contexts.append(paragraph)
                
                # 最多提取5个上下文
                if len(contexts) >= 5:
                    break
                    
            except Exception as e:
                logger.warning(f"提取章节{chapter_num}上下文失败: {e}")
                continue
        
        return contexts
    
    @staticmethod
    def _get_status_message(status: str, progress: float) -> str:
        """获取状态消息"""
        if status == IndexStatus.PENDING.value:
            return "等待索引"
        elif status == IndexStatus.PROCESSING.value:
            return f"索引中 ({progress*100:.1f}%)"
        elif status == IndexStatus.COMPLETED.value:
            return "索引完成"
        elif status == IndexStatus.FAILED.value:
            return "索引失败"
        else:
            return "未知状态"


# 全局索引服务实例
_indexing_service: Optional[IndexingService] = None


def get_indexing_service() -> IndexingService:
    """获取全局索引服务实例（单例）"""
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service

