"""
章节管理API - User Story 2: 在线阅读
实现章节列表、章节内容获取、章节缓存等功能
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from functools import lru_cache
import os

from app.models.database import Novel, Chapter
from app.db.init_db import get_db_session
from app.models.schemas import ChapterListItem, ChapterContent
from app.utils.encoding_detector import EncodingDetector

router = APIRouter(
    prefix="/api/novels/{novel_id}/chapters",
    tags=["chapters"],
    responses={404: {"description": "小说或章节不存在"}},
)


# ==================== 章节缓存 ====================

class ChapterCache:
    """简单的内存缓存,最多缓存100个章节内容"""
    
    def __init__(self, max_size: int = 100):
        self._cache = {}
        self._max_size = max_size
        self._access_order = []
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存内容"""
        if key in self._cache:
            # 更新访问顺序(LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def set(self, key: str, value: str):
        """设置缓存内容"""
        # 如果已存在,更新访问顺序
        if key in self._cache:
            self._access_order.remove(key)
        # 如果缓存已满,删除最久未使用的
        elif len(self._cache) >= self._max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = value
        self._access_order.append(key)
    
    def clear_novel(self, novel_id: int):
        """清除特定小说的所有缓存"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"novel_{novel_id}_")]
        for key in keys_to_remove:
            del self._cache[key]
            self._access_order.remove(key)


# 全局缓存实例
chapter_cache = ChapterCache(max_size=100)


# ==================== API端点 ====================

@router.get("", response_model=List[ChapterListItem])
def get_chapter_list(
    novel_id: int,
    db: Session = Depends(get_db_session)
):
    """
    T076: 获取章节列表
    
    返回指定小说的所有章节列表(章节号、标题、字数)
    """
    # 验证小说存在
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail=f"小说ID {novel_id} 不存在")
    
    # 获取所有章节
    chapters = db.query(Chapter).filter(
        Chapter.novel_id == novel_id
    ).order_by(Chapter.chapter_num).all()
    
    # 转换为响应模型
    return [
        ChapterListItem(
            num=chapter.chapter_num,
            title=chapter.chapter_title,
            char_count=chapter.char_count
        )
        for chapter in chapters
    ]


@router.get("/{chapter_num}", response_model=ChapterContent)
def get_chapter_content(
    novel_id: int,
    chapter_num: int,
    db: Session = Depends(get_db_session)
):
    """
    T077: 获取章节内容
    
    返回指定章节的完整内容,包括导航信息(上一章/下一章)
    """
    # 验证小说存在
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail=f"小说ID {novel_id} 不存在")
    
    # 获取章节信息
    chapter = db.query(Chapter).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_num == chapter_num
    ).first()
    
    if not chapter:
        raise HTTPException(
            status_code=404, 
            detail=f"小说ID {novel_id} 的第 {chapter_num} 章不存在"
        )
    
    # 尝试从缓存读取
    cache_key = f"novel_{novel_id}_chapter_{chapter_num}"
    content = chapter_cache.get(cache_key)
    
    # 缓存未命中,从文件读取
    if content is None:
        content = _read_chapter_from_file(novel, chapter)
        # 写入缓存
        chapter_cache.set(cache_key, content)
    
    # 获取导航信息
    prev_chapter = db.query(Chapter.chapter_num).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_num < chapter_num
    ).order_by(Chapter.chapter_num.desc()).first()
    
    next_chapter = db.query(Chapter.chapter_num).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_num > chapter_num
    ).order_by(Chapter.chapter_num).first()
    
    return ChapterContent(
        chapter_num=chapter_num,
        title=chapter.chapter_title,
        content=content,
        prev_chapter=prev_chapter[0] if prev_chapter else None,
        next_chapter=next_chapter[0] if next_chapter else None,
        total_chapters=novel.total_chapters
    )


# ==================== 辅助函数 ====================

def _read_chapter_from_file(novel: Novel, chapter: Chapter) -> str:
    """
    从原文件中读取章节内容
    
    Args:
        novel: 小说对象
        chapter: 章节对象
    
    Returns:
        章节文本内容
    """
    file_path = novel.file_path
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=500, 
            detail=f"小说文件不存在: {file_path}"
        )
    
    # 检测文件编码
    detection = EncodingDetector.detect_file_encoding(file_path)
    encoding = detection['encoding']
    
    # 处理常见编码别名
    if encoding and encoding.lower() in ['gb2312', 'gb18030']:
        encoding = 'gbk'  # GBK兼容GB2312和GB18030
    
    # 读取章节内容(根据start_pos和end_pos)
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            f.seek(chapter.start_pos)
            content = f.read(chapter.end_pos - chapter.start_pos)
        return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"读取章节内容失败: {str(e)}"
        )


# ==================== 管理端点 ====================

@router.delete("/{chapter_num}/cache")
def clear_chapter_cache(
    novel_id: int,
    chapter_num: int
):
    """
    清除特定章节的缓存
    (管理功能,可选实现)
    """
    cache_key = f"novel_{novel_id}_chapter_{chapter_num}"
    if cache_key in chapter_cache._cache:
        del chapter_cache._cache[cache_key]
        chapter_cache._access_order.remove(cache_key)
        return {"message": f"已清除章节 {chapter_num} 的缓存"}
    return {"message": "缓存不存在"}


@router.delete("/cache")
def clear_novel_cache(novel_id: int):
    """
    清除整本小说的缓存
    (管理功能,可选实现)
    """
    chapter_cache.clear_novel(novel_id)
    return {"message": f"已清除小说 {novel_id} 的所有章节缓存"}

