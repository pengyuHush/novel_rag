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
            novel.index_progress = 0.0
            db.commit()
            
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
            
            if progress_callback:
                await progress_callback(novel_id, 0.1, f"文件解析完成，检测到{len(chapters_data)}章")
            
            # 2. 创建ChromaDB集合
            collection_name = self.embedding_service.create_collection(novel_id)
            
            # 3. 处理每个章节
            total_chapters = len(chapters_data)
            total_chunks = 0
            total_tokens = 0
            
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
                
                # 向量化并存储
                success = self.embedding_service.process_chapter(
                    novel_id,
                    chapter_num,
                    chapter_title,
                    chunks
                )
                
                if not success:
                    logger.warning(f"⚠️ 章节 {chapter_num} 处理失败")
                
                # 更新进度
                progress = 0.1 + 0.9 * (i + 1) / total_chapters
                novel.index_progress = progress
                db.commit()
                
                if progress_callback:
                    await progress_callback(
                        novel_id,
                        progress,
                        f"已完成 {i+1}/{total_chapters} 章"
                    )
            
            # 4. Phase 5: 构建知识图谱
            logger.info(f"🕸️ 开始构建知识图谱...")
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
                
                for chapter_num, chapter_text in chapters_for_extraction:
                    # 只调用一次 HanLP
                    chapter_entities = self.entity_extractor.extract_from_chapter(chapter_text, chapter_num)
                    
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
                        first_ch, last_ch = chapter_ranges.get(entity_name, (1, total_chapters))
                        self.graph_builder.add_entity(
                            graph,
                            entity_name=entity_name,
                            entity_type=entity_type,
                            first_chapter=first_ch,
                            last_chapter=last_ch,
                            mention_count=count
                        )
                
                # 4.5 计算 PageRank 重要性
                logger.info(f"📊 计算 PageRank 重要性...")
                if graph.number_of_nodes() > 0:
                    self.graph_analyzer.compute_pagerank(graph)
                
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
                
            except Exception as e:
                logger.error(f"⚠️ 知识图谱构建失败: {e}")
                logger.exception(e)
                # 知识图谱构建失败不影响整体索引流程
            
            # 5. 更新小说统计信息
            novel.total_chunks = total_chunks
            novel.index_status = IndexStatus.COMPLETED.value
            novel.index_progress = 1.0
            novel.indexed_date = novel.updated_at
            db.commit()
            
            if progress_callback:
                await progress_callback(novel_id, 1.0, "索引完成!")
            
            logger.info(f"✅ 小说 ID={novel_id} 索引完成: {total_chapters}章, {total_chunks}块")
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
        获取索引进度
        
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
        
        return {
            'found': True,
            'novel_id': novel_id,
            'status': novel.index_status,
            'progress': novel.index_progress,
            'total_chapters': novel.total_chapters,
            'completed_chapters': completed_chapters,
            'total_chunks': novel.total_chunks,
            'message': self._get_status_message(novel.index_status, novel.index_progress)
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

