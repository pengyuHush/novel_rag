"""
索引服务
整合文件解析、章节识别、文本分块、向量化等功能
"""

import logging
import asyncio
from typing import Dict, Optional, Callable
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
from app.models.database import Novel, Chapter
from app.models.schemas import IndexStatus, FileFormat

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
            
            if progress_callback:
                await progress_callback(novel_id, 0.1, f"文件解析完成，检测到{len(chapters_data)}章")
            
            # 2. 创建ChromaDB集合
            collection_name = self.embedding_service.create_collection(novel_id)
            
            # 3. 处理每个章节
            total_chapters = len(chapters_data)
            total_chunks = 0
            total_embedding_tokens = 0  # 初始化token计数器
            
            # 更新步骤2为completed，步骤3为processing
            from app.services.indexing_progress_tracker import get_progress_tracker
            tracker = get_progress_tracker()
            tracker.update_step(novel_id, 2, 'completed', 1.0, f'准备处理{total_chapters}个章节')
            tracker.update_step(novel_id, 3, 'processing', 0.0, '开始处理章节...')
            
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
                
                # 更新进度（确保不超过1.0）
                progress = clamp_progress(0.1 + 0.9 * (i + 1) / total_chapters)
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
            
            # 4. Phase 5: 构建知识图谱
            logger.info(f"🕸️ 开始构建知识图谱...")
            
            # 更新步骤4为processing
            tracker.update_step(novel_id, 4, 'processing', 0.0, '开始构建知识图谱...')
            
            if progress_callback:
                await progress_callback(novel_id, 0.95, "开始构建知识图谱...")
            
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
                
                # 4.2 实体去重与合并
                logger.info(f"🔀 实体去重与合并中...")
                merged_entities = {}
                merged_chapter_ranges = {}
                
                for entity_type in ['characters', 'locations', 'organizations']:
                    # 获取该类型的所有实体
                    entity_list = list(entity_counters.get(entity_type, {}).keys())
                    
                    # 合并相似实体
                    merge_mapping = self.entity_merger.merge_entities(entity_list)
                    
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
                
                # 4.4 构建知识图谱
                logger.info(f"🕸️ 构建知识图谱...")
                graph = self.graph_builder.create_graph(novel_id)
                
                # 添加实体节点
                for entity_type in ['characters', 'locations', 'organizations']:
                    for entity_name, count in merged_entities.get(entity_type, {}).items():
                        # 使用合并后的章节范围
                        first_ch, last_ch = merged_chapter_ranges.get(entity_name, (1, total_chapters))
                        self.graph_builder.add_entity(
                            graph,
                            entity_name=entity_name,
                            entity_type=entity_type,
                            first_chapter=first_ch,
                            last_chapter=last_ch,
                            mention_count=count
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
                
                # 添加共现关系边（过滤掉共现次数少于3次的弱关系）
                min_cooccurrence = 3
                relation_count = 0
                for (entity1, entity2), count in cooccurrence_count.items():
                    if count >= min_cooccurrence:
                        chapters = cooccurrence_chapters[(entity1, entity2)]
                        start_chapter = min(chapters)
                        end_chapter = max(chapters)
                        
                        # 根据共现频率计算关系强度（归一化到0-1）
                        strength = min(count / 20.0, 1.0)  # 共现20次以上视为强关系
                        
                        # 添加双向边（共现关系是对称的）
                        self.graph_builder.add_relation(
                            graph,
                            source=entity1,
                            target=entity2,
                            relation_type='共现',
                            start_chapter=start_chapter,
                            end_chapter=end_chapter,
                            strength=strength,
                            cooccurrence_count=count
                        )
                        
                        # 添加反向边
                        self.graph_builder.add_relation(
                            graph,
                            source=entity2,
                            target=entity1,
                            relation_type='共现',
                            start_chapter=start_chapter,
                            end_chapter=end_chapter,
                            strength=strength,
                            cooccurrence_count=count
                        )
                        
                        relation_count += 1
                
                logger.info(f"✅ 添加了 {relation_count} 对双向共现关系（共 {relation_count * 2} 条边）")
                
                # 4.5 计算 PageRank 重要性
                logger.info(f"📊 计算 PageRank 重要性...")
                if graph.number_of_nodes() > 0:
                    pagerank = self.graph_analyzer.compute_pagerank(graph)
                    self.graph_analyzer.update_node_importance(graph, pagerank)
                
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
                
                # 4.7 保存知识图谱
                logger.info(f"💾 保存知识图谱...")
                self.graph_builder.save_graph(graph, novel_id)
                
                logger.info(f"✅ 知识图谱构建完成: {graph.number_of_nodes()}节点, {graph.number_of_edges()}边")
                
                # 更新步骤4
                from app.services.indexing_progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                tracker.update_step(novel_id, 4, 'completed', 1.0, f"知识图谱构建完成({graph.number_of_nodes()}节点)")
                
            except Exception as e:
                logger.error(f"⚠️ 知识图谱构建失败: {e}")
                logger.exception(e)
                # 知识图谱构建失败不影响整体索引流程
                
                # 更新步骤4为失败
                from app.services.indexing_progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                tracker.update_step(novel_id, 4, 'failed', 0.0, "知识图谱构建失败", error=str(e))
                tracker.add_warning(novel_id, f"知识图谱构建失败: {str(e)}")
            
            # 5. 更新小说统计信息并保存token统计
            novel.total_chunks = total_chunks
            novel.embedding_tokens = total_embedding_tokens  # 保存embedding token消耗
            novel.index_status = IndexStatus.COMPLETED.value
            novel.index_progress = clamp_progress(1.0)  # 确保精确为1.0
            novel.indexed_date = novel.updated_at
            db.commit()
            
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
                logger.info(f"✅ Token统计已保存: {total_embedding_tokens} tokens")
            except Exception as e:
                logger.warning(f"⚠️ Token统计保存失败（不影响索引）: {e}")
            
            # 发送最终进度（包含完整的token统计）
            final_token_stats = {
                "embeddingTokens": total_embedding_tokens,
                "totalTokens": total_embedding_tokens
            }
            
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

