"""重新处理状态为failed的小说."""

import asyncio
from pathlib import Path

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Novel
from app.services.text_processing_service import TextProcessingService


async def reprocess_failed_novels():
    """重新处理所有失败的小说."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # 查找所有失败的小说
        result = await session.execute(select(Novel).where(Novel.processing_status == "failed"))
        failed_novels = result.scalars().all()

        if not failed_novels:
            logger.info("没有找到失败的小说")
            return

        logger.info(f"找到 {len(failed_novels)} 本失败的小说")

        for novel in failed_novels:
            logger.info(f"开始重新处理小说: {novel.id} - {novel.title}")

            # 检查文件是否存在
            if not novel.file_path:
                logger.warning(f"小说 {novel.id} 没有file_path，跳过")
                continue

            file_path = Path(novel.file_path)
            if not file_path.exists():
                logger.warning(f"小说 {novel.id} 的文件不存在: {file_path}，跳过")
                continue

            try:
                # 重置状态
                novel.processing_status = "pending"
                novel.processing_error = None
                novel.processing_progress = 0.0
                novel.processing_message = "等待重新处理"
                await session.commit()

                logger.info(f"文件路径: {file_path}")

                # 创建新的session来处理
                async with AsyncSessionLocal() as process_session:
                    text_service = TextProcessingService(process_session)

                    # 定义进度回调
                    async def progress_callback(progress: float, message: str):
                        logger.info(f"[{novel.id}] {progress*100:.1f}% - {message}")

                    # 重新处理
                    await text_service.process_novel(novel.id, file_path, progress_callback)

                logger.info(f"✅ 小说 {novel.id} - {novel.title} 重新处理成功")

            except Exception as e:
                logger.exception(f"❌ 小说 {novel.id} - {novel.title} 重新处理失败: {e}")

                # 更新失败状态
                async with AsyncSessionLocal() as error_session:
                    result = await error_session.execute(select(Novel).where(Novel.id == novel.id))
                    novel_to_update = result.scalar_one_or_none()
                    if novel_to_update:
                        novel_to_update.processing_status = "failed"
                        novel_to_update.processing_error = str(e)
                        await error_session.commit()

    await engine.dispose()


async def reprocess_single_novel(novel_id: str):
    """重新处理单个小说."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Novel).where(Novel.id == novel_id))
        novel = result.scalar_one_or_none()

        if not novel:
            logger.error(f"小说 {novel_id} 不存在")
            return

        logger.info(f"小说信息: {novel.title}, 状态: {novel.processing_status}")

        if not novel.file_path:
            logger.error(f"小说 {novel_id} 没有file_path")
            return

        file_path = Path(novel.file_path)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return

        try:
            # 重置状态
            novel.processing_status = "pending"
            novel.processing_error = None
            novel.processing_progress = 0.0
            novel.processing_message = "等待重新处理"
            await session.commit()

            logger.info(f"开始重新处理小说: {novel_id} - {novel.title}")

            # 创建新的session来处理
            async with AsyncSessionLocal() as process_session:
                text_service = TextProcessingService(process_session)

                # 定义进度回调
                async def progress_callback(progress: float, message: str):
                    logger.info(f"[{novel.id}] {progress*100:.1f}% - {message}")

                # 重新处理
                await text_service.process_novel(novel.id, file_path, progress_callback)

            logger.info(f"✅ 小说 {novel_id} - {novel.title} 重新处理成功")

        except Exception as e:
            logger.exception(f"❌ 小说 {novel_id} - {novel.title} 重新处理失败: {e}")

    await engine.dispose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        novel_id = sys.argv[1]
        logger.info(f"重新处理单个小说: {novel_id}")
        asyncio.run(reprocess_single_novel(novel_id))
    else:
        logger.info("重新处理所有失败的小说")
        asyncio.run(reprocess_failed_novels())

