"""
智能问答API
"""

import logging
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

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
        
        # Token计数器
        from app.utils.token_counter import get_token_counter
        token_counter = get_token_counter()
        
        # 统计Embedding tokens
        embedding_tokens = token_counter.count_tokens(request.query)
        
        # 执行RAG查询
        rag_engine = get_rag_engine()
        answer, citations, stats = rag_engine.query(
            db=db,
            novel_id=request.novel_id,
            query=request.query,
            model=request.model.value
        )
        
        # 统计Prompt和Completion tokens
        # 注意：这里使用估算，因为非流式接口不返回实际的usage信息
        # 可以通过重新构建prompt来计算，或者估算
        query_embedding = rag_engine.query_embedding(request.query)
        vector_results = rag_engine.vector_search(request.novel_id, query_embedding)
        reranked_chunks = rag_engine.rerank(request.query, vector_results, None)
        
        # 构建prompt用于计算tokens
        prompt = rag_engine.build_prompt(db, request.novel_id, request.query, reranked_chunks)
        prompt_tokens = token_counter.count_tokens(prompt)
        completion_tokens = token_counter.count_tokens(answer)
        
        total_tokens = embedding_tokens + prompt_tokens + completion_tokens
        
        response_time = time.time() - start_time
        
        # 保存查询历史
        query_record = Query(
            novel_id=request.novel_id,
            query_text=request.query,
            answer_text=answer,
            model_used=request.model.value,
            response_time=response_time,
            total_tokens=total_tokens
        )
        db.add(query_record)
        db.commit()
        db.refresh(query_record)
        
        # 记录Token使用统计
        try:
            from app.services.token_stats_service import get_token_stats_service
            token_stats_service = get_token_stats_service()
            
            # Embedding-3使用记录
            token_stats_service.record_token_usage(
                db=db,
                operation_type='query',
                operation_id=query_record.id,
                model_name='embedding-3',
                input_tokens=embedding_tokens,
                output_tokens=0
            )
            
            # LLM模型使用记录
            token_stats_service.record_token_usage(
                db=db,
                operation_type='query',
                operation_id=query_record.id,
                model_name=request.model.value,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens
            )
        except Exception as e:
            logger.warning(f"⚠️ Token统计记录失败（不影响主流程）: {e}")
        
        # 构建详细的TokenStats对象（包含阶段统计）
        by_stage = [
            {
                'stage': 'retrieving',
                'model': 'embedding-3',
                'inputTokens': embedding_tokens,
                'outputTokens': 0,
                'totalTokens': embedding_tokens
            },
            {
                'stage': 'generating',
                'model': request.model.value,
                'inputTokens': prompt_tokens,
                'outputTokens': completion_tokens,
                'totalTokens': prompt_tokens + completion_tokens
            }
        ]
        
        token_stats_obj = TokenStats(
            total_tokens=total_tokens,
            input_tokens=embedding_tokens + prompt_tokens,
            output_tokens=completion_tokens,
            embedding_tokens=embedding_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            by_model={
                'embedding-3': {
                    'inputTokens': embedding_tokens
                },
                request.model.value: {
                    'promptTokens': prompt_tokens,
                    'completionTokens': completion_tokens,
                    'totalTokens': prompt_tokens + completion_tokens
                }
            },
            by_stage=by_stage
        )
        
        # 构建响应
        return QueryResponse(
            query_id=query_record.id,
            answer=answer,
            citations=citations,
            token_stats=token_stats_obj,
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
            
            # Token统计初始化
            from app.services.token_stats_service import get_token_stats_service
            token_stats_service = get_token_stats_service()
            
            embedding_tokens = 0
            prompt_tokens = 0
            completion_tokens = 0
            
            # 查询向量化（统计Embedding tokens）
            from app.utils.token_counter import get_token_counter
            token_counter = get_token_counter()
            embedding_tokens += token_counter.count_tokens(query)
            
            query_embedding = rag_engine.query_embedding(query)
            
            # 语义检索
            vector_results = rag_engine.vector_search(novel_id, query_embedding)
            
            # Rerank（带GraphRAG增强）
            reranked_chunks = rag_engine.rerank(
                query=query,
                vector_results=vector_results,
                novel_id=novel_id,
                db=db
            )
            
            if not reranked_chunks:
                await websocket.send_json({
                    'stage': 'finalizing',
                    'content': '抱歉，在小说中未找到相关内容。',
                    'progress': 1.0,
                    'done': True
                })
                await websocket.close()
                return
            
            # ✨ 检索完成后立即构建并发送引用列表
            logger.info("📚 检索完成，构建引用列表...")
            citations = []
            seen_chapters = set()
            
            for chunk in reranked_chunks[:5]:  # 只返回前5条引用
                metadata = chunk['metadata']
                chapter_num = metadata.get('chapter_num')
                
                if chapter_num in seen_chapters:
                    continue
                seen_chapters.add(chapter_num)
                
                # 获取章节标题，如果metadata中没有，从数据库查询
                chapter_title = metadata.get('chapter_title')
                if not chapter_title and chapter_num:
                    try:
                        from app.models.database import Chapter
                        chapter = db.query(Chapter).filter(
                            Chapter.novel_id == novel_id,
                            Chapter.num == chapter_num
                        ).first()
                        if chapter:
                            chapter_title = chapter.title
                    except Exception as e:
                        logger.warning(f"获取章节标题失败: {e}")
                
                citations.append({
                    'chapter_num': chapter_num,
                    'chapter_title': chapter_title,
                    'text': chunk['content'][:200] + "...",
                    'score': chunk.get('score')
                })
            
            # 发送包含引用的检索完成消息
            logger.info(f"📤 发送引用列表: {len(citations)} 条")
            await websocket.send_json({
                'stage': 'retrieving',
                'content': f"检索完成，找到 {len(citations)} 个相关章节",
                'progress': 0.4,
                'citations': citations
            })
            
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
            generation_usage = None
            finish_reason = None
            
            logger.info("🔄 开始流式生成答案...")
            
            for chunk_data in rag_engine.generate_answer_with_stats(prompt, model, stream=True):
                # chunk_data可能包含content、thinking和usage
                if isinstance(chunk_data, dict):
                    chunk = chunk_data.get('content', '')
                    thinking_chunk = chunk_data.get('reasoning_content')  # 提取thinking内容
                    usage = chunk_data.get('usage')
                    finish_reason_value = chunk_data.get('finish_reason')
                    
                    if usage:
                        # 保存最后的usage信息
                        generation_usage = usage
                        logger.info(f"💡 [WebSocket] 收到usage: {usage}")
                    
                    if finish_reason_value:
                        finish_reason = finish_reason_value
                        logger.info(f"🏁 [WebSocket] 收到finish_reason: {finish_reason}")
                else:
                    # 向后兼容：纯文本chunk
                    chunk = chunk_data if chunk_data else ''
                    thinking_chunk = None
                
                # 发送thinking内容（如果有）
                if thinking_chunk:
                    await websocket.send_json({
                        'stage': 'generating',
                        'thinking': thinking_chunk,  # 发送thinking增量内容
                        'content': '',
                        'progress': 0.6,
                        'is_delta': True
                    })
                
                # 发送答案内容（如果有）
                if chunk:
                    full_answer += chunk
                    await websocket.send_json({
                        'stage': 'generating',
                        'content': chunk,  # 发送增量内容
                        'progress': 0.7,
                        'is_delta': True
                    })
            
            logger.info(f"✅ 流式生成完成，答案长度: {len(full_answer)}, 是否有usage: {generation_usage is not None}")
            
            # 从generation_usage中提取Token统计
            if generation_usage:
                prompt_tokens = generation_usage.get('prompt_tokens', 0)
                completion_tokens = generation_usage.get('completion_tokens', 0)
                logger.info(f"✅ 使用API返回的Token统计: prompt={prompt_tokens}, completion={completion_tokens}")
            else:
                # 如果没有从API获取到usage，使用估算
                logger.warning("⚠️ API未返回usage信息，使用Token计数器估算")
                prompt_tokens = token_counter.count_tokens(prompt)
                completion_tokens = token_counter.count_tokens(full_answer)
                logger.info(f"📊 估算Token数: prompt={prompt_tokens}, completion={completion_tokens}")
            
            # 阶段4: Self-RAG验证
            # 注意：不发送 content，避免覆盖之前的答案
            await websocket.send_json({
                'stage': 'validating',
                'progress': 0.8,
                'metadata': {'message': '正在验证答案准确性...'}
            })
            
            # Self-RAG验证流程
            from app.services.self_rag import (
                get_assertion_extractor,
                get_evidence_collector,
                get_evidence_scorer,
                get_consistency_checker,
                get_contradiction_detector,
                get_answer_corrector
            )
            
            contradictions_list = []
            confidence_level = "high"
            corrected_answer = full_answer
            
            try:
                # 1. 提取断言
                assertion_extractor = get_assertion_extractor()
                assertions = assertion_extractor.extract_assertions(full_answer)
                logger.info(f"✅ 提取断言: {len(assertions)} 个")
                
                if assertions:
                    # 2. 收集证据
                    evidence_collector = get_evidence_collector()
                    evidence_map = {}
                    
                    for idx, assertion in enumerate(assertions):
                        evidence_list = evidence_collector.collect_evidence_for_assertion(
                            db, novel_id, assertion, top_k=3
                        )
                        evidence_map[idx] = evidence_list
                    
                    logger.info(f"✅ 收集证据完成")
                    
                    # 3. 评分证据
                    evidence_scorer = get_evidence_scorer()
                    for idx, assertion in enumerate(assertions):
                        evidence_list = evidence_map.get(idx, [])
                        # 对每条证据进行评分
                        scored_evidence_list = []
                        for evidence in evidence_list:
                            scored = evidence_scorer.score_evidence(
                                db=db,
                                novel_id=novel_id,
                                evidence=evidence,
                                query_context={'assertion': assertion}
                            )
                            # 将评分信息添加到证据中
                            evidence['score'] = scored
                            scored_evidence_list.append(evidence)
                        evidence_map[idx] = scored_evidence_list
                    
                    # 4. 一致性检查
                    consistency_checker = get_consistency_checker()
                    
                    # 4.1 时序一致性检查
                    temporal_issues = consistency_checker.check_temporal_consistency(
                        assertions, evidence_map
                    )
                    
                    # 4.2 角色一致性检查
                    character_issues = consistency_checker.check_character_consistency(
                        db, novel_id, assertions, evidence_map
                    )
                    
                    # 合并一致性检查结果
                    consistency_report = {
                        'temporal_issues': temporal_issues,
                        'character_issues': character_issues,
                        'total_issues': len(temporal_issues) + len(character_issues)
                    }
                    
                    logger.info(f"✅ 一致性检查完成: {consistency_report['total_issues']} 个问题")
                    
                    # 5. 检测矛盾
                    contradiction_detector = get_contradiction_detector()
                    contradictions = contradiction_detector.detect_contradictions(
                        db, novel_id, assertions, evidence_map, consistency_report
                    )
                    
                    # 转换为可序列化的字典列表
                    contradictions_list = [
                        {
                            'type': c.type,
                            'earlyDescription': c.early_description,
                            'earlyChapter': c.early_chapter,
                            'lateDescription': c.late_description,
                            'lateChapter': c.late_chapter,
                            'analysis': c.analysis,
                            'confidence': c.confidence
                        }
                        for c in contradictions
                    ]
                    
                    logger.info(f"✅ 检测到矛盾: {len(contradictions_list)} 个")
                    
                    # 6. 修正答案
                    if contradictions:
                        answer_corrector = get_answer_corrector()
                        correction_result = answer_corrector.correct_answer(
                            full_answer, contradictions, "high"
                        )
                        corrected_answer = correction_result.get('corrected_answer', full_answer)
                        confidence_level = correction_result.get('final_confidence', 'high')
                        
                        logger.info(f"✅ 答案修正完成，置信度: {confidence_level}")
                
            except Exception as e:
                logger.error(f"⚠️ Self-RAG验证失败: {e}")
                # Self-RAG失败不影响主流程，继续返回原答案
            
            # 阶段5: 完成汇总
            logger.info("📋 开始构建最终结果...")
            # 注意：不发送 content，避免覆盖之前的答案
            await websocket.send_json({
                'stage': 'finalizing',
                'progress': 0.9,
                'metadata': {'message': '正在整理结果...'}  # 状态信息放在 metadata 中
            })
            
            # 计算总Token消耗
            total_tokens = embedding_tokens + prompt_tokens + completion_tokens
            
            # 构建详细的Token统计信息（包含阶段级别统计）
            by_stage = [
                {
                    'stage': 'retrieving',
                    'model': 'embedding-3',
                    'inputTokens': embedding_tokens,
                    'outputTokens': 0,
                    'totalTokens': embedding_tokens
                },
                {
                    'stage': 'generating',
                    'model': model,
                    'inputTokens': prompt_tokens,
                    'outputTokens': completion_tokens,
                    'totalTokens': prompt_tokens + completion_tokens
                }
            ]
            
            token_stats = {
                'totalTokens': total_tokens,
                'inputTokens': embedding_tokens + prompt_tokens,
                'outputTokens': completion_tokens,
                'byModel': {
                    'embedding-3': {
                        'inputTokens': embedding_tokens,
                        'stage': 'retrieving'
                    },
                    model: {
                        'inputTokens': prompt_tokens,
                        'completionTokens': completion_tokens,
                        'totalTokens': prompt_tokens + completion_tokens,
                        'stage': 'generating'
                    }
                },
                'byStage': by_stage
            }
            
            logger.info(f"✅ Token统计: 总计 {total_tokens} tokens")
            logger.info(f"💾 保存查询记录到数据库...")
            
            # 保存查询历史（使用修正后的答案）
            query_record = Query(
                novel_id=novel_id,
                query_text=query,
                answer_text=corrected_answer,
                model_used=model,
                response_time=0.0,  # WebSocket不统计总时间
                confidence=confidence_level,  # 保存置信度
                total_tokens=total_tokens  # 保存Token消耗
            )
            db.add(query_record)
            db.commit()
            db.refresh(query_record)
            logger.info(f"✅ 查询记录已保存，query_id={query_record.id}")
            
            # 记录Token使用情况到统计表
            try:
                # Embedding-3使用记录
                if embedding_tokens > 0:
                    token_stats_service.record_token_usage(
                        db=db,
                        operation_type='query',
                        operation_id=query_record.id,
                        model_name='embedding-3',
                        input_tokens=embedding_tokens,
                        output_tokens=0
                    )
                
                # GLM模型使用记录
                if prompt_tokens > 0 or completion_tokens > 0:
                    token_stats_service.record_token_usage(
                        db=db,
                        operation_type='query',
                        operation_id=query_record.id,
                        model_name=model,
                        input_tokens=prompt_tokens,
                        output_tokens=completion_tokens
                    )
            except Exception as e:
                logger.warning(f"⚠️ Token统计记录失败（不影响主流程）: {e}")
            
            # 发送最终结果（包含query_id和完整token统计）
            # 注意：citations 已在 retrieving 阶段发送，这里不再重复发送
            final_message = {
                'stage': 'finalizing',
                'content': corrected_answer,
                'progress': 1.0,
                'done': True,
                'contradictions': contradictions_list,
                'confidence': confidence_level,
                'query_id': query_record.id,
                'original_answer': full_answer if corrected_answer != full_answer else None,
                'metadata': {
                    'token_stats': token_stats  # 使用完整的token统计信息
                }
            }
            
            logger.info(f"📤 准备发送最终消息: query_id={query_record.id}, done=True, answer_length={len(corrected_answer)}")
            await websocket.send_json(final_message)
            logger.info(f"✅ 流式查询完成，最终消息已发送")
            
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


@router.get("/{query_id}/token-stats", response_model=TokenStats, summary="获取查询Token统计")
async def get_query_token_stats(
    query_id: int,
    db: Session = Depends(get_db_session)
):
    """
    获取指定查询的Token消耗统计
    
    - 从token_stats表查询并聚合
    - 按模型分组统计
    - 返回详细的Token消耗信息
    """
    try:
        from app.models.database import TokenStat
        
        # 查询该query的所有token统计记录
        stats_records = db.query(TokenStat).filter(
            TokenStat.operation_type == 'query',
            TokenStat.operation_id == query_id
        ).all()
        
        if not stats_records:
            raise HTTPException(status_code=404, detail="未找到Token统计记录")
        
        # 按模型聚合
        by_model = {}
        total_tokens = 0
        
        for record in stats_records:
            model_name = record.model_name
            
            if model_name not in by_model:
                by_model[model_name] = {}
            
            # 根据模型类型设置不同的字段
            if 'embedding' in model_name.lower():
                # Embedding模型只有input_tokens
                by_model[model_name]['inputTokens'] = record.input_tokens or 0
            else:
                # LLM模型有prompt和completion
                by_model[model_name]['promptTokens'] = record.prompt_tokens or 0
                by_model[model_name]['completionTokens'] = record.completion_tokens or 0
                by_model[model_name]['totalTokens'] = record.total_tokens or 0
            
            total_tokens += record.total_tokens or 0
        
        logger.info(f"✅ 获取查询#{query_id}的Token统计: {total_tokens} tokens")
        
        return TokenStats(
            total_tokens=total_tokens,
            by_model=by_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Token统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Token统计失败: {str(e)}")


@router.get("/history", summary="获取查询历史")
async def get_query_history(
    novel_id: Optional[int] = QueryParam(None, description="按小说ID过滤"),
    page: int = QueryParam(1, ge=1, description="页码"),
    page_size: int = QueryParam(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db_session)
):
    """
    获取查询历史
    
    - 支持分页
    - 支持按小说ID过滤
    - 按时间倒序排列
    """
    try:
        # 构建查询
        query = db.query(Query)
        
        if novel_id:
            query = query.filter(Query.novel_id == novel_id)
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        queries = query.order_by(Query.created_at.desc()).offset(offset).limit(page_size).all()
        
        # 构建响应
        items = []
        for q in queries:
            items.append({
                "id": q.id,
                "novel_id": q.novel_id,
                "query": q.query_text,
                "answer": q.answer_text[:200] + "..." if len(q.answer_text) > 200 else q.answer_text,
                "model": q.model_used,
                "total_tokens": q.total_tokens or 0,
                "confidence": q.confidence or "medium",
                "created_at": q.created_at if q.created_at else None,
                "feedback": "positive" if q.user_feedback == 1 else ("negative" if q.user_feedback == -1 else None)
            })
        
        logger.info(f"✅ 获取查询历史成功: {len(items)} 条")
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"❌ 获取查询历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取查询历史失败: {str(e)}")


@router.post("/{query_id}/feedback", summary="提交用户反馈")
async def submit_feedback(
    query_id: int,
    feedback: str = QueryParam(..., regex="^(positive|negative)$", description="反馈类型"),
    note: Optional[str] = QueryParam(None, max_length=500, description="反馈备注"),
    db: Session = Depends(get_db_session)
):
    """
    提交用户反馈
    
    - positive: 答案准确
    - negative: 答案不准确
    """
    try:
        # 查询记录
        query_record = db.query(Query).filter(Query.id == query_id).first()
        
        if not query_record:
            raise HTTPException(status_code=404, detail=f"查询记录 ID={query_id} 不存在")
        
        # 更新反馈
        query_record.user_feedback = 1 if feedback == "positive" else -1
        if note:
            query_record.feedback_note = note
        
        db.commit()
        
        logger.info(f"✅ 用户反馈已提交: query_id={query_id}, feedback={feedback}")
        
        return {
            "success": True,
            "message": "感谢您的反馈！",
            "query_id": query_id,
            "feedback": feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")

