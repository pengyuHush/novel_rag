"""
图谱布局计算器

提供多种布局算法：
- Spring Layout（弹簧布局）：适合小规模网络（<100节点）
- ForceAtlas2：适合中大规模网络（100-1000节点）
- 分层圆形布局：作为备选方案
"""

import logging
from typing import Dict, List, Tuple, Optional
import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class LayoutCalculator:
    """图谱布局计算器"""
    
    def __init__(self):
        """初始化布局计算器"""
        logger.info("✅ 图谱布局计算器初始化完成")
    
    def calculate_layout(
        self,
        graph: nx.MultiDiGraph,
        algorithm: str = 'spring',
        width: float = 1000.0,
        height: float = 1000.0,
        **kwargs
    ) -> Dict[str, Tuple[float, float]]:
        """
        计算图谱布局
        
        Args:
            graph: NetworkX图谱对象
            algorithm: 布局算法 ('spring', 'force_atlas2', 'circular', 'hierarchical')
            width: 画布宽度
            height: 画布高度
            **kwargs: 额外参数
        
        Returns:
            Dict[str, Tuple[float, float]]: 节点ID -> (x, y) 坐标的字典
        """
        if graph.number_of_nodes() == 0:
            return {}
        
        logger.info(f"🎨 开始计算布局: algorithm={algorithm}, nodes={graph.number_of_nodes()}")
        
        if algorithm == 'spring':
            positions = self._spring_layout(graph, width, height, **kwargs)
        elif algorithm == 'force_atlas2':
            positions = self._force_atlas2_layout(graph, width, height, **kwargs)
        elif algorithm == 'circular':
            positions = self._circular_layout(graph, width, height, **kwargs)
        elif algorithm == 'hierarchical':
            positions = self._hierarchical_layout(graph, width, height, **kwargs)
        else:
            logger.warning(f"未知的布局算法: {algorithm}，使用默认的 spring 布局")
            positions = self._spring_layout(graph, width, height, **kwargs)
        
        logger.info(f"✅ 布局计算完成: {len(positions)} 个节点")
        return positions
    
    def _spring_layout(
        self,
        graph: nx.MultiDiGraph,
        width: float,
        height: float,
        iterations: int = 50,
        k: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Tuple[float, float]]:
        """
        弹簧布局（Fruchterman-Reingold算法）
        
        Args:
            graph: 图谱对象
            width: 宽度
            height: 高度
            iterations: 迭代次数
            k: 最佳距离（None时自动计算）
        
        Returns:
            节点位置字典
        """
        try:
            # 转换为无向图以便计算布局
            undirected = graph.to_undirected()
            
            # 使用NetworkX的spring_layout
            pos = nx.spring_layout(
                undirected,
                k=k,
                iterations=iterations,
                seed=42  # 固定随机种子以保证一致性
            )
            
            # 将坐标缩放到指定范围
            positions = {}
            for node, (x, y) in pos.items():
                positions[node] = (
                    x * width / 2 + width / 2,
                    y * height / 2 + height / 2
                )
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ Spring布局计算失败: {e}")
            return self._fallback_layout(graph, width, height)
    
    def _force_atlas2_layout(
        self,
        graph: nx.MultiDiGraph,
        width: float,
        height: float,
        iterations: int = 100,
        **kwargs
    ) -> Dict[str, Tuple[float, float]]:
        """
        ForceAtlas2 布局（适合大规模图）
        
        注意：需要安装 fa2 包。如果未安装，将回退到 spring 布局。
        
        Args:
            graph: 图谱对象
            width: 宽度
            height: 高度
            iterations: 迭代次数
        
        Returns:
            节点位置字典
        """
        try:
            from fa2 import ForceAtlas2
        except ImportError:
            logger.warning("⚠️ fa2 库未安装，ForceAtlas2 布局不可用，回退到 spring 布局")
            return self._spring_layout(graph, width, height, iterations=iterations, **kwargs)
        
        try:
            
            # 转换为无向图
            undirected = graph.to_undirected()
            
            # 初始化ForceAtlas2
            forceatlas2 = ForceAtlas2(
                outboundAttractionDistribution=True,
                linLogMode=False,
                adjustSizes=False,
                edgeWeightInfluence=1.0,
                jitterTolerance=1.0,
                barnesHutOptimize=True,
                barnesHutTheta=1.2,
                scalingRatio=2.0,
                strongGravityMode=False,
                gravity=1.0,
                verbose=False
            )
            
            # 计算布局
            pos_list = forceatlas2.forceatlas2_networkx_layout(
                undirected,
                pos=None,
                iterations=iterations
            )
            
            # 转换为字典并缩放
            positions = {}
            if pos_list:
                # 找到坐标范围
                xs = [p[0] for p in pos_list.values()]
                ys = [p[1] for p in pos_list.values()]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                # 归一化并缩放
                for node, (x, y) in pos_list.items():
                    norm_x = (x - min_x) / (max_x - min_x) if max_x != min_x else 0.5
                    norm_y = (y - min_y) / (max_y - min_y) if max_y != min_y else 0.5
                    positions[node] = (
                        norm_x * width,
                        norm_y * height
                    )
            
            return positions if positions else self._fallback_layout(graph, width, height)
            
        except Exception as e:
            logger.error(f"❌ ForceAtlas2布局计算失败: {e}")
            return self._fallback_layout(graph, width, height)
    
    def _circular_layout(
        self,
        graph: nx.MultiDiGraph,
        width: float,
        height: float,
        **kwargs
    ) -> Dict[str, Tuple[float, float]]:
        """
        圆形布局
        
        Args:
            graph: 图谱对象
            width: 宽度
            height: 高度
        
        Returns:
            节点位置字典
        """
        try:
            # 按重要性排序节点
            nodes = list(graph.nodes())
            nodes_data = [(n, graph.nodes[n].get('importance', 0.5)) for n in nodes]
            nodes_data.sort(key=lambda x: -x[1])  # 重要节点在前
            
            positions = {}
            n = len(nodes_data)
            
            # 圆形布局
            radius = min(width, height) * 0.4
            center_x = width / 2
            center_y = height / 2
            
            for i, (node, importance) in enumerate(nodes_data):
                angle = 2 * np.pi * i / n
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                positions[node] = (x, y)
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ 圆形布局计算失败: {e}")
            return self._fallback_layout(graph, width, height)
    
    def _hierarchical_layout(
        self,
        graph: nx.MultiDiGraph,
        width: float,
        height: float,
        **kwargs
    ) -> Dict[str, Tuple[float, float]]:
        """
        分层布局（基于重要性）
        
        Args:
            graph: 图谱对象
            width: 宽度
            height: 高度
        
        Returns:
            节点位置字典
        """
        try:
            # 按重要性分层
            nodes_by_importance = {}
            for node, data in graph.nodes(data=True):
                importance = data.get('importance', 0.5)
                level = int(importance * 3)  # 分为4层：0-3
                if level not in nodes_by_importance:
                    nodes_by_importance[level] = []
                nodes_by_importance[level].append(node)
            
            positions = {}
            num_levels = len(nodes_by_importance)
            
            for level_idx, (level, nodes) in enumerate(sorted(nodes_by_importance.items(), reverse=True)):
                y = height * (level_idx + 1) / (num_levels + 1)
                num_nodes = len(nodes)
                
                for node_idx, node in enumerate(nodes):
                    x = width * (node_idx + 1) / (num_nodes + 1)
                    positions[node] = (x, y)
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ 分层布局计算失败: {e}")
            return self._fallback_layout(graph, width, height)
    
    def _fallback_layout(
        self,
        graph: nx.MultiDiGraph,
        width: float,
        height: float
    ) -> Dict[str, Tuple[float, float]]:
        """
        备用布局（简单网格）
        
        Args:
            graph: 图谱对象
            width: 宽度
            height: 高度
        
        Returns:
            节点位置字典
        """
        nodes = list(graph.nodes())
        n = len(nodes)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        
        positions = {}
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = width * (col + 0.5) / cols
            y = height * (row + 0.5) / rows
            positions[node] = (x, y)
        
        return positions
    
    def detect_communities(
        self,
        graph: nx.MultiDiGraph
    ) -> Dict[str, int]:
        """
        社区检测
        
        Args:
            graph: 图谱对象
        
        Returns:
            Dict[str, int]: 节点ID -> 社区ID的字典
        """
        try:
            # 转换为无向图
            undirected = graph.to_undirected()
            
            # 使用Louvain算法进行社区检测
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(undirected)
                logger.info(f"✅ 社区检测完成: {len(set(partition.values()))} 个社区")
                return partition
            except ImportError:
                # 如果没有python-louvain，使用NetworkX的贪心模块化算法
                from networkx.algorithms import community
                communities = community.greedy_modularity_communities(undirected)
                
                partition = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        partition[node] = i
                
                logger.info(f"✅ 社区检测完成（贪心算法）: {len(communities)} 个社区")
                return partition
                
        except Exception as e:
            logger.error(f"❌ 社区检测失败: {e}")
            # 返回默认值：所有节点都在社区0
            return {node: 0 for node in graph.nodes()}
    
    def calculate_node_degrees(
        self,
        graph: nx.MultiDiGraph
    ) -> Dict[str, int]:
        """
        计算节点度数
        
        Args:
            graph: 图谱对象
        
        Returns:
            Dict[str, int]: 节点ID -> 度数的字典
        """
        degrees = {}
        for node in graph.nodes():
            # 计算总度数（入度 + 出度）
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            degrees[node] = in_degree + out_degree
        
        return degrees


# 全局实例
_layout_calculator: Optional[LayoutCalculator] = None


def get_layout_calculator() -> LayoutCalculator:
    """获取全局布局计算器实例（单例）"""
    global _layout_calculator
    if _layout_calculator is None:
        _layout_calculator = LayoutCalculator()
    return _layout_calculator


