"""测试工具函数."""

import pytest
from pathlib import Path

from app.utils.text_processing import (
    detect_encoding,
    extract_chapters,
    count_chinese_chars,
)
from app.utils.hashing import generate_hash
from tests.helpers.utils import create_test_file, cleanup_test_files


@pytest.mark.unit
class TestTextProcessing:
    """测试文本处理工具."""

    def test_detect_encoding_utf8(self):
        """测试UTF-8编码检测."""
        content = "这是一段UTF-8编码的中文文本。"
        file_path = create_test_file(content, encoding="utf-8")

        try:
            detected = detect_encoding(file_path)
            assert detected.lower() in ["utf-8", "utf8"]
        finally:
            cleanup_test_files(file_path)

    def test_extract_chapters(self):
        """测试章节提取."""
        content = """第一章 开始

这是第一章的内容。

第二章 继续

这是第二章的内容。

第三章 结束

这是第三章的内容。
"""
        chapters = extract_chapters(content)
        assert len(chapters) >= 3
        assert chapters[0]["chapter_number"] == 1
        assert "开始" in chapters[0]["title"]

    def test_count_chinese_chars(self):
        """测试中文字符计数."""
        text = "这是中文abc123！@#"
        count = count_chinese_chars(text)
        assert count == 4  # "这是中文"

    def test_count_chinese_chars_empty(self):
        """测试空文本字符计数."""
        count = count_chinese_chars("")
        assert count == 0


@pytest.mark.unit
class TestHashing:
    """测试哈希工具."""

    def test_generate_hash_consistency(self):
        """测试哈希一致性."""
        content = "测试内容"
        hash1 = generate_hash(content)
        hash2 = generate_hash(content)
        assert hash1 == hash2

    def test_generate_hash_uniqueness(self):
        """测试哈希唯一性."""
        hash1 = generate_hash("内容1")
        hash2 = generate_hash("内容2")
        assert hash1 != hash2

    def test_generate_hash_length(self):
        """测试哈希长度."""
        content = "任意内容"
        hash_value = generate_hash(content)
        assert len(hash_value) == 32  # MD5 哈希为32个字符

