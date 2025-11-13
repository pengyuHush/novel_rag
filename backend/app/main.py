"""
网络小说智能问答系统 - FastAPI Main Application
Created: 2025-11-13
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.db.init_db import init_database, check_database_initialized
from app.core.chromadb_client import get_chroma_client
from app.api import health

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

# 应用元数据
APP_NAME = settings.app_name
APP_VERSION = settings.app_version
APP_DESCRIPTION = """
## 网络小说智能问答系统

基于RAG（Retrieval-Augmented Generation）架构的网络小说智能问答系统。

### 核心功能

- 📚 **小说管理**: 支持TXT/EPUB格式上传，自动解析章节
- 🤖 **智能问答**: 基于GraphRAG和Self-RAG的高准确率问答
- 📖 **在线阅读**: 分章节浏览，支持10万字超长章节
- 🕸️ **知识图谱**: 角色关系自动提取，时序演变分析
- 🎭 **诡计识别**: 检测叙述诡计、矛盾信息
- 📊 **可视化**: 角色关系图、时间线可视化
- 💰 **成本控制**: Token统计、多模型切换

### 技术栈

- **后端**: FastAPI + Python 3.12
- **AI**: 智谱AI (GLM-4系列 + Embedding-3)
- **向量库**: ChromaDB
- **图谱**: NetworkX
- **NLP**: HanLP

### 文档

- API文档: `/docs`
- 备选文档: `/redoc`
- 健康检查: `/health`
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info(f"🚀 {APP_NAME} v{APP_VERSION} 启动中...")
    
    try:
        # 确保数据目录存在
        settings.ensure_directories()
        
        # 初始化数据库
        if not check_database_initialized():
            logger.info("📊 初始化数据库...")
            init_database()
        else:
            logger.info("✅ 数据库已初始化")
        
        # 初始化ChromaDB客户端
        logger.info("🔍 初始化ChromaDB...")
        chroma_client = get_chroma_client()
        collections = chroma_client.list_collections()
        logger.info(f"✅ ChromaDB已就绪 ({len(collections)} 个集合)")
        
        # 检查智谱AI配置
        if settings.zhipu_api_key == "your_zhipuai_api_key_here":
            logger.warning("⚠️ 智谱AI API Key未配置，请编辑.env文件")
        else:
            logger.info("✅ 智谱AI已配置")
        
        logger.info(f"✅ {APP_NAME} 启动完成!")
        logger.info(f"📖 API文档: http://localhost:{settings.port}/docs")
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info(f"👋 {APP_NAME} 关闭中...")
    logger.info("✅ 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # OpenAPI配置
    openapi_tags=[
        {
            "name": "健康检查",
            "description": "服务健康状态检查"
        },
        {
            "name": "小说管理",
            "description": "小说上传、列表、详情、删除"
        },
        {
            "name": "智能问答",
            "description": "RAG问答、流式响应"
        },
        {
            "name": "章节管理",
            "description": "章节列表、内容获取"
        },
        {
            "name": "知识图谱",
            "description": "关系图、时间线"
        },
        {
            "name": "统计分析",
            "description": "Token统计、性能指标"
        }
    ]
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(health.router)

# 导入并注册novels路由
from app.api import novels
app.include_router(novels.router)

# 导入并注册query路由
from app.api import query
app.include_router(query.router)

# 根端点
@app.get("/", tags=["基本信息"])
async def root():
    """
    根端点
    
    返回应用基本信息和快速导航链接
    """
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "description": "网络小说智能问答系统",
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "health_detailed": "/health/detailed"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

