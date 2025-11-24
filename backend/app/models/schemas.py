"""
Pydantic数据模型（API请求/响应）
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
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
    """LLM模型类型 - 支持多提供商"""
    # 智谱AI
    ZHIPU_GLM_4_5_FLASH = "zhipu/GLM-4.5-Flash"
    ZHIPU_GLM_4_5 = "zhipu/GLM-4.5"
    ZHIPU_GLM_4_6 = "zhipu/GLM-4.6"
    ZHIPU_GLM_4_5_AIR = "zhipu/GLM-4.5-Air"
    ZHIPU_GLM_4_PLUS = "zhipu/GLM-4-Plus"
    ZHIPU_GLM_4_LONG = "zhipu/GLM-4-Long"
    
    # OpenAI
    OPENAI_GPT_4O = "openai/gpt-4o"
    OPENAI_GPT_4O_MINI = "openai/gpt-4o-mini"
    OPENAI_GPT_4_TURBO = "openai/gpt-4-turbo"
    OPENAI_GPT_3_5_TURBO = "openai/gpt-3.5-turbo"
    
    # DeepSeek
    DEEPSEEK_CHAT = "deepseek/deepseek-chat"
    DEEPSEEK_REASONER = "deepseek/deepseek-reasoner"
    
    # Gemini
    GEMINI_1_5_PRO = "gemini/gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini/gemini-1.5-flash"
    GEMINI_2_0_FLASH_EXP = "gemini/gemini-2.0-flash-exp"
    GEMINI_3_PRO_PREVIEW = "gemini/gemini-3-pro-preview"
    
    # 阿里通义千问
    ALI_QWEN_MAX = "ali/qwen-max"
    ALI_QWEN_PLUS = "ali/qwen-plus"
    ALI_QWEN_TURBO = "ali/qwen-turbo"


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
    index_progress: float = Field(ge=0.0, description="索引进度 0-1")
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
    
    @field_validator('index_progress')
    @classmethod
    def clamp_index_progress(cls, v: float) -> float:
        """确保进度在0-1范围内，处理浮点数精度问题"""
        return max(0.0, min(v, 1.0))


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


class IndexingStep(BaseModel):
    """索引步骤"""
    name: str = Field(..., description="步骤名称")
    status: str = Field(..., description="状态：pending/processing/completed/failed")
    progress: float = Field(0.0, ge=0.0, description="步骤进度 0-1")
    message: str = Field("", description="状态消息")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    @field_validator('progress')
    @classmethod
    def clamp_progress(cls, v: float) -> float:
        """确保进度在0-1范围内，处理浮点数精度问题"""
        return max(0.0, min(v, 1.0))


class FailedChapter(BaseModel):
    """失败的章节"""
    chapter_num: int
    chapter_title: Optional[str] = None
    error: str


class IndexingDetail(BaseModel):
    """索引详情"""
    steps: List[IndexingStep] = Field(default_factory=list, description="处理步骤")
    failed_chapters: List[FailedChapter] = Field(default_factory=list, description="失败的章节")
    token_stats: Optional[Dict[str, Any]] = Field(None, description="Token统计")
    warnings: List[str] = Field(default_factory=list, description="警告信息")


class NovelProgressResponse(BaseModel):
    """索引进度响应（扩展版）"""
    novel_id: int
    status: IndexStatus
    progress: float = Field(ge=0.0, description="索引进度 0-1")
    current_chapter: Optional[int] = None
    total_chapters: int
    total_chars: int = 0  # 总字数
    message: str
    detail: Optional[IndexingDetail] = None  # 详细信息
    
    @field_validator('progress')
    @classmethod
    def clamp_progress(cls, v: float) -> float:
        """确保进度在0-1范围内，处理浮点数精度问题"""
        return max(0.0, min(v, 1.0))


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
    novel_id: int = Field(..., gt=0, description="小说ID（主小说ID，向后兼容）")
    novel_ids: Optional[List[int]] = Field(None, description="多个小说ID（支持多小说查询）")
    query: str = Field(..., min_length=1, max_length=1000, description="查询文本")
    model: ModelType = Field(default=ModelType.ZHIPU_GLM_4_5_FLASH, description="使用的模型")
    enable_query_rewrite: bool = Field(default=True, description="是否启用查询改写")
    recency_bias_weight: float = Field(default=0.15, ge=0.0, le=0.5, description="时间衰减权重")


class Citation(BaseModel):
    """原文引用"""
    model_config = ConfigDict(populate_by_name=True)
    
    novel_id: int = Field(..., alias="novelId", description="来源小说ID")
    novel_title: Optional[str] = Field(None, alias="novelTitle", description="来源小说标题")
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


class StageTokenStats(BaseModel):
    """阶段级别的Token统计"""
    stage: str = Field(..., description="阶段名称")
    model: str = Field(..., description="使用的模型")
    inputTokens: int = Field(..., alias="inputTokens", description="输入Token数")
    outputTokens: int = Field(..., alias="outputTokens", description="输出Token数")
    totalTokens: int = Field(..., alias="totalTokens", description="该阶段总Token数")


class TokenStats(BaseModel):
    """Token统计"""
    model_config = ConfigDict(populate_by_name=True)
    
    total_tokens: int = Field(..., alias="totalTokens", description="总Token数")
    input_tokens: int = Field(0, alias="inputTokens", description="总输入Token数")
    output_tokens: int = Field(0, alias="outputTokens", description="总输出Token数")
    embedding_tokens: int = Field(0, alias="embeddingTokens", description="Embedding消耗的Token")
    prompt_tokens: int = Field(0, alias="promptTokens", description="提示词Token数")
    completion_tokens: int = Field(0, alias="completionTokens", description="生成内容Token数")
    self_rag_tokens: int = Field(0, alias="selfRagTokens", description="Self-RAG验证额外消耗的Token")
    by_model: Dict[str, Dict[str, int]] = Field(default_factory=dict, alias="byModel", description="按模型分类的Token统计")
    by_stage: List[Dict[str, Any]] = Field(default_factory=list, alias="byStage", description="按阶段分类的Token统计")


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
    rewritten_query: Optional[str] = Field(None, description="改写后的查询（如有）")


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
    thinking: Optional[str] = None  # 思考过程内容（thinking模式）
    progress: float = Field(ge=0.0, default=0.0, description="进度 0-1")
    is_delta: bool = False  # 是否为增量消息
    done: bool = False  # 是否完成
    citations: Optional[List[Citation]] = None  # 引用来源
    contradictions: Optional[List[Contradiction]] = None  # 矛盾检测结果
    query_id: Optional[int] = None  # 查询ID
    error: Optional[str] = None  # 错误信息
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('progress')
    @classmethod
    def clamp_progress(cls, v: float) -> float:
        """确保进度在0-1范围内，处理浮点数精度问题"""
        return max(0.0, min(v, 1.0))


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
    token_stats: Optional[Dict[str, Any]] = Field(None, description="Token统计信息")


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
    by_operation: Dict[str, Dict[str, Any]]
    period: str

