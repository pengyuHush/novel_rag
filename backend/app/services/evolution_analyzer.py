"""
演变分析模块

实现角色/关系演变分析功能：
- 时序分段检索（早期/中期/后期）
- 演变点识别（关键转折）
- 演变轨迹生成
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.database import Novel, Chapter
from app.services.embedding_service import get_embedding_service
from app.core.chromadb_client import get_chroma_client

logger = logging.getLogger(__name__)


class EvolutionAnalyzer:
    """演变分析器"""
    
    # 演变关键词（用于识别转折点）
    EVOLUTION_KEYWORDS = [
        # 情感变化
        "爱上", "讨厌", "恨", "喜欢", "敬佩", "鄙视", "背叛", "原谅",
        # 关系变化
        "成为", "变成", "转变", "改变", "不再", "开始", "结束",
        # 能力变化
        "突破", "领悟", "觉醒", "失去", "获得", "掌握", "丧失",
        # 身份变化
        "继承", "接任", "上位", "退位", "晋升", "降职",
        # 态度变化
        "意识到", "发现", "明白", "了解", "误解", "怀疑",
    ]
    
    def __init__(self):
        """初始化演变分析器"""
        self.embedding_service = get_embedding_service()
        self.chroma_client = get_chroma_client()
        
        logger.info("✅ 演变分析器初始化完成")
    
    def temporal_segmented_retrieval(
        self,
        db: Session,
        novel_id: int,
        query_embedding: List[float],
        top_k_per_period: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        时序分段检索
        
        将小说分为早期/中期/后期三个阶段，分别检索
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query_embedding: 查询向量
            top_k_per_period: 每个时期返回的结果数量
        
        Returns:
            Dict[str, List[Dict]]: 按时期分组的检索结果
        """
        # 获取小说章节信息
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            logger.error(f"❌ 小说不存在: {novel_id}")
            return {"early": [], "middle": [], "late": []}
        
        total_chapters = novel.total_chapters
        
        # 划分时期（早期1/3，中期1/3，后期1/3）
        early_end = total_chapters // 3
        middle_end = (total_chapters * 2) // 3
        
        periods = {
            "early": (1, early_end),
            "middle": (early_end + 1, middle_end),
            "late": (middle_end + 1, total_chapters)
        }
        
        logger.info(f"📅 时序分段: 早期(1-{early_end}), 中期({early_end+1}-{middle_end}), 后期({middle_end+1}-{total_chapters})")
        
        results = {}
        collection_name = f"novel_{novel_id}"
        
        for period_name, (start_chapter, end_chapter) in periods.items():
            try:
                # 按章节范围过滤检索
                period_results = self.chroma_client.query_documents(
                    collection_name=collection_name,
                    query_embeddings=[query_embedding],
                    n_results=top_k_per_period * 2,  # 多检索一些以便过滤
                    where={
                        "chapter_num": {
                            "$gte": start_chapter,
                            "$lte": end_chapter
                        }
                    }
                )
                
                # 转换为标准格式
                documents = period_results.get('documents', [[]])[0]
                metadatas = period_results.get('metadatas', [[]])[0]
                distances = period_results.get('distances', [[]])[0]
                
                period_chunks = []
                for doc, metadata, distance in zip(documents, metadatas, distances):
                    period_chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'score': 1 - distance,
                        'period': period_name
                    })
                
                # 按分数排序，取Top-K
                period_chunks.sort(key=lambda x: -x['score'])
                results[period_name] = period_chunks[:top_k_per_period]
                
                logger.info(f"✅ {period_name}期检索完成: {len(results[period_name])} 个结果")
                
            except Exception as e:
                logger.error(f"❌ {period_name}期检索失败: {e}")
                results[period_name] = []
        
        return results
    
    def identify_evolution_points(
        self,
        temporal_results: Dict[str, List[Dict]],
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        识别演变点（关键转折）
        
        通过关键词匹配识别可能的演变转折点
        
        Args:
            temporal_results: 时序分段检索结果
            threshold: 相关性阈值（低于此值的结果将被过滤）
        
        Returns:
            List[Dict]: 演变点列表
        """
        evolution_points = []
        
        for period, chunks in temporal_results.items():
            for chunk in chunks:
                # 检查是否包含演变关键词
                content = chunk['content']
                matched_keywords = []
                
                for keyword in self.EVOLUTION_KEYWORDS:
                    if keyword in content:
                        matched_keywords.append(keyword)
                
                # 如果包含演变关键词且分数足够高，标记为演变点
                if matched_keywords and chunk['score'] >= threshold:
                    evolution_points.append({
                        'period': period,
                        'chapter_num': chunk['metadata'].get('chapter_num'),
                        'chapter_title': chunk['metadata'].get('chapter_title'),
                        'content': content,
                        'keywords': matched_keywords,
                        'score': chunk['score'],
                        'is_key_point': True
                    })
        
        # 按章节号排序
        evolution_points.sort(key=lambda x: x['chapter_num'])
        
        logger.info(f"✅ 识别到 {len(evolution_points)} 个演变点")
        
        return evolution_points
    
    def generate_evolution_trajectory(
        self,
        db: Session,
        novel_id: int,
        query: str,
        entity_name: Optional[str] = None
    ) -> Dict:
        """
        生成演变轨迹
        
        完整的演变分析流程：
        1. 时序分段检索
        2. 识别演变点
        3. 生成轨迹摘要
        
        Args:
            db: 数据库会话
            novel_id: 小说ID
            query: 查询文本（如"萧炎的实力如何演变"）
            entity_name: 可选，指定实体名称
        
        Returns:
            Dict: 演变轨迹分析结果
        """
        logger.info(f"📈 开始演变分析: {query}")
        
        # 1. 查询向量化
        from app.services.zhipu_client import get_zhipu_client
        zhipu_client = get_zhipu_client()
        query_embedding = zhipu_client.embed_text(query)
        
        # 2. 时序分段检索
        temporal_results = self.temporal_segmented_retrieval(
            db, novel_id, query_embedding, top_k_per_period=5
        )
        
        # 3. 识别演变点
        evolution_points = self.identify_evolution_points(temporal_results)
        
        # 4. 按时期汇总
        summary_by_period = {}
        for period in ["early", "middle", "late"]:
            period_chunks = temporal_results.get(period, [])
            period_evolution_points = [
                ep for ep in evolution_points if ep['period'] == period
            ]
            
            summary_by_period[period] = {
                'total_chunks': len(period_chunks),
                'evolution_points': len(period_evolution_points),
                'key_chapters': list(set([
                    ep['chapter_num'] for ep in period_evolution_points
                ])),
                'keywords': list(set([
                    kw for ep in period_evolution_points for kw in ep['keywords']
                ]))
            }
        
        # 5. 构建完整轨迹
        trajectory = {
            'query': query,
            'entity_name': entity_name,
            'temporal_results': temporal_results,
            'evolution_points': evolution_points,
            'summary_by_period': summary_by_period,
            'total_evolution_points': len(evolution_points)
        }
        
        logger.info(f"✅ 演变分析完成: {len(evolution_points)} 个关键点")
        
        return trajectory
    
    def extract_entity_from_query(self, query: str) -> Optional[str]:
        """
        从查询中提取实体名称
        
        使用简单的正则匹配提取人名/组织名
        
        Args:
            query: 查询文本
        
        Returns:
            Optional[str]: 实体名称
        """
        import re
        
        # 匹配模式："XXX的YYY"，"XXX如何"，"XXX为什么"
        patterns = [
            r'([^的]+?)的',
            r'([^如何]+?)如何',
            r'([^为什么]+?)为什么',
            r'([^怎么]+?)怎么',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                entity = match.group(1).strip()
                # 过滤无效提取
                if len(entity) >= 2 and len(entity) <= 10:
                    return entity
        
        return None


# 全局演变分析器实例
_evolution_analyzer: Optional[EvolutionAnalyzer] = None


def get_evolution_analyzer() -> EvolutionAnalyzer:
    """获取全局演变分析器实例（单例）"""
    global _evolution_analyzer
    if _evolution_analyzer is None:
        _evolution_analyzer = EvolutionAnalyzer()
    return _evolution_analyzer

