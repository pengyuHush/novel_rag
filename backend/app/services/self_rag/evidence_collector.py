"""
多源证据收集器

为每个断言收集多个证据源
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """证据收集器"""
    
    def __init__(self):
        """初始化证据收集器"""
        logger.info("✅ 证据收集器初始化完成")
    
    def collect_evidence_for_assertion(
        self,
        db: Session,
        novel_id: int,
        assertion: Dict,
        top_k: int = 3
    ) -> List[Dict]:
        """
        为单个断言收集证据
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            assertion: 断言字典
            top_k: 收集证据数量
        
        Returns:
            List[Dict]: 证据列表
                - content: 证据内容
                - chapter_num: 章节号
                - chapter_title: 章节标题
                - score: 相关性分数
                - source: 证据来源（vector/keyword/graph）
        """
        evidence_list = []
        
        assertion_text = assertion.get('assertion', '')
        entities = assertion.get('entities', [])
        chapter_ref = assertion.get('chapter_ref')
        
        # 1. 向量检索证据
        vector_evidence = self._collect_from_vector_search(
            novel_id, assertion_text, top_k
        )
        evidence_list.extend(vector_evidence)
        
        # 2. 关键词检索证据（如果有实体）
        if entities:
            keyword_evidence = self._collect_from_keyword_search(
                db, novel_id, entities, chapter_ref, top_k
            )
            evidence_list.extend(keyword_evidence)
        
        # 3. 图谱检索证据（如果是关系类断言）
        if assertion.get('type') == 'relation' and len(entities) >= 2:
            graph_evidence = self._collect_from_graph(
                db, novel_id, entities[:2]
            )
            evidence_list.extend(graph_evidence)
        
        # 去重和排序
        evidence_list = self._deduplicate_and_rank(evidence_list, top_k)
        
        logger.info(f"✅ 收集证据: {len(evidence_list)} 条")
        
        return evidence_list
    
    def _collect_from_vector_search(
        self,
        novel_id: int,
        query: str,
        top_k: int
    ) -> List[Dict]:
        """
        从向量检索收集证据
        
        Args:
            novel_id: 小说ID
            query: 查询文本
            top_k: 结果数量
        
        Returns:
            List[Dict]: 证据列表
        """
        try:
            from app.services.zhipu_client import get_zhipu_client
            from app.core.chromadb_client import get_chroma_client
            
            zhipu_client = get_zhipu_client()
            chroma_client = get_chroma_client()
            
            # 向量化
            query_embedding = zhipu_client.embed_text(query)
            
            # 检索
            collection_name = f"novel_{novel_id}"
            results = chroma_client.query_documents(
                collection_name=collection_name,
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # 转换为标准格式
            evidence_list = []
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                evidence_list.append({
                    'content': doc,
                    'chapter_num': metadata.get('chapter_num'),
                    'chapter_title': metadata.get('chapter_title'),
                    'score': 1 - distance,
                    'source': 'vector'
                })
            
            return evidence_list
            
        except Exception as e:
            logger.error(f"❌ 向量检索证据失败: {e}")
            return []
    
    def _collect_from_keyword_search(
        self,
        db: Session,
        novel_id: int,
        entities: List[str],
        chapter_ref: Optional[int],
        top_k: int
    ) -> List[Dict]:
        """
        从关键词检索收集证据
        
        优先检索章节引用附近的内容
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entities: 实体列表
            chapter_ref: 章节引用
            top_k: 结果数量
        
        Returns:
            List[Dict]: 证据列表
        """
        # TODO: 实现基于数据库的关键词检索
        # 暂时返回空列表
        return []
    
    def _collect_from_graph(
        self,
        db: Session,
        novel_id: int,
        entities: List[str]
    ) -> List[Dict]:
        """
        从知识图谱收集证据
        
        查询两个实体之间的关系
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entities: 实体列表（至少2个）
        
        Returns:
            List[Dict]: 证据列表
        """
        if len(entities) < 2:
            return []
        
        try:
            import pickle
            from pathlib import Path
            from app.services.graph.graph_query import get_graph_query
            
            # 加载图谱
            graph_path = Path(f"./backend/data/graphs/novel_{novel_id}_graph.pkl")
            if not graph_path.exists():
                return []
            
            with open(graph_path, 'rb') as f:
                graph = pickle.load(f)
            
            # 查询关系
            graph_query = get_graph_query()
            evolution = graph_query.get_relationship_evolution(
                graph, entities[0], entities[1]
            )
            
            if evolution:
                # 将演变历史转换为证据
                evidence_list = []
                for evo in evolution:
                    evidence_list.append({
                        'content': f"{entities[0]}与{entities[1]}的关系在第{evo['chapter']}章为：{evo['type']}",
                        'chapter_num': evo['chapter'],
                        'chapter_title': None,
                        'score': 0.8,
                        'source': 'graph'
                    })
                return evidence_list
            
        except Exception as e:
            logger.error(f"❌ 图谱检索证据失败: {e}")
        
        return []
    
    def _deduplicate_and_rank(
        self,
        evidence_list: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        去重和排序证据
        
        Args:
            evidence_list: 证据列表
            top_k: 保留数量
        
        Returns:
            List[Dict]: 去重排序后的证据
        """
        # 按章节号去重（保留每章最高分）
        chapter_best = {}
        for evidence in evidence_list:
            chapter_num = evidence.get('chapter_num')
            if chapter_num is None:
                continue
            
            if chapter_num not in chapter_best or evidence['score'] > chapter_best[chapter_num]['score']:
                chapter_best[chapter_num] = evidence
        
        # 转换为列表并按分数排序
        deduplicated = list(chapter_best.values())
        deduplicated.sort(key=lambda x: -x['score'])
        
        return deduplicated[:top_k]
    
    def collect_contradiction_evidence_with_graph(
        self,
        db: Session,
        novel_id: int,
        entity: str,
        attribute: str = "立场"
    ) -> List[Dict]:
        """
        基于图谱演变信息收集矛盾证据
        
        场景：检测"角色A的立场是否矛盾？"
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            entity: 实体名称
            attribute: 要检测的属性（默认"立场"）
        
        Returns:
            List[Dict]: 证据对列表，包含early和late描述
        """
        from app.services.graph.graph_builder import GraphBuilder
        from app.services.graph.graph_query import GraphQuery
        from app.models.database import Novel, Chapter
        from pathlib import Path
        
        graph_builder = GraphBuilder()
        graph_query = GraphQuery()
        
        try:
            # 加载图谱
            graph = graph_builder.load_graph(novel_id)
            if not graph:
                logger.warning(f"图谱不存在，无法使用图谱增强")
                return []
            
            # 获取实体的关系演变
            evolutions = []
            if entity not in graph:
                logger.warning(f"实体 {entity} 不在图谱中")
                return []
            
            for neighbor in graph.neighbors(entity):
                relation_evolution = graph_query.get_relationship_evolution(
                    graph, entity, neighbor
                )
                if len(relation_evolution) > 1:  # 有演变
                    evolutions.append({
                        'target': neighbor,
                        'evolution': relation_evolution
                    })
            
            if not evolutions:
                logger.info(f"实体 {entity} 无关系演变")
                return []
            
            # 针对每个演变节点，检索前后的原文描述
            evidence_pairs = []
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            
            if not novel:
                return []
            
            for evo in evolutions:
                for i in range(len(evo['evolution']) - 1):
                    early = evo['evolution'][i]
                    late = evo['evolution'][i+1]
                    
                    # 仅检索关系类型变化的节点（避免无效检索）
                    if early['type'] != late['type']:
                        # 检索两个时期的原文描述
                        early_text = self._retrieve_at_chapter(
                            entity, early['chapter'], novel, db
                        )
                        late_text = self._retrieve_at_chapter(
                            entity, late['chapter'], novel, db
                        )
                        
                        if early_text and late_text:
                            evidence_pairs.append({
                                'early_chapter': early['chapter'],
                                'late_chapter': late['chapter'],
                                'early_relation': early['type'],
                                'late_relation': late['type'],
                                'early_text': early_text,
                                'late_text': late_text,
                                'target': evo['target']
                            })
            
            logger.info(f"✅ 基于图谱收集了 {len(evidence_pairs)} 对矛盾证据")
            return evidence_pairs
            
        except Exception as e:
            logger.error(f"图谱增强证据收集失败: {e}")
            return []
    
    def _retrieve_at_chapter(
        self,
        entity: str,
        chapter_num: int,
        novel,
        db: Session
    ) -> Optional[str]:
        """
        在指定章节检索包含实体的段落
        
        Args:
            entity: 实体名称
            chapter_num: 章节号
            novel: 小说对象
            db: 数据库会话
        
        Returns:
            Optional[str]: 段落内容
        """
        from app.models.database import Chapter
        from pathlib import Path
        
        try:
            chapter = db.query(Chapter).filter(
                Chapter.novel_id == novel.id,
                Chapter.chapter_num == chapter_num
            ).first()
            
            if not chapter:
                return None
            
            file_path = Path(novel.file_path)
            if not file_path.exists():
                return None
            
            # 尝试多种编码
            content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.seek(chapter.start_pos)
                        content = f.read(min(2000, chapter.end_pos - chapter.start_pos))
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                return None
            
            # 查找包含实体的段落
            if entity in content:
                idx = content.find(entity)
                start = max(0, idx - 150)
                end = min(len(content), idx + 350)
                return content[start:end]
            
            return None
            
        except Exception as e:
            logger.warning(f"检索章节{chapter_num}失败: {e}")
            return None


# 全局实例
_evidence_collector: Optional[EvidenceCollector] = None


def get_evidence_collector() -> EvidenceCollector:
    """获取全局证据收集器实例（单例）"""
    global _evidence_collector
    if _evidence_collector is None:
        _evidence_collector = EvidenceCollector()
    return _evidence_collector

