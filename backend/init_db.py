#!/usr/bin/env python3
"""初始化数据库表"""

import asyncio
import sys

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.db.session import init_db


async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())

