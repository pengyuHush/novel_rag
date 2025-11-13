"""
小说管理API
"""

import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from app.db.init_db import get_db_session
from app.models.database import Novel, Chapter
from app.models.schemas import (
    NovelResponse, NovelListItem, NovelProgressResponse,
    IndexStatus, FileFormat
)
from app.utils.file_storage import get_file_storage
from app.services.indexing_service import get_indexing_service
from app.core.error_handlers import NovelNotFoundError, FileUploadError

router = APIRouter(prefix="/api/novels", tags=["小说管理"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=NovelResponse, summary="上传小说")
async def upload_novel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="小说文件（TXT或EPUB）"),
    title: str = Form(..., description="小说标题"),
    author: Optional[str] = Form(None, description="作者"),
    db: Session = Depends(get_db_session)
):
    """
    上传小说文件
    
    - 支持TXT和EPUB格式
    - 自动检测编码
    - 后台异步索引
    """
    try:
        # 验证文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.txt', '.epub']:
            raise FileUploadError(f"不支持的文件格式: {file_ext}")
        
        file_format = FileFormat.TXT if file_ext == '.txt' else FileFormat.EPUB
        
        # 保存文件
        logger.info(f"📤 接收文件: {file.filename} ({file.content_type})")
        file_storage = get_file_storage()
        
        # 临时保存文件
        file_path = file_storage.save_upload_file(
            file.file,
            file.filename
        )
        
        # 创建小说记录
        novel = Novel(
            title=title,
            author=author,
            file_path=file_path,
            file_format=file_format.value,
            index_status=IndexStatus.PENDING.value,
            total_chars=0,
            total_chapters=0
        )
        
        db.add(novel)
        db.commit()
        db.refresh(novel)
        
        logger.info(f"✅ 小说记录已创建: ID={novel.id}, 标题={title}")
        
        # 启动后台索引任务
        background_tasks.add_task(
            start_indexing,
            novel.id,
            file_path,
            file_format
        )
        
        return NovelResponse.model_validate(novel)
        
    except FileUploadError:
        raise
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("", response_model=List[NovelListItem], summary="获取小说列表")
async def list_novels(
    skip: int = 0,
    limit: int = 100,
    status: Optional[IndexStatus] = None,
    db: Session = Depends(get_db_session)
):
    """
    获取小说列表
    
    - 支持分页
    - 支持按状态过滤
    """
    query = db.query(Novel)
    
    if status:
        query = query.filter(Novel.index_status == status.value)
    
    query = query.order_by(Novel.upload_date.desc())
    novels = query.offset(skip).limit(limit).all()
    
    return [NovelListItem.model_validate(novel) for novel in novels]


@router.get("/{novel_id}", response_model=NovelResponse, summary="获取小说详情")
async def get_novel(
    novel_id: int,
    db: Session = Depends(get_db_session)
):
    """
    获取小说详情
    """
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    
    if not novel:
        raise NovelNotFoundError(novel_id)
    
    return NovelResponse.model_validate(novel)


@router.delete("/{novel_id}", summary="删除小说")
async def delete_novel(
    novel_id: int,
    db: Session = Depends(get_db_session)
):
    """
    删除小说
    
    - 删除数据库记录
    - 删除上传的文件
    - 删除ChromaDB集合
    """
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    
    if not novel:
        raise NovelNotFoundError(novel_id)
    
    try:
        # 删除文件
        file_storage = get_file_storage()
        file_storage.delete_file(novel.file_path)
        
        # 删除ChromaDB集合
        from app.core.chromadb_client import get_chroma_client
        chroma_client = get_chroma_client()
        try:
            chroma_client.delete_collection(f"novel_{novel_id}")
        except:
            pass  # 集合可能不存在
        
        # 删除数据库记录（CASCADE会自动删除chapters）
        db.delete(novel)
        db.commit()
        
        logger.info(f"✅ 小说已删除: ID={novel_id}")
        
        return {"message": f"小说 {novel.title} 已删除", "novel_id": novel_id}
        
    except Exception as e:
        logger.error(f"❌ 删除小说失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/{novel_id}/progress", response_model=NovelProgressResponse, summary="获取索引进度")
async def get_indexing_progress(
    novel_id: int,
    db: Session = Depends(get_db_session)
):
    """
    获取小说索引进度
    """
    indexing_service = get_indexing_service()
    progress_info = indexing_service.get_indexing_progress(db, novel_id)
    
    if not progress_info.get('found'):
        raise NovelNotFoundError(novel_id)
    
    return NovelProgressResponse(
        novel_id=novel_id,
        status=IndexStatus(progress_info['status']),
        progress=progress_info['progress'],
        current_chapter=progress_info.get('completed_chapters'),
        total_chapters=progress_info['total_chapters'],
        message=progress_info['message']
    )


# ========================================
# 辅助函数
# ========================================

def start_indexing(novel_id: int, file_path: str, file_format: FileFormat):
    """
    启动索引任务（后台任务）
    """
    try:
        logger.info(f"🔄 开始索引小说 ID={novel_id}")
        
        # 创建新的事件循环（后台任务需要）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from app.db.init_db import get_database_url
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 创建独立的数据库会话
        engine = create_engine(get_database_url())
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            indexing_service = get_indexing_service()
            
            # 执行索引
            loop.run_until_complete(
                indexing_service.index_novel(
                    db=db,
                    novel_id=novel_id,
                    file_path=file_path,
                    file_format=file_format
                )
            )
        finally:
            db.close()
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ 索引任务失败: {e}")

