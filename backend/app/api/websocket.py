"""
WebSocket API端点
提供实时进度推送功能
"""

import logging
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.db.init_db import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()

# 管理活跃的WebSocket连接
class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # novel_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, novel_id: int):
        """连接WebSocket"""
        await websocket.accept()
        if novel_id not in self.active_connections:
            self.active_connections[novel_id] = set()
        self.active_connections[novel_id].add(websocket)
        logger.info(f"📡 WebSocket连接: novel_id={novel_id}, 当前连接数={len(self.active_connections[novel_id])}")
    
    def disconnect(self, websocket: WebSocket, novel_id: int):
        """断开WebSocket"""
        if novel_id in self.active_connections:
            self.active_connections[novel_id].discard(websocket)
            if not self.active_connections[novel_id]:
                del self.active_connections[novel_id]
        logger.info(f"📡 WebSocket断开: novel_id={novel_id}")
    
    async def send_progress(
        self,
        novel_id: int,
        progress: float,
        message: str,
        status: str = "processing",
        token_stats: Optional[Dict[str, Any]] = None
    ):
        """
        发送进度更新到所有监听该小说的客户端
        
        Args:
            novel_id: 小说ID
            progress: 进度 (0.0-1.0)
            message: 进度消息
            status: 状态 (pending, processing, completed, failed)
            token_stats: Token统计信息（可选）
        """
        if novel_id not in self.active_connections:
            return
        
        data = {
            "type": "progress",
            "novel_id": novel_id,
            "progress": progress,
            "message": message,
            "status": status
        }
        
        # 添加token统计信息（如果有）
        if token_stats:
            data["tokenStats"] = token_stats
        
        # 移除已关闭的连接
        dead_connections = set()
        
        for websocket in self.active_connections[novel_id]:
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(data)
                else:
                    dead_connections.add(websocket)
            except Exception as e:
                logger.error(f"发送进度失败: {e}")
                dead_connections.add(websocket)
        
        # 清理死连接
        for websocket in dead_connections:
            self.disconnect(websocket, novel_id)
    
    async def broadcast_error(self, novel_id: int, error_message: str):
        """广播错误消息"""
        await self.send_progress(novel_id, 0.0, error_message, status="failed")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/progress/{novel_id}")
async def progress_websocket(websocket: WebSocket, novel_id: int):
    """
    索引进度WebSocket端点
    
    客户端连接后会接收实时的索引进度更新
    
    消息格式:
    {
        "type": "progress",
        "novel_id": 1,
        "progress": 0.5,  // 0.0 ~ 1.0
        "message": "已完成 50/100 章",
        "status": "processing"  // pending, processing, completed, failed
    }
    """
    await manager.connect(websocket, novel_id)
    
    try:
        # 立即发送当前状态
        db = next(get_db_session())
        try:
            from app.services.indexing_service import get_indexing_service
            indexing_service = get_indexing_service()
            progress_info = indexing_service.get_indexing_progress(db, novel_id)
            
            if progress_info['found']:
                await websocket.send_json({
                    "type": "progress",
                    "novel_id": novel_id,
                    "progress": progress_info['progress'],
                    "message": progress_info['message'],
                    "status": progress_info['status'],
                    "total_chapters": progress_info.get('total_chapters', 0),
                    "completed_chapters": progress_info.get('completed_chapters', 0),
                    "total_chunks": progress_info.get('total_chunks', 0),
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": progress_info['message']
                })
        finally:
            db.close()
        
        # 保持连接，等待客户端消息或断开
        while True:
            try:
                # 接收客户端消息（心跳包或其他）
                data = await websocket.receive_text()
                logger.debug(f"收到客户端消息: {data}")
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        logger.info(f"客户端主动断开: novel_id={novel_id}")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        manager.disconnect(websocket, novel_id)


async def progress_callback(
    novel_id: int, 
    progress: float, 
    message: str,
    token_stats: Optional[Dict[str, Any]] = None
):
    """
    进度回调函数
    供IndexingService调用，推送进度更新
    
    Args:
        novel_id: 小说ID
        progress: 进度 (0.0-1.0)
        message: 进度消息
        token_stats: Token统计信息（可选）
    """
    status = "processing"
    if progress >= 1.0:
        status = "completed"
    elif progress == 0.0 and "失败" in message:
        status = "failed"
    
    await manager.send_progress(novel_id, progress, message, status, token_stats)

