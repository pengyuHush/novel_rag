"""Test schema serialization with camelCase aliases."""

import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from app.schemas.novel import NovelSummary

# Create a test novel
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

# Serialize with aliases (camelCase)
print("✅ Schema serialization test:")
print(novel.model_dump(by_alias=True, mode="json"))

