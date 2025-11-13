"""
NLP服务模块 (User Story 3: 知识图谱与GraphRAG)

包含:
- HanLP客户端: 实体识别
- 实体提取器: 批量提取和去重
- 实体合并器: 相似实体合并
"""

from .hanlp_client import get_hanlp_client, extract_entities

__all__ = ['get_hanlp_client', 'extract_entities']

