"""
Pydantic数据模型（API请求/响应）
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========================================
# 枚举类型
# ========================================

class IndexStatus(str, Enum):
    """索引状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileFormat(str, Enum):
    """文件格式"""
    TXT = "txt"
    EPUB = "epub"


class ModelType(str, Enum):
    """智谱AI模型类型 - 基于官方文档 https://docs.bigmodel.cn/cn/guide/start/model-overview"""
    # 免费模型
    GLM_4_5_FLASH = "GLM-4.5-Flash"
    GLM_4_FLASH = "GLM-4-Flash-250414"
    
    # 高性价比模型
    GLM_4_5_AIR = "GLM-4.5-Air"
    GLM_4_5_AIRX = "GLM-4.5-AirX"
    GLM_4_AIR = "GLM-4-Air-250414"
    
    # 极速模型
    GLM_4_5_X = "GLM-4.5-X"
    GLM_4_AIRX = "GLM-4-AirX"
    GLM_4_FLASHX = "GLM-4-FlashX-250414"
    
    # 高性能模型
    GLM_4_5 = "GLM-4.5"
    GLM_4_PLUS = "GLM-4-Plus"
    GLM_4_6 = "GLM-4.6"
    
    # 超长上下文
    GLM_4_LONG = "GLM-4-Long"


class Confidence(str, Enum):
    """置信度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ========================================
# 小说相关模型
# ========================================

class NovelCreate(BaseModel):
    """小说上传请求"""
    title: str = Field(..., min_length=1, max_length=200, description="小说标题")
    author: Optional[str] = Field(None, max_length=100, description="作者")


class NovelResponse(BaseModel):
    """小说详情响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    author: Optional[str] = None
    total_chars: int
    total_chapters: int
    index_status: IndexStatus
    index_progress: float = Field(ge=0.0, le=1.0, description="索引进度 0-1")
    file_format: FileFormat
    
    # 索引统计
    total_chunks: int = 0
    total_entities: int = 0
    total_relations: int = 0
    embedding_tokens: int = 0
    
    upload_date: str
    indexed_date: Optional[str] = None
    created_at: str
    updated_at: str


class NovelListItem(BaseModel):
    """小说列表项"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    author: Optional[str] = None
    total_chars: int
    total_chapters: int
    index_status: IndexStatus
    index_progress: float
    file_format: FileFormat
    upload_date: str


class NovelProgressResponse(BaseModel):
    """索引进度响应"""
    novel_id: int
    status: IndexStatus
    progress: float = Field(ge=0.0, le=1.0)
    current_chapter: Optional[int] = None
    total_chapters: int
    message: str


# ========================================
# 章节相关模型
# ========================================

class ChapterListItem(BaseModel):
    """章节列表项 (User Story 2: 在线阅读)"""
    model_config = ConfigDict(from_attributes=True)
    
    num: int = Field(..., description="章节号")
    title: Optional[str] = Field(None, description="章节标题")
    char_count: int = Field(..., description="章节字数")


class ChapterContent(BaseModel):
    """章节内容 (User Story 2: 在线阅读)"""
    chapter_num: int = Field(..., description="章节号")
    title: Optional[str] = Field(None, description="章节标题")
    content: str = Field(..., description="章节内容")
    prev_chapter: Optional[int] = Field(None, description="上一章章节号")
    next_chapter: Optional[int] = Field(None, description="下一章章节号")
    total_chapters: int = Field(..., description="总章节数")


# ========================================
# 查询相关模型
# ========================================

class QueryRequest(BaseModel):
    """查询请求"""
    novel_id: int = Field(..., gt=0, description="小说ID")
    query: str = Field(..., min_length=1, max_length=1000, description="查询文本")
    model: ModelType = Field(default=ModelType.GLM_4_5, description="使用的模型")


class Citation(BaseModel):
    """原文引用"""
    model_config = ConfigDict(populate_by_name=True)
    
    chapter_num: int = Field(..., alias="chapterNum", description="章节号")
    chapter_title: Optional[str] = Field(None, alias="chapterTitle", description="章节标题")
    text: str = Field(..., description="引用文本")
    score: Optional[float] = Field(None, description="相关性分数")


class Contradiction(BaseModel):
    """矛盾检测结果"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = Field(..., description="矛盾类型")
    early_description: str = Field(..., alias="earlyDescription", description="早期描述")
    early_chapter: int = Field(..., alias="earlyChapter", description="早期章节")
    late_description: str = Field(..., alias="lateDescription", description="后期描述")
    late_chapter: int = Field(..., alias="lateChapter", description="后期章节")
    analysis: str = Field(..., description="矛盾分析")
    confidence: Confidence = Field(..., description="置信度")


class TokenStats(BaseModel):
    """Token统计"""
    model_config = ConfigDict(populate_by_name=True)
    
    total_tokens: int = Field(..., alias="totalTokens", description="总Token数")
    embedding_tokens: int = Field(0, alias="embeddingTokens", description="Embedding消耗的Token")
    prompt_tokens: int = Field(0, alias="promptTokens", description="提示词Token数")
    completion_tokens: int = Field(0, alias="completionTokens", description="生成内容Token数")
    self_rag_tokens: int = Field(0, alias="selfRagTokens", description="Self-RAG验证额外消耗的Token")
    by_model: Dict[str, Dict[str, int]] = Field(default_factory=dict, alias="byModel", description="按模型分类的Token统计")


class QueryResponse(BaseModel):
    """查询响应"""
    query_id: int
    answer: str
    citations: List[Citation] = []
    graph_info: Optional[Dict[str, Any]] = None
    contradictions: List[Contradiction] = []
    token_stats: TokenStats
    response_time: float
    retrieve_time: Optional[float] = None
    generate_time: Optional[float] = None
    confidence: Confidence
    model: str
    timestamp: str


class QueryStage(str, Enum):
    """查询处理阶段"""
    UNDERSTANDING = "understanding"  # 查询理解
    RETRIEVING = "retrieving"        # 检索上下文
    GENERATING = "generating"        # 生成答案
    VALIDATING = "validating"        # Self-RAG验证
    FINALIZING = "finalizing"        # 完成汇总


class StreamMessage(BaseModel):
    """流式消息"""
    stage: QueryStage
    content: str = ""
    progress: float = Field(ge=0.0, le=1.0, default=0.0)
    metadata: Optional[Dict[str, Any]] = None


# ========================================
# WebSocket消息
# ========================================

class IndexingProgressMessage(BaseModel):
    """索引进度消息"""
    novel_id: int
    status: IndexStatus
    progress: float
    current_chapter: int
    total_chapters: int
    message: str
    timestamp: str


# ========================================
# 统计相关模型
# ========================================

class TokenStatsQuery(BaseModel):
    """Token统计查询参数"""
    period: Optional[str] = Field(None, pattern="^(day|week|month)$", description="时间段")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    model: Optional[str] = None


class TokenStatsResponse(BaseModel):
    """Token统计响应"""
    total_tokens: int
    total_cost: float
    by_model: Dict[str, Dict[str, Any]]
    by_operation: Dict[str, int]
    period: str

