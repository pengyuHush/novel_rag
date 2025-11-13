"""
配置管理模块 - 加载环境变量和应用配置
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 智谱AI配置
    zhipu_api_key: str = Field(..., env="ZHIPU_API_KEY")
    zhipu_default_model: str = Field(default="glm-4", env="ZHIPU_DEFAULT_MODEL")
    
    # 支持的智谱AI模型列表
    supported_models: List[str] = [
        "glm-4-flash",
        "glm-4",
        "glm-4-plus",
        "glm-4-5",
        "glm-4-6"
    ]
    
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
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
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
    
    # 智谱AI Embedding配置
    embedding_model: str = Field(default="embedding-3", description="Embedding模型")
    embedding_dimension: int = Field(default=1024, description="向量维度")
    
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

