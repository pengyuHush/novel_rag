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

    def to_payload(self) -> dict:
        return {
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
        
        # 1. Embedding阶段 - 将问题转为向量
        embedding_result = await self.embed_texts([request.query])
        query_vector = embedding_result.vectors[0]
        
        # 追踪embedding token
        if embedding_result.usage:
            embedding_tokens = embedding_result.usage.total_tokens
            total_tokens += embedding_tokens
            api_calls += 1

        filter_condition = None
        if request.novel_ids:
            filter_condition = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="novel_id",
                        match=qmodels.MatchAny(any=request.novel_ids),
                    )
                ]
            )

        # 2. 向量检索阶段 - 无token消耗
        try:
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=min(request.top_k, settings.MAX_TOP_K),
                query_filter=filter_condition,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as e:
            # Handle collection not found error gracefully
            elapsed = time.perf_counter() - start
            logger.warning(f"Search failed - collection may not exist: {e}")
            return SearchResponse(
                query=request.query,
                answer="知识库中没有找到相关内容。请确保已上传并处理了小说文本。",
                references=[],
                elapsed=elapsed,
            )

        references: List[SearchReference] = []
        context_parts: List[str] = []
        for point in results:
            payload = point.payload or {}
            content = payload.get("content", "")
            context_parts.append(content)
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
                )
            )

        # 3. 答案生成阶段
        answer, chat_usage = await self._generate_answer(request.query, context_parts)
        
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
        self, question: str, context_chunks: Iterable[str]
    ) -> Tuple[str, Optional[TokenUsage]]:
        """生成答案并返回token使用情况.
        
        Returns:
            Tuple[str, Optional[TokenUsage]]: (答案文本, token使用情况)
        """
        if not context_chunks:
            return "未在知识库中找到相关内容，请尝试换一个问题或扩大检索范围。", None

        if not self.client:
            return "LLM 未配置，无法生成回答，请联系管理员。", None

        context = "\n\n".join(context_chunks)
        prompt = (
            "你是一个中文小说分析助手，请根据以下提供的原文片段回答问题。\n"
            "如果原文不足以回答，请明确说明。\n\n原文片段：\n"
            f"{context}\n\n问题：{question}\n回答："
        )

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "你是专业的小说分析助手"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            ),
        )

        content = response.choices[0].message.content if response.choices else ""
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

    def _cache_key(self, request: SearchRequest) -> str:
        payload = {
            "query": request.query,
            "novel_ids": request.novel_ids,
            "top_k": request.top_k,
        }
        return f"rag:search:{sha256_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True))}"


__all__ = ["RAGService", "ChunkPayload", "TokenUsage", "EmbeddingResult"]

