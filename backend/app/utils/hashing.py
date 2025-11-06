"""Hash helpers."""

from __future__ import annotations

import hashlib


def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


__all__ = ["sha256_hash"]

