"""
健康检查API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.init_db import get_db_session
from app.core.chromadb_client import get_chroma_client
from app.core.config import settings

router = APIRouter(tags=["健康检查"])
logger = logging.getLogger(__name__)


@router.get("/health", summary="健康检查")
async def health_check():
    """
    基本健康检查
    
    返回服务状态和版本信息
    """
    return {
        "status": "healthy",
        "service": "novel-rag-backend",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed", summary="详细健康检查")
async def detailed_health_check(db: Session = Depends(get_db_session)):
    """
    详细健康检查
    
    检查各个组件的健康状态：
    - 数据库连接
    - ChromaDB连接
    - 文件存储
    """
    health_status = {
        "service": "novel-rag-backend",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # 检查数据库
    try:
        # 执行简单查询测试连接
        db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "SQLite"
        }
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 检查ChromaDB
    try:
        chroma_client = get_chroma_client()
        collections = chroma_client.list_collections()
        health_status["components"]["chromadb"] = {
            "status": "healthy",
            "collections_count": len(collections)
        }
    except Exception as e:
        logger.error(f"ChromaDB健康检查失败: {e}")
        health_status["components"]["chromadb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 检查文件存储
    try:
        from pathlib import Path
        upload_dir = Path(settings.upload_dir)
        graph_dir = Path(settings.graph_dir)
        
        health_status["components"]["file_storage"] = {
            "status": "healthy",
            "upload_dir": str(upload_dir),
            "upload_dir_exists": upload_dir.exists(),
            "graph_dir": str(graph_dir),
            "graph_dir_exists": graph_dir.exists()
        }
    except Exception as e:
        logger.error(f"文件存储健康检查失败: {e}")
        health_status["components"]["file_storage"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 检查智谱AI配置
    try:
        has_api_key = bool(settings.zhipu_api_key and settings.zhipu_api_key != "your_zhipuai_api_key_here")
        health_status["components"]["zhipu_ai"] = {
            "status": "configured" if has_api_key else "not_configured",
            "default_model": settings.zhipu_default_model,
            "api_key_configured": has_api_key
        }
    except Exception as e:
        logger.error(f"智谱AI配置检查失败: {e}")
        health_status["components"]["zhipu_ai"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 计算总体状态
    all_healthy = all(
        comp.get("status") in ["healthy", "configured"]
        for comp in health_status["components"].values()
    )
    
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status


@router.get("/health/ready", summary="就绪检查")
async def readiness_check(db: Session = Depends(get_db_session)):
    """
    就绪检查（Kubernetes readiness probe）
    
    检查服务是否准备好接收流量
    """
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        
        # 检查ChromaDB
        chroma_client = get_chroma_client()
        chroma_client.list_collections()
        
        return {"ready": True}
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return {"ready": False, "error": str(e)}


@router.get("/health/live", summary="存活检查")
async def liveness_check():
    """
    存活检查（Kubernetes liveness probe）
    
    检查服务是否存活
    """
    return {"alive": True}

