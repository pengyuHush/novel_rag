"""
图谱数据导出器

将NetworkX图谱转换为前端可用的JSON格式
"""

import logging
from typing import List, Dict, Optional
import networkx as nx

logger = logging.getLogger(__name__)


class GraphExporter:
    """图谱数据导出器"""
    
    def __init__(self):
        """初始化导出器"""
        logger.info("✅ 图谱导出器初始化完成")
    
    def export_to_json(
        self,
        graph: nx.MultiDiGraph,
        chapter_filter: Optional[tuple] = None,
        max_nodes: int = 50,
        min_importance: float = 0.3
    ) -> Dict:
        """
        导出图谱为JSON格式
        
        Args:
            graph: NetworkX图谱对象
            chapter_filter: 章节范围过滤 (start_chapter, end_chapter)
            max_nodes: 最多返回节点数
            min_importance: 最小重要性阈值
        
        Returns:
            Dict: 包含nodes和edges的JSON数据
        """
        # 1. 筛选节点
        filtered_nodes = self._filter_nodes(
            graph, chapter_filter, max_nodes, min_importance
        )
        
        # 2. 筛选边
        filtered_edges = self._filter_edges(
            graph, filtered_nodes, chapter_filter
        )
        
        # 3. 转换为JSON格式
        json_data = {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'metadata': {
                'total_nodes': len(filtered_nodes),
                'total_edges': len(filtered_edges),
                'chapter_filter': chapter_filter,
            }
        }
        
        logger.info(
            f"✅ 图谱导出完成: {len(filtered_nodes)} 节点, "
            f"{len(filtered_edges)} 边"
        )
        
        return json_data
    
    def _filter_nodes(
        self,
        graph: nx.MultiDiGraph,
        chapter_filter: Optional[tuple],
        max_nodes: int,
        min_importance: float
    ) -> List[Dict]:
        """
        筛选和转换节点
        
        Args:
            graph: 图谱对象
            chapter_filter: 章节范围
            max_nodes: 最多节点数
            min_importance: 最小重要性
        
        Returns:
            List[Dict]: 节点列表
        """
        nodes = []
        
        for node_id, data in graph.nodes(data=True):
            # 重要性过滤
            importance = data.get('importance', 0.5)
            if importance < min_importance:
                continue
            
            # 章节范围过滤
            if chapter_filter:
                start_ch, end_ch = chapter_filter
                first_chapter = data.get('first_chapter', 1)
                last_chapter = data.get('last_chapter')
                
                # 检查节点是否在章节范围内活跃
                if first_chapter > end_ch:
                    continue
                if last_chapter and last_chapter < start_ch:
                    continue
            
            # 转换节点数据
            node_json = {
                'id': node_id,
                'name': node_id,
                'type': data.get('type', 'unknown'),
                'importance': importance,
                'first_chapter': data.get('first_chapter', 1),
                'last_chapter': data.get('last_chapter'),
                'is_protagonist': data.get('is_protagonist', False),
                'is_antagonist': data.get('is_antagonist', False),
                # 额外属性
                'attributes': {
                    k: v for k, v in data.items()
                    if k not in ['type', 'importance', 'first_chapter', 
                                'last_chapter', 'is_protagonist', 'is_antagonist']
                }
            }
            
            nodes.append(node_json)
        
        # 按重要性排序
        nodes.sort(key=lambda x: -x['importance'])
        
        # 限制数量
        return nodes[:max_nodes]
    
    def _filter_edges(
        self,
        graph: nx.MultiDiGraph,
        filtered_nodes: List[Dict],
        chapter_filter: Optional[tuple]
    ) -> List[Dict]:
        """
        筛选和转换边
        
        Args:
            graph: 图谱对象
            filtered_nodes: 已筛选的节点列表
            chapter_filter: 章节范围
        
        Returns:
            List[Dict]: 边列表
        """
        node_ids = {node['id'] for node in filtered_nodes}
        edges = []
        
        for source, target, key, data in graph.edges(keys=True, data=True):
            # 只保留两端都在筛选节点中的边
            if source not in node_ids or target not in node_ids:
                continue
            
            # 章节范围过滤
            if chapter_filter:
                start_ch, end_ch = chapter_filter
                edge_start = data.get('start_chapter', 1)
                edge_end = data.get('end_chapter')
                
                # 检查边是否在章节范围内有效
                if edge_start > end_ch:
                    continue
                if edge_end and edge_end < start_ch:
                    continue
            
            # 转换边数据
            edge_json = {
                'source': source,
                'target': target,
                'relation_type': data.get('relation_type', '未知'),
                'strength': data.get('strength', 0.5),
                'start_chapter': data.get('start_chapter', 1),
                'end_chapter': data.get('end_chapter'),
                'is_public': data.get('is_public', True),
                'reveal_chapter': data.get('reveal_chapter'),
                # 演变信息
                'evolution': data.get('evolution', []),
            }
            
            edges.append(edge_json)
        
        return edges
    
    def export_node_details(
        self,
        graph: nx.MultiDiGraph,
        node_id: str
    ) -> Optional[Dict]:
        """
        导出单个节点的详细信息
        
        Args:
            graph: 图谱对象
            node_id: 节点ID
        
        Returns:
            Optional[Dict]: 节点详细信息
        """
        if node_id not in graph:
            return None
        
        data = graph.nodes[node_id]
        
        # 获取所有邻居
        neighbors_out = list(graph.successors(node_id))
        neighbors_in = list(graph.predecessors(node_id))
        
        # 获取所有关系
        relations = []
        for _, target, key, edge_data in graph.out_edges(node_id, keys=True, data=True):
            relations.append({
                'direction': 'outgoing',
                'target': target,
                'type': edge_data.get('relation_type', '未知'),
                'strength': edge_data.get('strength', 0.5),
                'start_chapter': edge_data.get('start_chapter'),
                'end_chapter': edge_data.get('end_chapter'),
            })
        
        for source, _, key, edge_data in graph.in_edges(node_id, keys=True, data=True):
            relations.append({
                'direction': 'incoming',
                'source': source,
                'type': edge_data.get('relation_type', '未知'),
                'strength': edge_data.get('strength', 0.5),
                'start_chapter': edge_data.get('start_chapter'),
                'end_chapter': edge_data.get('end_chapter'),
            })
        
        details = {
            'id': node_id,
            'name': node_id,
            'type': data.get('type', 'unknown'),
            'importance': data.get('importance', 0.5),
            'first_chapter': data.get('first_chapter', 1),
            'last_chapter': data.get('last_chapter'),
            'neighbors_count': len(set(neighbors_out + neighbors_in)),
            'relations': relations,
            'attributes': data,
        }
        
        return details


# 全局实例
_graph_exporter: Optional[GraphExporter] = None


def get_graph_exporter() -> GraphExporter:
    """获取全局图谱导出器实例（单例）"""
    global _graph_exporter
    if _graph_exporter is None:
        _graph_exporter = GraphExporter()
    return _graph_exporter

