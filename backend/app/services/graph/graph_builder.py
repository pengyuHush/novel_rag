"""
T089-T094: 知识图谱构建器 (User Story 3: 知识图谱与GraphRAG)

功能:
- 初始化NetworkX图谱
- 添加节点(实体)和边(关系)
- 时序属性标注
- 图谱持久化(pickle)
"""

import networkx as nx
import pickle
import os
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class GraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, data_dir: str = "./data/graphs"):
        """
        Args:
            data_dir: 图谱文件存储目录（相对于backend目录）
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def create_graph(self, novel_id: int) -> nx.MultiDiGraph:
        """
        T089: 初始化NetworkX图谱
        
        Args:
            novel_id: 小说ID
        
        Returns:
            空的多重有向图
        """
        # 使用MultiDiGraph支持同一对节点间的多种关系
        graph = nx.MultiDiGraph()
        graph.graph['novel_id'] = novel_id
        graph.graph['created_at'] = str(pd.Timestamp.now())
        
        logger.info(f"创建小说{novel_id}的知识图谱")
        return graph
    
    def add_entity(
        self,
        graph: nx.MultiDiGraph,
        entity_name: str,
        entity_type: str,
        first_chapter: int,
        last_chapter: Optional[int] = None,
        importance: float = 0.5,
        **attributes
    ):
        """
        T090: 添加节点(实体)
        
        Args:
            graph: 图谱对象
            entity_name: 实体名称
            entity_type: 实体类型('character', 'location', 'organization')
            first_chapter: 首次出现章节
            last_chapter: 最后出现章节
            importance: 重要性(0-1)
            **attributes: 其他属性
        """
        graph.add_node(
            entity_name,
            type=entity_type,
            first_chapter=first_chapter,
            last_chapter=last_chapter,
            importance=importance,
            **attributes
        )
        
        logger.debug(f"添加节点: {entity_name} ({entity_type})")
    
    def add_relation(
        self,
        graph: nx.MultiDiGraph,
        source: str,
        target: str,
        relation_type: str,
        start_chapter: int,
        end_chapter: Optional[int] = None,
        strength: float = 0.5,
        evolution: Optional[List[Dict]] = None,
        **attributes
    ):
        """
        T092: 添加边(关系)
        
        Args:
            graph: 图谱对象
            source: 源实体名称
            target: 目标实体名称
            relation_type: 关系类型('盟友','敌对','师徒'等)
            start_chapter: 关系开始章节
            end_chapter: 关系结束章节
            strength: 关系强度(0-1)
            evolution: 关系演变轨迹 [{'chapter': 10, 'type': '陌生'}, ...]
            **attributes: 其他属性
        """
        # T093: 添加时序属性
        graph.add_edge(
            source,
            target,
            relation_type=relation_type,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            strength=strength,
            evolution=evolution or [],
            **attributes
        )
        
        logger.debug(
            f"添加关系: {source} --[{relation_type}]--> {target} "
            f"(章节{start_chapter}-{end_chapter})"
        )
    
    def save_graph(
        self,
        graph: nx.MultiDiGraph,
        novel_id: int
    ) -> str:
        """
        T094: 图谱持久化(pickle)
        
        Args:
            graph: 图谱对象
            novel_id: 小说ID
        
        Returns:
            保存的文件路径
        """
        file_path = self.data_dir / f"novel_{novel_id}_graph.pkl"
        
        with open(file_path, 'wb') as f:
            pickle.dump(graph, f)
        
        logger.info(
            f"图谱已保存: {file_path} "
            f"({graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边)"
        )
        
        return str(file_path)
    
    def load_graph(self, novel_id: int) -> Optional[nx.MultiDiGraph]:
        """
        加载图谱
        
        Args:
            novel_id: 小说ID
        
        Returns:
            图谱对象,不存在则返回None
        """
        file_path = self.data_dir / f"novel_{novel_id}_graph.pkl"
        
        if not file_path.exists():
            logger.warning(f"图谱文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                graph = pickle.load(f)
            
            logger.info(
                f"图谱已加载: {file_path} "
                f"({graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边)"
            )
            return graph
            
        except Exception as e:
            logger.error(f"加载图谱失败: {e}")
            return None
    
    def graph_exists(self, novel_id: int) -> bool:
        """检查图谱是否存在"""
        file_path = self.data_dir / f"novel_{novel_id}_graph.pkl"
        return file_path.exists()
    
    def delete_graph(self, novel_id: int) -> bool:
        """删除图谱文件"""
        file_path = self.data_dir / f"novel_{novel_id}_graph.pkl"
        
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"图谱已删除: {file_path}")
            return True
        
        return False
    
    def get_graph_stats(self, graph: nx.MultiDiGraph) -> Dict:
        """
        获取图谱统计信息
        
        Returns:
            {
                'nodes': 节点数,
                'edges': 边数,
                'avg_degree': 平均度数,
                'density': 密度
            }
        """
        return {
            'nodes': graph.number_of_nodes(),
            'edges': graph.number_of_edges(),
            'avg_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
            'density': nx.density(graph)
        }


# 添加pandas导入用于时间戳
try:
    import pandas as pd
except ImportError:
    # 如果pandas未安装,使用datetime
    from datetime import datetime
    class pd:
        class Timestamp:
            @staticmethod
            def now():
                return datetime.now()


# 全局实例
_graph_builder = None

def get_graph_builder() -> GraphBuilder:
    """获取图谱构建器单例"""
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = GraphBuilder()
    return _graph_builder

