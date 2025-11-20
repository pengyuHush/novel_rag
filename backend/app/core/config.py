"""
配置管理模块 - 加载环境变量和应用配置
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 智谱AI配置 - 基于官方文档 https://docs.bigmodel.cn/cn/guide/start/model-overview
    zhipu_api_key: str = Field(..., env="ZHIPU_API_KEY")
    zhipu_default_model: str = Field(default="GLM-4.5-Air", env="ZHIPU_DEFAULT_MODEL")
    
    # 支持的智谱AI模型列表（按官方文档分类）
    supported_models: List[str] = [
        # 免费模型
        "GLM-4.5-Flash",
        "GLM-4-Flash-250414",
        # 高性价比
        "GLM-4.5-Air",
        "GLM-4.5-AirX",
        "GLM-4-Air-250414",
        # 极速模型
        "GLM-4.5-X",
        "GLM-4-AirX",
        "GLM-4-FlashX-250414",
        # 高性能模型
        "GLM-4.5",
        "GLM-4-Plus",
        "GLM-4.6",
        # 超长上下文
        "GLM-4-Long",
    ]
    
    # 模型元数据（用于前端展示和成本计算）
    model_metadata: dict = {
        "GLM-4.5-Flash": {
            "name": "GLM-4.5-Flash",
            "category": "免费",
            "max_tokens": 8192,
            "price_input": 0.0,  # 免费
            "price_output": 0.0,
            "description": "免费模型，适合日常查询"
        },
        "GLM-4-Flash-250414": {
            "name": "GLM-4-Flash",
            "category": "免费",
            "max_tokens": 128000,
            "price_input": 0.0,
            "price_output": 0.0,
            "description": "免费模型，支持超长上下文"
        },
        "GLM-4.5-Air": {
            "name": "GLM-4.5-Air",
            "category": "高性价比",
            "max_tokens": 8192,
            "price_input": 0.001,  # 元/千tokens
            "price_output": 0.001,
            "description": "推荐使用，性价比最高"
        },
        "GLM-4.5-AirX": {
            "name": "GLM-4.5-AirX",
            "category": "高性价比",
            "max_tokens": 8192,
            "price_input": 0.001,
            "price_output": 0.001,
            "description": "高性价比，增强版"
        },
        "GLM-4.5-X": {
            "name": "GLM-4.5-X",
            "category": "极速",
            "max_tokens": 8192,
            "price_input": 0.01,
            "price_output": 0.01,
            "description": "极速响应"
        },
        "GLM-4.5": {
            "name": "GLM-4.5",
            "category": "高性能",
            "max_tokens": 8192,
            "price_input": 0.05,
            "price_output": 0.05,
            "description": "高性能模型"
        },
        "GLM-4-Plus": {
            "name": "GLM-4-Plus",
            "category": "高性能",
            "max_tokens": 128000,
            "price_input": 0.05,
            "price_output": 0.05,
            "description": "顶级性能，超长上下文"
        },
        "GLM-4.6": {
            "name": "GLM-4.6",
            "category": "高性能",
            "max_tokens": 8192,
            "price_input": 0.1,
            "price_output": 0.1,
            "description": "最新旗舰模型"
        },
        "GLM-4-Long": {
            "name": "GLM-4-Long",
            "category": "超长上下文",
            "max_tokens": 1000000,
            "price_input": 0.001,
            "price_output": 0.001,
            "description": "百万tokens超长上下文"
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
    embedding_dimension: int = Field(default=1024, description="向量维度")
    
    # 图谱构建配置
    use_batch_api_for_graph: bool = Field(default=True, description="图谱构建是否使用Batch API（默认开启，完全免费）", env="USE_BATCH_API_FOR_GRAPH")
    use_batch_api_for_embedding: bool = Field(default=True, description="向量化是否使用Batch API（默认开启，价格便宜50%）", env="USE_BATCH_API_FOR_EMBEDDING")
    
    # 并发控制配置（根据智谱AI速率限制调整）
    # 参考：https://bigmodel.cn/usercenter/proj-mgmt/rate-limits
    # 测试显示最大并发10，建议8，但实际项目中使用2-3更安全（考虑多阶段并发）
    # 注意：启用Batch API后，这些并发限制不再适用（Batch API无并发限制）
    graph_attribute_concurrency: int = Field(default=3, description="图谱属性提取最大并发数（非Batch模式）", env="GRAPH_ATTRIBUTE_CONCURRENCY")
    graph_relation_concurrency: int = Field(default=5, description="图谱关系分类最大并发数（非Batch模式）", env="GRAPH_RELATION_CONCURRENCY")
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
            self.upload_dir,
            self.graph_dir,
            self.chromadb_path,
            Path(self.database_url.replace("sqlite:///", "")).parent,
            Path(self.log_file).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ 数据目录初始化完成")


# 全局配置实例
settings = Settings()

# 确保目录存在
settings.ensure_directories()

