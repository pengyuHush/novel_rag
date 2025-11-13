"""
Token统计服务

负责Token统计的存储、查询和分析
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.database import TokenStat
from app.utils.token_counter import get_token_counter

logger = logging.getLogger(__name__)


class TokenStatsService:
    """Token统计服务"""
    
    def __init__(self):
        """初始化Token统计服务"""
        self.token_counter = get_token_counter()
        logger.info("✅ Token统计服务初始化完成")
    
    def record_token_usage(
        self,
        db: Session,
        operation_type: str,
        operation_id: int,
        model_name: str,
        input_tokens: int,
        output_tokens: int = 0
    ) -> TokenStat:
        """
        记录Token使用情况
        
        Args:
            db: 数据库会话
            operation_type: 操作类型（'index' 或 'query'）
            operation_id: 操作ID（novel_id或query_id）
            model_name: 模型名称
            input_tokens: 输入Token数
            output_tokens: 输出Token数
        
        Returns:
            TokenStat: Token统计记录
        """
        total_tokens = input_tokens + output_tokens
        cost = self.token_counter.calculate_cost(input_tokens, output_tokens, model_name)
        
        token_stat = TokenStat(
            operation_type=operation_type,
            operation_id=operation_id,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            timestamp=datetime.now()
        )
        
        db.add(token_stat)
        db.commit()
        db.refresh(token_stat)
        
        logger.info(
            f"✅ 记录Token使用: {operation_type}#{operation_id}, "
            f"{model_name}, {total_tokens} tokens, ¥{cost:.4f}"
        )
        
        return token_stat
    
    def get_total_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取总体统计
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict: 总体统计数据
        """
        query = db.query(
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.input_tokens).label('input_tokens'),
            func.sum(TokenStat.output_tokens).label('output_tokens'),
            func.sum(TokenStat.cost).label('total_cost')
        )
        
        # 时间范围过滤
        if start_date:
            query = query.filter(TokenStat.timestamp >= start_date)
        if end_date:
            query = query.filter(TokenStat.timestamp <= end_date)
        
        result = query.first()
        
        return {
            'total_tokens': result.total_tokens or 0,
            'input_tokens': result.input_tokens or 0,
            'output_tokens': result.output_tokens or 0,
            'total_cost': float(result.total_cost or 0.0)
        }
    
    def get_stats_by_model(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        按模型分类统计 (T147)
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict: 按模型分类的统计数据
        """
        query = db.query(
            TokenStat.model_name,
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.input_tokens).label('input_tokens'),
            func.sum(TokenStat.output_tokens).label('output_tokens'),
            func.sum(TokenStat.cost).label('total_cost'),
            func.count(TokenStat.id).label('usage_count')
        ).group_by(TokenStat.model_name)
        
        # 时间范围过滤
        if start_date:
            query = query.filter(TokenStat.timestamp >= start_date)
        if end_date:
            query = query.filter(TokenStat.timestamp <= end_date)
        
        results = query.all()
        
        stats_by_model = {}
        for result in results:
            stats_by_model[result.model_name] = {
                'total_tokens': result.total_tokens,
                'input_tokens': result.input_tokens,
                'output_tokens': result.output_tokens,
                'total_cost': float(result.total_cost),
                'usage_count': result.usage_count
            }
        
        return stats_by_model
    
    def get_stats_by_operation(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        按操作类型统计 (T148)
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict: 按操作类型分类的统计数据
        """
        query = db.query(
            TokenStat.operation_type,
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.cost).label('total_cost'),
            func.count(TokenStat.id).label('operation_count')
        ).group_by(TokenStat.operation_type)
        
        # 时间范围过滤
        if start_date:
            query = query.filter(TokenStat.timestamp >= start_date)
        if end_date:
            query = query.filter(TokenStat.timestamp <= end_date)
        
        results = query.all()
        
        stats_by_operation = {}
        for result in results:
            stats_by_operation[result.operation_type] = {
                'total_tokens': result.total_tokens,
                'total_cost': float(result.total_cost),
                'operation_count': result.operation_count
            }
        
        return stats_by_operation
    
    def get_stats_by_period(
        self,
        db: Session,
        period: str = 'day',
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        按时间段统计
        
        Args:
            db: 数据库会话
            period: 时间段类型 ('day', 'week', 'month')
            limit: 返回的记录数量
        
        Returns:
            List[Dict]: 按时间段分组的统计数据
        """
        # 根据period确定分组格式
        if period == 'day':
            date_format = func.date(TokenStat.timestamp)
        elif period == 'week':
            # SQLite的周统计
            date_format = func.strftime('%Y-W%W', TokenStat.timestamp)
        elif period == 'month':
            date_format = func.strftime('%Y-%m', TokenStat.timestamp)
        else:
            date_format = func.date(TokenStat.timestamp)
        
        query = db.query(
            date_format.label('period'),
            func.sum(TokenStat.total_tokens).label('total_tokens'),
            func.sum(TokenStat.cost).label('total_cost')
        ).group_by('period').order_by(date_format.desc()).limit(limit)
        
        results = query.all()
        
        stats_by_period = []
        for result in results:
            stats_by_period.append({
                'period': str(result.period),
                'total_tokens': result.total_tokens,
                'total_cost': float(result.total_cost)
            })
        
        # 反转顺序，使时间从早到晚
        stats_by_period.reverse()
        
        return stats_by_period


# 全局实例
_token_stats_service: Optional[TokenStatsService] = None


def get_token_stats_service() -> TokenStatsService:
    """获取全局Token统计服务实例（单例）"""
    global _token_stats_service
    if _token_stats_service is None:
        _token_stats_service = TokenStatsService()
    return _token_stats_service

