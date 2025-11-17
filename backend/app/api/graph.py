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

router = APIRouter(prefix="/api/graph", tags=["graph"])


class RelationGraphResponse(BaseModel):
    """关系图响应"""
    nodes: list
    edges: list
    metadata: dict


class TimelineResponse(BaseModel):
    """时间线响应"""
    events: list
    metadata: dict


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_chapters: int
    total_characters: int
    total_chars: int
    character_count: int
    relation_count: int
    average_chapter_length: float
    top_characters: list
    chapter_density: list


@router.get("/relations/{novel_id}", response_model=RelationGraphResponse)
async def get_relation_graph(
    novel_id: int,
    start_chapter: Optional[int] = Query(None, description="起始章节"),
    end_chapter: Optional[int] = Query(None, description="结束章节"),
    max_nodes: int = Query(50, ge=10, le=200, description="最大节点数"),
    min_importance: float = Query(0.0, ge=0.0, le=1.0, description="最小重要性阈值")
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
        graph_path = Path(f"./data/graphs/novel_{novel_id}_graph.pkl")
        if not graph_path.exists():
            logger.warning(f"小说 {novel_id} 的知识图谱不存在，返回空数据")
            # 返回空图谱数据而不是报错
            return RelationGraphResponse(
                nodes=[],
                edges=[],
                metadata={
                    "novel_id": novel_id,
                    "total_nodes": 0,
                    "total_edges": 0,
                    "chapter_range": [start_chapter or 0, end_chapter or 0],
                    "message": "知识图谱尚未构建，请先完成小说索引"
                }
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
        
    except FileNotFoundError as e:
        logger.warning(f"小说 {novel_id} 的知识图谱文件不存在: {e}")
        # 返回空图谱数据
        return RelationGraphResponse(
            nodes=[],
            edges=[],
            metadata={
                "novel_id": novel_id,
                "total_nodes": 0,
                "total_edges": 0,
                "message": "知识图谱文件不存在"
            }
        )
    except Exception as e:
        logger.error(f"❌ 获取关系图失败: {type(e).__name__}: {str(e)}", exc_info=True)
        # 返回空数据而不是报错
        return RelationGraphResponse(
            nodes=[],
            edges=[],
            metadata={
                "novel_id": novel_id,
                "total_nodes": 0,
                "total_edges": 0,
                "error": f"加载图谱失败: {type(e).__name__}"
            }
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
        graph_path = Path(f"./data/graphs/novel_{novel_id}_graph.pkl")
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
        logger.error(f"❌ 获取节点详情失败: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取节点详情失败: {type(e).__name__}"
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
        graph_path = Path(f"./data/graphs/novel_{novel_id}_graph.pkl")
        if not graph_path.exists():
            logger.warning(f"小说 {novel_id} 的知识图谱不存在，返回空时间线")
            return TimelineResponse(
                events=[],
                metadata={
                    "total_events": 0,
                    "entity_filter": entity_filter,
                    "chapter_range": [0, 0],
                    "message": "知识图谱尚未构建"
                }
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
        
        # 添加叙述顺序和转换字段名以匹配前端期望的格式
        formatted_events = []
        for i, event in enumerate(events):
            formatted_events.append({
                'chapterNum': event['chapter'],  # 前端期望的字段名
                'narrativeOrder': i + 1,  # 叙述顺序，从1开始
                'description': event['description'],
                'eventType': event.get('type', 'unknown'),  # 事件类型
                'importance': event.get('importance', 0.5),  # 重要性
                # 保留额外信息用于悬停提示
                'entity': event.get('entity'),
                'source': event.get('source'),
                'target': event.get('target'),
                'relationType': event.get('relation_type'),
            })
        
        metadata = {
            'total_events': len(formatted_events),
            'entity_filter': entity_filter,
            'chapter_range': (
                min(e['chapterNum'] for e in formatted_events) if formatted_events else 0,
                max(e['chapterNum'] for e in formatted_events) if formatted_events else 0
            )
        }
        
        logger.info(
            f"✅ 成功获取小说 {novel_id} 的时间线: {len(formatted_events)} 个事件"
        )
        
        return TimelineResponse(events=formatted_events, metadata=metadata)
        
    except FileNotFoundError as e:
        logger.warning(f"小说 {novel_id} 的知识图谱文件不存在: {e}")
        return TimelineResponse(
            events=[],
            metadata={
                "total_events": 0,
                "entity_filter": entity_filter,
                "chapter_range": [0, 0],
                "message": "知识图谱文件不存在"
            }
        )
    except Exception as e:
        logger.error(f"❌ 获取时间线失败: {type(e).__name__}: {str(e)}", exc_info=True)
        return TimelineResponse(
            events=[],
            metadata={
                "total_events": 0,
                "entity_filter": entity_filter,
                "chapter_range": [0, 0],
                "error": f"加载时间线失败: {type(e).__name__}"
            }
        )


@router.get("/statistics/{novel_id}", response_model=StatisticsResponse)
async def get_statistics(novel_id: int):
    """
    获取小说统计数据
    
    Args:
        novel_id: 小说ID
    
    Returns:
        StatisticsResponse: 统计数据
    """
    try:
        from sqlalchemy.orm import Session
        from app.db.init_db import get_db_session, get_database_url
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.database import Novel, Chapter
        
        # 创建数据库会话
        engine = create_engine(get_database_url())
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # 获取小说基本信息
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            if not novel:
                raise HTTPException(
                    status_code=404,
                    detail=f"小说 {novel_id} 不存在"
                )
            
            # 获取章节信息
            chapters = db.query(Chapter).filter(Chapter.novel_id == novel_id).all()
            
            # 加载知识图谱
            graph_path = Path(f"./data/graphs/novel_{novel_id}_graph.pkl")
            graph = None
            if graph_path.exists():
                with open(graph_path, 'rb') as f:
                    graph = pickle.load(f)
            
            # 计算统计数据
            total_chapters = novel.total_chapters or len(chapters)
            total_chars = novel.total_chars or 0
            
            # 从图谱统计角色和关系
            character_count = 0
            relation_count = 0
            character_importance = {}
            
            if graph:
                # 统计角色（类型为character的节点）
                for node_id, data in graph.nodes(data=True):
                    if data.get('type') == 'character':
                        character_count += 1
                        character_importance[node_id] = data.get('importance', 0.5)
                
                # 统计关系
                relation_count = graph.number_of_edges()
            
            # 平均章节长度
            average_chapter_length = total_chars / total_chapters if total_chapters > 0 else 0
            
            # Top角色（按重要性排序）
            top_characters = []
            if character_importance:
                sorted_characters = sorted(
                    character_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                for name, importance in sorted_characters:
                    top_characters.append({
                        'name': name,
                        'importance': importance
                    })
            
            # 章节密度（实体出现密度）
            chapter_density = []
            if graph and chapters:
                for chapter in chapters[:50]:  # 限制前50章
                    # 统计该章节的实体数量
                    entity_count = 0
                    for node_id, data in graph.nodes(data=True):
                        first_chapter = data.get('first_chapter', 0)
                        last_chapter = data.get('last_chapter')
                        
                        if first_chapter <= chapter.chapter_num:
                            if last_chapter is None or chapter.chapter_num <= last_chapter:
                                entity_count += 1
                    
                    chapter_density.append({
                        'chapter': chapter.chapter_num,
                        'entity_count': entity_count,
                        'char_count': chapter.char_count or 0
                    })
            
            logger.info(f"✅ 成功获取小说 {novel_id} 的统计数据")
            
            return StatisticsResponse(
                total_chapters=total_chapters,
                total_characters=character_count,
                total_chars=total_chars,
                character_count=character_count,
                relation_count=relation_count,
                average_chapter_length=average_chapter_length,
                top_characters=top_characters,
                chapter_density=chapter_density
            )
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取统计数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        )

