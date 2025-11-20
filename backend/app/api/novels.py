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
    
    from app.models.schemas import IndexingDetail
    
    # 构建详细信息
    detail = None
    if progress_info.get('detail'):
        detail = IndexingDetail(**progress_info['detail'])
    
    return NovelProgressResponse(
        novel_id=novel_id,
        status=IndexStatus(progress_info['status']),
        progress=progress_info['progress'],
        current_chapter=progress_info.get('completed_chapters'),
        total_chapters=progress_info['total_chapters'],
        total_chars=progress_info.get('total_chars', 0),
        message=progress_info['message'],
        detail=detail
    )


@router.post("/{novel_id}/append-chapters", response_model=NovelResponse, summary="追加章节")
async def append_chapters(
    novel_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="包含所有章节的完整小说文件"),
    db: Session = Depends(get_db_session)
):
    """
    追加章节到已索引的小说
    
    - 用户上传包含所有章节（旧+新）的完整文件
    - 系统自动跳过已索引的章节，只处理新章节
    - 支持TXT和EPUB格式
    - 后台异步处理
    """
    try:
        # 验证小说是否存在
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise NovelNotFoundError(novel_id)
        
        # 验证小说状态（必须是completed状态才能追加）
        if novel.index_status != IndexStatus.COMPLETED.value:
            raise HTTPException(
                status_code=409,
                detail=f"小说当前状态为 {novel.index_status}，只能对已完成索引的小说追加章节"
            )
        
        # 验证文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.txt', '.epub']:
            raise FileUploadError(f"不支持的文件格式: {file_ext}")
        
        file_format = FileFormat.TXT if file_ext == '.txt' else FileFormat.EPUB
        
        # 验证文件格式是否与原文件一致
        if file_format.value != novel.file_format:
            raise HTTPException(
                status_code=400,
                detail=f"文件格式不匹配：原文件为 {novel.file_format}，上传文件为 {file_format.value}"
            )
        
        logger.info(f"📤 接收追加章节文件: {file.filename} for novel_id={novel_id}")
        
        # 保存文件（替换原文件）
        file_storage = get_file_storage()
        
        # 使用相同的文件名保存，覆盖原文件
        old_file_path = novel.file_path
        new_file_path = file_storage.save_upload_file(
            file.file,
            f"novel_{novel_id}_{Path(file.filename).name}",
            novel_id=novel_id
        )
        
        # 更新文件路径
        novel.file_path = new_file_path
        
        # 删除旧文件（如果路径不同）
        if old_file_path != new_file_path and Path(old_file_path).exists():
            try:
                Path(old_file_path).unlink()
                logger.info(f"✅ 旧文件已删除: {old_file_path}")
            except Exception as e:
                logger.warning(f"⚠️ 删除旧文件失败: {e}")
        
        # 将状态设为processing
        novel.index_status = IndexStatus.PROCESSING.value
        novel.index_progress = 0.0
        db.commit()
        
        logger.info(f"✅ 文件已更新，准备追加章节: novel_id={novel_id}")
        
        # 启动后台追加任务
        background_tasks.add_task(
            start_appending,
            novel_id,
            new_file_path,
            file_format
        )
        
        return NovelResponse.model_validate(novel)
        
    except NovelNotFoundError:
        raise
    except FileUploadError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 追加章节失败: {e}")
        raise HTTPException(status_code=500, detail=f"追加章节失败: {str(e)}")


@router.get("/{novel_id}/token-stats", summary="获取小说Token统计")
async def get_novel_token_stats(
    novel_id: int,
    db: Session = Depends(get_db_session)
):
    """
    获取小说的Token消耗统计
    
    返回该小说索引过程中的详细Token统计信息：
    - 按模型分类的Token消耗
    - Embedding总消耗
    - 估算成本
    """
    try:
        # 验证小说是否存在
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise NovelNotFoundError(novel_id)
        
        # 从token_stats表查询该小说的统计记录
        from app.models.database import TokenStat
        from app.services.token_stats_service import get_token_stats_service
        
        token_stats_service = get_token_stats_service()
        
        # 查询该小说的所有token记录
        stats_records = db.query(TokenStat).filter(
            TokenStat.operation_type == 'index',
            TokenStat.operation_id == novel_id
        ).all()
        
        # 按模型汇总
        by_model = {}
        total_tokens = 0
        total_cost = 0.0
        
        for record in stats_records:
            model_name = record.model_name
            
            if model_name not in by_model:
                by_model[model_name] = {
                    'inputTokens': 0,
                    'outputTokens': 0,
                    'totalTokens': 0,
                    'cost': 0.0
                }
            
            # Embedding模型只有input tokens
            if record.input_tokens:
                by_model[model_name]['inputTokens'] += record.input_tokens
            
            # LLM模型有prompt和completion tokens（这里索引阶段应该只有embedding）
            if record.prompt_tokens:
                by_model[model_name]['promptTokens'] = by_model[model_name].get('promptTokens', 0) + record.prompt_tokens
            if record.completion_tokens:
                by_model[model_name]['completionTokens'] = by_model[model_name].get('completionTokens', 0) + record.completion_tokens
            
            by_model[model_name]['totalTokens'] += record.total_tokens
            by_model[model_name]['cost'] += float(record.estimated_cost or 0.0)
            
            total_tokens += record.total_tokens
            total_cost += float(record.estimated_cost or 0.0)
        
        # 如果没有详细记录，使用Novel表中的embedding_tokens
        if not by_model and novel.embedding_tokens > 0:
            # 计算成本
            from app.utils.token_counter import get_token_counter
            token_counter = get_token_counter()
            cost = token_counter.calculate_cost(novel.embedding_tokens, 0, 'embedding-3')
            
            by_model = {
                'embedding-3': {
                    'inputTokens': novel.embedding_tokens,
                    'totalTokens': novel.embedding_tokens,
                    'cost': cost
                }
            }
            total_tokens = novel.embedding_tokens
            total_cost = cost
        
        logger.info(f"✅ 获取小说 {novel_id} 的Token统计: {total_tokens} tokens, ¥{total_cost:.4f}")
        
        return {
            "novel_id": novel_id,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "by_model": by_model,
            "novel_info": {
                "title": novel.title,
                "total_chapters": novel.total_chapters,
                "total_chunks": novel.total_chunks,
                "index_status": novel.index_status
            }
        }
        
    except NovelNotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Token统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Token统计失败: {str(e)}")


# ========================================
# 辅助函数
# ========================================

def start_indexing(novel_id: int, file_path: str, file_format: FileFormat):
    """
    启动索引任务（后台任务）
    
    注意：不使用progress_callback，因为会导致事件循环冲突
    前端通过轮询数据库获取进度
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
            
            # 执行索引（不使用WebSocket回调，避免事件循环冲突）
            # 前端会通过轮询 /api/novels/{id}/progress 来获取进度
            loop.run_until_complete(
                indexing_service.index_novel(
                    db=db,
                    novel_id=novel_id,
                    file_path=file_path,
                    file_format=file_format,
                    progress_callback=None  # 不使用WebSocket回调
                )
            )
            logger.info(f"✅ 索引任务完成: novel_id={novel_id}")
        finally:
            db.close()
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ 索引任务失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 更新小说状态为失败
        try:
            from app.db.init_db import get_database_url
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(get_database_url())
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            try:
                novel = db.query(Novel).filter(Novel.id == novel_id).first()
                if novel:
                    novel.index_status = IndexStatus.FAILED.value
                    db.commit()
            finally:
                db.close()
        except Exception as inner_e:
            logger.error(f"❌ 更新失败状态失败: {inner_e}")


def start_appending(novel_id: int, file_path: str, file_format: FileFormat):
    """
    启动追加章节任务（后台任务）
    
    Args:
        novel_id: 小说ID
        file_path: 新文件路径
        file_format: 文件格式
    """
    try:
        logger.info(f"🔄 开始追加章节: novel_id={novel_id}")
        
        # 创建新的事件循环
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
            
            # 执行追加章节
            loop.run_until_complete(
                indexing_service.append_chapters(
                    db=db,
                    novel_id=novel_id,
                    file_path=file_path,
                    file_format=file_format,
                    progress_callback=None
                )
            )
            logger.info(f"✅ 追加章节任务完成: novel_id={novel_id}")
        finally:
            db.close()
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ 追加章节任务失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 更新小说状态为失败
        try:
            from app.db.init_db import get_database_url
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(get_database_url())
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            try:
                novel = db.query(Novel).filter(Novel.id == novel_id).first()
                if novel:
                    novel.index_status = IndexStatus.FAILED.value
                    db.commit()
            finally:
                db.close()
        except Exception as inner_e:
            logger.error(f"❌ 更新失败状态失败: {inner_e}")

