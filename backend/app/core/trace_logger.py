"""
TRACE日志配置模块
用于输出查询流程的详细步骤日志到独立文件
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# 定义TRACE日志级别 (介于DEBUG和INFO之间)
TRACE_LEVEL = 15
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, message, *args, **kwargs):
    """TRACE日志方法"""
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


# 将trace方法添加到Logger类
logging.Logger.trace = trace


class TraceLogger:
    """TRACE日志工具类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not TraceLogger._initialized:
            self.logger = logging.getLogger("query_trace")
            self.logger.setLevel(TRACE_LEVEL)
            
            # 确保logs目录存在
            log_dir = Path("backend/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 配置文件处理器
            file_handler = logging.FileHandler(
                log_dir / "query_detail.log",
                mode='a',
                encoding='utf-8'
            )
            file_handler.setLevel(TRACE_LEVEL)
            
            # 简单格式：时间 + 消息
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            TraceLogger._initialized = True
    
    def trace_step(
        self,
        query_id: Optional[int],
        step_name: str,
        emoji: str,
        input_data: Any,
        output_data: Any,
        status: str = "success"
    ):
        """
        记录一个完整的处理步骤
        
        Args:
            query_id: 查询ID
            step_name: 步骤名称
            emoji: emoji图标
            input_data: 输入数据
            output_data: 输出数据
            status: 状态（success/failed/skipped）
        """
        prefix = f"[Query-{query_id}] " if query_id else ""
        separator = "━" * 60
        
        # 构建日志消息
        lines = [
            "",
            f"{prefix}{emoji} {step_name}",
            separator,
        ]
        
        # 输入
        if input_data is not None:
            lines.append("📥 输入：")
            lines.extend(self._format_data(input_data, indent="  "))
        
        # 输出
        if output_data is not None:
            lines.append("📤 输出：")
            lines.extend(self._format_data(output_data, indent="  "))
        
        # 状态
        status_emoji = {"success": "✅", "failed": "❌", "skipped": "⏭️"}.get(status, "ℹ️")
        lines.append(f"{status_emoji} 状态：{status}")
        lines.append(separator)
        
        self.logger.trace("\n".join(lines))
    
    def trace_section(
        self,
        query_id: Optional[int],
        section_name: str,
        emoji: str = "📋"
    ):
        """
        记录一个章节标题
        
        Args:
            query_id: 查询ID
            section_name: 章节名称
            emoji: emoji图标
        """
        prefix = f"[Query-{query_id}] " if query_id else ""
        separator = "═" * 60
        
        lines = [
            "",
            separator,
            f"{prefix}{emoji} {section_name}",
            separator,
        ]
        
        self.logger.trace("\n".join(lines))
    
    def _format_data(self, data: Any, indent: str = "") -> List[str]:
        """
        格式化数据为可读的多行文本
        
        Args:
            data: 要格式化的数据
            indent: 缩进字符串
        
        Returns:
            List[str]: 格式化后的行列表
        """
        lines = []
        
        if isinstance(data, str):
            # 字符串：完整输出，保持原始格式
            for line in data.split('\n'):
                lines.append(f"{indent}{line}")
        
        elif isinstance(data, (list, tuple)):
            # 列表：带编号输出
            if len(data) == 0:
                lines.append(f"{indent}(空列表)")
            else:
                for i, item in enumerate(data, 1):
                    if isinstance(item, dict):
                        lines.append(f"{indent}[{i}]")
                        lines.extend(self._format_dict(item, indent + "  "))
                    elif isinstance(item, str) and len(item) > 100:
                        # 长字符串换行显示
                        lines.append(f"{indent}[{i}] {item[:100]}...")
                        lines.append(f"{indent}    (长度: {len(item)} 字符)")
                    else:
                        lines.append(f"{indent}[{i}] {item}")
        
        elif isinstance(data, dict):
            # 字典：键值对输出
            lines.extend(self._format_dict(data, indent))
        
        elif isinstance(data, (int, float, bool)):
            # 基础类型
            lines.append(f"{indent}{data}")
        
        elif data is None:
            lines.append(f"{indent}(无)")
        
        else:
            # 其他类型：尝试转字符串
            try:
                lines.append(f"{indent}{str(data)}")
            except:
                lines.append(f"{indent}(无法格式化)")
        
        return lines
    
    def _format_dict(self, data: dict, indent: str = "") -> List[str]:
        """格式化字典"""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, str):
                if '\n' in value or len(value) > 100:
                    # 多行或长字符串
                    lines.append(f"{indent}{key}:")
                    for line in value.split('\n'):
                        lines.append(f"{indent}  {line}")
                    if len(value) > 500:
                        lines.append(f"{indent}  (总长度: {len(value)} 字符)")
                else:
                    lines.append(f"{indent}{key}: {value}")
            
            elif isinstance(value, (list, tuple)):
                lines.append(f"{indent}{key}: ({len(value)} 项)")
                for i, item in enumerate(value[:5], 1):  # 只显示前5项
                    if isinstance(item, dict):
                        lines.append(f"{indent}  [{i}]")
                        lines.extend(self._format_dict(item, indent + "    "))
                    else:
                        item_str = str(item)
                        if len(item_str) > 80:
                            lines.append(f"{indent}  [{i}] {item_str[:80]}...")
                        else:
                            lines.append(f"{indent}  [{i}] {item_str}")
                
                if len(value) > 5:
                    lines.append(f"{indent}  ... (还有 {len(value) - 5} 项)")
            
            elif isinstance(value, dict):
                lines.append(f"{indent}{key}:")
                lines.extend(self._format_dict(value, indent + "  "))
            
            else:
                lines.append(f"{indent}{key}: {value}")
        
        return lines
    
    def trace_embedding(
        self,
        query_id: Optional[int],
        query_text: str,
        embedding_vector: List[float]
    ):
        """
        记录向量化步骤
        
        Args:
            query_id: 查询ID
            query_text: 查询文本
            embedding_vector: 向量
        """
        vector_stats = {
            "维度": len(embedding_vector),
            "均值": f"{sum(embedding_vector) / len(embedding_vector):.6f}",
            "最大值": f"{max(embedding_vector):.6f}",
            "最小值": f"{min(embedding_vector):.6f}",
            "向量预览": f"[{', '.join(f'{v:.4f}' for v in embedding_vector[:5])}, ...]"
        }
        
        self.trace_step(
            query_id=query_id,
            step_name="查询向量化",
            emoji="🎯",
            input_data=query_text,
            output_data=vector_stats,
            status="success"
        )
    
    def trace_retrieval(
        self,
        query_id: Optional[int],
        top_k: int,
        results: List[Dict]
    ):
        """
        记录向量检索步骤
        
        Args:
            query_id: 查询ID
            top_k: 检索数量
            results: 检索结果
        """
        # 格式化检索结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "排名": i,
                "文档ID": result.get('id', 'N/A'),
                "章节": f"第{result.get('metadata', {}).get('chapter_num', '?')}章",
                "章节标题": result.get('metadata', {}).get('chapter_title', ''),
                "相似度分数": f"{result.get('distance', 0):.4f}",
                "内容片段": result.get('content', '')[:150] + "..." if result.get('content', '') else ""
            })
        
        self.trace_step(
            query_id=query_id,
            step_name=f"向量检索 (Top-{top_k})",
            emoji="🔍",
            input_data=f"请求Top-{top_k}个最相似文档",
            output_data=formatted_results,
            status="success"
        )
    
    def trace_rerank(
        self,
        query_id: Optional[int],
        query: str,
        candidates_count: int,
        reranked_results: List[Dict],
        top_k: int
    ):
        """
        记录Rerank步骤
        
        Args:
            query_id: 查询ID
            query: 查询文本
            candidates_count: 候选文档数量
            reranked_results: 重排序结果
            top_k: 返回数量
        """
        # 格式化重排序结果
        formatted_results = []
        for i, result in enumerate(reranked_results, 1):
            formatted_results.append({
                "排名": i,
                "章节": f"第{result.get('metadata', {}).get('chapter_num', '?')}章",
                "章节标题": result.get('metadata', {}).get('chapter_title', ''),
                "重排序分数": f"{result.get('score', 0):.4f}",
                "完整内容": result.get('content', '')
            })
        
        input_info = {
            "查询": query,
            "候选文档数": candidates_count,
            "目标数量": top_k
        }
        
        self.trace_step(
            query_id=query_id,
            step_name=f"Rerank重排序 (Top-{top_k})",
            emoji="📊",
            input_data=input_info,
            output_data=formatted_results,
            status="success"
        )


# 全局单例
_trace_logger = None


def get_trace_logger() -> TraceLogger:
    """获取TRACE日志记录器单例"""
    global _trace_logger
    if _trace_logger is None:
        _trace_logger = TraceLogger()
    return _trace_logger

