#!/usr/bin/env python3
"""Direct test of novel service"""

import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.services.novel_service import NovelService


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = NovelService(session)
        result = await service.list_novels()
        print("Result:", result)


if __name__ == "__main__":
    asyncio.run(main())

