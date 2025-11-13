"""
智能问答API
"""

import logging
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.init_db import get_db_session
from app.models.schemas import (
    QueryRequest, QueryResponse, Citation,
    TokenStats, Confidence, ModelType, StreamMessage, QueryStage
)
from app.services.rag_engine import get_rag_engine
from app.core.error_handlers import NovelNotFoundError
from app.models.database import Novel, Query

router = APIRouter(prefix="/api/query", tags=["智能问答"])
logger = logging.getLogger(__name__)


@router.post("", response_model=QueryResponse, summary="非流式查询")
async def query_novel(
    request: QueryRequest,
    db: Session = Depends(get_db_session)
):
    """
    非流式智能问答
    
    - 基础RAG检索
    - 完整答案返回
    - 包含引用和统计信息
    """
    start_time = time.time()
    
    try:
        # 验证小说是否存在
        novel = db.query(Novel).filter(Novel.id == request.novel_id).first()
        if not novel:
            raise NovelNotFoundError(request.novel_id)
        
        # 执行RAG查询
        rag_engine = get_rag_engine()
        answer, citations, stats = rag_engine.query(
            db=db,
            novel_id=request.novel_id,
            query=request.query,
            model=request.model.value
        )
        
        response_time = time.time() - start_time
        
        # 保存查询历史
        query_record = Query(
            novel_id=request.novel_id,
            query_text=request.query,
            answer_text=answer,
            model_used=request.model.value,
            response_time=response_time
        )
        db.add(query_record)
        db.commit()
        db.refresh(query_record)
        
        # 构建响应
        return QueryResponse(
            query_id=query_record.id,
            answer=answer,
            citations=citations,
            token_stats=TokenStats(
                total_tokens=0,  # TODO: 实际统计
                prompt_tokens=0,
                completion_tokens=0
            ),
            response_time=response_time,
            confidence=Confidence.MEDIUM,  # TODO: 计算置信度
            model=request.model.value,
            timestamp=datetime.now().isoformat()
        )
        
    except NovelNotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.websocket("/stream")
async def query_stream(websocket: WebSocket):
    """
    流式智能问答 WebSocket
    
    接收: {"novel_id": 1, "query": "xxx", "model": "glm-4"}
    发送: {"stage": "xxx", "content": "xxx", "progress": 0.5}
    """
    await websocket.accept()
    logger.info("🔌 WebSocket连接已建立")
    
    try:
        # 接收查询请求
        data = await websocket.receive_json()
        novel_id = data.get('novel_id')
        query = data.get('query')
        model = data.get('model', 'glm-4')
        
        if not novel_id or not query:
            await websocket.send_json({
                'error': '缺少必要参数: novel_id 或 query'
            })
            await websocket.close()
            return
        
        # 获取数据库会话
        from app.db.init_db import get_database_url
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(get_database_url())
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # 验证小说存在
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            if not novel:
                await websocket.send_json({
                    'error': f'小说 ID={novel_id} 不存在'
                })
                await websocket.close()
                return
            
            # 阶段1: 查询理解
            await websocket.send_json(StreamMessage(
                stage=QueryStage.UNDERSTANDING,
                content="正在理解您的问题...",
                progress=0.1
            ).model_dump())
            
            rag_engine = get_rag_engine()
            
            # 阶段2: 检索上下文
            await websocket.send_json(StreamMessage(
                stage=QueryStage.RETRIEVING,
                content="正在检索相关内容...",
                progress=0.3
            ).model_dump())
            
            # 查询向量化
            query_embedding = rag_engine.query_embedding(query)
            
            # 语义检索
            vector_results = rag_engine.vector_search(novel_id, query_embedding)
            
            # Rerank
            reranked_chunks = rag_engine.rerank(query, vector_results)
            
            if not reranked_chunks:
                await websocket.send_json({
                    'stage': 'finalizing',
                    'content': '抱歉，在小说中未找到相关内容。',
                    'progress': 1.0,
                    'done': True
                })
                await websocket.close()
                return
            
            # 阶段3: 生成答案
            await websocket.send_json(StreamMessage(
                stage=QueryStage.GENERATING,
                content="",
                progress=0.5
            ).model_dump())
            
            # 构建Prompt
            prompt = rag_engine.build_prompt(db, novel_id, query, reranked_chunks)
            
            # 流式生成答案
            full_answer = ""
            for chunk in rag_engine.generate_answer(prompt, model, stream=True):
                if chunk:
                    full_answer += chunk
                    await websocket.send_json({
                        'stage': 'generating',
                        'content': chunk,  # 发送增量内容
                        'progress': 0.7,
                        'is_delta': True
                    })
            
            # 阶段4: 完成汇总
            await websocket.send_json(StreamMessage(
                stage=QueryStage.FINALIZING,
                content="正在整理结果...",
                progress=0.9
            ).model_dump())
            
            # 构建引用列表
            citations = []
            seen_chapters = set()
            
            for chunk in reranked_chunks[:5]:  # 只返回前5条引用
                metadata = chunk['metadata']
                chapter_num = metadata.get('chapter_num')
                
                if chapter_num in seen_chapters:
                    continue
                seen_chapters.add(chapter_num)
                
                citations.append({
                    'chapter_num': chapter_num,
                    'chapter_title': metadata.get('chapter_title'),
                    'text': chunk['content'][:200] + "...",
                    'score': chunk.get('score')
                })
            
            # 发送最终结果
            await websocket.send_json({
                'stage': 'finalizing',
                'content': full_answer,
                'progress': 1.0,
                'done': True,
                'citations': citations
            })
            
            # 保存查询历史
            query_record = Query(
                novel_id=novel_id,
                query_text=query,
                answer_text=full_answer,
                model_used=model,
                response_time=0.0  # WebSocket不统计总时间
            )
            db.add(query_record)
            db.commit()
            
            logger.info(f"✅ 流式查询完成")
            
        finally:
            db.close()
        
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket连接已断开")
    except Exception as e:
        logger.error(f"❌ 流式查询失败: {e}")
        try:
            await websocket.send_json({
                'error': f'查询失败: {str(e)}'
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

