"""
数据库初始化脚本
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging

from app.models.database import Base
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """获取数据库URL"""
    db_url = settings.database_url
    # 确保SQLite数据库目录存在
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return db_url


def init_database():
    """初始化数据库"""
    try:
        # 创建引擎
        engine = create_engine(
            get_database_url(),
            echo=settings.debug,
            connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ 数据库初始化成功")
        logger.info(f"📍 数据库位置: {get_database_url()}")
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


def get_db_session():
    """获取数据库会话（用于依赖注入）"""
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_initialized() -> bool:
    """检查数据库是否已初始化"""
    try:
        engine = create_engine(get_database_url())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM schema_version LIMIT 1"))
            version = result.scalar()
            if version:
                logger.info(f"✅ 数据库已初始化 (版本: {version})")
                return True
            return False
    except Exception:
        return False


def reset_database():
    """重置数据库（仅用于开发/测试）"""
    if not settings.debug:
        raise RuntimeError("重置数据库仅允许在DEBUG模式下执行")
    
    logger.warning("⚠️ 正在重置数据库...")
    
    engine = create_engine(get_database_url())
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ 数据库已重置")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 初始化数据库
    init_database()

