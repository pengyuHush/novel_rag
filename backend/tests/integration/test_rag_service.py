"""测试RAG服务集成."""

import pytest

from app.services.rag_service import RAGService
from app.core.config import settings


@pytest.mark.integration
@pytest.mark.external
class TestRAGService:
    """测试RAG服务（需要智谱AI）."""

    @pytest.fixture(autouse=True)
    def skip_if_no_api_key(self):
        """如果没有配置API Key则跳过测试."""
        if not settings.ZAI_API_KEY and not settings.ZHIPU_API_KEY:
            pytest.skip("未配置智谱AI API Key")

    async def test_embedding_single_text(self):
        """测试单个文本embedding."""
        rag = RAGService()

        if not rag.client:
            pytest.skip("智谱AI客户端未配置")

        test_text = "这是一段测试文本。" * 10  # 100字符左右
        embeddings = await rag.embed_texts([test_text])

        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0  # 向量维度应该大于0
        assert isinstance(embeddings[0][0], float)

    async def test_embedding_long_text(self):
        """测试长文本embedding（接近CHUNK_SIZE限制）."""
        rag = RAGService()

        if not rag.client:
            pytest.skip("智谱AI客户端未配置")

        # 创建接近800字符的文本
        test_text = "这是一段较长的测试文本，用于测试是否能处理接近限制的文本。" * 20
        embeddings = await rag.embed_texts([test_text])

        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0

    async def test_embedding_batch(self):
        """测试批量文本embedding."""
        rag = RAGService()

        if not rag.client:
            pytest.skip("智谱AI客户端未配置")

        # 创建多个测试文本
        test_texts = [f"这是第{i+1}段测试文本。" * 20 for i in range(3)]
        embeddings = await rag.embed_texts(test_texts)

        assert len(embeddings) == len(test_texts)
        for embedding in embeddings:
            assert len(embedding) > 0

    @pytest.mark.slow
    async def test_embedding_realistic_scenario(self):
        """测试真实场景（多个800字符的chunk）."""
        rag = RAGService()

        if not rag.client:
            pytest.skip("智谱AI客户端未配置")

        # 模拟真实的小说chunk
        sample_text = """
        在那个风雨交加的夜晚，主人公终于来到了传说中的古堡前。
        城堡的大门紧闭，四周一片寂静，只有风声和雨声在耳边回荡。
        他深吸一口气，推开了那扇沉重的大门，开始了他的冒险之旅。
        """ * 20  # 约800字符

        test_texts = [sample_text for _ in range(3)]
        embeddings = await rag.embed_texts(test_texts)

        assert len(embeddings) == len(test_texts)
        for embedding in embeddings:
            assert len(embedding) == 1024  # 智谱AI embedding-3 维度为1024


@pytest.mark.integration
class TestRAGServiceWithMock:
    """测试RAG服务（使用Mock）."""

    async def test_search_without_data(self, mock_qdrant_client):
        """测试空数据搜索."""
        rag = RAGService()
        rag.qdrant_client = mock_qdrant_client

        # 搜索应该返回空结果
        results = await rag.search("测试查询", top_k=5)
        assert results == []

    async def test_embed_texts_error_handling(self):
        """测试embedding错误处理."""
        rag = RAGService()
        rag.client = None  # 模拟未配置客户端

        # 应该抛出异常或返回空列表
        with pytest.raises(Exception):
            await rag.embed_texts(["测试文本"])

