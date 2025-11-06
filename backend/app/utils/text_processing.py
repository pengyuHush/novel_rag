"""Text processing helpers for novel content."""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence

CHAPTER_PATTERN = re.compile(r"第[零一二三四五六七八九十百千万两\d]+[章节回节话].*")


def clean_text(text: str) -> str:
    # Normalize line endings and remove trailing spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> List[str]:
    paragraphs = [para.strip() for para in text.split("\n") if para.strip()]
    return paragraphs


def detect_chapters(text: str, pattern: re.Pattern[str] | None = None) -> List[dict]:
    pattern = pattern or CHAPTER_PATTERN
    chapters: List[dict] = []
    matches = list(pattern.finditer(text))
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chapters.append(
            {
                "id": None,
                "number": idx + 1,
                "title": match.group().strip(),
                "start_position": start,
                "end_position": end,
                "word_count": max(0, end - start),
            }
        )

    if not chapters:
        paragraphs = split_paragraphs(text)
        chunk_size = 2000
        for idx, chunk_start in enumerate(range(0, len(paragraphs), chunk_size)):
            chunk_paras = paragraphs[chunk_start : chunk_start + chunk_size]
            start_pos = text.find(chunk_paras[0]) if chunk_paras else 0
            end_pos = start_pos + sum(len(p) for p in chunk_paras)
            chapters.append(
                {
                    "id": None,
                    "number": idx + 1,
                    "title": f"自动分段 {idx + 1}",
                    "start_position": max(0, start_pos),
                    "end_position": min(len(text), end_pos),
                    "word_count": len("".join(chunk_paras)),
                }
            )
    return chapters


def chinese_character_ratio(text: str) -> float:
    if not text:
        return 0.0
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    return chinese_chars / len(text)


def estimate_reading_progress(total: int, current: int) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, current / total))


__all__ = [
    "clean_text",
    "split_paragraphs",
    "detect_chapters",
    "chinese_character_ratio",
    "estimate_reading_progress",
]

