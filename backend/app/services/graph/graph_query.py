"""
T099: 图谱查询 (User Story 3: 知识图谱与GraphRAG)

功能:
- 时序关系查询
- 关系演变追踪
- 实体邻居查询
"""

import networkx as nx
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class GraphQuery:
    """图谱查询器"""
    
    def get_relationship_at_chapter(
        self,
        graph: nx.MultiDiGraph,
        entity1: str,
        entity2: str,
        chapter_num: int
    ) -> Optional[str]:
        """
        T099: 查询特定章节两实体的关系
        
        Args:
            graph: 图谱对象
            entity1: 实体1
            entity2: 实体2
            chapter_num: 章节号
        
        Returns:
            关系类型,如'师徒','盟友',不存在则返回None
        """
        if entity1 not in graph or entity2 not in graph:
            return None
        
        # 检查entity1 -> entity2的边
        if graph.has_edge(entity1, entity2):
            for _, _, data in graph.edges(entity1, entity2, data=True):
                if self._is_relation_active(data, chapter_num):
                    return data.get('relation_type')
        
        # 检查entity2 -> entity1的边(反向)
        if graph.has_edge(entity2, entity1):
            for _, _, data in graph.edges(entity2, entity1, data=True):
                if self._is_relation_active(data, chapter_num):
                    return data.get('relation_type')
        
        return None
    
    def get_relationship_evolution(
        self,
        graph: nx.MultiDiGraph,
        entity1: str,
        entity2: str
    ) -> List[Dict]:
        """
        获取关系演变历史
        
        Args:
            graph: 图谱对象
            entity1: 实体1
            entity2: 实体2
        
        Returns:
            [
                {'chapter': 3, 'type': '陌生'},
                {'chapter': 10, 'type': '师徒'},
                ...
            ]
        """
        if entity1 not in graph or entity2 not in graph:
            return []
        
        # 查找entity1 -> entity2的边
        for _, _, data in graph.edges(entity1, entity2, data=True):
            evolution = data.get('evolution', [])
            if evolution:
                return evolution
        
        # 查找entity2 -> entity1的边
        for _, _, data in graph.edges(entity2, entity1, data=True):
            evolution = data.get('evolution', [])
            if evolution:
                return evolution
        
        return []
    
    def get_entity_neighbors(
        self,
        graph: nx.MultiDiGraph,
        entity: str,
        chapter_num: Optional[int] = None,
        max_neighbors: int = 10
    ) -> List[Tuple[str, str, float]]:
        """
        获取实体的邻居节点
        
        Args:
            graph: 图谱对象
            entity: 实体名称
            chapter_num: 指定章节(可选)
            max_neighbors: 最多返回邻居数
        
        Returns:
            [(neighbor_name, relation_type, importance), ...]
        """
        if entity not in graph:
            return []
        
        neighbors = []
        
        # 出边(entity -> neighbor)
        for _, neighbor, data in graph.out_edges(entity, data=True):
            if chapter_num is None or self._is_relation_active(data, chapter_num):
                importance = graph.nodes[neighbor].get('importance', 0.5)
                neighbors.append((
                    neighbor,
                    data.get('relation_type', '未知'),
                    importance
                ))
        
        # 入边(neighbor -> entity)
        for neighbor, _, data in graph.in_edges(entity, data=True):
            if chapter_num is None or self._is_relation_active(data, chapter_num):
                importance = graph.nodes[neighbor].get('importance', 0.5)
                neighbors.append((
                    neighbor,
                    data.get('relation_type', '未知'),
                    importance
                ))
        
        # 按重要性排序
        neighbors.sort(key=lambda x: x[2], reverse=True)
        
        return neighbors[:max_neighbors]
    
    def get_entities_by_chapter_range(
        self,
        graph: nx.MultiDiGraph,
        start_chapter: int,
        end_chapter: int
    ) -> List[str]:
        """
        获取指定章节范围内活跃的实体
        
        Args:
            graph: 图谱对象
            start_chapter: 起始章节
            end_chapter: 结束章节
        
        Returns:
            实体名称列表
        """
        entities = []
        
        for node, data in graph.nodes(data=True):
            first_chapter = data.get('first_chapter', 1)
            last_chapter = data.get('last_chapter')
            
            # 判断是否在范围内
            if first_chapter <= end_chapter and (last_chapter is None or last_chapter >= start_chapter):
                entities.append(node)
        
        return entities
    
    def find_path(
        self,
        graph: nx.MultiDiGraph,
        source: str,
        target: str,
        max_length: int = 3
    ) -> Optional[List[str]]:
        """
        查找两实体间的最短路径
        
        Args:
            graph: 图谱对象
            source: 源实体
            target: 目标实体
            max_length: 最大路径长度
        
        Returns:
            路径节点列表,如['萧炎', '药老', '美杜莎']
        """
        if source not in graph or target not in graph:
            return None
        
        try:
            path = nx.shortest_path(graph, source, target, weight=None)
            if len(path) <= max_length + 1:  # +1因为路径包含起点和终点
                return path
        except nx.NetworkXNoPath:
            pass
        
        return None
    
    def _is_relation_active(self, edge_data: Dict, chapter_num: int) -> bool:
        """判断关系在指定章节是否有效"""
        start_chapter = edge_data.get('start_chapter', 1)
        end_chapter = edge_data.get('end_chapter')
        
        return start_chapter <= chapter_num and (end_chapter is None or end_chapter >= chapter_num)


# 全局实例
_graph_query = None

def get_graph_query() -> GraphQuery:
    """获取图谱查询器单例"""
    global _graph_query
    if _graph_query is None:
        _graph_query = GraphQuery()
    return _graph_query

