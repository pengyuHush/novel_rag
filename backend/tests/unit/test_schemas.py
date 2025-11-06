"""测试Schema序列化和验证."""

import pytest
from datetime import datetime

from app.schemas.novel import NovelSummary, NovelCreate, NovelUpdate
from app.schemas.chapter import ChapterResponse
from app.schemas.search import SearchRequest, SearchResponse


@pytest.mark.unit
class TestNovelSchemas:
    """测试小说相关Schema."""

    def test_novel_summary_serialization(self):
        """测试小说摘要序列化（camelCase）."""
        novel = NovelSummary(
            id="test123",
            title="测试小说",
            author="测试作者",
            description="测试描述",
            tags=["tag1", "tag2"],
            word_count=10000,
            chapter_count=10,
            status="completed",
            has_graph=True,
            processing_progress=1.0,
            processing_message="完成",
            imported_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 使用别名序列化（camelCase）
        data = novel.model_dump(by_alias=True, mode="json")

        # 验证camelCase字段名
        assert "wordCount" in data
        assert "chapterCount" in data
        assert "hasGraph" in data
        assert "processingProgress" in data
        assert "processingMessage" in data
        assert "importedAt" in data
        assert "updatedAt" in data

        # 验证值
        assert data["title"] == "测试小说"
        assert data["wordCount"] == 10000
        assert data["chapterCount"] == 10

    def test_novel_create_validation(self):
        """测试创建小说数据验证."""
        # 有效数据
        valid_data = {
            "title": "测试小说",
            "author": "测试作者",
            "description": "测试描述",
            "tags": ["测试"],
        }
        novel = NovelCreate(**valid_data)
        assert novel.title == "测试小说"

        # 无效数据 - 缺少必填字段
        with pytest.raises(Exception):
            NovelCreate(author="测试作者")  # 缺少title

    def test_novel_update_partial(self):
        """测试部分更新小说数据."""
        # 只更新部分字段
        update_data = {
            "description": "新的描述",
        }
        novel_update = NovelUpdate(**update_data)
        assert novel_update.description == "新的描述"
        assert novel_update.title is None  # 未设置的字段为None


@pytest.mark.unit
class TestChapterSchemas:
    """测试章节相关Schema."""

    def test_chapter_response_serialization(self):
        """测试章节响应序列化."""
        chapter = ChapterResponse(
            id="chapter123",
            novel_id="novel123",
            chapter_number=1,
            title="第一章",
            start_position=0,
            end_position=1000,
            word_count=1000,
        )

        data = chapter.model_dump(by_alias=True, mode="json")

        # 验证camelCase字段名
        assert "novelId" in data
        assert "chapterNumber" in data
        assert "startPosition" in data
        assert "endPosition" in data
        assert "wordCount" in data


@pytest.mark.unit
class TestSearchSchemas:
    """测试搜索相关Schema."""

    def test_search_request_validation(self):
        """测试搜索请求验证."""
        # 有效请求
        request = SearchRequest(
            query="主角是谁？",
            top_k=5,
            include_references=True,
        )
        assert request.query == "主角是谁？"
        assert request.top_k == 5

        # 验证默认值
        request2 = SearchRequest(query="测试")
        assert request2.top_k == 5  # 默认值
        assert request2.include_references is True  # 默认值

    def test_search_response_serialization(self):
        """测试搜索响应序列化."""
        response = SearchResponse(
            query="测试查询",
            answer="测试答案",
            references=[],
            elapsed=1.23,
        )

        data = response.model_dump(by_alias=True, mode="json")
        assert data["query"] == "测试查询"
        assert data["answer"] == "测试答案"
        assert data["elapsed"] == 1.23

