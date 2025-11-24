"""
向量化服务
调用智谱AI Embedding-3进行文本向量化
"""

import logging
import time
from typing import List, Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.zhipu_client import get_zhipu_client
from app.core.chromadb_client import get_chroma_client
from app.core.config import settings
from app.utils.token_counter import get_token_counter

logger = logging.getLogger(__name__)


class EmbeddingService:
    """向量化服务"""
    
    def __init__(self):
        """初始化向量化服务"""
        self.zhipu_client = get_zhipu_client()
        self.chroma_client = get_chroma_client()
        self.token_counter = get_token_counter()
        self.batch_size = settings.embedding_batch_size  # 批量处理大小（从配置读取）
        logger.info(f"✅ 向量化服务初始化完成 (batch_size={self.batch_size})")
    
    def embed_texts(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> Tuple[List[List[float]], int]:
        """
        批量向量化文本
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
        
        Returns:
            Tuple[List[List[float]], int]: (向量列表, 消耗的token数)
        """
        if not texts:
            return [], 0
        
        batch_size = batch_size or self.batch_size
        all_embeddings = []
        total_tokens = 0
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(texts) - 1)//batch_size + 1
            logger.info(f"🔄 正在向量化批次 {batch_num}/{total_batches}...")
            
            # 计算本批次的token消耗
            batch_tokens = sum(self.token_counter.count_tokens(text) for text in batch)
            total_tokens += batch_tokens
            
            try:
                # 调用智谱AI
                embeddings = self.zhipu_client.embed_texts(batch)
                all_embeddings.extend(embeddings)
                
            except Exception as e:
                logger.error(f"❌ 批次 {batch_num} 向量化失败: {e}")
                # 对失败的批次使用零向量
                zero_embeddings = [[0.0] * settings.embedding_dimension for _ in batch]
                all_embeddings.extend(zero_embeddings)
            
            # 批次间添加延迟，避免请求过于密集
            if i + batch_size < len(texts):
                time.sleep(0.5)
        
        logger.info(f"✅ 完成 {len(all_embeddings)} 个文本的向量化，消耗 {total_tokens} tokens")
        return all_embeddings, total_tokens
    
    def create_collection(self, novel_id: int) -> str:
        """
        为小说创建向量集合
        
        Args:
            novel_id: 小说ID
        
        Returns:
            str: 集合名称
        """
        collection_name = f"novel_{novel_id}"
        
        try:
            self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "novel_id": str(novel_id),
                    "hnsw:space": "cosine",
                    "hnsw:construction_ef": 200,
                    "hnsw:M": 16
                }
            )
            logger.info(f"✅ 创建/获取Collection: {collection_name}")
            return collection_name
            
        except Exception as e:
            logger.error(f"❌ 创建Collection失败: {e}")
            raise
    
    def add_chapter_chunks(
        self,
        collection_name: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata_list: List[Dict]
    ) -> bool:
        """
        添加章节块到向量库
        
        Args:
            collection_name: 集合名称
            chunks: 文本块列表
            embeddings: 向量列表
            metadata_list: 元数据列表
        
        Returns:
            bool: 是否成功
        """
        if not chunks or not embeddings:
            logger.warning("⚠️ 没有内容需要添加")
            return False
        
        try:
            # 生成ID
            ids = [
                f"novel_{metadata['novel_id']}_ch{metadata['chapter_num']}_chunk{metadata['chunk_index']}"
                for metadata in metadata_list
            ]
            
            # 添加到ChromaDB
            self.chroma_client.add_documents(
                collection_name=collection_name,
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadata_list
            )
            
            logger.info(f"✅ 成功添加 {len(chunks)} 个块到 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加到ChromaDB失败: {e}")
            return False
    
    def process_chapter(
        self,
        novel_id: int,
        chapter_num: int,
        chapter_title: str,
        chapter_chunks: List[Dict]
    ) -> Tuple[bool, int]:
        """
        处理单个章节（向量化并存储）
        
        Args:
            novel_id: 小说ID
            chapter_num: 章节编号
            chapter_title: 章节标题
            chapter_chunks: 章节块列表（包含content和metadata）
        
        Returns:
            Tuple[bool, int]: (是否成功, 消耗的token数)
        """
        if not chapter_chunks:
            logger.warning(f"⚠️ 章节 {chapter_num} 没有内容")
            return False, 0
        
        try:
            # 提取文本
            texts = [chunk['content'] for chunk in chapter_chunks]
            
            # 向量化（获取token消耗）
            embeddings, tokens_used = self.embed_texts(texts)
            
            # 准备元数据
            metadata_list = []
            for i, chunk in enumerate(chapter_chunks):
                metadata = {
                    'novel_id': novel_id,
                    'chapter_num': chapter_num,
                    'chapter_title': chapter_title,
                    'chunk_index': i,
                    'char_count': len(chunk['content']),
                }
                # 合并chunk自带的metadata
                if 'metadata' in chunk:
                    metadata.update(chunk['metadata'])
                metadata_list.append(metadata)
            
            # 存储到ChromaDB
            collection_name = f"novel_{novel_id}"
            success = self.add_chapter_chunks(
                collection_name=collection_name,
                chunks=texts,
                embeddings=embeddings,
                metadata_list=metadata_list
            )
            
            return success, tokens_used
            
        except Exception as e:
            logger.error(f"❌ 处理章节 {chapter_num} 失败: {e}")
            return False, 0
    
    async def process_novel_with_batch_api(
        self,
        novel_id: int,
        all_chapters_data: List[Dict]
    ) -> Tuple[bool, int, List[int]]:
        """
        使用 Batch API 批量处理整本小说的向量化
        
        根据智谱AI文档，Embedding-3支持Batch API，限制为10000个请求/批次
        
        Args:
            novel_id: 小说ID
            all_chapters_data: 所有章节数据
                [
                    {
                        'chapter_num': 1,
                        'chapter_title': '第一章',
                        'chunks': [chunk1, chunk2, ...]
                    },
                    ...
                ]
        
        Returns:
            Tuple[bool, int, List[int]]: (是否成功, 总token数, 失败的章节列表)
        """
        from app.services.batch_api_client import get_batch_client
        
        # 先统计总请求数
        total_chunks_count = sum(len(chapter_data['chunks']) for chapter_data in all_chapters_data)
        
        # 🎯 智能判断：请求数 < 阈值时使用实时API
        if total_chunks_count < settings.batch_api_threshold:
            logger.info(f"📊 请求数({total_chunks_count}) < 阈值({settings.batch_api_threshold})，使用实时API（更快）")
            return await self._embed_chapters_realtime(novel_id, all_chapters_data)
        
        logger.info(f"🚀 请求数({total_chunks_count}) ≥ 阈值({settings.batch_api_threshold})，使用Batch API（更省钱）")
        
        # 收集所有chunks并构建batch任务
        batch_tasks = []
        chunk_mapping = []  # 记录每个chunk对应的章节信息
        for chapter_data in all_chapters_data:
            chapter_num = chapter_data['chapter_num']
            chapter_title = chapter_data['chapter_title']
            chunks = chapter_data['chunks']
            
            for chunk_idx, chunk in enumerate(chunks):
                chunk_text = chunk['content']
                custom_id = f"embedding-novel{novel_id}-ch{chapter_num}-chunk{chunk_idx}"
                
                # 构建Batch API任务（使用embedding模型）
                # Embedding 模型需要使用 /v4/embeddings 端点
                batch_tasks.append({
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v4/embeddings",
                    "body": {
                        "model": "embedding-3",
                        "input": chunk_text
                    }
                })
                
                # 记录映射关系
                chunk_mapping.append({
                    'chapter_num': chapter_num,
                    'chapter_title': chapter_title,
                    'chunk_index': chunk_idx,
                    'chunk': chunk,
                    'novel_id': novel_id
                })
        
        logger.info(f"📊 准备批量向量化 {total_chunks_count} 个文本块")
        
        # 检查是否超过限制（10000个请求/批次）
        if len(batch_tasks) > 10000:
            logger.warning(f"⚠️ 文本块数量({len(batch_tasks)})超过Batch API限制(10000)，将分批处理")
            return await self._process_novel_in_batches(
                novel_id, all_chapters_data, batch_tasks, chunk_mapping
            )
        
        # 提交Batch API
        batch_client = get_batch_client()
        
        def progress_callback(batch_id, status, progress, completed, total, failed):
            logger.info(f"📊 向量化进度: {status} | {completed}/{total} ({progress*100:.1f}%) | 失败: {failed}")
        
        try:
            results_map, token_stats = await asyncio.to_thread(
                batch_client.submit_and_wait,
                batch_tasks,
                check_interval=30,
                progress_callback=progress_callback
            )
            
            total_tokens = token_stats.get('total_tokens', 0)
            logger.info(f"📊 Batch API向量化Token统计: {token_stats}")
            
        except Exception as e:
            logger.error(f"❌ Batch API调用失败，降级使用实时API: {e}")
            return await self._fallback_to_realtime_api(novel_id, all_chapters_data)
        
        # 解析结果并存储到ChromaDB
        collection_name = f"novel_{novel_id}"
        failed_chapters = set()
        
        embeddings_by_chapter = {}  # 按章节组织embeddings
        
        for i, chunk_info in enumerate(chunk_mapping):
            custom_id = f"embedding-novel{novel_id}-ch{chunk_info['chapter_num']}-chunk{chunk_info['chunk_index']}"
            
            if custom_id not in results_map:
                logger.warning(f"⚠️ 未找到结果: {custom_id}")
                failed_chapters.add(chunk_info['chapter_num'])
                continue
            
            result = results_map[custom_id]
            
            if result['status'] != 'success':
                logger.warning(f"⚠️ 向量化失败: {custom_id}, 错误: {result.get('error')}")
                failed_chapters.add(chunk_info['chapter_num'])
                continue
            
            # 从返回结果中提取embedding向量
            # Batch API返回格式: data[0].embedding
            try:
                usage = result.get('usage', {})
                embedding = None
                
                # 从data字段提取embedding（batch_api_client已解析）
                if 'data' in result and len(result['data']) > 0:
                    embedding = result['data'][0].get('embedding')
                
                if embedding is None or not isinstance(embedding, list):
                    logger.error(f"❌ 无法提取embedding或格式错误: {custom_id}, result keys: {result.keys()}")
                    failed_chapters.add(chunk_info['chapter_num'])
                    continue
                
                # 验证embedding维度
                if len(embedding) != settings.embedding_dimension:
                    logger.error(f"❌ Embedding维度错误: {custom_id}, expected={settings.embedding_dimension}, got={len(embedding)}")
                    failed_chapters.add(chunk_info['chapter_num'])
                    continue
                
                # 按章节组织
                chapter_num = chunk_info['chapter_num']
                if chapter_num not in embeddings_by_chapter:
                    embeddings_by_chapter[chapter_num] = {
                        'chapter_title': chunk_info['chapter_title'],
                        'chunks': [],
                        'embeddings': [],
                        'metadata_list': []
                    }
                
                embeddings_by_chapter[chapter_num]['chunks'].append(chunk_info['chunk']['content'])
                embeddings_by_chapter[chapter_num]['embeddings'].append(embedding)
                embeddings_by_chapter[chapter_num]['metadata_list'].append({
                    'novel_id': novel_id,
                    'chapter_num': chapter_num,
                    'chapter_title': chunk_info['chapter_title'],
                    'chunk_index': chunk_info['chunk_index'],
                    'char_count': len(chunk_info['chunk']['content'])
                })
                
            except Exception as e:
                logger.error(f"❌ 处理embedding结果失败: {custom_id}, 错误: {e}")
                failed_chapters.add(chunk_info['chapter_num'])
        
        # 批量存储到ChromaDB（按章节）
        for chapter_num, chapter_data in embeddings_by_chapter.items():
            try:
                success = self.add_chapter_chunks(
                    collection_name=collection_name,
                    chunks=chapter_data['chunks'],
                    embeddings=chapter_data['embeddings'],
                    metadata_list=chapter_data['metadata_list']
                )
                
                if not success:
                    failed_chapters.add(chapter_num)
                    
            except Exception as e:
                logger.error(f"❌ 存储章节 {chapter_num} 失败: {e}")
                failed_chapters.add(chapter_num)
        
        success = len(failed_chapters) == 0
        logger.info(f"✅ Batch API向量化完成: 总tokens={total_tokens}, 失败章节数={len(failed_chapters)}")
        
        return success, total_tokens, list(failed_chapters)
    
    async def _process_novel_in_batches(
        self,
        novel_id: int,
        all_chapters_data: List[Dict],
        all_tasks: List[Dict],
        all_mappings: List[Dict]
    ) -> Tuple[bool, int, List[int]]:
        """
        分批处理大量chunks（超过10000个）
        """
        batch_size = 10000
        total_tokens = 0
        all_failed_chapters = set()
        
        for i in range(0, len(all_tasks), batch_size):
            logger.info(f"📦 处理批次 {i//batch_size + 1}/{(len(all_tasks)-1)//batch_size + 1}")
            
            batch_tasks = all_tasks[i:i+batch_size]
            batch_mappings = all_mappings[i:i+batch_size]
            
            # 递归调用（单批次）
            success, tokens, failed = await self.process_novel_with_batch_api(
                novel_id, all_chapters_data
            )
            
            total_tokens += tokens
            all_failed_chapters.update(failed)
        
        return len(all_failed_chapters) == 0, total_tokens, list(all_failed_chapters)
    
    async def _fallback_to_realtime_api(
        self,
        novel_id: int,
        all_chapters_data: List[Dict]
    ) -> Tuple[bool, int, List[int]]:
        """
        降级到实时API处理
        """
        logger.warning("⚠️ 降级使用实时API处理向量化")
        
        total_tokens = 0
        failed_chapters = []
        
        for chapter_data in all_chapters_data:
            chapter_num = chapter_data['chapter_num']
            chapter_title = chapter_data['chapter_title']
            chunks = chapter_data['chunks']
            
            try:
                success, chapter_tokens = self.process_chapter(
                    novel_id, chapter_num, chapter_title, chunks
                )
                
                if success:
                    total_tokens += chapter_tokens
                else:
                    failed_chapters.append(chapter_num)
                    
            except Exception as e:
                logger.error(f"❌ 章节 {chapter_num} 处理失败: {e}")
                failed_chapters.append(chapter_num)
        
        return len(failed_chapters) == 0, total_tokens, failed_chapters
    
    def query_similar_chunks(
        self,
        novel_id: int,
        query_text: str,
        top_k: int = 30,
        chapter_filter: Optional[Dict] = None
    ) -> Dict:
        """
        查询相似文本块
        
        Args:
            novel_id: 小说ID
            query_text: 查询文本
            top_k: 返回Top-K结果
            chapter_filter: 章节过滤条件
        
        Returns:
            Dict: 查询结果
        """
        try:
            # 向量化查询文本
            query_embedding = self.zhipu_client.embed_text(query_text)
            
            # 从ChromaDB检索
            collection_name = f"novel_{novel_id}"
            results = self.chroma_client.query_documents(
                collection_name=collection_name,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=chapter_filter
            )
            
            logger.info(f"✅ 检索到 {len(results.get('ids', [[]])[0])} 个相似块")
            return results
            
        except Exception as e:
            logger.error(f"❌ 相似块查询失败: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}


# 全局向量化服务实例
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """获取全局向量化服务实例（单例）"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

