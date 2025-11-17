"""
T095-T096: 图谱分析器 (User Story 3: 知识图谱与GraphRAG)

功能:
- PageRank重要性计算
- 社区检测
- 中心度分析
- 章节重要性评分
"""

import networkx as nx
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """图谱分析器"""
    
    def compute_pagerank(
        self,
        graph: nx.MultiDiGraph,
        alpha: float = 0.85,
        max_iter: int = 100
    ) -> Dict[str, float]:
        """
        T095: 计算PageRank重要性
        
        Args:
            graph: 图谱对象
            alpha: 阻尼系数(0-1)，推荐0.85
            max_iter: 最大迭代次数
        
        Returns:
            {'萧炎': 1.0, '药老': 0.9, ...}
        """
        if graph.number_of_nodes() == 0:
            return {}
        
        try:
            # NetworkX内置PageRank算法
            # 对于共现关系图，使用权重(strength)来提升重要关系的影响
            pagerank = nx.pagerank(
                graph,
                alpha=alpha,
                max_iter=max_iter,
                weight='strength'  # 使用边的strength属性作为权重
            )
            
            # 归一化到合理的范围(0.1-1.0)，避免过小的值
            if pagerank:
                min_val = min(pagerank.values())
                max_val = max(pagerank.values())
                
                if max_val > min_val:
                    # 线性归一化到 0.1-1.0 范围
                    normalized = {
                        node: 0.1 + 0.9 * (score - min_val) / (max_val - min_val)
                        for node, score in pagerank.items()
                    }
                    
                    logger.info(
                        f"PageRank计算完成: {len(pagerank)} 个节点 "
                        f"(范围: {min(normalized.values()):.3f} - {max(normalized.values()):.3f})"
                    )
                    
                    return normalized
                else:
                    # 所有节点重要性相同，设为中等重要性
                    logger.warning(f"所有节点PageRank值相同，设置为默认值0.5")
                    return {node: 0.5 for node in pagerank.keys()}
            
            return pagerank
            
        except Exception as e:
            logger.error(f"PageRank计算失败: {e}")
            return {}
    
    def update_node_importance(
        self,
        graph: nx.MultiDiGraph,
        pagerank: Dict[str, float]
    ):
        """
        更新节点的importance属性
        
        Args:
            graph: 图谱对象
            pagerank: PageRank结果
        """
        for node, importance in pagerank.items():
            if node in graph:
                graph.nodes[node]['importance'] = importance
        
        logger.info("节点重要性已更新")
    
    def compute_chapter_importance(
        self,
        graph: nx.MultiDiGraph,
        chapter_num: int
    ) -> float:
        """
        T096: 计算章节重要性评分
        
        评分维度:
        - 新增实体数量 (30%)
        - 关系变化数量 (50%)
        - 事件密度 (20%)
        
        Args:
            graph: 图谱对象
            chapter_num: 章节号
        
        Returns:
            重要性评分(0-1)
        """
        # 统计新增实体
        new_entities = self._count_new_entities(graph, chapter_num)
        
        # 统计关系变化
        relation_changes = self._count_relation_changes(graph, chapter_num)
        
        # 统计事件密度(关系数量/该章出现的实体数量)
        active_entities = self._count_active_entities(graph, chapter_num)
        event_density = relation_changes / max(active_entities, 1)
        
        # 加权计算
        importance = (
            0.30 * min(new_entities / 5, 1.0) +  # 归一化到0-1
            0.50 * min(relation_changes / 10, 1.0) +
            0.20 * min(event_density, 1.0)
        )
        
        return importance
    
    def _count_new_entities(self, graph: nx.MultiDiGraph, chapter_num: int) -> int:
        """统计章节新增实体数量"""
        count = 0
        for node, data in graph.nodes(data=True):
            if data.get('first_chapter') == chapter_num:
                count += 1
        return count
    
    def _count_relation_changes(self, graph: nx.MultiDiGraph, chapter_num: int) -> int:
        """统计章节关系变化数量"""
        count = 0
        for u, v, data in graph.edges(data=True):
            # 关系开始或结束
            if data.get('start_chapter') == chapter_num or data.get('end_chapter') == chapter_num:
                count += 1
            
            # 关系演变
            evolution = data.get('evolution', [])
            for evt in evolution:
                if evt.get('chapter') == chapter_num:
                    count += 1
                    break
        
        return count
    
    def _count_active_entities(self, graph: nx.MultiDiGraph, chapter_num: int) -> int:
        """统计章节活跃实体数量"""
        count = 0
        for node, data in graph.nodes(data=True):
            first_chapter = data.get('first_chapter', 1)
            last_chapter = data.get('last_chapter')
            
            if first_chapter <= chapter_num and (last_chapter is None or last_chapter >= chapter_num):
                count += 1
        
        return count
    
    def get_main_characters(
        self,
        graph: nx.MultiDiGraph,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        获取主要角色(按重要性排序)
        
        Args:
            graph: 图谱对象
            top_n: 返回前N个
        
        Returns:
            [('萧炎', 1.0), ('药老', 0.9), ...]
        """
        characters = []
        
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'character':
                importance = data.get('importance', 0.5)
                characters.append((node, importance))
        
        # 按重要性排序
        characters.sort(key=lambda x: x[1], reverse=True)
        
        return characters[:top_n]
    
    def get_entity_relationships(
        self,
        graph: nx.MultiDiGraph,
        entity_name: str,
        chapter_num: Optional[int] = None
    ) -> List[Dict]:
        """
        获取实体的所有关系
        
        Args:
            graph: 图谱对象
            entity_name: 实体名称
            chapter_num: 指定章节(可选),如果指定则只返回该章节有效的关系
        
        Returns:
            [
                {
                    'target': '药老',
                    'relation_type': '师徒',
                    'strength': 0.9,
                    'start_chapter': 3,
                    'end_chapter': None
                },
                ...
            ]
        """
        relationships = []
        
        if entity_name not in graph:
            return relationships
        
        # 出边(source -> target)
        for _, target, data in graph.out_edges(entity_name, data=True):
            if chapter_num is None or self._is_relation_active(data, chapter_num):
                relationships.append({
                    'direction': 'outgoing',
                    'target': target,
                    'relation_type': data.get('relation_type'),
                    'strength': data.get('strength', 0.5),
                    'start_chapter': data.get('start_chapter'),
                    'end_chapter': data.get('end_chapter')
                })
        
        # 入边(source -> entity_name)
        for source, _, data in graph.in_edges(entity_name, data=True):
            if chapter_num is None or self._is_relation_active(data, chapter_num):
                relationships.append({
                    'direction': 'incoming',
                    'source': source,
                    'relation_type': data.get('relation_type'),
                    'strength': data.get('strength', 0.5),
                    'start_chapter': data.get('start_chapter'),
                    'end_chapter': data.get('end_chapter')
                })
        
        return relationships
    
    def _is_relation_active(self, edge_data: Dict, chapter_num: int) -> bool:
        """判断关系在指定章节是否有效"""
        start_chapter = edge_data.get('start_chapter', 1)
        end_chapter = edge_data.get('end_chapter')
        
        return start_chapter <= chapter_num and (end_chapter is None or end_chapter >= chapter_num)


# 全局实例
_graph_analyzer = None

def get_graph_analyzer() -> GraphAnalyzer:
    """获取图谱分析器单例"""
    global _graph_analyzer
    if _graph_analyzer is None:
        _graph_analyzer = GraphAnalyzer()
    return _graph_analyzer

