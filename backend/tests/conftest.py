"""Pytest 全局配置和共享 fixtures."""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 设置 UTF-8 输出（Windows兼容）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.base import Base
from app.main import app


# ============================================================================
# 事件循环 Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环（会话级别）."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# 数据库 Fixtures
# ============================================================================

@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎（会话级别）."""
    # 使用内存数据库进行测试
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话（函数级别）."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()  # 每个测试后回滚


# ============================================================================
# API 客户端 Fixtures
# ============================================================================

@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    """创建 API 测试客户端."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Mock 服务 Fixtures
# ============================================================================

@pytest.fixture
def mock_zhipu_client(monkeypatch):
    """Mock 智谱AI客户端."""
    class MockZhipuClient:
        """模拟智谱AI客户端."""
        
        class Embeddings:
            def create(self, model: str, input: str | list[str], **kwargs):
                # 返回模拟的embedding
                if isinstance(input, str):
                    inputs = [input]
                else:
                    inputs = input
                
                class Response:
                    data = [type('obj', (), {'embedding': [0.1] * 1024}) for _ in inputs]
                
                return Response()
        
        class Chat:
            class Completions:
                def create(self, model: str, messages: list, **kwargs):
                    # 返回模拟的聊天响应
                    class Response:
                        class Choice:
                            class Message:
                                content = "这是一个模拟的回答。"
                            message = Message()
                        choices = [Choice()]
                    
                    return Response()
            
            completions = Completions()
        
        embeddings = Embeddings()
        chat = Chat()
    
    return MockZhipuClient()


@pytest.fixture
def mock_qdrant_client(monkeypatch):
    """Mock Qdrant客户端."""
    class MockQdrantClient:
        """模拟Qdrant客户端."""
        
        def search(self, collection_name: str, query_vector: list, limit: int = 5, **kwargs):
            # 返回模拟的搜索结果
            return []
        
        def upsert(self, collection_name: str, points: list, **kwargs):
            # 模拟插入操作
            return {"status": "ok"}
        
        def create_collection(self, collection_name: str, vectors_config: dict, **kwargs):
            # 模拟创建集合
            return {"status": "ok"}
        
        def collection_exists(self, collection_name: str) -> bool:
            # 假设集合总是存在
            return True
    
    return MockQdrantClient()


# ============================================================================
# 测试数据 Fixtures
# ============================================================================

@pytest.fixture
def sample_novel_data() -> dict:
    """示例小说数据."""
    return {
        "title": "测试小说",
        "author": "测试作者",
        "description": "这是一个测试小说的描述",
        "tags": ["测试", "示例"],
    }


@pytest.fixture
def sample_novel_content() -> str:
    """示例小说内容."""
    return """第一章 开始

这是第一章的内容。主人公在这里开始了他的冒险之旅。
他遇到了很多困难，但最终克服了所有障碍。

第二章 冒险

在这一章中，主人公继续前进，遇到了更多的挑战。
他结识了新的朋友，也遭遇了强大的敌人。

第三章 结束

最终，主人公完成了他的使命，获得了成长。
这段旅程改变了他的一生。
"""


@pytest.fixture
def sample_chapters() -> list[dict]:
    """示例章节数据."""
    return [
        {
            "chapter_number": 1,
            "title": "第一章 开始",
            "start_position": 0,
            "end_position": 100,
            "word_count": 100,
        },
        {
            "chapter_number": 2,
            "title": "第二章 冒险",
            "start_position": 100,
            "end_position": 200,
            "word_count": 100,
        },
        {
            "chapter_number": 3,
            "title": "第三章 结束",
            "start_position": 200,
            "end_position": 300,
            "word_count": 100,
        },
    ]


# ============================================================================
# 环境配置 Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_settings():
    """每个测试前重置配置（自动使用）."""
    # 可以在这里设置测试环境的特殊配置
    yield
    # 测试后恢复


# ============================================================================
# 测试报告增强
# ============================================================================

def pytest_configure(config):
    """Pytest 配置钩子."""
    config.addinivalue_line(
        "markers", "asyncio: 标记为异步测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项集合."""
    for item in items:
        # 为所有异步测试添加 asyncio 标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

