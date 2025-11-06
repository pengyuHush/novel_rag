"""端到端API测试."""

import pytest
from httpx import AsyncClient

from tests.helpers import NovelFactory, assert_response_success, assert_pagination


@pytest.mark.e2e
class TestHealthAndSystemEndpoints:
    """测试健康检查和系统信息端点."""

    async def test_health_check(self, api_client: AsyncClient):
        """测试健康检查端点."""
        response = await api_client.get("/api/v1/system/health")
        assert_response_success(response, 200)

        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "components" in data

        # 检查各个组件状态
        components = data["components"]
        assert "database" in components
        assert "redis" in components
        assert "qdrant" in components

    async def test_system_info(self, api_client: AsyncClient):
        """测试系统信息端点."""
        response = await api_client.get("/api/v1/system/info")
        assert_response_success(response, 200)

        data = response.json()
        assert "project_name" in data
        assert "version" in data
        assert "features" in data
        assert isinstance(data["features"], dict)


@pytest.mark.e2e
class TestNovelCRUDEndpoints:
    """测试小说CRUD端点."""

    async def test_create_novel(self, api_client: AsyncClient):
        """测试创建小说."""
        novel_data = NovelFactory.create_novel_data()

        response = await api_client.post("/api/v1/novels", json=novel_data)
        assert_response_success(response, 201)

        data = response.json()
        assert "id" in data
        assert data["title"] == novel_data["title"]
        assert data["author"] == novel_data["author"]

        return data["id"]

    async def test_get_novel(self, api_client: AsyncClient):
        """测试获取单个小说."""
        # 先创建小说
        novel_id = await self.test_create_novel(api_client)

        # 获取小说
        response = await api_client.get(f"/api/v1/novels/{novel_id}")
        assert_response_success(response, 200)

        data = response.json()
        assert data["id"] == novel_id

    async def test_list_novels(self, api_client: AsyncClient):
        """测试列出小说."""
        # 创建几个小说
        for _ in range(3):
            await self.test_create_novel(api_client)

        # 列出小说
        response = await api_client.get("/api/v1/novels")
        assert_response_success(response, 200)

        data = response.json()
        assert "data" in data
        assert_pagination(data, expected_page=1, expected_size=10)
        assert data["pagination"]["total"] >= 3

    async def test_update_novel(self, api_client: AsyncClient):
        """测试更新小说."""
        # 先创建小说
        novel_id = await self.test_create_novel(api_client)

        # 更新小说
        update_data = {"description": "更新后的描述"}
        response = await api_client.put(f"/api/v1/novels/{novel_id}", json=update_data)
        assert_response_success(response, 200)

        data = response.json()
        assert data["description"] == "更新后的描述"

    async def test_delete_novel(self, api_client: AsyncClient):
        """测试删除小说."""
        # 先创建小说
        novel_id = await self.test_create_novel(api_client)

        # 删除小说
        response = await api_client.delete(f"/api/v1/novels/{novel_id}")
        assert_response_success(response, 200)

        # 验证已删除
        response = await api_client.get(f"/api/v1/novels/{novel_id}")
        assert response.status_code == 404


@pytest.mark.e2e
@pytest.mark.external
class TestSearchEndpoints:
    """测试RAG搜索端点."""

    @pytest.mark.slow
    async def test_search_without_data(self, api_client: AsyncClient):
        """测试空数据搜索."""
        search_data = {
            "query": "主角是谁？",
            "top_k": 5,
            "include_references": True,
        }

        response = await api_client.post("/api/v1/search", json=search_data)

        # 可能成功返回空结果，也可能因未配置API而失败
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "answer" in data
            assert "references" in data
        else:
            # 如果GLM API未配置，这是预期的
            assert response.status_code in [400, 500]


@pytest.mark.e2e
class TestChapterEndpoints:
    """测试章节端点."""

    async def test_list_chapters(self, api_client: AsyncClient):
        """测试列出小说章节."""
        # 先创建小说
        novel_data = NovelFactory.create_novel_data()
        response = await api_client.post("/api/v1/novels", json=novel_data)
        novel_id = response.json()["id"]

        # 列出章节（新创建的小说可能还没有章节）
        response = await api_client.get(f"/api/v1/novels/{novel_id}/chapters")
        assert_response_success(response, 200)

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)


@pytest.mark.e2e
class TestCompleteWorkflow:
    """测试完整工作流程."""

    @pytest.mark.slow
    async def test_full_novel_workflow(self, api_client: AsyncClient):
        """测试完整的小说处理流程."""
        # 1. 创建小说
        novel_data = NovelFactory.create_novel_data()
        response = await api_client.post("/api/v1/novels", json=novel_data)
        assert_response_success(response, 201)
        novel_id = response.json()["id"]

        # 2. 获取小说详情
        response = await api_client.get(f"/api/v1/novels/{novel_id}")
        assert_response_success(response, 200)

        # 3. 列出章节
        response = await api_client.get(f"/api/v1/novels/{novel_id}/chapters")
        assert_response_success(response, 200)

        # 4. 更新小说
        response = await api_client.put(
            f"/api/v1/novels/{novel_id}",
            json={"description": "工作流测试"},
        )
        assert_response_success(response, 200)

        # 5. 删除小说
        response = await api_client.delete(f"/api/v1/novels/{novel_id}")
        assert_response_success(response, 200)

