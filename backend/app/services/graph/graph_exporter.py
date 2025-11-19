"""
图谱数据导出器

将NetworkX图谱转换为前端可用的JSON格式
"""

import logging
from typing import List, Dict, Optional, Tuple
import networkx as nx
from collections import Counter

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
        min_importance: float = 0.3,
        include_layout: bool = False,
        layout_algorithm: str = 'spring'
    ) -> Dict:
        """
        导出图谱为JSON格式
        
        Args:
            graph: NetworkX图谱对象
            chapter_filter: 章节范围过滤 (start_chapter, end_chapter)
            max_nodes: 最多返回节点数
            min_importance: 最小重要性阈值
            include_layout: 是否包含布局坐标
            layout_algorithm: 布局算法
        
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
        
        # 3. 添加布局坐标（如果需要）
        if include_layout and filtered_nodes:
            from .layout_calculator import get_layout_calculator
            
            # 创建子图用于布局计算
            node_ids = [n['id'] for n in filtered_nodes]
            subgraph = graph.subgraph(node_ids).copy()
            
            # 计算布局
            layout_calc = get_layout_calculator()
            positions = layout_calc.calculate_layout(
                subgraph,
                algorithm=layout_algorithm,
                width=1000,
                height=1000
            )
            
            # 添加坐标到节点
            for node in filtered_nodes:
                if node['id'] in positions:
                    x, y = positions[node['id']]
                    node['x'] = x
                    node['y'] = y
        
        # 4. 收集关系类型
        relation_types = list(set(edge['relationType'] for edge in filtered_edges))
        
        # 5. 转换为JSON格式
        json_data = {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'metadata': {
                'total_nodes': len(filtered_nodes),
                'total_edges': len(filtered_edges),
                'chapter_filter': chapter_filter,
                'relation_types': relation_types,
                'layout_algorithm': layout_algorithm if include_layout else None,
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
            
            # 计算节点度数
            in_degree = graph.in_degree(node_id)
            out_degree = graph.out_degree(node_id)
            total_degree = in_degree + out_degree
            
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
                'degree': total_degree,  # 新增：节点度数
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
        
        # 调试日志
        total_edges = graph.number_of_edges()
        logger.info(f"🔍 开始筛选边: 图谱总边数={total_edges}, 筛选后节点数={len(node_ids)}")
        
        filtered_by_node = 0
        filtered_by_chapter = 0
        
        for source, target, key, data in graph.edges(keys=True, data=True):
            # 只保留两端都在筛选节点中的边
            if source not in node_ids or target not in node_ids:
                filtered_by_node += 1
                continue
            
            # 章节范围过滤
            if chapter_filter:
                start_ch, end_ch = chapter_filter
                edge_start = data.get('start_chapter', 1)
                edge_end = data.get('end_chapter')
                
                # 检查边是否在章节范围内有效
                if edge_start > end_ch:
                    filtered_by_chapter += 1
                    continue
                if edge_end and edge_end < start_ch:
                    filtered_by_chapter += 1
                    continue
            
            # 转换边数据
            edge_json = {
                'source': source,
                'target': target,
                'relationType': data.get('relation_type', '未知'),  # 使用驼峰命名
                'strength': data.get('strength', 0.5),
                'startChapter': data.get('start_chapter', 1),  # 使用驼峰命名
                'endChapter': data.get('end_chapter'),  # 使用驼峰命名
                'isPublic': data.get('is_public', True),
                'revealChapter': data.get('reveal_chapter'),
                # 演变信息
                'evolution': data.get('evolution', []),
            }
            
            edges.append(edge_json)
        
        logger.info(
            f"✅ 边筛选完成: 原始{total_edges}条 -> "
            f"节点过滤掉{filtered_by_node}条, "
            f"章节过滤掉{filtered_by_chapter}条, "
            f"最终{len(edges)}条"
        )
        
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
    
    def export_with_layout(
        self,
        graph: nx.MultiDiGraph,
        layout_type: str = 'force',
        chapter_filter: Optional[tuple] = None,
        max_nodes: int = 50,
        min_importance: float = 0.3
    ) -> Dict:
        """
        导出带布局坐标的图谱数据
        
        Args:
            graph: 图谱对象
            layout_type: 布局类型
            chapter_filter: 章节范围
            max_nodes: 最大节点数
            min_importance: 最小重要性
        
        Returns:
            图谱数据（包含坐标）
        """
        return self.export_to_json(
            graph=graph,
            chapter_filter=chapter_filter,
            max_nodes=max_nodes,
            min_importance=min_importance,
            include_layout=True,
            layout_algorithm=layout_type
        )
    
    def export_statistics(self, graph: nx.MultiDiGraph) -> Dict:
        """
        导出图谱统计信息
        
        Args:
            graph: 图谱对象
        
        Returns:
            统计信息字典
        """
        # 基本统计
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        
        # 节点类型统计
        node_types = Counter()
        for _, data in graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            node_types[node_type] += 1
        
        # 关系类型统计
        relation_types = Counter()
        for _, _, _, data in graph.edges(keys=True, data=True):
            rel_type = data.get('relation_type', '未知')
            relation_types[rel_type] += 1
        
        # 度数统计
        degrees = [graph.in_degree(n) + graph.out_degree(n) for n in graph.nodes()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0
        
        # 密度
        density = nx.density(graph)
        
        # 章节范围
        chapter_ranges = []
        for _, data in graph.nodes(data=True):
            first = data.get('first_chapter', 0)
            last = data.get('last_chapter', 0)
            if first:
                chapter_ranges.append(first)
            if last:
                chapter_ranges.append(last)
        
        min_chapter = min(chapter_ranges) if chapter_ranges else 0
        max_chapter = max(chapter_ranges) if chapter_ranges else 0
        
        # 社区检测
        try:
            from .layout_calculator import get_layout_calculator
            layout_calc = get_layout_calculator()
            communities = layout_calc.detect_communities(graph)
            num_communities = len(set(communities.values()))
        except Exception as e:
            logger.warning(f"社区检测失败: {e}")
            num_communities = 0
        
        # Top节点（按度数）
        top_nodes = []
        nodes_with_degree = [(n, graph.in_degree(n) + graph.out_degree(n), 
                             graph.nodes[n].get('importance', 0.5)) 
                            for n in graph.nodes()]
        nodes_with_degree.sort(key=lambda x: (-x[2], -x[1]))  # 按重要性和度数排序
        
        for node, degree, importance in nodes_with_degree[:10]:
            top_nodes.append({
                'name': node,
                'degree': degree,
                'importance': importance,
                'type': graph.nodes[node].get('type', 'unknown')
            })
        
        return {
            'total_nodes': num_nodes,
            'total_edges': num_edges,
            'density': density,
            'average_degree': avg_degree,
            'max_degree': max_degree,
            'chapter_range': [min_chapter, max_chapter],
            'node_types': dict(node_types),
            'relation_types': dict(relation_types),
            'num_communities': num_communities,
            'top_nodes': top_nodes,
        }
    
    def export_relation_types_summary(self, graph: nx.MultiDiGraph) -> List[Dict]:
        """
        导出关系类型汇总
        
        Args:
            graph: 图谱对象
        
        Returns:
            关系类型列表
        """
        relation_stats = {}
        
        for _, _, _, data in graph.edges(keys=True, data=True):
            rel_type = data.get('relation_type', '未知')
            
            if rel_type not in relation_stats:
                relation_stats[rel_type] = {
                    'type': rel_type,
                    'count': 0,
                    'avg_strength': 0.0,
                    'strengths': []
                }
            
            relation_stats[rel_type]['count'] += 1
            strength = data.get('strength', 0.5)
            relation_stats[rel_type]['strengths'].append(strength)
        
        # 计算平均强度
        result = []
        for rel_type, stats in relation_stats.items():
            strengths = stats['strengths']
            avg_strength = sum(strengths) / len(strengths) if strengths else 0.5
            
            result.append({
                'type': rel_type,
                'count': stats['count'],
                'avgStrength': avg_strength,
            })
        
        # 按数量排序
        result.sort(key=lambda x: -x['count'])
        
        return result


# 全局实例
_graph_exporter: Optional[GraphExporter] = None


def get_graph_exporter() -> GraphExporter:
    """获取全局图谱导出器实例（单例）"""
    global _graph_exporter
    if _graph_exporter is None:
        _graph_exporter = GraphExporter()
    return _graph_exporter

