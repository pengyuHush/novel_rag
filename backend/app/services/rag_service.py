"""RAG search and indexing service."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from loguru import logger
from redis.asyncio import Redis
from zai import ZhipuAiClient

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.schemas.search import SearchReference, SearchRequest, SearchResponse
from app.utils.hashing import sha256_hash

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError as exc:  # pragma: no cover - dependency guaranteed by pyproject
    raise RuntimeError("qdrant-client must be installed") from exc


EMBEDDING_MODEL = "embedding-3"
CHAT_MODEL = "glm-4.5"


@dataclass
class TokenUsage:
    """Token使用统计（智谱AI API响应）."""
    
    prompt_tokens: int = 0  # 输入token数
    completion_tokens: int = 0  # 输出token数（embedding通常为0）
    total_tokens: int = 0  # 总token数


@dataclass
class EmbeddingResult:
    """Embedding结果，包含向量和token使用统计."""
    
    vectors: List[List[float]]
    usage: TokenUsage


@dataclass
class ChunkPayload:
    id: str
    content: str
    novel_id: str
    novel_title: str | None
    chapter_id: str | None
    chapter_title: str | None
    chapter_number: int | None
    paragraph_index: int
    start_position: int | None
    
    # 🔥 元数据丰富化字段
    characters: List[str] | None = None  # 该chunk中出现的角色
    keywords: List[str] | None = None     # 关键词
    summary: str | None = None            # chunk摘要
    scene_type: str | None = None         # 场景类型（对话/描述/动作/心理）
    emotional_tone: str | None = None     # 情感基调（积极/消极/中性/紧张/温馨等）

    def to_payload(self) -> dict:
        payload = {
            "chunk_id": self.id,
            "content": self.content,
            "novel_id": self.novel_id,
            "novel_title": self.novel_title,
            "chapter_id": self.chapter_id,
            "chapter_title": self.chapter_title,
            "chapter_number": self.chapter_number,
            "paragraph_index": self.paragraph_index,
            "start_position": self.start_position,
        }
        
        # 添加元数据字段（如果存在）
        if self.characters:
            payload["characters"] = self.characters
        if self.keywords:
            payload["keywords"] = self.keywords
        if self.summary:
            payload["summary"] = self.summary
        if self.scene_type:
            payload["scene_type"] = self.scene_type
        if self.emotional_tone:
            payload["emotional_tone"] = self.emotional_tone
            
        return payload


class RAGService:
    """Provide semantic indexing and question answering."""

    def __init__(self, redis_client: Optional[Redis] = None):
        api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        if not api_key:
            logger.warning("ZAI/GLM API key not configured; RAG functionality is limited")
        self.redis = redis_client
        self.client = ZhipuAiClient(api_key=api_key) if api_key else None
        self.qdrant: QdrantClient = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION
    
    @staticmethod
    def _extract_message_content(response) -> str:
        """从智谱AI响应中提取内容.
        
        根据智谱AI官方文档，实际输出内容在 content 字段，
        reasoning_content 是推理过程文本。此函数优先读取 content。
        
        Args:
            response: 智谱AI API响应对象
            
        Returns:
            str: 提取的内容文本
        """
        if not response or not response.choices:
            return ""
        
        message = response.choices[0].message
        # 优先读取 content（实际输出），reasoning_content 是推理过程
        content = message.content or getattr(message, 'reasoning_content', None) or ""
        return content

    async def ensure_collection(self, vector_size: int) -> None:
        collections = self.qdrant.get_collections().collections
        names = {c.name for c in collections}
        if self.collection_name in names:
            return
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )

    async def embed_texts(self, texts: Iterable[str]) -> EmbeddingResult:
        """
        向量化文本并返回结果（包含token使用统计）.
        
        返回:
            EmbeddingResult: 包含向量列表和token使用统计
        """
        texts = list(texts)
        if not texts:
            return EmbeddingResult(vectors=[], usage=TokenUsage())

        if not self.client:
            raise RuntimeError("Zhipu client not configured")

        # 验证文本长度 - 智谱AI embedding-3模型支持最多3072个token
        # 约等于3000-4500个中文字符（按1.5字符=1token估算）
        MAX_TEXT_LENGTH = 3072
        for idx, text in enumerate(texts):
            if len(text) > MAX_TEXT_LENGTH:
                logger.warning(
                    f"Text {idx} length ({len(text)}) exceeds recommended limit ({MAX_TEXT_LENGTH}). "
                    f"Truncating to avoid API error."
                )
                texts[idx] = text[:MAX_TEXT_LENGTH]

        # 验证批次大小 - 智谱AI embedding-3支持最多64条/次
        if len(texts) > 64:
            logger.warning(
                f"Batch size ({len(texts)}) exceeds API limit (64). "
                f"Consider reducing EMBEDDING_BATCH_SIZE to avoid errors."
            )

        try:
            loop = asyncio.get_running_loop()
            # 使用配置的向量维度（支持256/512/1024/2048）
            dimension = settings.EMBEDDING_DIMENSION
            response = await loop.run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=texts,
                    dimensions=dimension  # 新增: 自定义向量维度
                ),
            )
            
            # 提取向量
            vectors = [item.embedding for item in response.data]
            
            # 提取token使用统计（智谱AI API响应）
            usage = TokenUsage()
            if hasattr(response, 'usage') and response.usage:
                usage.prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                usage.completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                usage.total_tokens = getattr(response.usage, 'total_tokens', 0)
                
                logger.info(
                    f"Embedding API call completed: "
                    f"texts={len(texts)}, "
                    f"total_tokens={usage.total_tokens}, "
                    f"prompt_tokens={usage.prompt_tokens}"
                )
            else:
                logger.warning("API response does not contain usage information")
            
            return EmbeddingResult(vectors=vectors, usage=usage)
        except Exception as e:
            error_msg = str(e)
            if "1210" in error_msg or "Too Large" in error_msg:
                logger.error(
                    f"Embedding request too large. Batch size: {len(texts)}, "
                    f"Text lengths: {[len(t) for t in texts]}"
                )
                raise RuntimeError(
                    f"请求数据过大。批次大小: {len(texts)}, "
                    f"最大文本长度: {max(len(t) for t in texts)}字符。"
                    f"请减小CHUNK_SIZE或EMBEDDING_BATCH_SIZE配置。"
                ) from e
            raise

    async def upsert_chunks(self, chunks: Iterable[ChunkPayload], embeddings: Iterable[List[float]]) -> None:
        chunk_list = list(chunks)
        vector_list = list(embeddings)
        if not chunk_list:
            return

        await self.ensure_collection(len(vector_list[0]))

        points = []
        for payload, vector in zip(chunk_list, vector_list, strict=True):
            # 使用UUID5基于chunk_id生成确定性UUID
            # 这样相同的chunk_id总是生成相同的UUID
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, payload.id))
            
            points.append(
                qmodels.PointStruct(
                    id=point_uuid,
                    vector=vector,
                    payload=payload.to_payload(),
                )
            )

        # 使用batch方式上传点
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=qmodels.Batch(
                ids=[p.id for p in points],
                vectors=[p.vector for p in points],
                payloads=[p.payload for p in points],
            ),
        )

    async def delete_novel_chunks(self, novel_id: str) -> None:
        self.qdrant.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(must=[qmodels.FieldCondition(key="novel_id", match=qmodels.MatchValue(value=novel_id))])
            ),
        )
    
    async def _rewrite_query(self, original_query: str) -> List[str]:
        """查询改写 - 生成改写的查询以提高召回率.
        
        Args:
            original_query: 原始查询
            
        Returns:
            List[str]: 改写后的查询列表（不包含原查询）
        """
        if not self.client:
            return []
        
        try:
            prompt = f"""请将下面的问题改写成2个不同但意思相近的版本，用于搜索小说内容。
要求：
1. 保持原问题的核心意图
2. 使用不同的表达方式和关键词
3. 每行一个改写版本，不要编号

原问题：{original_query}

改写版本："""

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": "你是查询改写助手，擅长用不同方式表达同一个问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=200,
                ),
            )
            
            content = self._extract_message_content(response)
            if not content:
                return []
            
            # 解析改写的查询
            rewritten = [line.strip() for line in content.split('\n') if line.strip()]
            # 过滤掉包含"改写"、"版本"等元信息的行
            rewritten = [q for q in rewritten if not any(word in q for word in ['改写', '版本', '：', ':'])]
            
            logger.info(f"Query rewriting: '{original_query}' -> {rewritten}")
            return rewritten[:2]  # 最多返回2个改写
            
        except Exception as e:
            logger.warning(f"Query rewriting failed: {e}")
            return []
    
    async def _expand_context_window(
        self,
        novel_id: str,
        chapter_id: Optional[str],
        paragraph_index: int,
        window_size: int = 1
    ) -> List[str]:
        """扩展上下文窗口 - 获取相邻的chunk内容.
        
        Args:
            novel_id: 小说ID
            chapter_id: 章节ID
            paragraph_index: 段落索引
            window_size: 窗口大小（前后各扩展N个段落）
            
        Returns:
            List[str]: 扩展的上下文内容列表
        """
        if window_size <= 0:
            return []
        
        try:
            expanded_contexts = []
            
            # 构建查询条件：同一章节，段落索引在范围内
            for offset in range(-window_size, window_size + 1):
                if offset == 0:  # 跳过当前段落
                    continue
                
                target_index = paragraph_index + offset
                if target_index < 0:  # 跳过负数索引
                    continue
                
                # 构建过滤条件
                filter_conditions = [
                    qmodels.FieldCondition(key="novel_id", match=qmodels.MatchValue(value=novel_id)),
                    qmodels.FieldCondition(key="paragraph_index", match=qmodels.MatchValue(value=target_index))
                ]
                
                if chapter_id:
                    filter_conditions.append(
                        qmodels.FieldCondition(key="chapter_id", match=qmodels.MatchValue(value=chapter_id))
                    )
                
                # 查询相邻chunk
                results = self.qdrant.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=qmodels.Filter(must=filter_conditions),
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                )
                
                if results and results[0]:
                    for point in results[0]:
                        if point.payload:
                            content = point.payload.get("content", "")
                            if content:
                                expanded_contexts.append(content)
            
            logger.debug(f"Expanded context window: found {len(expanded_contexts)} adjacent chunks")
            return expanded_contexts
            
        except Exception as e:
            logger.warning(f"Context expansion failed: {e}")
            return []
    
    async def _generate_hypothetical_answer(self, query: str) -> str:
        """HyDE: 生成假设性答案用于检索.
        
        与其直接用问题检索，不如让LLM先生成一个假设性答案，
        然后用这个答案的向量去检索。假设答案的语义往往更接近真实答案。
        
        Args:
            query: 用户问题
            
        Returns:
            str: 假设性答案（50-100字）
        """
        if not self.client:
            logger.warning("HyDE: LLM client not available, using original query")
            return query  # 如果LLM不可用，返回原问题
        
        try:
            # 优化策略：不用"假设答案"，而是让模型扩写/改述问题
            # 这样模型更容易理解和生成内容
            prompt = f"""请将下面的问题扩展成一段更详细的描述，包含可能的答案形式和相关背景。

原问题：{query}

扩展描述："""

            # 使用配置的HYDE_MODEL（默认glm-4-flash，更稳定）
            hyde_model = settings.HYDE_MODEL
            
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=hyde_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是小说分析助手。请将用户的简短问题扩展成一段包含上下文和可能答案形式的描述。"
                        },
                        {"role": "user", "content": prompt}
                    ],
                    thinking={
                        "type": "disable",  # 启用深度思考模式
                    },
                    temperature=0.8,  # 稍高温度增加生成多样性
                    max_tokens=200,
                ),
            )
            
            # 详细的响应检查
            if not response:
                logger.error("HyDE: API returned None response")
                return query
            
            if not response.choices:
                logger.error("HyDE: API response has no choices")
                return query
            
            if not response.choices[0].message:
                logger.error("HyDE: API response choice has no message")
                return query
                
            hypothetical = self._extract_message_content(response)
            
            if not hypothetical or not hypothetical.strip():
                logger.warning("HyDE: First attempt generated empty content, trying fallback strategy")
                
                # 备选策略：使用更简单的任务 - 直接扩写问题
                fallback_response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=hyde_model,
                        messages=[
                            {
                                "role": "user",
                                "content": f"请用50-100字扩写这个问题，添加更多细节和上下文：\n\n{query}\n\n扩写："
                            }
                        ],
                        thinking={
                            "type": "disable",  # 启用深度思考模式
                        },
                        temperature=0.7,
                        max_tokens=150,
                    ),
                )
                
                if fallback_response and fallback_response.choices:
                    hypothetical = self._extract_message_content(fallback_response)
                    if hypothetical and hypothetical.strip():
                        hypothetical = hypothetical.strip()
                        logger.info(f"HyDE fallback strategy succeeded (length={len(hypothetical)})")
                        return hypothetical
                
                logger.warning("HyDE: Both strategies failed, using original query")
                return query
            
            hypothetical = hypothetical.strip()
            logger.info(f"HyDE generated hypothetical answer successfully (length={len(hypothetical)})")
            logger.debug(f"Original query: {query}")
            logger.debug(f"Hypothetical answer: {hypothetical[:100]}...")
            
            return hypothetical
                
        except Exception as e:
            logger.error(f"HyDE generation failed with exception: {type(e).__name__}: {str(e)}")
            logger.exception("HyDE generation exception details:")
            return query
    
    async def _simple_rerank(
        self, 
        query: str, 
        results: List[tuple], 
        top_k: int = 10
    ) -> List[tuple]:
        """简单重排序 - 使用LLM评分重新排序候选结果.
        
        Args:
            query: 用户查询
            results: 结果列表 [(point, content), ...]
            top_k: 返回前K个结果
            
        Returns:
            List[tuple]: 重排序后的结果
        """
        if not self.client or len(results) <= 3:
            return results[:top_k]
        
        try:
            # 为每个结果生成相关性评分
            scored_results = []
            
            for point, content in results[:15]:  # 只对前15个候选进行重排序
                # 构建简单的评分prompt
                prompt = f"""请评估以下文本片段与用户问题的相关性，给出1-10的评分（10表示高度相关，1表示不相关）。

用户问题：{query}

文本片段：{content[:300]}

评分（只需输出数字1-10）："""

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=CHAT_MODEL,
                        messages=[
                            {"role": "system", "content": "你是文本相关性评估专家。"},
                            {"role": "user", "content": prompt}
                        ],
                        thinking={
                            "type": "disable",  # 启用深度思考模式
                        },
                        temperature=0.1,
                        max_tokens=10,
                    ),
                )
                
                content_text = self._extract_message_content(response)
                try:
                    # 提取数字评分
                    score = float(''.join(c for c in content_text if c.isdigit() or c == '.'))
                    score = min(max(score, 1.0), 10.0)  # 限制在1-10范围
                except:
                    score = 5.0  # 默认中等分数
                
                # 结合原始向量相似度和LLM评分
                combined_score = (point.score * 0.6 + score / 10.0 * 0.4)
                scored_results.append((point, content, combined_score))
            
            # 按组合分数排序
            scored_results.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Reranking completed: reranked {len(scored_results)} results")
            return [(point, content) for point, content, _ in scored_results[:top_k]]
            
        except Exception as e:
            logger.warning(f"Reranking failed: {e}, falling back to original order")
            return results[:top_k]

    async def search(self, request: SearchRequest) -> SearchResponse:
        if self.redis:
            cache_key = self._cache_key(request)
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return SearchResponse(**data)

        start = time.perf_counter()
        
        # 初始化token统计
        total_tokens = 0
        embedding_tokens = 0
        chat_tokens = 0
        api_calls = 0
        
        # Check if collection exists
        try:
            collections = self.qdrant.get_collections().collections
            collection_names = {c.name for c in collections}
            if self.collection_name not in collection_names:
                # Collection doesn't exist - no data has been indexed yet
                elapsed = time.perf_counter() - start
                return SearchResponse(
                    query=request.query,
                    answer="知识库为空，请先上传并处理小说文本。上传步骤：1) 创建小说记录 2) 上传TXT文件 3) 等待处理完成。",
                    references=[],
                    elapsed=elapsed,
                )
        except Exception as e:
            logger.warning(f"Failed to check collections: {e}")
        
        # 查询列表：原始查询 + 改写查询/HyDE查询（如果启用）
        queries_to_search = [request.query]
        hyde_used = False
        
        # 1. HyDE模式（如果启用，优先使用）
        if settings.ENABLE_HYDE:
            logger.info("Using HyDE mode for enhanced retrieval")
            hypothetical_answer = await self._generate_hypothetical_answer(request.query)
            if hypothetical_answer != request.query:  # 确认生成了假设答案
                # HyDE模式：用假设答案替换原始查询
                queries_to_search = [hypothetical_answer]
                hyde_used = True
                logger.info(f"HyDE mode activated, using hypothetical answer for retrieval")
            else:
                logger.info("HyDE generation failed, falling back to normal mode")
        
        # 2. 查询改写（如果启用且未使用HyDE）
        # 注意：HyDE和查询改写不同时使用，避免过度复杂化
        if not hyde_used and settings.ENABLE_QUERY_REWRITE:
            rewritten_queries = await self._rewrite_query(request.query)
            queries_to_search.extend(rewritten_queries)
            logger.info(f"Using {len(queries_to_search)} queries for multi-query search")
        
        # 3. Embedding阶段 - 将所有查询转为向量
        embedding_result = await self.embed_texts(queries_to_search)
        query_vectors = embedding_result.vectors
        
        # 追踪embedding token
        if embedding_result.usage:
            embedding_tokens = embedding_result.usage.total_tokens
            total_tokens += embedding_tokens
            api_calls += 1

        # 构建过滤条件（小说ID + 元数据过滤）
        filter_conditions = []
        
        # 小说ID过滤
        if request.novel_ids:
            filter_conditions.append(
                qmodels.FieldCondition(
                    key="novel_id",
                    match=qmodels.MatchAny(any=request.novel_ids),
                )
            )
        
        # 🔥 元数据过滤（如果启用）
        if settings.ENABLE_METADATA_FILTERING:
            # 角色过滤
            if request.filter_characters:
                filter_conditions.append(
                    qmodels.FieldCondition(
                        key="characters",
                        match=qmodels.MatchAny(any=request.filter_characters),
                    )
                )
            
            # 场景类型过滤
            if request.filter_scene_type:
                filter_conditions.append(
                    qmodels.FieldCondition(
                        key="scene_type",
                        match=qmodels.MatchValue(value=request.filter_scene_type),
                    )
                )
            
            # 情感基调过滤
            if request.filter_emotional_tone:
                filter_conditions.append(
                    qmodels.FieldCondition(
                        key="emotional_tone",
                        match=qmodels.MatchValue(value=request.filter_emotional_tone),
                    )
                )
        
        filter_condition = qmodels.Filter(must=filter_conditions) if filter_conditions else None

        # 3. 多查询向量检索 - 收集所有结果
        all_results_map = {}  # 用于去重，key为chunk_id
        
        for idx, query_vector in enumerate(query_vectors):
            try:
                results = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=min(request.top_k, settings.MAX_TOP_K),
                    query_filter=filter_condition,
                    with_payload=True,
                    with_vectors=False,
                )
                
                # 合并结果，保留最高分数
                for point in results:
                    chunk_id = point.payload.get("chunk_id") if point.payload else None
                    if chunk_id:
                        if chunk_id not in all_results_map or point.score > all_results_map[chunk_id].score:
                            all_results_map[chunk_id] = point
                
            except Exception as e:
                logger.warning(f"Search failed for query {idx}: {e}")
                continue
        
        # 转换为列表并按分数排序
        merged_results = sorted(all_results_map.values(), key=lambda x: x.score, reverse=True)
        
        if not merged_results:
            # Handle no results
            elapsed = time.perf_counter() - start
            return SearchResponse(
                query=request.query,
                answer="知识库中没有找到相关内容。请确保已上传并处理了小说文本。",
                references=[],
                elapsed=elapsed,
            )

        # 4. 🔥 元数据加权（如果启用）
        if settings.ENABLE_METADATA_WEIGHTING and merged_results:
            logger.info("Applying metadata-based score weighting")
            merged_results = self._apply_metadata_weighting(merged_results, request)
        
        # 5. 相似度阈值过滤
        min_score = settings.MIN_RELEVANCE_SCORE
        filtered_results = [point for point in merged_results if point.score >= min_score]
        
        if not filtered_results:
            logger.info(f"All results filtered out by relevance threshold {min_score}")
            filtered_results = merged_results[:3]  # 至少保留前3个结果
        
        logger.info(f"Retrieved {len(merged_results)} results, {len(filtered_results)} after filtering (threshold={min_score})")
        
        # 6. 重排序（如果配置启用）
        results_with_content = [(point, point.payload.get("content", "")) for point in filtered_results if point.payload]
        
        if settings.ENABLE_RERANKING and len(results_with_content) > 3:
            logger.info("Applying reranking to improve result quality")
            reranked = await self._simple_rerank(request.query, results_with_content, top_k=request.top_k)
            final_results = [point for point, _ in reranked]
        else:
            final_results = filtered_results[:request.top_k]
        
        # 7. 构建上下文和引用
        references: List[SearchReference] = []
        context_parts: List[str] = []
        seen_contents = set()  # 用于去重相同内容
        
        for point in final_results:
            payload = point.payload or {}
            content = payload.get("content", "")
            
            # 去重检查
            content_hash = hash(content[:100])  # 使用前100字符做简单去重
            if content_hash in seen_contents:
                continue
            seen_contents.add(content_hash)
            
            context_parts.append(content)
            
            # 8. 上下文窗口扩展（如果配置启用）
            if settings.CONTEXT_EXPAND_WINDOW > 0:
                expanded = await self._expand_context_window(
                    novel_id=payload.get("novel_id"),
                    chapter_id=payload.get("chapter_id"),
                    paragraph_index=payload.get("paragraph_index", 0),
                    window_size=settings.CONTEXT_EXPAND_WINDOW
                )
                context_parts.extend(expanded)
            
            # 🔥 包含元数据信息
            references.append(
                SearchReference(
                    novel_id=payload.get("novel_id"),
                    novel_title=payload.get("novel_title"),
                    chapter_id=payload.get("chapter_id"),
                    chapter_title=payload.get("chapter_title"),
                    chapter_number=payload.get("chapter_number"),
                    paragraph_index=payload.get("paragraph_index"),
                    content=content[:500],
                    relevance_score=point.score or 0.0,
                    characters=payload.get("characters"),
                    keywords=payload.get("keywords"),
                    scene_type=payload.get("scene_type"),
                    emotional_tone=payload.get("emotional_tone"),
                )
            )

        # 9. 答案生成阶段（支持思维链）
        use_cot = len(context_parts) > 5  # 如果上下文较多，使用思维链
        answer, chat_usage = await self._generate_answer(
            request.query, 
            context_parts,
            use_chain_of_thought=use_cot
        )
        
        # 追踪chat token
        if chat_usage:
            chat_tokens = chat_usage.total_tokens
            total_tokens += chat_tokens
            api_calls += 1
        
        elapsed = time.perf_counter() - start
        
        # 4. 计算预估费用
        # Embedding-3: 0.5元/百万tokens
        # GLM-4-Plus: 输入5元/百万 + 输出10元/百万
        embedding_cost = embedding_tokens * 0.5 / 1_000_000
        chat_cost = 0.0
        if chat_usage:
            chat_cost = (
                chat_usage.prompt_tokens * 5 / 1_000_000 +
                chat_usage.completion_tokens * 10 / 1_000_000
            )
        estimated_cost = embedding_cost + chat_cost

        # 5. 构建响应
        from app.schemas.search import SearchTokenStats
        
        response = SearchResponse(
            query=request.query,
            answer=answer,
            references=references if request.include_references else [],
            elapsed=elapsed,
            token_stats=SearchTokenStats(
                total_tokens=total_tokens,
                embedding_tokens=embedding_tokens,
                chat_tokens=chat_tokens,
                api_calls=api_calls,
                estimated_cost=estimated_cost
            )
        )

        if self.redis:
            await self.redis.set(cache_key, response.model_dump_json(), ex=600)

        return response

    async def _generate_answer(
        self, 
        question: str, 
        context_chunks: Iterable[str],
        use_chain_of_thought: bool = False
    ) -> Tuple[str, Optional[TokenUsage]]:
        """生成答案并返回token使用情况.
        
        Args:
            question: 用户问题
            context_chunks: 上下文片段列表
            use_chain_of_thought: 是否使用思维链推理
        
        Returns:
            Tuple[str, Optional[TokenUsage]]: (答案文本, token使用情况)
        """
        if not context_chunks:
            return "未在知识库中找到相关内容，请尝试换一个问题或扩大检索范围。", None

        if not self.client:
            return "LLM 未配置，无法生成回答，请联系管理员。", None

        context = "\n\n".join(context_chunks)
        
        # 选择不同的prompt策略
        if use_chain_of_thought:
            # 思维链prompt - 引导模型逐步推理
            prompt = f"""你是一个专业的中文小说分析助手。请按以下步骤仔细回答问题：

【分析步骤】
1. 在原文中定位相关信息
2. 提取关键事实和细节
3. 综合分析并组织答案
4. 指出是否有不确定的部分

【重要规则】
- 答案必须完全基于提供的原文内容，不要编造信息
- 如果原文信息不足，明确说明"原文中未明确提及"
- 尽可能引用原文关键句子来支撑你的答案
- 保持客观中立，不要添加个人解读

【原文片段】
{context}

【用户问题】
{question}

【你的分析和回答】
请按照上述步骤详细回答："""
        else:
            # 标准prompt - 更直接的回答方式
            prompt = f"""你是一个专业的中文小说分析助手。请基于以下原文片段，准确、详细地回答用户问题。

【重要规则】
1. 答案必须完全基于提供的原文内容，不要编造信息
2. 如果原文信息不足，明确说明"原文中未提及"或"信息不足"
3. 尽可能引用原文关键句子来支撑你的答案
4. 如果涉及多个角色或事件，分点说明
5. 保持客观中立，不要添加个人解读

【原文片段】
{context}

【用户问题】
{question}

【你的回答】
请基于上述原文，详细回答问题："""

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是专业的中文小说分析助手。严格基于提供的原文回答问题，不编造内容。如果信息不足，明确说明。"
                    },
                    {"role": "user", "content": prompt},
                ],
                thinking={
                    "type": "enabled",  # 启用深度思考模式
                },
                temperature=0.3,  # 降低temperature提高准确性
                top_p=0.8,  # 添加top_p控制
            ),
        )

        content = self._extract_message_content(response)
        answer = content or "未能生成有效回答，请稍后重试。"
        
        # 提取token使用情况
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            logger.info(
                f"Chat API call completed: prompt_tokens={usage.prompt_tokens}, "
                f"completion_tokens={usage.completion_tokens}, total_tokens={usage.total_tokens}"
            )
        
        return answer, usage

    def _apply_metadata_weighting(self, results: List, request: SearchRequest) -> List:
        """基于元数据对检索结果进行加权.
        
        根据查询中提到的角色、关键词、场景类型等，调整相关度分数。
        
        Args:
            results: 检索结果列表
            request: 搜索请求
            
        Returns:
            List: 加权后的结果列表（按新分数排序）
        """
        if not results:
            return results
        
        query_lower = request.query.lower()
        weighted_results = []
        
        for point in results:
            if not point.payload:
                weighted_results.append(point)
                continue
            
            # 基础分数（向量相似度）
            base_score = point.score or 0.0
            boost = 0.0
            
            # 1. 角色匹配加权（权重: +5%）
            characters = point.payload.get("characters", [])
            if characters:
                for char in characters:
                    if char and char.lower() in query_lower:
                        boost += 0.05
                        logger.debug(f"Character match boost: {char} (+0.05)")
                        break
            
            # 2. 关键词匹配加权（权重: +3%）
            keywords = point.payload.get("keywords", [])
            if keywords:
                matched_keywords = [kw for kw in keywords if kw and kw.lower() in query_lower]
                if matched_keywords:
                    boost += 0.03 * min(len(matched_keywords), 2)  # 最多+6%
                    logger.debug(f"Keyword match boost: {matched_keywords} (+{0.03 * min(len(matched_keywords), 2)})")
            
            # 3. 场景类型匹配加权（权重: +4%）
            scene_type = point.payload.get("scene_type")
            if scene_type:
                scene_keywords = {
                    "对话": ["说", "道", "问", "答", "讲", "谈"],
                    "动作": ["打", "跑", "跳", "飞", "走", "击"],
                    "描述": ["景色", "环境", "样子", "外观"],
                    "心理": ["想", "思", "念", "感觉", "认为"],
                }
                if scene_type in scene_keywords:
                    for keyword in scene_keywords[scene_type]:
                        if keyword in query_lower:
                            boost += 0.04
                            logger.debug(f"Scene type match boost: {scene_type} (+0.04)")
                            break
            
            # 4. 情感基调匹配加权（权重: +3%）
            emotional_tone = point.payload.get("emotional_tone")
            if emotional_tone:
                emotion_keywords = {
                    "积极": ["高兴", "快乐", "喜悦", "幸福"],
                    "消极": ["悲伤", "痛苦", "难过", "绝望"],
                    "紧张": ["紧张", "危险", "惊险", "激烈"],
                    "温馨": ["温暖", "温馨", "温柔", "平和"],
                }
                if emotional_tone in emotion_keywords:
                    for keyword in emotion_keywords[emotional_tone]:
                        if keyword in query_lower:
                            boost += 0.03
                            logger.debug(f"Emotional tone match boost: {emotional_tone} (+0.03)")
                            break
            
            # 应用加权（限制最大boost为+20%）
            final_boost = min(boost, 0.20)
            new_score = base_score * (1 + final_boost)
            
            if final_boost > 0:
                logger.debug(
                    f"Metadata weighting: base_score={base_score:.4f}, "
                    f"boost={final_boost:.2%}, new_score={new_score:.4f}"
                )
            
            # 更新分数
            point.score = new_score
            weighted_results.append(point)
        
        # 按新分数重新排序
        weighted_results.sort(key=lambda x: x.score or 0.0, reverse=True)
        
        logger.info(f"Metadata weighting applied to {len(weighted_results)} results")
        return weighted_results
    
    def _cache_key(self, request: SearchRequest) -> str:
        payload = {
            "query": request.query,
            "novel_ids": request.novel_ids,
            "top_k": request.top_k,
        }
        return f"rag:search:{sha256_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True))}"


__all__ = ["RAGService", "ChunkPayload", "TokenUsage", "EmbeddingResult"]

