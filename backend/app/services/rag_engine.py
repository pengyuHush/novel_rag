"""
RAG引擎 - 检索增强生成
实现基础RAG流程
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.services.embedding_service import get_embedding_service
from app.services.zhipu_client import get_zhipu_client
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
        
        logger.info("✅ RAG引擎初始化完成")
    
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
        top_k: int = None
    ) -> List[Dict]:
        """
        混合Rerank
        
        Args:
            query: 查询文本
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            top_k: 返回Top-K结果
        
        Returns:
            List[Dict]: Rerank后的结果
        """
        top_k = top_k or self.top_k_rerank
        
        # 提取向量检索结果
        documents = vector_results.get('documents', [[]])[0]
        metadatas = vector_results.get('metadatas', [[]])[0]
        distances = vector_results.get('distances', [[]])[0]
        
        # 构建候选文档
        candidates = []
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            candidates.append({
                'content': doc,
                'metadata': metadata,
                'score': 1 - distance,  # 转换为相似度分数
                'rank': i + 1
            })
        
        # 简单排序（实际可以使用更复杂的Rerank算法）
        # 按章节号和分数排序
        candidates.sort(
            key=lambda x: (
                -x['score'],  # 分数降序
                x['metadata'].get('chapter_num', 999)  # 章节号升序
            )
        )
        
        # 返回Top-K
        reranked = candidates[:top_k]
        logger.info(f"✅ Rerank完成: 返回 {len(reranked)} 个结果")
        
        return reranked
    
    def build_prompt(
        self,
        db: Session,
        novel_id: int,
        query: str,
        context_chunks: List[Dict]
    ) -> str:
        """
        构建RAG Prompt
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本
            context_chunks: 上下文块列表
        
        Returns:
            str: 构建好的Prompt
        """
        # 获取小说信息
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        novel_title = novel.title if novel else "未知"
        novel_author = novel.author if novel and novel.author else "未知"
        
        # 构建上下文
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
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

