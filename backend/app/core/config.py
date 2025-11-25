"""
配置管理模块 - 加载环境变量和应用配置
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # ==================== LLM提供商配置 ====================
    # 智谱AI配置 - 基于官方文档 https://docs.bigmodel.cn/cn/guide/start/model-overview
    zhipu_api_key: str = Field(..., env="ZHIPU_API_KEY")
    zhipu_default_model: str = Field(default="GLM-4.5-Air", env="ZHIPU_DEFAULT_MODEL")
    
    # OpenAI配置（可选）
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    
    # DeepSeek配置（可选）
    deepseek_api_key: str = Field(default="", env="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", env="DEEPSEEK_BASE_URL")
    
    # Gemini配置（可选）
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    
    # 阿里通义千问配置（可选）
    ali_api_key: str = Field(default="", env="ALI_API_KEY")
    ali_base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1", env="ALI_BASE_URL")
    
    # 默认LLM提供商
    default_llm_provider: str = Field(default="zhipu", env="DEFAULT_LLM_PROVIDER")
    
    # 支持的模型列表（带提供商前缀）
    supported_models: List[str] = [
        # 智谱AI
        "zhipu/GLM-4.5-Flash",
        "zhipu/GLM-4.5",
        "zhipu/GLM-4.6",
        "zhipu/GLM-4.5-Air",
        "zhipu/GLM-4-Plus",
        "zhipu/GLM-4-Long",
        # OpenAI
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4-turbo",
        "openai/gpt-3.5-turbo",
        # DeepSeek
        "deepseek/deepseek-chat",
        "deepseek/deepseek-reasoner",
        # Gemini
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-2.0-flash-exp",
        "gemini/gemini-3-pro-preview",
        # 阿里通义千问
        "ali/qwen-max",
        "ali/qwen-plus",
        "ali/qwen-turbo",
    ]
    
    # 模型元数据（用于前端展示）
    model_metadata: dict = {
        # 智谱AI
        "zhipu/GLM-4.5-Flash": {
            "name": "GLM-4.5-Flash",
            "provider": "zhipu",
            "category": "免费",
            "max_tokens": 8192,
            "supports_thinking": False,
            "description": "免费模型，适合日常查询"
        },
        "zhipu/GLM-4.5": {
            "name": "GLM-4.5",
            "provider": "zhipu",
            "category": "高性能",
            "max_tokens": 8192,
            "supports_thinking": False,
            "description": "高性能模型"
        },
        "zhipu/GLM-4.6": {
            "name": "GLM-4.6",
            "provider": "zhipu",
            "category": "高性能",
            "max_tokens": 8192,
            "supports_thinking": False,
            "description": "最新旗舰模型"
        },
        "zhipu/GLM-4.5-Air": {
            "name": "GLM-4.5-Air",
            "provider": "zhipu",
            "category": "高性价比",
            "max_tokens": 8192,
            "supports_thinking": False,
            "description": "推荐使用，性价比最高"
        },
        "zhipu/GLM-4-Plus": {
            "name": "GLM-4-Plus",
            "provider": "zhipu",
            "category": "高性能",
            "max_tokens": 128000,
            "supports_thinking": False,
            "description": "顶级性能，超长上下文"
        },
        "zhipu/GLM-4-Long": {
            "name": "GLM-4-Long",
            "provider": "zhipu",
            "category": "超长上下文",
            "max_tokens": 1000000,
            "supports_thinking": False,
            "description": "百万tokens超长上下文"
        },
        # OpenAI
        "openai/gpt-4o": {
            "name": "GPT-4o",
            "provider": "openai",
            "category": "旗舰",
            "max_tokens": 16384,
            "supports_thinking": False,
            "description": "OpenAI最强多模态模型"
        },
        "openai/gpt-4o-mini": {
            "name": "GPT-4o-mini",
            "provider": "openai",
            "category": "高性价比",
            "max_tokens": 16384,
            "supports_thinking": False,
            "description": "小型高效模型"
        },
        "openai/gpt-4-turbo": {
            "name": "GPT-4-Turbo",
            "provider": "openai",
            "category": "高性能",
            "max_tokens": 128000,
            "supports_thinking": False,
            "description": "GPT-4 Turbo 长上下文"
        },
        "openai/gpt-3.5-turbo": {
            "name": "GPT-3.5-Turbo",
            "provider": "openai",
            "category": "经济",
            "max_tokens": 16384,
            "supports_thinking": False,
            "description": "快速经济的模型"
        },
        # DeepSeek
        "deepseek/deepseek-chat": {
            "name": "DeepSeek-Chat",
            "provider": "deepseek",
            "category": "对话",
            "max_tokens": 64000,
            "supports_thinking": False,
            "description": "高性价比对话模型"
        },
        "deepseek/deepseek-reasoner": {
            "name": "DeepSeek-Reasoner",
            "provider": "deepseek",
            "category": "推理",
            "max_tokens": 64000,
            "supports_thinking": True,
            "description": "推理模型，支持思维链展示"
        },
        # Gemini
        "gemini/gemini-1.5-pro": {
            "name": "Gemini-1.5-Pro",
            "provider": "gemini",
            "category": "旗舰",
            "max_tokens": 2097152,
            "supports_thinking": False,
            "description": "Google最强模型，超长上下文"
        },
        "gemini/gemini-1.5-flash": {
            "name": "Gemini-1.5-Flash",
            "provider": "gemini",
            "category": "高效",
            "max_tokens": 1048576,
            "supports_thinking": False,
            "description": "快速高效模型"
        },
        "gemini/gemini-2.0-flash-exp": {
            "name": "Gemini-2.0-Flash-Exp",
            "provider": "gemini",
            "category": "实验",
            "max_tokens": 1048576,
            "supports_thinking": False,
            "description": "实验性最新模型"
        },
        "gemini/gemini-3-pro-preview": {
            "name": "Gemini-3-Pro-Preview",
            "provider": "gemini",
            "category": "预览",
            "max_tokens": 1048576,
            "supports_thinking": False,
            "description": "Gemini 3 Pro预览版"
        },
        # 阿里通义千问（Qwen3+ 支持深度思考模式）
        "ali/qwen-max": {
            "name": "Qwen-Max",
            "provider": "ali",
            "category": "旗舰",
            "max_tokens": 32000,
            "supports_thinking": True,
            "description": "通义千问最强模型，支持深度思考"
        },
        "ali/qwen-plus": {
            "name": "Qwen-Plus",
            "provider": "ali",
            "category": "高性能",
            "max_tokens": 32000,
            "supports_thinking": True,
            "description": "高性能模型，支持深度思考"
        },
        "ali/qwen-turbo": {
            "name": "Qwen-Turbo",
            "provider": "ali",
            "category": "高效",
            "max_tokens": 8000,
            "supports_thinking": True,
            "description": "快速响应模型，支持深度思考"
        },
    }
    
    # 应用配置
    app_name: str = Field(default="网络小说智能问答系统", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./data/sqlite/metadata.db",
        env="DATABASE_URL"
    )
    
    # ChromaDB配置
    chromadb_path: str = Field(default="./data/chromadb", env="CHROMADB_PATH")
    
    # 文件存储配置
    data_dir: str = Field(default="./data", env="DATA_DIR")
    upload_dir: str = Field(default="./data/uploads", env="UPLOAD_DIR")
    graph_dir: str = Field(default="./data/graphs", env="GRAPH_DIR")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # CORS配置
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000",
                 "http://localhost:3001", "http://127.0.0.1:3001"
                 ],
        env="ALLOWED_ORIGINS"
    )
    
    # Token限制
    max_tokens_per_query: int = Field(default=8000, env="MAX_TOKENS_PER_QUERY")
    max_context_chunks: int = Field(default=10, env="MAX_CONTEXT_CHUNKS")
    
    # RAG配置
    chunk_size: int = Field(default=550, description="文本块大小")
    chunk_overlap: int = Field(default=125, description="文本块重叠")
    top_k_retrieval: int = Field(default=30, description="初始检索Top-K")
    top_k_rerank: int = Field(default=10, description="Rerank后Top-K")
    min_similarity_threshold: float = Field(default=1.2, description="向量检索最大L2距离阈值(越小越相似)")
    recency_bias_weight: float = Field(default=0.15, description="时间衰减权重(0.0-0.5,越大越偏向后期)")
    
    # 智谱AI Embedding配置
    embedding_model: str = Field(default="embedding-3", description="Embedding模型")
    embedding_dimension: int = Field(default=2048, description="向量维度（embedding-3 默认 2048）")
    
    # 查询分解配置
    query_decomposition_enabled: bool = Field(default=True, description="是否启用查询分解功能", env="QUERY_DECOMPOSITION_ENABLED")
    query_decomposition_max_subqueries: int = Field(default=5, description="查询分解最多子查询数", env="QUERY_DECOMPOSITION_MAX_SUBQUERIES")
    query_decomposition_model: str = Field(default="glm-4-flash", description="查询分解使用的模型", env="QUERY_DECOMPOSITION_MODEL")
    query_decomposition_complexity_threshold: int = Field(default=30, description="查询复杂度阈值（字数）", env="QUERY_DECOMPOSITION_COMPLEXITY_THRESHOLD")
    
    # 图谱构建配置
    use_batch_api_for_graph: bool = Field(default=True, description="图谱构建是否使用Batch API（默认开启，完全免费）", env="USE_BATCH_API_FOR_GRAPH")
    use_batch_api_for_embedding: bool = Field(default=True, description="向量化是否使用Batch API（默认开启，价格便宜50%）", env="USE_BATCH_API_FOR_EMBEDDING")
    batch_api_threshold: int = Field(default=20, description="Batch API 最小请求数阈值（< 此值使用实时API）", env="BATCH_API_THRESHOLD")
    
    # 并发控制配置（根据智谱AI速率限制调整）
    # 参考：https://bigmodel.cn/usercenter/proj-mgmt/rate-limits
    # 测试显示最大并发10，建议8，但实际项目中使用2-3更安全（考虑多阶段并发）
    # 注意：启用Batch API后，这些并发限制不再适用（Batch API无并发限制）
    # GLM-4.5-Flash 最大并发数为2
    graph_attribute_concurrency: int = Field(default=2, description="图谱属性提取最大并发数（非Batch模式）", env="GRAPH_ATTRIBUTE_CONCURRENCY")
    graph_relation_concurrency: int = Field(default=2, description="图谱关系分类最大并发数（非Batch模式）", env="GRAPH_RELATION_CONCURRENCY")
    embedding_batch_size: int = Field(default=20, description="向量化批处理大小（非Batch API模式时的每批次文本数）", env="EMBEDDING_BATCH_SIZE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_data_dir(self) -> Path:
        """获取数据目录路径"""
        return Path("./data")
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.data_dir,
            self.upload_dir,
            self.graph_dir,
            self.chromadb_path,
            Path(self.data_dir) / "indices",  # BM25 索引目录
            Path(self.database_url.replace("sqlite:///", "")).parent,
            Path(self.log_file).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ 数据目录初始化完成")
    
    def is_provider_available(self, provider: str) -> bool:
        """检查提供商是否可用（API密钥已配置）"""
        provider_key_map = {
            "zhipu": self.zhipu_api_key,
            "openai": self.openai_api_key,
            "deepseek": self.deepseek_api_key,
            "gemini": self.gemini_api_key,
            "ali": self.ali_api_key,
        }
        api_key = provider_key_map.get(provider, "")
        return bool(api_key and api_key.strip())
    
    def get_available_models(self) -> List[str]:
        """获取所有可用的模型列表（根据已配置的API密钥筛选）"""
        available = []
        for model in self.supported_models:
            provider = model.split("/")[0]
            if self.is_provider_available(provider):
                available.append(model)
        return available


# 全局配置实例
settings = Settings()

# 确保目录存在
settings.ensure_directories()

