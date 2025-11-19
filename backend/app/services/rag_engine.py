"""
RAG引擎 - 检索增强生成
实现基础RAG流程，支持智能查询路由、查询改写、自适应Prompt
"""

import logging
import math
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.services.embedding_service import get_embedding_service
from app.services.zhipu_client import get_zhipu_client
from app.services.query_router import query_router, QueryType
from app.services.query_rewriter import get_query_rewriter
from app.services.adaptive_prompt_builder import get_adaptive_prompt_builder
from app.services.nlp import get_hanlp_client
from app.models.database import Novel, Chapter
from app.models.schemas import Citation, Confidence
from app.core.trace_logger import get_trace_logger
from app.core.config import settings

logger = logging.getLogger(__name__)
trace_logger = get_trace_logger()


class RAGEngine:
    """RAG引擎"""
    
    def __init__(self):
        """初始化RAG引擎"""
        self.embedding_service = get_embedding_service()
        self.zhipu_client = get_zhipu_client()
        self.top_k_retrieval = 30  # 检索Top-30
        self.top_k_rerank = 10     # Rerank后Top-10
        self.min_similarity_threshold = settings.min_similarity_threshold  # 相似度阈值
        
        # 查询优化组件
        self.query_rewriter = get_query_rewriter()
        self.prompt_builder = get_adaptive_prompt_builder()
        
        # NLP组件（复用现有的HanLP客户端）
        self.hanlp_client = get_hanlp_client()
        
        # GraphRAG组件
        from app.services.graph.graph_query import GraphQuery
        from app.services.graph.graph_analyzer import GraphAnalyzer
        from app.services.graph.graph_builder import GraphBuilder
        
        self.graph_query = GraphQuery()
        self.graph_analyzer = GraphAnalyzer()
        self.graph_builder = GraphBuilder()
        
        logger.info("✅ RAG引擎初始化完成（含查询优化、GraphRAG支持）")
    
    def query_embedding(self, query: str, query_id: Optional[int] = None) -> List[float]:
        """
        查询向量化
        
        Args:
            query: 查询文本
            query_id: 查询ID（用于日志记录）
        
        Returns:
            List[float]: 查询向量
        """
        embedding = self.zhipu_client.embed_text(query)
        
        # 详细日志
        if query_id:
            trace_logger.trace_embedding(
                query_id=query_id,
                query_text=query,
                embedding_vector=embedding
            )
        
        return embedding
    
    def vector_search(
        self,
        novel_id: int,
        query_embedding: List[float],
        top_k: int = None,
        query_id: Optional[int] = None
    ) -> Dict:
        """
        语义检索
        
        Args:
            novel_id: 小说ID
            query_embedding: 查询向量
            top_k: 返回Top-K结果
            query_id: 查询ID（用于日志记录）
        
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
            
            original_count = len(results.get('ids', [[]])[0])
            
            # 🎯 相似度阈值过滤
            ids = results.get('ids', [[]])[0]
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # 过滤低相似度结果
            filtered_ids = []
            filtered_documents = []
            filtered_metadatas = []
            filtered_distances = []
            
            for doc_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
                # L2距离：距离越小越相似，过滤掉距离大于阈值的结果
                if distance <= self.min_similarity_threshold:
                    filtered_ids.append(doc_id)
                    filtered_documents.append(content)
                    filtered_metadatas.append(metadata)
                    filtered_distances.append(distance)
            
            # 更新结果
            results['ids'] = [filtered_ids]
            results['documents'] = [filtered_documents]
            results['metadatas'] = [filtered_metadatas]
            results['distances'] = [filtered_distances]
            
            filtered_count = len(filtered_ids)
            logger.info(f"✅ 语义检索完成: {original_count} 个结果 → 过滤后 {filtered_count} 个 (阈值: {self.min_similarity_threshold:.2f})")
            
            # 详细日志
            if query_id:
                # 格式化检索结果
                formatted_results = []
                for i, (doc_id, content, metadata, distance) in enumerate(zip(filtered_ids, filtered_documents, filtered_metadatas, filtered_distances), 1):
                    # L2距离：distance本身就是距离值（越小越相似）
                    formatted_results.append({
                        'id': doc_id,
                        'content': content,
                        'metadata': metadata,
                        'distance': distance,
                        'l2_distance': f"{distance:.4f}"
                    })
                
                trace_logger.trace_retrieval(
                    query_id=query_id,
                    top_k=top_k,
                    results=formatted_results
                )
                
                # 如果过滤掉了结果，记录详情
                if original_count > filtered_count:
                    trace_logger.trace_step(
                        query_id=query_id,
                        step_name="L2距离过滤",
                        emoji="🔍",
                        input_data=f"原始结果: {original_count} 个",
                        output_data={
                            "过滤后结果": filtered_count,
                            "过滤掉": original_count - filtered_count,
                            "L2距离阈值": self.min_similarity_threshold,
                            "最小L2距离": f"{min(filtered_distances):.4f}" if filtered_distances else "N/A",
                            "最大L2距离": f"{max(filtered_distances):.4f}" if filtered_distances else "N/A"
                        },
                        status="success"
                    )
            
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
    
    def _extract_entities(self, query: str) -> List[str]:
        """
        从查询中提取关键实体（人名、地名等）
        
        复用现有的HanLP客户端（与小说导入流程共享），fallback到简单正则
        """
        try:
            # 使用现有的HanLP客户端（与小说导入共享同一个实例）
            if not self.hanlp_client.is_available():
                logger.warning("⚠️ HanLP不可用，使用简单正则提取实体")
                return self._extract_entities_fallback(query)
            
            # 调用HanLP提取实体 - 使用宽松模式（查询时）
            entities_dict = self.hanlp_client.extract_entities(
                query, 
                max_length=512,
                strict=False  # 🔑 查询时使用宽松模式
            )
            
            # 合并三类实体：人名、地名、组织名
            entities = []
            entities.extend(entities_dict.get('characters', []))
            entities.extend(entities_dict.get('locations', []))
            entities.extend(entities_dict.get('organizations', []))
            
            # 如果HanLP没提取到实体，使用fallback
            if not entities:
                logger.debug("HanLP未提取到实体，使用fallback方法")
                return self._extract_entities_fallback(query)
            
            # 去重并保持顺序
            seen = set()
            unique_entities = []
            for e in entities:
                if e not in seen:
                    seen.add(e)
                    unique_entities.append(e)
            
            logger.info(f"🎯 HanLP提取实体: {unique_entities} (人名:{len(entities_dict.get('characters', []))}, 地名:{len(entities_dict.get('locations', []))}, 组织:{len(entities_dict.get('organizations', []))})")
            return unique_entities
            
        except Exception as e:
            logger.warning(f"⚠️ HanLP实体提取失败（{type(e).__name__}: {e}），使用fallback")
            return self._extract_entities_fallback(query)
    
    def _extract_entities_fallback(self, query: str) -> List[str]:
        """
        Fallback实体提取方法（简单正则）
        """
        import re
        
        # 提取连续中文字符（2-4字）
        entities = re.findall(r'[\u4e00-\u9fa5]{2,4}', query)
        
        # 过滤常见停用词
        stopwords = {'什么', '怎么', '为什么', '哪里', '如何', '是否', '有没有', 
                     '关于', '描述', '介绍', '说明', '解释', '分析', '评价', '时候',
                     '这个', '那个', '一个', '这些', '那些', '发生', '事情'}
        entities = [e for e in entities if e not in stopwords]
        
        return entities
    
    def _resolve_entity_aliases(
        self, 
        entities: List[str], 
        novel_id: Optional[int],
        db: Optional[Session]
    ) -> List[str]:
        """
        将实体别名解析为规范名称
        
        Args:
            entities: 提取的实体列表（可能包含别名）
            novel_id: 小说ID
            db: 数据库会话
        
        Returns:
            解析后的规范名称列表
        """
        if not entities or not novel_id or not db:
            return entities
        
        try:
            from app.services.entity_service import get_entity_service
            entity_service = get_entity_service()
            
            canonical_entities = []
            for entity in entities:
                canonical = entity_service.get_canonical_name(db, novel_id, entity)
                if canonical != entity:
                    logger.info(f"🔄 实体别名解析: '{entity}' → '{canonical}'")
                canonical_entities.append(canonical)
            
            return canonical_entities
        except Exception as e:
            logger.warning(f"⚠️ 别名解析失败: {e}")
            return entities
    
    def _calculate_entity_match_score(self, text: str, entities: List[str]) -> float:
        """
        计算文本中实体匹配得分（改进版，避免误匹配）
        
        Args:
            text: 文档内容
            entities: 查询中的实体列表
        
        Returns:
            float: 匹配得分 (0-1.5)
        """
        if not entities:
            return 1.0  # 没有明确实体，不惩罚
        
        import re
        
        matched_count = 0
        partial_match_count = 0  # 部分匹配计数
        
        for entity in entities:
            # 策略1：长实体（≥3字符）使用简单包含即可
            if len(entity) >= 3:
                if entity in text:
                    matched_count += 1
                continue
            
            # 策略2：短实体（2字符）需要精确匹配
            # 使用词边界：实体前后不能是中文字符
            pattern = f'(?<![\\u4e00-\\u9fa5]){re.escape(entity)}(?![\\u4e00-\\u9fa5])'
            
            if re.search(pattern, text):
                # 精确匹配（独立词）
                matched_count += 1
            elif entity in text:
                # 部分匹配（包含在其他词中）
                partial_match_count += 1
        
        # 计算得分
        total_entities = len(entities)
        match_ratio = matched_count / total_entities
        partial_ratio = partial_match_count / total_entities
        
        # 精确匹配 + 部分匹配（权重减半）
        effective_ratio = match_ratio + (partial_ratio * 0.5)
        
        # 得分计算
        if effective_ratio >= 0.5:
            return 1.0 + (effective_ratio - 0.5)  # 1.0 - 1.5
        else:
            # 严重惩罚：匹配不足50%
            return 0.3 + (effective_ratio * 0.7)  # 0.3 - 0.65
    
    def _calculate_recency_bias(
        self, 
        chapter_num: int, 
        total_chapters: int, 
        bias_weight: float
    ) -> float:
        """
        计算时间衰减偏向得分
        
        Args:
            chapter_num: 当前章节号
            total_chapters: 总章节数
            bias_weight: 衰减权重 (0.0-0.5)
        
        Returns:
            float: 时间衰减得分 (0.7-1.3)
        """
        if bias_weight == 0.0 or total_chapters == 0:
            return 1.0  # 无偏向
        
        # 章节位置归一化 (0.0 = 第1章, 1.0 = 最后一章)
        position = chapter_num / total_chapters
        
        # 指数增长权重
        recency_score = math.exp(bias_weight * position)
        
        # 归一化到 [0.7, 1.3] 范围
        # bias_weight=0.5, chapter_num=total_chapters时: recency_score ≈ 1.65
        # 归一化后 ≈ 1.3
        normalized = 0.7 + (recency_score - 1.0) * 0.6
        
        return max(0.7, min(1.3, normalized))
    
    def rerank(
        self,
        query: str,
        vector_results: Dict,
        keyword_results: List[Dict] = None,
        top_k: int = None,
        query_type: QueryType = None,
        novel_id: int = None,
        db: Session = None,
        query_id: Optional[int] = None,
        recency_bias_weight: float = 0.15
    ) -> List[Dict]:
        """
        混合Rerank，支持查询类型特定策略 + GraphRAG增强 + 实体匹配
        
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
        
        # 提取查询中的关键实体
        query_entities = self._extract_entities(query)
        logger.info(f"🎯 提取查询实体: {query_entities}")
        
        # 解析实体别名为规范名称
        query_entities = self._resolve_entity_aliases(query_entities, novel_id, db)
        if query_entities:
            logger.info(f"✅ 别名解析后实体: {query_entities}")
        
        # 自动检测查询类型
        if query_type is None:
            query_type = query_router.classify_query(query)
        
        logger.info(f"🔍 查询类型: {query_type.value}")
        
        # 获取总章节数（用于时间衰减计算）
        total_chapters = 0
        if novel_id and db:
            try:
                novel = db.query(Novel).filter(Novel.id == novel_id).first()
                if novel:
                    total_chapters = novel.total_chapters
                    logger.debug(f"📚 小说总章节数: {total_chapters}")
            except Exception as e:
                logger.warning(f"⚠️ 获取章节数失败: {e}")
        
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
            # L2距离转换为相似度分数：使用高斯核函数
            # distance=0 -> score=1.0, distance=2 -> score≈0.135
            base_score = math.exp(-distance**2 / 2)
            
            # 🎯 实体匹配得分
            entity_match_score = self._calculate_entity_match_score(doc, query_entities)
            
            # GraphRAG: 获取章节重要性（时序权重）
            chapter_num = metadata.get('chapter_num')
            chapter_importance = 0.5  # 默认中等重要性
            
            if chapter_num and chapter_num in chapter_importance_map:
                chapter_importance = chapter_importance_map[chapter_num]
            
            # 应用查询类型特定的权重
            if query_type == QueryType.DIALOGUE:
                # 对话类查询：提升包含引号的内容权重 + 实体匹配
                quote_boost = self._calculate_quote_boost(doc)
                
                # 动态调整：高相似度时降低quote_boost影响
                if base_score > 0.85:
                    quote_boost = 1.0 + (quote_boost - 1.0) * 0.5  # 减弱quote影响
                    logger.debug(f"🔥 高相似度({base_score:.3f})：降低对话标记权重影响")
                
                # 应用时间衰减
                recency_bias = self._calculate_recency_bias(
                    chapter_num, total_chapters, recency_bias_weight
                )
                
                final_score = base_score * quote_boost * entity_match_score * recency_bias
            elif query_type == QueryType.ANALYSIS:
                # 分析类查询：提升重要章节权重（使用图谱章节重要性）+ 实体匹配
                importance_boost = chapter_importance + 0.5
                
                # 动态调整：低相似度时增强章节重要性影响
                if base_score < 0.60:
                    importance_boost = importance_boost * 1.3  # 增强30%
                    logger.debug(f"⚠️ 低相似度({base_score:.3f})：增强章节重要性权重")
                
                # 应用时间衰减
                recency_bias = self._calculate_recency_bias(
                    chapter_num, total_chapters, recency_bias_weight
                )
                
                final_score = base_score * importance_boost * entity_match_score * recency_bias
            else:
                # 事实类查询 - 动态权重调整
                # 基础权重配比
                w_semantic = 0.50
                w_temporal = 0.10
                w_entity = 0.40
                
                # 🚀 动态调整策略
                if base_score > 0.85:
                    # 高相似度（>0.85）：显著增强语义权重
                    w_semantic = 0.60  # +0.10
                    w_entity = 0.30    # -0.10
                    logger.debug(f"🔥 高相似度检测({base_score:.3f})：增强语义权重")
                
                elif base_score < 0.50:
                    # 低相似度（<0.50）：大幅增强实体匹配权重
                    w_semantic = 0.30  # -0.20
                    w_entity = 0.60    # +0.20
                    logger.debug(f"⚠️ 低相似度检测({base_score:.3f})：增强实体权重")
                
                # 实体匹配情况动态调整
                if entity_match_score > 1.3:
                    # 实体匹配优秀：进一步提升实体权重
                    w_entity = min(w_entity + 0.10, 0.70)  # 最高不超过70%
                    w_semantic = max(w_semantic - 0.10, 0.20)
                    logger.debug(f"✨ 实体匹配优秀({entity_match_score:.2f})：进一步提升实体权重")
                
                elif entity_match_score < 0.5:
                    # 实体匹配差：降低实体权重，提升语义权重
                    w_entity = max(w_entity - 0.15, 0.15)
                    w_semantic = min(w_semantic + 0.15, 0.75)
                    logger.debug(f"🔻 实体匹配不佳({entity_match_score:.2f})：降低实体权重")
                
                # 计算最终得分（确保权重和为1.0）
                total_weight = w_semantic + w_temporal + w_entity
                semantic_weight = (base_score * w_semantic) / total_weight
                temporal_weight = (chapter_importance * w_temporal) / total_weight
                entity_weight = (entity_match_score * w_entity) / total_weight
                
                final_score = semantic_weight + temporal_weight + entity_weight
                
                # 应用时间衰减
                recency_bias = self._calculate_recency_bias(
                    chapter_num, total_chapters, recency_bias_weight
                )
                final_score = final_score * recency_bias
            
            candidates.append({
                'content': doc,
                'metadata': metadata,
                'score': final_score,
                'base_score': base_score,
                'entity_match_score': entity_match_score,  # 新增：实体匹配分数
                'rank': i + 1,
                'query_type': query_type.value
            })
        
        # 演变节点优先rerank：提升演变章节的权重
        if graph and query_entities and len(query_entities) >= 2:
            for candidate in candidates:
                chapter_num = candidate['metadata'].get('chapter_num')
                if chapter_num and self._is_relation_evolution_chapter(graph, chapter_num, query_entities):
                    candidate['score'] *= 1.5  # 演变节点权重提升50%
                    logger.info(f"🔄 检测到关系演变章节{chapter_num}，提升权重")
        
        # 排序
        candidates.sort(key=lambda x: -x['score'])
        
        # 分析类查询：合并相邻块
        if query_type == QueryType.ANALYSIS:
            candidates = self._merge_adjacent_chunks(candidates)
        
        # 返回Top-K
        reranked = candidates[:top_k]
        logger.info(f"✅ Rerank完成 ({query_type.value}): 返回 {len(reranked)} 个结果")
        
        # 📊 记录权重使用情况（仅记录前5个候选）
        if len(candidates) > 0:
            logger.info(f"📊 Top-5候选权重分布:")
            for idx, cand in enumerate(candidates[:5]):
                recency_info = ""
                if recency_bias_weight > 0:
                    ch_num = cand['metadata'].get('chapter_num', 0)
                    if ch_num and total_chapters:
                        bias = self._calculate_recency_bias(ch_num, total_chapters, recency_bias_weight)
                        recency_info = f" | 时间:{bias:.2f}"
                
                logger.info(
                    f"  [{idx+1}] 最终得分:{cand['score']:.3f} | "
                    f"语义:{cand['base_score']:.3f} | "
                    f"实体:{cand.get('entity_match_score', 1.0):.2f} | "
                    f"章节:{cand['metadata'].get('chapter_num', '?')}{recency_info}"
                )
        
        # 详细日志
        if query_id:
            # 为日志结果添加实体匹配信息
            reranked_with_entity_info = []
            for result in reranked:
                result_copy = result.copy()
                result_copy['entity_match'] = f"{result.get('entity_match_score', 1.0):.2f}"
                reranked_with_entity_info.append(result_copy)
            
            trace_logger.trace_rerank(
                query_id=query_id,
                query=query,
                candidates_count=len(candidates),
                reranked_results=reranked_with_entity_info,
                top_k=top_k
            )
            
            # 额外记录实体匹配详情
            if query_entities:
                trace_logger.trace_step(
                    query_id=query_id,
                    step_name="实体匹配分析",
                    emoji="🎯",
                    input_data={
                        "查询实体": query_entities,
                        "候选文档数": len(candidates)
                    },
                    output_data={
                        "Top-10实体匹配情况": [
                            {
                                "排名": i+1,
                                "章节": f"第{r.get('metadata', {}).get('chapter_num', '?')}章",
                                "实体匹配分": f"{r.get('entity_match_score', 1.0):.2f}",
                                "语义相似度": f"{r.get('base_score', 0):.2f}",
                                "最终得分": f"{r.get('score', 0):.2f}",
                                "匹配的实体": [e for e in query_entities if e in r.get('content', '')]
                            }
                            for i, r in enumerate(reranked[:10])
                        ]
                    },
                    status="success"
                )
        
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
        model: str = "glm-4",
        enable_query_rewrite: bool = True,
        query_id: Optional[int] = None,
        recency_bias_weight: float = 0.15
    ) -> Tuple[str, List[Citation], Dict, Optional[str]]:
        """
        完整RAG查询流程（含查询优化）
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本
            model: 使用的模型
            enable_query_rewrite: 是否启用查询改写
            query_id: 查询ID（用于日志记录）
        
        Returns:
            Tuple[str, List[Citation], Dict, Optional[str]]: (答案, 引用列表, 统计信息, 改写后的查询)
        """
        logger.info(f"📝 开始RAG查询: {query}")
        
        # 0. 查询改写（可选）
        rewrite_result = self.query_rewriter.rewrite_query(
            query, 
            enable=enable_query_rewrite,
            query_id=query_id
        )
        query_for_retrieval = rewrite_result["rewritten"]
        query_type = rewrite_result.get("query_type")
        rewritten_query = query_for_retrieval if rewrite_result["rewrite_applied"] else None
        
        # 1. 查询向量化（使用改写后的查询）
        query_embedding = self.query_embedding(query_for_retrieval, query_id=query_id)
        
        # 2. 语义检索
        vector_results = self.vector_search(novel_id, query_embedding, query_id=query_id)
        
        # 3. 关键词检索（可选）
        keyword_results = self.keyword_search(db, novel_id, query_for_retrieval)
        
        # 4. 混合Rerank
        reranked_chunks = self.rerank(
            query_for_retrieval, 
            vector_results, 
            keyword_results,
            novel_id=novel_id,
            db=db,
            query_id=query_id,
            recency_bias_weight=recency_bias_weight
        )
        
        if not reranked_chunks:
            logger.warning("⚠️ 未找到相关内容")
            return "抱歉，在小说中未找到相关内容。", [], {}, rewritten_query
        
        # 5. 构建自适应Prompt（使用原始查询）
        prompt = self.prompt_builder.build_prompt(
            db, novel_id, query, reranked_chunks,
            query_type=QueryType(query_type) if query_type else None,
            query_id=query_id
        )
        
        # 6. 生成答案
        answer = self.generate_answer(prompt, model, stream=False)
        
        # 7. 构建引用列表
        citations = []
        
        # 返回前10条引用（或所有chunk，取较小值）
        # 不进行章节去重，因为同一章节可能有多个相关片段
        max_citations = min(10, len(reranked_chunks))
        
        for chunk in reranked_chunks[:max_citations]:
            metadata = chunk['metadata']
            chapter_num = metadata.get('chapter_num')
            
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
            'citations': len(citations),
            'query_rewrite_applied': rewrite_result["rewrite_applied"]
        }
        
        logger.info(f"✅ RAG查询完成: {len(citations)} 条引用")
        
        return answer, citations, stats, rewritten_query
    
    def _is_relationship_query(self, query: str) -> bool:
        """
        判断是否为关系查询
        
        Args:
            query: 查询文本
        
        Returns:
            bool: 是否为关系查询
        """
        relation_keywords = ['关系', '什么样', '如何', '是不是', '变化', '演变', '对待', '看待']
        return any(kw in query for kw in relation_keywords)
    
    def _is_relation_evolution_chapter(
        self,
        graph,
        chapter_num: int,
        query_entities: List[str]
    ) -> bool:
        """
        检查章节是否为演变节点
        
        Args:
            graph: 知识图谱
            chapter_num: 章节号
            query_entities: 查询实体列表
        
        Returns:
            bool: 是否为演变节点
        """
        if len(query_entities) < 2 or not graph:
            return False
        
        try:
            # 获取两实体间的关系演变
            evolution = self.graph_query.get_relationship_evolution(
                graph, query_entities[0], query_entities[1]
            )
            
            # 检查该章节是否在演变列表中
            evolution_chapters = [evt['chapter'] for evt in evolution]
            return chapter_num in evolution_chapters
        except Exception as e:
            logger.debug(f"检查演变节点失败: {e}")
            return False
    
    def _filter_by_entity_attributes(
        self,
        candidates: List[Dict],
        graph,
        query_constraints: Dict
    ) -> List[Dict]:
        """
        基于实体属性过滤候选文档
        
        Args:
            candidates: 候选文档列表
            graph: 知识图谱
            query_constraints: 属性约束，如{"性别": "男", "阵营": "反派"}
        
        Returns:
            List[Dict]: 过滤后的候选文档
        """
        if not graph or not query_constraints:
            return candidates
        
        filtered = []
        for candidate in candidates:
            entities_in_doc = candidate['metadata'].get('entities', [])
            
            # 如果没有实体信息，保留（避免过度过滤）
            if not entities_in_doc:
                filtered.append(candidate)
                continue
            
            # 检查文档中的实体是否满足约束
            for entity in entities_in_doc:
                if entity in graph:
                    attributes = graph.nodes[entity].get('attributes', {})
                    
                    # 检查是否满足所有约束
                    if all(attributes.get(k) == v for k, v in query_constraints.items()):
                        filtered.append(candidate)
                        break
        
        return filtered


# 全局RAG引擎实例
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """获取全局RAG引擎实例（单例）"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

