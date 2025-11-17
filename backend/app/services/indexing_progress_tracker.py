"""
索引进度追踪器
在内存中维护详细的索引进度信息
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class IndexingProgressTracker:
    """索引进度追踪器（单例）"""
    
    def __init__(self):
        self._details: Dict[int, Dict] = {}  # novel_id -> detail
        self._lock = Lock()
    
    def init_progress(self, novel_id: int, total_chapters: int):
        """初始化进度追踪"""
        with self._lock:
            self._details[novel_id] = {
                'steps': [
                    {
                        'name': '解析文件',
                        'status': 'pending',
                        'progress': 0.0,
                        'message': '等待开始',
                        'started_at': None,
                        'completed_at': None,
                        'error': None
                    },
                    {
                        'name': '检测章节',
                        'status': 'pending',
                        'progress': 0.0,
                        'message': '等待开始',
                        'started_at': None,
                        'completed_at': None,
                        'error': None
                    },
                    {
                        'name': '文本分块',
                        'status': 'pending',
                        'progress': 0.0,
                        'message': '等待开始',
                        'started_at': None,
                        'completed_at': None,
                        'error': None
                    },
                    {
                        'name': '生成嵌入向量',
                        'status': 'pending',
                        'progress': 0.0,
                        'message': f'共{total_chapters}章待处理',
                        'started_at': None,
                        'completed_at': None,
                        'error': None
                    },
                    {
                        'name': '构建知识图谱',
                        'status': 'pending',
                        'progress': 0.0,
                        'message': '等待开始',
                        'started_at': None,
                        'completed_at': None,
                        'error': None
                    }
                ],
                'failed_chapters': [],
                'token_stats': {
                    'steps': [],  # 每个步骤的Token消耗
                    'total': {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0,
                        'estimated_cost': 0.0
                    }
                },
                'warnings': []
            }
            logger.info(f"📋 初始化索引进度追踪: novel_id={novel_id}")
    
    def update_step(
        self, 
        novel_id: int, 
        step_index: int, 
        status: str, 
        progress: float = None,
        message: str = None,
        error: str = None
    ):
        """更新步骤状态"""
        with self._lock:
            if novel_id not in self._details:
                return
            
            step = self._details[novel_id]['steps'][step_index]
            step['status'] = status
            
            if progress is not None:
                step['progress'] = progress
            if message is not None:
                step['message'] = message
            if error is not None:
                step['error'] = error
            
            if status == 'processing' and step['started_at'] is None:
                step['started_at'] = datetime.now().isoformat()
            elif status in ['completed', 'failed']:
                step['completed_at'] = datetime.now().isoformat()
    
    def add_failed_chapter(self, novel_id: int, chapter_num: int, chapter_title: str, error: str):
        """添加失败章节"""
        with self._lock:
            if novel_id not in self._details:
                return
            
            self._details[novel_id]['failed_chapters'].append({
                'chapter_num': chapter_num,
                'chapter_title': chapter_title,
                'error': error
            })
            logger.warning(f"⚠️ 章节处理失败: novel_id={novel_id}, chapter={chapter_num}, error={error}")
    
    def add_warning(self, novel_id: int, warning: str):
        """添加警告信息"""
        with self._lock:
            if novel_id not in self._details:
                return
            
            self._details[novel_id]['warnings'].append(warning)
    
    def add_token_usage(
        self, 
        novel_id: int, 
        step_name: str, 
        model_name: str,
        input_tokens: int,
        output_tokens: int = 0,
        cost: float = 0.0
    ):
        """添加Token使用记录"""
        with self._lock:
            if novel_id not in self._details:
                return
            
            total_tokens = input_tokens + output_tokens
            
            # 添加步骤级统计
            self._details[novel_id]['token_stats']['steps'].append({
                'step': step_name,
                'model': model_name,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': total_tokens,
                'cost': cost
            })
            
            # 更新总计
            total = self._details[novel_id]['token_stats']['total']
            total['input_tokens'] += input_tokens
            total['output_tokens'] += output_tokens
            total['total_tokens'] += total_tokens
            total['estimated_cost'] += cost
            
            logger.info(f"📊 Token统计更新: novel_id={novel_id}, step={step_name}, model={model_name}, tokens={total_tokens}")
    
    def get_detail(self, novel_id: int) -> Optional[Dict]:
        """获取详细信息"""
        with self._lock:
            return self._details.get(novel_id)
    
    def clear_detail(self, novel_id: int):
        """清除详细信息（索引完成后）"""
        with self._lock:
            if novel_id in self._details:
                del self._details[novel_id]
                logger.info(f"🗑️ 清除索引详情: novel_id={novel_id}")


# 全局实例
_tracker: Optional[IndexingProgressTracker] = None


def get_progress_tracker() -> IndexingProgressTracker:
    """获取全局进度追踪器"""
    global _tracker
    if _tracker is None:
        _tracker = IndexingProgressTracker()
    return _tracker

