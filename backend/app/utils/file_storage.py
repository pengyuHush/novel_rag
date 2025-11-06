"""Helpers for storing uploaded novel files."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import UploadFile

STORAGE_ROOT = Path("storage/novels")


def ensure_storage_root() -> Path:
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    return STORAGE_ROOT


def novel_file_path(novel_id: str, suffix: str = ".txt") -> Path:
    root = ensure_storage_root()
    return root / f"{novel_id}{suffix}"


async def save_upload_file(novel_id: str, upload_file: UploadFile) -> Path:
    data = await upload_file.read()
    path = novel_file_path(novel_id, suffix=Path(upload_file.filename or "").suffix or ".txt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def delete_novel_file(novel_id: str) -> None:
    for path in STORAGE_ROOT.glob(f"{novel_id}.*"):
        try:
            path.unlink()
        except FileNotFoundError:
            continue


__all__ = ["save_upload_file", "novel_file_path", "delete_novel_file", "STORAGE_ROOT"]

