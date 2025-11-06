"""Test listing novels from database."""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from app.db.session import get_db_session
from app.repositories.novel_repository import NovelRepository


async def main():
    session_gen = get_db_session()
    session = await anext(session_gen)
    try:
        repo = NovelRepository(session)
        novels, _ = await repo.list()
        print(f"Found {len(novels)} novels in database")
        for novel in novels:
            print(f"  - {novel.title} (ID: {novel.id})")
    finally:
        try:
            await anext(session_gen)
        except StopAsyncIteration:
            pass


if __name__ == "__main__":
    asyncio.run(main())

