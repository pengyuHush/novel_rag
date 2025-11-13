"""
文件存储工具类
"""

import shutil
import hashlib
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileStorage:
    """文件存储管理类"""
    
    def __init__(self):
        """初始化文件存储"""
        self.upload_dir = Path(settings.upload_dir)
        self.graph_dir = Path(settings.graph_dir)
        
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.graph_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ 文件存储初始化完成")
    
    def save_upload_file(
        self,
        file: BinaryIO,
        filename: str,
        novel_id: Optional[int] = None
    ) -> str:
        """
        保存上传的文件
        
        Args:
            file: 文件对象
            filename: 原始文件名
            novel_id: 小说ID（可选）
        
        Returns:
            str: 保存的文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(filename).suffix
            
            if novel_id:
                new_filename = f"novel_{novel_id}_{timestamp}{file_ext}"
            else:
                # 使用文件内容的hash作为唯一标识
                file.seek(0)
                file_hash = hashlib.md5(file.read()).hexdigest()[:8]
                file.seek(0)
                new_filename = f"{timestamp}_{file_hash}{file_ext}"
            
            # 保存文件
            file_path = self.upload_dir / new_filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file, f)
            
            logger.info(f"✅ 文件已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ 保存文件失败: {e}")
            raise
    
    def get_file_path(self, filename: str) -> Path:
        """获取文件完整路径"""
        return self.upload_dir / filename
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 是否删除成功
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"✅ 文件已删除: {file_path}")
                return True
            else:
                logger.warning(f"⚠️ 文件不存在: {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ 删除文件失败: {e}")
            return False
    
    def save_graph_file(self, novel_id: int, graph_data: bytes) -> str:
        """
        保存知识图谱文件（pickle格式）
        
        Args:
            novel_id: 小说ID
            graph_data: 图谱数据（二进制）
        
        Returns:
            str: 保存的文件路径
        """
        try:
            filename = f"novel_{novel_id}_graph.pkl"
            file_path = self.graph_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(graph_data)
            
            logger.info(f"✅ 知识图谱已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ 保存知识图谱失败: {e}")
            raise
    
    def load_graph_file(self, novel_id: int) -> Optional[bytes]:
        """
        加载知识图谱文件
        
        Args:
            novel_id: 小说ID
        
        Returns:
            Optional[bytes]: 图谱数据，如果不存在返回None
        """
        try:
            filename = f"novel_{novel_id}_graph.pkl"
            file_path = self.graph_dir / filename
            
            if not file_path.exists():
                logger.warning(f"⚠️ 知识图谱文件不存在: {file_path}")
                return None
            
            with open(file_path, "rb") as f:
                data = f.read()
            
            logger.info(f"✅ 知识图谱已加载: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ 加载知识图谱失败: {e}")
            raise
    
    def delete_graph_file(self, novel_id: int) -> bool:
        """删除知识图谱文件"""
        filename = f"novel_{novel_id}_graph.pkl"
        file_path = self.graph_dir / filename
        return self.delete_file(str(file_path))
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        try:
            upload_files = list(self.upload_dir.glob("*"))
            graph_files = list(self.graph_dir.glob("*.pkl"))
            
            upload_size = sum(f.stat().st_size for f in upload_files if f.is_file())
            graph_size = sum(f.stat().st_size for f in graph_files if f.is_file())
            
            return {
                "upload_files_count": len(upload_files),
                "upload_files_size_mb": upload_size / (1024 * 1024),
                "graph_files_count": len(graph_files),
                "graph_files_size_mb": graph_size / (1024 * 1024),
                "total_size_mb": (upload_size + graph_size) / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"❌ 获取存储统计失败: {e}")
            return {}


# 全局文件存储实例
_file_storage: Optional[FileStorage] = None


def get_file_storage() -> FileStorage:
    """获取全局文件存储实例（单例）"""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage

