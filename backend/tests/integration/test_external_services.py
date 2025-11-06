"""测试外部服务集成."""

import pytest
import asyncio

from app.core.config import settings
from zai import ZhipuAiClient


@pytest.mark.integration
@pytest.mark.external
class TestZhipuAIService:
    """测试智谱AI服务连接性."""

    @pytest.fixture(autouse=True)
    def skip_if_no_api_key(self):
        """如果没有配置API Key则跳过测试."""
        api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        if not api_key:
            pytest.skip("未配置智谱AI API Key")

    async def test_api_key_configuration(self):
        """测试API Key配置."""
        api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        assert api_key is not None
        assert len(api_key) > 0

    @pytest.mark.slow
    async def test_embedding_api(self):
        """测试Embedding API."""
        api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        client = ZhipuAiClient(api_key=api_key)

        test_text = "这是一个测试文本"

        response = await asyncio.to_thread(
            client.embeddings.create,
            model="embedding-3",
            input=test_text,
        )

        assert response.data is not None
        embedding = response.data[0].embedding
        assert len(embedding) == 1024  # embedding-3 维度
        assert all(isinstance(x, float) for x in embedding[:5])

    @pytest.mark.slow
    async def test_chat_api(self):
        """测试Chat API."""
        api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
        client = ZhipuAiClient(api_key=api_key)

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="glm-4-plus",
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
        )

        assert response.choices is not None
        answer = response.choices[0].message.content
        assert len(answer) > 0

    @pytest.mark.slow
    async def test_api_error_handling(self):
        """测试API错误处理."""
        # 使用无效的API Key
        client = ZhipuAiClient(api_key="invalid_key")

        with pytest.raises(Exception):
            await asyncio.to_thread(
                client.embeddings.create,
                model="embedding-3",
                input="测试",
            )


@pytest.mark.integration
class TestQdrantService:
    """测试Qdrant向量数据库服务."""

    @pytest.mark.skip_ci
    async def test_qdrant_connection(self):
        """测试Qdrant连接（需要运行Qdrant服务）."""
        from app.core.qdrant import get_qdrant_client

        client = get_qdrant_client()
        # 简单的连接测试
        # 如果连接失败会抛出异常
        assert client is not None

    @pytest.mark.skip_ci
    async def test_qdrant_collection_operations(self):
        """测试Qdrant集合操作."""
        from app.core.qdrant import get_qdrant_client

        client = get_qdrant_client()
        collection_name = "test_collection"

        # 测试集合是否存在
        # 这里只是示例，实际测试需要更多逻辑
        exists = client.collection_exists(collection_name)
        assert isinstance(exists, bool)

