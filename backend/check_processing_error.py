"""Check the processing error for the failed novel."""

import sys
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

from app.db.session import get_db_session
from app.repositories.novel_repository import NovelRepository


async def main():
    session_gen = get_db_session()
    session = await anext(session_gen)
    try:
        repo = NovelRepository(session)
        novels, _ = await repo.list()
        
        for novel in novels:
            if novel.status == "failed":
                print(f"\n❌ 失败的小说: {novel.title}")
                print(f"   ID: {novel.id}")
                print(f"   状态: {novel.status}")
                print(f"   进度: {novel.processing_progress * 100:.1f}%")
                print(f"   错误消息: {novel.processing_message}")
                print(f"   字数: {novel.word_count}")
                print(f"   章节数: {novel.chapter_count}")
                print(f"   文件路径: {novel.file_path}")
                
        print("\n💡 建议：")
        print("1. 检查 ZHIPU_API_KEY 或 ZAI_API_KEY 是否正确配置")
        print("2. 查看后端日志中的详细错误信息")
        print("3. 尝试重新上传小说文件")
        
    finally:
        try:
            await anext(session_gen)
        except StopAsyncIteration:
            pass


if __name__ == "__main__":
    asyncio.run(main())

