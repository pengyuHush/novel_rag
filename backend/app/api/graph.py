"""
图谱可视化 API

提供关系图和时间线数据
"""

import logging
import pickle
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.graph.graph_exporter import get_graph_exporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


class RelationGraphResponse(BaseModel):
    """关系图响应"""
    nodes: list
    edges: list
    metadata: dict


class TimelineResponse(BaseModel):
    """时间线响应"""
    events: list
    metadata: dict


@router.get("/relations/{novel_id}", response_model=RelationGraphResponse)
async def get_relation_graph(
    novel_id: int,
    start_chapter: Optional[int] = Query(None, description="起始章节"),
    end_chapter: Optional[int] = Query(None, description="结束章节"),
    max_nodes: int = Query(50, ge=10, le=200, description="最大节点数"),
    min_importance: float = Query(0.3, ge=0.0, le=1.0, description="最小重要性阈值")
):
    """
    获取小说关系图数据
    
    Args:
        novel_id: 小说ID
        start_chapter: 起始章节（可选）
        end_chapter: 结束章节（可选）
        max_nodes: 最大节点数
        min_importance: 最小重要性阈值
    
    Returns:
        RelationGraphResponse: 关系图数据
    """
    try:
        # 加载图谱
        graph_path = Path(f"./backend/data/graphs/novel_{novel_id}_graph.pkl")
        if not graph_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"小说 {novel_id} 的知识图谱不存在，请先完成索引"
            )
        
        with open(graph_path, 'rb') as f:
            graph = pickle.load(f)
        
        # 章节范围过滤
        chapter_filter = None
        if start_chapter is not None and end_chapter is not None:
            chapter_filter = (start_chapter, end_chapter)
        
        # 导出为JSON
        exporter = get_graph_exporter()
        graph_data = exporter.export_to_json(
            graph=graph,
            chapter_filter=chapter_filter,
            max_nodes=max_nodes,
            min_importance=min_importance
        )
        
        logger.info(
            f"✅ 成功获取小说 {novel_id} 的关系图: "
            f"{graph_data['metadata']['total_nodes']} 节点, "
            f"{graph_data['metadata']['total_edges']} 边"
        )
        
        return RelationGraphResponse(**graph_data)
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"小说 {novel_id} 的知识图谱文件不存在"
        )
    except Exception as e:
        logger.error(f"❌ 获取关系图失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取关系图失败: {str(e)}"
        )


@router.get("/relations/{novel_id}/node/{node_id}")
async def get_node_details(
    novel_id: int,
    node_id: str
):
    """
    获取节点详细信息
    
    Args:
        novel_id: 小说ID
        node_id: 节点ID（实体名称）
    
    Returns:
        dict: 节点详细信息
    """
    try:
        # 加载图谱
        graph_path = Path(f"./backend/data/graphs/novel_{novel_id}_graph.pkl")
        if not graph_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"小说 {novel_id} 的知识图谱不存在"
            )
        
        with open(graph_path, 'rb') as f:
            graph = pickle.load(f)
        
        # 导出节点详情
        exporter = get_graph_exporter()
        node_details = exporter.export_node_details(graph, node_id)
        
        if node_details is None:
            raise HTTPException(
                status_code=404,
                detail=f"节点 '{node_id}' 不存在"
            )
        
        logger.info(f"✅ 成功获取节点详情: {node_id}")
        
        return node_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取节点详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取节点详情失败: {str(e)}"
        )


@router.get("/timeline/{novel_id}", response_model=TimelineResponse)
async def get_timeline(
    novel_id: int,
    entity_filter: Optional[str] = Query(None, description="实体名称过滤"),
    max_events: int = Query(100, ge=10, le=500, description="最大事件数")
):
    """
    获取小说时间线数据
    
    Args:
        novel_id: 小说ID
        entity_filter: 实体名称过滤（可选）
        max_events: 最大事件数
    
    Returns:
        TimelineResponse: 时间线数据
    """
    try:
        # 加载图谱
        graph_path = Path(f"./backend/data/graphs/novel_{novel_id}_graph.pkl")
        if not graph_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"小说 {novel_id} 的知识图谱不存在，请先完成索引"
            )
        
        with open(graph_path, 'rb') as f:
            graph = pickle.load(f)
        
        # 提取时间线事件
        events = []
        
        # 从节点提取事件（首次出现）
        for node_id, data in graph.nodes(data=True):
            if entity_filter and node_id != entity_filter:
                continue
            
            first_chapter = data.get('first_chapter', 1)
            events.append({
                'chapter': first_chapter,
                'type': 'entity_appear',
                'entity': node_id,
                'description': f"{node_id} 首次出现",
                'entity_type': data.get('type', 'unknown'),
                'importance': data.get('importance', 0.5),
            })
        
        # 从边提取事件（关系变化）
        for source, target, key, data in graph.edges(keys=True, data=True):
            if entity_filter and source != entity_filter and target != entity_filter:
                continue
            
            # 关系建立事件
            start_chapter = data.get('start_chapter', 1)
            events.append({
                'chapter': start_chapter,
                'type': 'relation_start',
                'source': source,
                'target': target,
                'relation_type': data.get('relation_type', '未知'),
                'description': f"{source} 与 {target} 建立 {data.get('relation_type', '未知')} 关系",
                'importance': data.get('strength', 0.5),
            })
            
            # 关系演变事件
            evolution = data.get('evolution', [])
            for evo in evolution:
                events.append({
                    'chapter': evo.get('chapter', 1),
                    'type': 'relation_evolve',
                    'source': source,
                    'target': target,
                    'relation_type': evo.get('type', '未知'),
                    'description': f"{source} 与 {target} 关系变为 {evo.get('type', '未知')}",
                    'importance': 0.7,
                })
        
        # 按章节排序
        events.sort(key=lambda x: x['chapter'])
        
        # 限制数量
        events = events[:max_events]
        
        metadata = {
            'total_events': len(events),
            'entity_filter': entity_filter,
            'chapter_range': (
                min(e['chapter'] for e in events) if events else 0,
                max(e['chapter'] for e in events) if events else 0
            )
        }
        
        logger.info(
            f"✅ 成功获取小说 {novel_id} 的时间线: {len(events)} 个事件"
        )
        
        return TimelineResponse(events=events, metadata=metadata)
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"小说 {novel_id} 的知识图谱文件不存在"
        )
    except Exception as e:
        logger.error(f"❌ 获取时间线失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取时间线失败: {str(e)}"
        )

