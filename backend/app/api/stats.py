"""
统计API

提供Token使用统计查询
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session

from app.db.init_db import get_db_session
from app.services.token_stats_service import get_token_stats_service
from app.models.schemas import TokenStatsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/tokens", response_model=TokenStatsResponse)
async def get_token_stats(
    period: str = QueryParam('all', regex='^(all|day|week|month)$', description="时间段"),
    start_date: str = QueryParam(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: str = QueryParam(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db_session)
):
    """
    获取Token使用统计
    
    支持按时间段筛选：
    - all: 全部统计
    - day: 最近30天
    - week: 最近12周
    - month: 最近12个月
    
    也可以使用start_date和end_date自定义日期范围
    
    Returns:
        TokenStatsResponse: Token统计数据
    """
    try:
        token_stats_service = get_token_stats_service()
        
        # 解析日期范围
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的开始日期格式: {start_date}，应为YYYY-MM-DD"
                )
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的结束日期格式: {end_date}，应为YYYY-MM-DD"
                )
        
        # 如果没有指定自定义日期，根据period设置日期范围
        if not start_date and period != 'all':
            if period == 'day':
                start_dt = datetime.now() - timedelta(days=30)
            elif period == 'week':
                start_dt = datetime.now() - timedelta(weeks=12)
            elif period == 'month':
                start_dt = datetime.now() - timedelta(days=365)
        
        # 获取总体统计
        total_stats = token_stats_service.get_total_stats(db, start_dt, end_dt)
        
        # 按模型分类统计
        stats_by_model = token_stats_service.get_stats_by_model(db, start_dt, end_dt)
        
        # 按操作类型统计
        stats_by_operation = token_stats_service.get_stats_by_operation(db, start_dt, end_dt)
        
        logger.info(
            f"✅ 获取Token统计成功: {total_stats['total_tokens']} tokens, "
            f"¥{total_stats['total_cost']:.4f}"
        )
        
        return TokenStatsResponse(
            total_tokens=total_stats['total_tokens'],
            total_cost=total_stats['total_cost'],
            by_model=stats_by_model,
            by_operation=stats_by_operation,
            period=period
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Token统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取Token统计失败: {str(e)}"
        )


@router.get("/tokens/trend")
async def get_token_trend(
    period: str = QueryParam('day', regex='^(day|week|month)$', description="时间段"),
    limit: int = QueryParam(30, ge=1, le=365, description="返回数据点数量"),
    db: Session = Depends(get_db_session)
):
    """
    获取Token使用趋势
    
    按时间段分组统计Token使用量，用于绘制趋势图
    
    Args:
        period: 时间段类型 (day/week/month)
        limit: 返回的数据点数量
    
    Returns:
        List: 趋势数据
    """
    try:
        token_stats_service = get_token_stats_service()
        
        trend_data = token_stats_service.get_stats_by_period(db, period, limit)
        
        logger.info(f"✅ 获取Token趋势成功: {len(trend_data)} 个数据点")
        
        return {
            'period': period,
            'data': trend_data
        }
        
    except Exception as e:
        logger.error(f"❌ 获取Token趋势失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取Token趋势失败: {str(e)}"
        )


@router.get("/tokens/summary")
async def get_token_summary(
    db: Session = Depends(get_db_session)
):
    """
    获取Token统计摘要
    
    快速获取关键统计数据，用于仪表盘展示
    
    Returns:
        Dict: 统计摘要
    """
    try:
        token_stats_service = get_token_stats_service()
        
        # 全部时间
        all_time = token_stats_service.get_total_stats(db)
        
        # 最近24小时
        last_24h_start = datetime.now() - timedelta(hours=24)
        last_24h = token_stats_service.get_total_stats(db, last_24h_start)
        
        # 最近7天
        last_7d_start = datetime.now() - timedelta(days=7)
        last_7d = token_stats_service.get_total_stats(db, last_7d_start)
        
        # 最近30天
        last_30d_start = datetime.now() - timedelta(days=30)
        last_30d = token_stats_service.get_total_stats(db, last_30d_start)
        
        logger.info("✅ 获取Token摘要成功")
        
        return {
            'all_time': all_time,
            'last_24h': last_24h,
            'last_7d': last_7d,
            'last_30d': last_30d
        }
        
    except Exception as e:
        logger.error(f"❌ 获取Token摘要失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取Token摘要失败: {str(e)}"
        )

