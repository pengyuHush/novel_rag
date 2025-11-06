#!/usr/bin/env python3
"""Reset database - delete and recreate"""

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.db.session import init_db


async def main():
    db_path = Path("novel_rag.db")
    
    if db_path.exists():
        print(f"Deleting existing database: {db_path}")
        try:
            db_path.unlink()
            print("Database deleted successfully")
        except Exception as e:
            print(f"Warning: Could not delete database: {e}")
            print("Please stop uvicorn first")
            return 1
    
    print("Creating new database...")
    await init_db()
    print("Database created successfully!")
    print("")
    print("You can now start uvicorn:")
    print("  poetry run uvicorn app.main:app --reload --port 8000")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

