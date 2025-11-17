"""
RAG引擎 - 检索增强生成
实现基础RAG流程，支持智能查询路由
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.services.embedding_service import get_embedding_service
from app.services.zhipu_client import get_zhipu_client
from app.services.query_router import query_router, QueryType
from app.models.database import Novel, Chapter
from app.models.schemas import Citation, Confidence

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG引擎"""
    
    def __init__(self):
        """初始化RAG引擎"""
        self.embedding_service = get_embedding_service()
        self.zhipu_client = get_zhipu_client()
        self.top_k_retrieval = 30  # 检索Top-30
        self.top_k_rerank = 10     # Rerank后Top-10
        
        # GraphRAG组件
        from app.services.graph.graph_query import GraphQuery
        from app.services.graph.graph_analyzer import GraphAnalyzer
        from app.services.graph.graph_builder import GraphBuilder
        
        self.graph_query = GraphQuery()
        self.graph_analyzer = GraphAnalyzer()
        self.graph_builder = GraphBuilder()
        
        logger.info("✅ RAG引擎初始化完成（含GraphRAG支持）")
    
    def query_embedding(self, query: str) -> List[float]:
        """
        查询向量化
        
        Args:
            query: 查询文本
        
        Returns:
            List[float]: 查询向量
        """
        return self.zhipu_client.embed_text(query)
    
    def vector_search(
        self,
        novel_id: int,
        query_embedding: List[float],
        top_k: int = None
    ) -> Dict:
        """
        语义检索
        
        Args:
            novel_id: 小说ID
            query_embedding: 查询向量
            top_k: 返回Top-K结果
        
        Returns:
            Dict: 检索结果
        """
        top_k = top_k or self.top_k_retrieval
        
        from app.core.chromadb_client import get_chroma_client
        chroma_client = get_chroma_client()
        
        collection_name = f"novel_{novel_id}"
        
        try:
            results = chroma_client.query_documents(
                collection_name=collection_name,
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            logger.info(f"✅ 语义检索完成: {len(results.get('ids', [[]])[0])} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"❌ 语义检索失败: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def keyword_search(
        self,
        db: Session,
        novel_id: int,
        query: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        关键词检索（简单实现）
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本
            top_k: 返回Top-K结果
        
        Returns:
            List[Dict]: 检索结果
        """
        # 简单的关键词匹配（实际应该用全文索引）
        # 这里只是演示，生产环境应该使用Elasticsearch等
        logger.info(f"🔍 关键词检索: {query}")
        
        # TODO: 实现基于数据库的关键词检索
        # 暂时返回空结果
        return []
    
    def rerank(
        self,
        query: str,
        vector_results: Dict,
        keyword_results: List[Dict] = None,
        top_k: int = None,
        query_type: QueryType = None,
        novel_id: int = None,
        db: Session = None
    ) -> List[Dict]:
        """
        混合Rerank，支持查询类型特定策略 + GraphRAG增强
        
        Args:
            query: 查询文本
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            top_k: 返回Top-K结果
            query_type: 查询类型（自动检测或手动指定）
            novel_id: 小说ID（用于GraphRAG）
            db: 数据库会话（用于GraphRAG）
        
        Returns:
            List[Dict]: Rerank后的结果
        """
        top_k = top_k or self.top_k_rerank
        
        # 自动检测查询类型
        if query_type is None:
            query_type = query_router.classify_query(query)
        
        logger.info(f"🔍 查询类型: {query_type.value}")
        
        # GraphRAG: 加载知识图谱（如果提供了novel_id）
        graph = None
        chapter_importance_map = {}
        
        if novel_id is not None:
            try:
                graph = self.graph_builder.load_graph(novel_id)
                
                # 计算所有章节的重要性评分（缓存）
                if graph:
                    # 获取所有章节号
                    chapters = set()
                    for node in graph.nodes():
                        first_chapter = graph.nodes[node].get('first_chapter')
                        if first_chapter:
                            chapters.add(first_chapter)
                    
                    # 计算每个章节的重要性
                    for chapter in chapters:
                        importance = self.graph_analyzer.compute_chapter_importance(graph, chapter)
                        chapter_importance_map[chapter] = importance
                    
                    logger.info(f"✅ GraphRAG: 加载图谱成功，计算了{len(chapter_importance_map)}个章节的重要性")
            except Exception as e:
                logger.warning(f"⚠️ GraphRAG加载失败（继续使用纯向量检索）: {e}")
        
        # 提取向量检索结果
        documents = vector_results.get('documents', [[]])[0]
        metadatas = vector_results.get('metadatas', [[]])[0]
        distances = vector_results.get('distances', [[]])[0]
        
        # 构建候选文档
        candidates = []
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            base_score = 1 - distance  # 转换为相似度分数
            
            # GraphRAG: 获取章节重要性（时序权重）
            chapter_num = metadata.get('chapter_num')
            chapter_importance = 0.5  # 默认中等重要性
            
            if chapter_num and chapter_num in chapter_importance_map:
                chapter_importance = chapter_importance_map[chapter_num]
            
            # 应用查询类型特定的权重
            if query_type == QueryType.DIALOGUE:
                # 对话类查询：提升包含引号的内容权重
                quote_boost = self._calculate_quote_boost(doc)
                final_score = base_score * quote_boost
            elif query_type == QueryType.ANALYSIS:
                # 分析类查询：提升重要章节权重（使用图谱章节重要性）
                importance_boost = chapter_importance + 0.5
                final_score = base_score * importance_boost
            else:
                # 事实类查询：混合权重
                # 语义相似度60% + 章节重要性15% (GraphRAG增强) + 实体匹配25%
                semantic_weight = base_score * 0.60
                temporal_weight = chapter_importance * 0.15
                entity_weight = 0.25 if metadata.get('entities') else 0.0
                
                final_score = semantic_weight + temporal_weight + entity_weight
            
            candidates.append({
                'content': doc,
                'metadata': metadata,
                'score': final_score,
                'base_score': base_score,
                'rank': i + 1,
                'query_type': query_type.value
            })
        
        # 排序
        candidates.sort(key=lambda x: -x['score'])
        
        # 分析类查询：合并相邻块
        if query_type == QueryType.ANALYSIS:
            candidates = self._merge_adjacent_chunks(candidates)
        
        # 返回Top-K
        reranked = candidates[:top_k]
        logger.info(f"✅ Rerank完成 ({query_type.value}): 返回 {len(reranked)} 个结果")
        
        return reranked
    
    def _calculate_quote_boost(self, text: str) -> float:
        """
        计算引号内容的权重加成
        
        对话类查询优先展示包含对话的内容
        
        Args:
            text: 文本内容
        
        Returns:
            float: 权重加成系数 (1.0-1.5)
        """
        # 统计引号数量（中文引号和英文引号）
        quote_count = (
            text.count('"') + text.count('"') + 
            text.count("'") + text.count("'") +
            text.count('"') // 2  # 英文双引号成对
        )
        
        # 计算引号占比
        if len(text) > 0:
            quote_density = min(quote_count / (len(text) / 100), 1.0)  # 标准化
            boost = 1.0 + (quote_density * 0.5)  # 最多增加50%权重
            return boost
        
        return 1.0
    
    def _merge_adjacent_chunks(self, candidates: List[Dict]) -> List[Dict]:
        """
        合并相邻的文本块（分析类查询）
        
        将同一章节的相邻块合并，提供更完整的上下文
        
        Args:
            candidates: 候选文档列表
        
        Returns:
            List[Dict]: 合并后的候选列表
        """
        if not candidates:
            return candidates
        
        merged = []
        skip_indices = set()
        
        for i, current in enumerate(candidates):
            if i in skip_indices:
                continue
            
            current_chapter = current['metadata'].get('chapter_num')
            current_block = current['metadata'].get('block_num')
            merged_content = current['content']
            merged_score = current['score']
            
            # 查找后续相邻块
            for j in range(i + 1, min(i + 3, len(candidates))):  # 最多向后看2个块
                next_candidate = candidates[j]
                next_chapter = next_candidate['metadata'].get('chapter_num')
                next_block = next_candidate['metadata'].get('block_num')
                
                # 同一章节且块号相邻
                if (current_chapter == next_chapter and 
                    current_block is not None and next_block is not None and
                    next_block == current_block + 1):
                    
                    merged_content += "\n" + next_candidate['content']
                    merged_score = (merged_score + next_candidate['score']) / 2  # 平均分数
                    skip_indices.add(j)
                    current_block = next_block  # 更新当前块号
            
            # 添加合并后的块
            merged.append({
                'content': merged_content,
                'metadata': current['metadata'],
                'score': merged_score,
                'base_score': current.get('base_score'),
                'rank': current.get('rank'),
                'query_type': current.get('query_type'),
                'is_merged': len(merged_content) > len(current['content'])
            })
        
        return merged
    
    def build_prompt(
        self,
        db: Session,
        novel_id: int,
        query: str,
        context_chunks: List[Dict],
        max_chunks: int = 10
    ) -> str:
        """
        构建RAG Prompt
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本
            context_chunks: 上下文块列表
            max_chunks: 最大使用的上下文块数量（默认10）
        
        Returns:
            str: 构建好的Prompt
        """
        # 获取小说信息
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        novel_title = novel.title if novel else "未知"
        novel_author = novel.author if novel and novel.author else "未知"
        
        # 限制上下文块数量
        limited_chunks = context_chunks[:max_chunks]
        
        # 构建上下文
        context_parts = []
        for i, chunk in enumerate(limited_chunks, 1):
            metadata = chunk['metadata']
            chapter_num = metadata.get('chapter_num', '?')
            chapter_title = metadata.get('chapter_title', '')
            content = chunk['content']
            
            context_parts.append(
                f"[片段{i} - 第{chapter_num}章 {chapter_title}]\n{content}"
            )
        
        context_text = "\n\n".join(context_parts)
        
        # 构建完整Prompt
        prompt = f"""你是一个专业的小说阅读助手。请基于以下小说内容回答用户的问题。

**小说信息**
- 标题: {novel_title}
- 作者: {novel_author}

**相关内容**
{context_text}

**用户问题**
{query}

**回答要求**
1. 基于提供的小说内容回答，不要编造
2. 如果内容中没有相关信息，请明确说明
3. 引用时请标注章节号
4. 回答要准确、完整、有条理

**你的回答**:"""
        
        return prompt
    
    def generate_answer(
        self,
        prompt: str,
        model: str = "glm-4",
        stream: bool = False
    ):
        """
        生成答案
        
        Args:
            prompt: 完整的Prompt
            model: 使用的模型
            stream: 是否流式输出
        
        Returns:
            str | Generator: 答案文本或生成器
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            if stream:
                # 流式生成
                for chunk in self.zhipu_client.chat_completion_stream(
                    messages=messages,
                    model=model
                ):
                    if chunk.get("content"):
                        yield chunk["content"]
            else:
                # 非流式生成
                response = self.zhipu_client.chat_completion(
                    messages=messages,
                    model=model
                )
                return response
        except Exception as e:
            logger.error(f"❌ 生成答案失败: {e}")
            raise
    
    def generate_answer_with_stats(
        self,
        prompt: str,
        model: str = "glm-4",
        stream: bool = False
    ):
        """
        生成答案（带Token统计）
        
        支持thinking模式的模型会自动返回reasoning_content（思考过程）
        
        Args:
            prompt: 完整的Prompt
            model: 使用的模型
            stream: 是否流式输出
        
        Returns:
            Dict | Generator[Dict]: 包含content、reasoning_content和usage的字典或生成器
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            if stream:
                # 流式生成（返回完整的chunk数据，包含content、reasoning_content和usage）
                for chunk_data in self.zhipu_client.chat_completion_stream(
                    messages=messages,
                    model=model
                ):
                    # 返回完整的chunk_data，某些模型会包含reasoning_content
                    yield chunk_data
            else:
                # 非流式生成
                response = self.zhipu_client.chat_completion(
                    messages=messages,
                    model=model
                )
                
                logger.info(f"✅ 答案生成完成")
                return response.get("content", "")
                
        except Exception as e:
            logger.error(f"❌ 答案生成失败: {e}")
            if stream:
                yield "抱歉，生成答案时出现错误。"
            else:
                return "抱歉，生成答案时出现错误。"
    
    def query(
        self,
        db: Session,
        novel_id: int,
        query: str,
        model: str = "glm-4"
    ) -> Tuple[str, List[Citation], Dict]:
        """
        完整RAG查询流程
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本
            model: 使用的模型
        
        Returns:
            Tuple[str, List[Citation], Dict]: (答案, 引用列表, 统计信息)
        """
        logger.info(f"📝 开始RAG查询: {query}")
        
        # 1. 查询向量化
        query_embedding = self.query_embedding(query)
        
        # 2. 语义检索
        vector_results = self.vector_search(novel_id, query_embedding)
        
        # 3. 关键词检索（可选）
        keyword_results = self.keyword_search(db, novel_id, query)
        
        # 4. 混合Rerank
        reranked_chunks = self.rerank(query, vector_results, keyword_results)
        
        if not reranked_chunks:
            logger.warning("⚠️ 未找到相关内容")
            return "抱歉，在小说中未找到相关内容。", [], {}
        
        # 5. 构建Prompt
        prompt = self.build_prompt(db, novel_id, query, reranked_chunks)
        
        # 6. 生成答案
        answer = self.generate_answer(prompt, model, stream=False)
        
        # 7. 构建引用列表
        citations = []
        seen_chapters = set()
        
        for chunk in reranked_chunks:
            metadata = chunk['metadata']
            chapter_num = metadata.get('chapter_num')
            
            # 去重（每章最多一条引用）
            if chapter_num in seen_chapters:
                continue
            seen_chapters.add(chapter_num)
            
            citations.append(Citation(
                chapter_num=chapter_num,
                chapter_title=metadata.get('chapter_title'),
                text=chunk['content'][:200] + "...",  # 截断显示
                score=chunk.get('score')
            ))
        
        # 统计信息
        stats = {
            'retrieved_chunks': len(vector_results.get('ids', [[]])[0]),
            'reranked_chunks': len(reranked_chunks),
            'citations': len(citations)
        }
        
        logger.info(f"✅ RAG查询完成: {len(citations)} 条引用")
        
        return answer, citations, stats


# 全局RAG引擎实例
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """获取全局RAG引擎实例（单例）"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

