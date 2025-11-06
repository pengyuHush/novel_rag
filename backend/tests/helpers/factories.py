"""测试数据工厂."""

import uuid
from datetime import datetime
from typing import Optional

from faker import Faker

fake = Faker("zh_CN")


class NovelFactory:
    """小说数据工厂."""

    @staticmethod
    def create_novel_data(
        title: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """创建小说数据字典."""
        return {
            "title": title or fake.sentence(nb_words=4),
            "author": author or fake.name(),
            "description": description or fake.text(max_nb_chars=200),
            "tags": tags or [fake.word() for _ in range(3)],
        }

    @staticmethod
    def create_novel_content(chapters: int = 3, words_per_chapter: int = 500) -> str:
        """创建小说内容文本."""
        content_parts = []
        for i in range(1, chapters + 1):
            chapter_title = f"第{i}章 {fake.sentence(nb_words=3)}"
            chapter_content = "\n\n".join(
                [fake.text(max_nb_chars=words_per_chapter // 5) for _ in range(5)]
            )
            content_parts.append(f"{chapter_title}\n\n{chapter_content}\n\n")
        return "\n".join(content_parts)


class ChapterFactory:
    """章节数据工厂."""

    @staticmethod
    def create_chapter_data(
        novel_id: Optional[str] = None,
        chapter_number: int = 1,
        title: Optional[str] = None,
        start_position: int = 0,
        end_position: int = 1000,
    ) -> dict:
        """创建章节数据字典."""
        return {
            "novel_id": novel_id or str(uuid.uuid4()),
            "chapter_number": chapter_number,
            "title": title or f"第{chapter_number}章 {fake.sentence(nb_words=3)}",
            "start_position": start_position,
            "end_position": end_position,
            "word_count": end_position - start_position,
        }


class GraphFactory:
    """关系图数据工厂."""

    @staticmethod
    def create_character_data(name: Optional[str] = None) -> dict:
        """创建角色数据."""
        return {
            "name": name or fake.name(),
            "description": fake.text(max_nb_chars=100),
            "importance": fake.random_int(min=1, max=10),
        }

    @staticmethod
    def create_relationship_data(
        source: str,
        target: str,
        relation_type: str = "认识",
    ) -> dict:
        """创建关系数据."""
        return {
            "source": source,
            "target": target,
            "type": relation_type,
            "description": fake.text(max_nb_chars=50),
        }


class SearchFactory:
    """搜索数据工厂."""

    @staticmethod
    def create_search_query(query: Optional[str] = None) -> dict:
        """创建搜索请求数据."""
        return {
            "query": query or fake.sentence(nb_words=5),
            "top_k": 5,
            "include_references": True,
        }

    @staticmethod
    def create_search_result(query: str) -> dict:
        """创建搜索结果数据."""
        return {
            "query": query,
            "answer": fake.text(max_nb_chars=200),
            "references": [
                {
                    "novel_id": str(uuid.uuid4()),
                    "novel_title": fake.sentence(nb_words=4),
                    "chapter_number": fake.random_int(min=1, max=100),
                    "chapter_title": f"第{fake.random_int(min=1, max=100)}章",
                    "content": fake.text(max_nb_chars=200),
                    "score": fake.pyfloat(min_value=0.5, max_value=1.0),
                }
                for _ in range(3)
            ],
            "elapsed": fake.pyfloat(min_value=0.1, max_value=5.0),
        }

