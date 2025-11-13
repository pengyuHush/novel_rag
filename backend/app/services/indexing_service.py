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
        
        logger.info("✅ 索引服务初始化完成")
    
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
            
            # 4. 更新小说统计信息
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

