"""测试Repository层."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.novel_repository import NovelRepository
from app.repositories.chapter_repository import ChapterRepository
from app.models.novel import Novel
from app.models.chapter import Chapter
from tests.helpers import NovelFactory, ChapterFactory


@pytest.mark.unit
class TestNovelRepository:
    """测试小说Repository."""

    async def test_create_novel(self, db_session: AsyncSession):
        """测试创建小说."""
        repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()

        novel = Novel(**novel_data)
        created = await repo.create(novel)

        assert created.id is not None
        assert created.title == novel_data["title"]
        assert created.author == novel_data["author"]

    async def test_get_novel_by_id(self, db_session: AsyncSession):
        """测试根据ID获取小说."""
        repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()

        # 创建小说
        novel = Novel(**novel_data)
        created = await repo.create(novel)

        # 获取小说
        retrieved = await repo.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == created.title

    async def test_list_novels(self, db_session: AsyncSession):
        """测试列出小说."""
        repo = NovelRepository(db_session)

        # 创建多个小说
        for _ in range(3):
            novel_data = NovelFactory.create_novel_data()
            novel = Novel(**novel_data)
            await repo.create(novel)

        # 列出小说
        novels, total = await repo.list(page=1, size=10)
        assert len(novels) == 3
        assert total == 3

    async def test_update_novel(self, db_session: AsyncSession):
        """测试更新小说."""
        repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()

        # 创建小说
        novel = Novel(**novel_data)
        created = await repo.create(novel)

        # 更新小说
        created.description = "新的描述"
        updated = await repo.update(created)

        assert updated.description == "新的描述"

    async def test_delete_novel(self, db_session: AsyncSession):
        """测试删除小说."""
        repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()

        # 创建小说
        novel = Novel(**novel_data)
        created = await repo.create(novel)

        # 删除小说
        deleted = await repo.delete(created.id)
        assert deleted is True

        # 验证已删除
        retrieved = await repo.get_by_id(created.id)
        assert retrieved is None


@pytest.mark.unit
class TestChapterRepository:
    """测试章节Repository."""

    async def test_create_chapter(self, db_session: AsyncSession):
        """测试创建章节."""
        # 先创建小说
        novel_repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()
        novel = Novel(**novel_data)
        created_novel = await novel_repo.create(novel)

        # 创建章节
        chapter_repo = ChapterRepository(db_session)
        chapter_data = ChapterFactory.create_chapter_data(novel_id=created_novel.id)
        chapter = Chapter(**chapter_data)
        created = await chapter_repo.create(chapter)

        assert created.id is not None
        assert created.novel_id == created_novel.id
        assert created.chapter_number == chapter_data["chapter_number"]

    async def test_list_chapters_by_novel(self, db_session: AsyncSession):
        """测试列出小说的所有章节."""
        # 创建小说和章节
        novel_repo = NovelRepository(db_session)
        novel_data = NovelFactory.create_novel_data()
        novel = Novel(**novel_data)
        created_novel = await novel_repo.create(novel)

        chapter_repo = ChapterRepository(db_session)
        for i in range(1, 4):
            chapter_data = ChapterFactory.create_chapter_data(
                novel_id=created_novel.id,
                chapter_number=i,
            )
            chapter = Chapter(**chapter_data)
            await chapter_repo.create(chapter)

        # 列出章节
        chapters = await chapter_repo.list_by_novel(created_novel.id)
        assert len(chapters) == 3
        assert chapters[0].chapter_number == 1
        assert chapters[2].chapter_number == 3

