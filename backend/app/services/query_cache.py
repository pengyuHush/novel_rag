"""
查询缓存服务
实现内存缓存以提升高频查询的响应速度
"""

import hashlib
import logging
import time
from typing import Optional, Any, Dict
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class QueryCacheService:
    """查询缓存服务"""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """
        初始化缓存服务
        
        Args:
            maxsize: 最大缓存条目数
            ttl: 缓存过期时间（秒），默认 1 小时
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hit_count = 0
        self.miss_count = 0
        logger.info(f"✅ 查询缓存服务初始化 (maxsize={maxsize}, ttl={ttl}s)")
    
    def _generate_key(
        self, 
        novel_id: int, 
        query: str, 
        model: str,
        enable_query_rewrite: bool = True,
        enable_query_decomposition: bool = True
    ) -> str:
        """
        生成缓存键
        
        Args:
            novel_id: 小说ID
            query: 查询文本
            model: 模型名称
            enable_query_rewrite: 是否启用查询改写
            enable_query_decomposition: 是否启用查询分解
        
        Returns:
            str: 缓存键（哈希值）
        """
        # 将配置参数也包含在key中，确保不同配置不会使用相同缓存
        key_string = f"{novel_id}:{query}:{model}:{enable_query_rewrite}:{enable_query_decomposition}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get(
        self, 
        novel_id: int, 
        query: str, 
        model: str,
        enable_query_rewrite: bool = True,
        enable_query_decomposition: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果
        
        Args:
            novel_id: 小说ID
            query: 查询文本
            model: 模型名称
            enable_query_rewrite: 是否启用查询改写
            enable_query_decomposition: 是否启用查询分解
        
        Returns:
            Optional[Dict]: 缓存的结果，如果不存在返回 None
        """
        key = self._generate_key(novel_id, query, model, enable_query_rewrite, enable_query_decomposition)
        
        if key in self.cache:
            self.hit_count += 1
            logger.info(f"🎯 缓存命中 (命中率: {self.get_hit_rate():.1%})")
            logger.debug(f"🔧 [DEBUG] 缓存key参数: rewrite={enable_query_rewrite}, decomposition={enable_query_decomposition}")
            return self.cache[key]
        else:
            self.miss_count += 1
            logger.debug(f"⚪ 缓存未命中")
            logger.debug(f"🔧 [DEBUG] 缓存key参数: rewrite={enable_query_rewrite}, decomposition={enable_query_decomposition}")
            return None
    
    def set(
        self, 
        novel_id: int, 
        query: str, 
        model: str, 
        result: Dict[str, Any],
        enable_query_rewrite: bool = True,
        enable_query_decomposition: bool = True
    ):
        """
        设置缓存
        
        Args:
            novel_id: 小说ID
            query: 查询文本
            model: 模型名称
            result: 查询结果
            enable_query_rewrite: 是否启用查询改写
            enable_query_decomposition: 是否启用查询分解
        """
        key = self._generate_key(novel_id, query, model, enable_query_rewrite, enable_query_decomposition)
        self.cache[key] = {
            'result': result,
            'cached_at': time.time()
        }
        logger.debug(f"💾 结果已缓存 (当前缓存数: {len(self.cache)})")
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("🗑️ 缓存已清空")
    
    def clear_novel(self, novel_id: int):
        """
        清空指定小说的缓存
        
        Args:
            novel_id: 小说ID
        """
        # 由于我们使用哈希键，无法直接按 novel_id 过滤
        # 简单实现：清空所有缓存（实际使用中可以改进为带前缀的键）
        logger.warning(f"⚠️ 清空所有缓存（包含 novel_id={novel_id}）")
        self.clear()
    
    def get_hit_rate(self) -> float:
        """
        获取缓存命中率
        
        Returns:
            float: 命中率 (0.0-1.0)
        """
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'size': len(self.cache),
            'maxsize': self.cache.maxsize,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self.get_hit_rate()
        }


# 全局缓存服务实例
_query_cache: Optional[QueryCacheService] = None


def get_query_cache() -> QueryCacheService:
    """获取全局查询缓存实例（单例）"""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCacheService()
    return _query_cache

