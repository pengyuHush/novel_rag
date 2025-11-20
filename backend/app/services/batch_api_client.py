"""
智谱AI Batch API客户端

功能:
- 批量提交LLM任务
- 异步等待批处理完成
- 结果文件解析
- 支持关系分类、属性提取等场景
"""

import json
import time
import logging
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from zhipuai import ZhipuAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class BatchAPIClient:
    """Batch API客户端封装"""
    
    def __init__(self):
        """初始化Batch API客户端"""
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)
        logger.info("✅ Batch API客户端初始化完成")
    
    def create_batch_file(
        self,
        tasks: List[Dict],
        file_name: str = "batch_tasks.jsonl"
    ) -> str:
        """
        创建批处理文件（JSONL格式）
        
        Args:
            tasks: 任务列表，每个任务包含：
                {
                    "custom_id": "唯一标识",
                    "method": "POST",
                    "url": "/v4/chat/completions",
                    "body": {...}
                }
            file_name: 文件名
        
        Returns:
            str: 临时文件路径
        """
        # 创建临时文件
        temp_dir = Path(tempfile.gettempdir())
        file_path = temp_dir / file_name
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for task in tasks:
                f.write(json.dumps(task, ensure_ascii=False) + '\n')
        
        # 检查文件大小是否超过智谱AI Batch API限制（100MB）
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            logger.error(f"❌ Batch文件大小({file_size_mb:.2f}MB)超过限制(100MB)")
            raise ValueError(f"Batch文件过大: {file_size_mb:.2f}MB > 100MB")
        
        logger.info(f"✅ 创建批处理文件: {file_path}, {len(tasks)} 个任务, 大小: {file_size_mb:.2f}MB")
        return str(file_path)
    
    def upload_file(self, file_path: str) -> str:
        """
        上传批处理文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 文件ID
        """
        try:
            file_object = self.client.files.create(
                file=Path(file_path),
                purpose="batch"
            )
            file_id = file_object.id
            logger.info(f"✅ 文件上传成功: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"❌ 文件上传失败: {e}")
            raise
    
    def create_batch(
        self,
        input_file_id: str,
        endpoint: str = "/v4/chat/completions",
        completion_window: str = "24h",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        创建批处理任务
        
        Args:
            input_file_id: 输入文件ID
            endpoint: API端点
            completion_window: 完成时间窗口（24h）
            metadata: 元数据
        
        Returns:
            str: 批处理ID
        """
        try:
            batch = self.client.batches.create(
                input_file_id=input_file_id,
                endpoint=endpoint,
                completion_window=completion_window,
                metadata=metadata or {}
            )
            batch_id = batch.id
            logger.info(f"✅ 批处理任务创建成功: {batch_id}")
            return batch_id
        except Exception as e:
            logger.error(f"❌ 批处理任务创建失败: {e}")
            raise
    
    def wait_for_completion(
        self,
        batch_id: str,
        check_interval: int = 60,
        max_wait_time: int = 86400,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        等待批处理完成
        
        Args:
            batch_id: 批处理ID
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒，默认24小时）
            progress_callback: 进度回调函数
        
        Returns:
            Dict: 批处理状态
        """
        start_time = time.time()
        
        while True:
            # 检查是否超时
            if time.time() - start_time > max_wait_time:
                logger.error(f"❌ 批处理超时: {batch_id}")
                raise TimeoutError(f"批处理超时，超过{max_wait_time}秒")
            
            # 获取批处理状态
            batch = self.client.batches.retrieve(batch_id)
            status = batch.status
            
            # 计算进度
            request_counts = batch.request_counts
            total = request_counts.total
            completed = request_counts.completed
            failed = request_counts.failed
            
            progress = completed / total if total > 0 else 0
            
            logger.info(
                f"📊 批处理进度: {status} | "
                f"{completed}/{total} ({progress*100:.1f}%) | "
                f"失败: {failed}"
            )
            
            # 回调进度
            if progress_callback:
                progress_callback(batch_id, status, progress, completed, total, failed)
            
            # 检查是否完成
            if status == "completed":
                logger.info(f"✅ 批处理完成: {batch_id}")
                return {
                    'status': status,
                    'output_file_id': batch.output_file_id,
                    'error_file_id': batch.error_file_id,
                    'completed': completed,
                    'failed': failed,
                    'total': total
                }
            elif status == "failed":
                logger.error(f"❌ 批处理失败: {batch_id}")
                raise RuntimeError(f"批处理失败: {batch_id}")
            elif status == "expired":
                logger.error(f"❌ 批处理过期: {batch_id}")
                raise RuntimeError(f"批处理过期: {batch_id}")
            elif status == "cancelled":
                logger.warning(f"⚠️ 批处理已取消: {batch_id}")
                raise RuntimeError(f"批处理已取消: {batch_id}")
            
            # 等待下一次检查
            time.sleep(check_interval)
    
    def download_results(
        self,
        file_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        下载结果文件
        
        Args:
            file_id: 文件ID
            output_path: 输出路径（可选）
        
        Returns:
            str: 结果文件路径
        """
        try:
            if not output_path:
                temp_dir = Path(tempfile.gettempdir())
                output_path = str(temp_dir / f"batch_results_{file_id}.jsonl")
            
            content = self.client.files.content(file_id)
            content.write_to_file(output_path)
            
            logger.info(f"✅ 结果文件下载成功: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"❌ 结果文件下载失败: {e}")
            raise
    
    def parse_results(self, file_path: str) -> Tuple[Dict[str, Dict], Dict]:
        """
        解析结果文件
        
        Args:
            file_path: 结果文件路径
        
        Returns:
            Tuple[Dict[str, Dict], Dict]: (结果字典, token统计)
            - 结果字典: {custom_id: result}
            - token统计: {'input_tokens': 123, 'output_tokens': 456, 'total_tokens': 579}
        """
        results = {}
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    item = json.loads(line)
                    custom_id = item.get('custom_id')
                    
                    # 提取响应内容
                    response = item.get('response', {})
                    body = response.get('body', {})
                    
                    # 判断是 Chat Completion 还是 Embedding 响应
                    if body.get('choices'):
                        # Chat Completion 响应
                        content = body['choices'][0]['message']['content']
                        usage = body.get('usage', {})
                        
                        results[custom_id] = {
                            'content': content,
                            'status': 'success',
                            'usage': usage
                        }
                        
                        # 累加token统计
                        total_input_tokens += usage.get('prompt_tokens', 0)
                        total_output_tokens += usage.get('completion_tokens', 0)
                        total_tokens += usage.get('total_tokens', 0)
                    elif body.get('data'):
                        # Embedding 响应
                        embedding_data = body.get('data', [])
                        usage = body.get('usage', {})
                        
                        results[custom_id] = {
                            'data': embedding_data,
                            'status': 'success',
                            'usage': usage
                        }
                        
                        # 累加token统计（embedding只有input tokens）
                        total_input_tokens += usage.get('prompt_tokens', 0) or usage.get('total_tokens', 0)
                        total_tokens += usage.get('total_tokens', 0)
                    else:
                        # 处理错误
                        error = item.get('error', {})
                        results[custom_id] = {
                            'content': None,
                            'status': 'error',
                            'error': error
                        }
            
            token_stats = {
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'total_tokens': total_tokens
            }
            
            logger.info(f"✅ 解析结果完成: {len(results)} 条, tokens: {total_tokens}")
            return results, token_stats
            
        except Exception as e:
            logger.error(f"❌ 解析结果文件失败: {e}")
            raise
    
    def submit_and_wait(
        self,
        tasks: List[Dict],
        check_interval: int = 60,
        progress_callback: Optional[callable] = None
    ) -> Tuple[Dict[str, Dict], Dict]:
        """
        一站式提交并等待结果
        
        Args:
            tasks: 任务列表
            check_interval: 检查间隔（秒）
            progress_callback: 进度回调
        
        Returns:
            Tuple[Dict[str, Dict], Dict]: (结果映射, token统计)
            - 结果映射: {custom_id: result}
            - token统计: {'input_tokens': 123, 'output_tokens': 456, 'total_tokens': 579}
        """
        # 1. 创建文件
        file_path = self.create_batch_file(tasks)
        
        # 2. 上传文件
        file_id = self.upload_file(file_path)
        
        # 3. 创建批处理
        batch_id = self.create_batch(file_id)
        
        # 4. 等待完成
        result_info = self.wait_for_completion(
            batch_id, 
            check_interval=check_interval,
            progress_callback=progress_callback
        )
        
        # 5. 下载结果
        output_file_id = result_info['output_file_id']
        result_path = self.download_results(output_file_id)
        
        # 6. 解析结果（返回结果和token统计）
        results, token_stats = self.parse_results(result_path)
        
        # 7. 下载错误文件（如果有）
        if result_info['failed'] > 0 and result_info.get('error_file_id'):
            error_path = self.download_results(result_info['error_file_id'])
            logger.warning(f"⚠️ 有 {result_info['failed']} 个任务失败，错误文件: {error_path}")
        
        # 8. 清理临时文件
        try:
            Path(file_path).unlink()
            Path(result_path).unlink()
        except:
            pass
        
        return results, token_stats


# 全局实例
_batch_client: Optional[BatchAPIClient] = None


def get_batch_client() -> BatchAPIClient:
    """获取全局Batch API客户端实例（单例）"""
    global _batch_client
    if _batch_client is None:
        _batch_client = BatchAPIClient()
    return _batch_client

