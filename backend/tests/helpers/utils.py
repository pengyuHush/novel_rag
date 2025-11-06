"""测试工具函数."""

import tempfile
from pathlib import Path
from typing import Optional


def create_test_file(
    content: str,
    suffix: str = ".txt",
    encoding: str = "utf-8",
) -> Path:
    """创建临时测试文件.

    Args:
        content: 文件内容
        suffix: 文件后缀
        encoding: 文件编码

    Returns:
        临时文件路径
    """
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding=encoding,
        suffix=suffix,
        delete=False,
    )
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def cleanup_test_files(*file_paths: Path):
    """清理测试文件.

    Args:
        file_paths: 要删除的文件路径列表
    """
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def create_mock_novel_file(
    chapters: int = 3,
    words_per_chapter: int = 500,
    encoding: str = "utf-8",
) -> Path:
    """创建模拟小说文件.

    Args:
        chapters: 章节数
        words_per_chapter: 每章字数
        encoding: 文件编码

    Returns:
        临时文件路径
    """
    content_parts = []
    for i in range(1, chapters + 1):
        chapter_title = f"第{i}章 测试章节{i}"
        chapter_content = "测试内容。" * (words_per_chapter // 5)
        content_parts.append(f"{chapter_title}\n\n{chapter_content}\n\n")

    content = "\n".join(content_parts)
    return create_test_file(content, suffix=".txt", encoding=encoding)


async def wait_for_processing(
    get_status_func,
    novel_id: str,
    timeout: int = 30,
    interval: float = 0.5,
):
    """等待处理完成.

    Args:
        get_status_func: 获取处理状态的异步函数
        novel_id: 小说ID
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）

    Raises:
        TimeoutError: 处理超时
    """
    import asyncio

    elapsed = 0
    while elapsed < timeout:
        status = await get_status_func(novel_id)
        if status in ["completed", "failed"]:
            return status
        await asyncio.sleep(interval)
        elapsed += interval

    raise TimeoutError(f"处理超时: {timeout}秒")

