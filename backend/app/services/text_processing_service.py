"""Text processing service for uploaded novels."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import List

import chardet
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InvalidFileError
from app.models import Chapter, Novel
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.novel_repository import NovelRepository
from app.services.rag_service import ChunkPayload, RAGService
from app.services.metadata_extraction_service import MetadataExtractionService
from app.utils.text_processing import chinese_character_ratio, clean_text, detect_chapters, split_paragraphs


class TextProcessingService:
    """Handle text upload, validation, chunking, and vectorization."""

    def __init__(self, session: AsyncSession, redis_client: Redis | None = None):
        self.session = session
        self.novel_repo = NovelRepository(session)
        self.chapter_repo = ChapterRepository(session)
        self.rag = RAGService(redis_client=redis_client)
        self.metadata_service = MetadataExtractionService()

    async def validate_file(self, file_content: bytes, filename: str) -> dict:
        """Validate uploaded file and return metadata."""
        # File size check
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_content) > max_size:
            raise InvalidFileError(f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE_MB}MB)", "FILE_TOO_LARGE")

        # Format check
        if not filename.lower().endswith(".txt"):
            raise InvalidFileError("只支持 TXT 格式文件", "INVALID_FILE_FORMAT")

        # Encoding detection with fallback
        detected = chardet.detect(file_content)
        detected_encoding = detected["encoding"] or "utf-8"
        confidence = detected["confidence"] or 0.0
        
        logger.debug(f"Detected encoding: {detected_encoding} (confidence: {confidence:.2f})")

        # Build encoding try list based on detection
        # GB2312/GBK/GB18030 are related, try them in order
        if detected_encoding and "gb" in detected_encoding.lower():
            # 中文编码回退链: GB2312 < GBK < GB18030
            encoding_attempts = ["gb18030", "gbk", "gb2312", "utf-8", "utf-16"]
        elif detected_encoding and "utf" in detected_encoding.lower():
            encoding_attempts = ["utf-8", "utf-16", "gb18030", "gbk"]
        else:
            # General fallback order
            encoding_attempts = ["utf-8", "gb18030", "gbk", "gb2312", "utf-16"]
        
        # Always prioritize detected encoding if confidence is high
        if confidence >= 0.7 and detected_encoding:
            encoding_attempts.insert(0, detected_encoding)
        
        # Try encodings in order
        text = None
        successful_encoding = None
        decode_errors = []
        
        for enc in encoding_attempts:
            try:
                text = file_content.decode(enc)
                successful_encoding = enc
                logger.info(f"Successfully decoded with {enc}")
                break
            except (UnicodeDecodeError, LookupError) as e:
                decode_errors.append(f"{enc}: {str(e)[:50]}")
                continue
        
        if text is None:
            error_details = "; ".join(decode_errors[:3])  # Show first 3 errors
            raise InvalidFileError(
                f"无法识别文件编码。尝试了多种编码但都失败: {error_details}",
                "INVALID_ENCODING"
            )
        
        encoding = successful_encoding

        # Content validation
        text = clean_text(text)
        word_count = len(text)

        if word_count < settings.MIN_WORD_COUNT:
            raise InvalidFileError(
                f"文本过短（{word_count}字），至少需要 {settings.MIN_WORD_COUNT} 字",
                "CONTENT_TOO_SHORT",
            )

        cn_ratio = chinese_character_ratio(text)
        if cn_ratio < settings.MIN_CHINESE_RATIO:
            raise InvalidFileError(
                f"中文字符占比过低（{cn_ratio:.1%}），至少需要 {settings.MIN_CHINESE_RATIO:.0%}",
                "INVALID_CONTENT",
            )

        return {
            "encoding": encoding,
            "word_count": word_count,
            "file_size": len(file_content),
            "text": text,
        }

    async def process_novel(self, novel_id: str, file_path: Path, progress_callback=None) -> None:
        """Process uploaded novel: parse, chunk, and index."""
        logger.info(f"Processing novel {novel_id} from {file_path}")
        novel = await self.novel_repo.get(novel_id)
        if not novel:
            raise ValueError(f"Novel {novel_id} not found")

        try:
            novel.mark_processing()
            await self.session.commit()

            # Read file
            file_bytes = file_path.read_bytes()
            validation = await self.validate_file(file_bytes, file_path.name)
            text = validation["text"]
            encoding = validation["encoding"]
            word_count = validation["word_count"]
            file_size = validation["file_size"]

            if progress_callback:
                await progress_callback(0.1, "文本验证完成")

            # Detect chapters
            chapter_dicts = detect_chapters(text)
            if progress_callback:
                await progress_callback(0.2, f"识别到 {len(chapter_dicts)} 个章节")

            # Save chapters to DB
            chapters: List[Chapter] = []
            for ch_data in chapter_dicts:
                chapter = Chapter(
                    novel_id=novel_id,
                    chapter_number=ch_data["number"],
                    title=ch_data["title"],
                    start_position=ch_data["start_position"],
                    end_position=ch_data["end_position"],
                    word_count=ch_data["word_count"],
                )
                chapters.append(chapter)

            await self.chapter_repo.bulk_create(chapters)
            await self.session.flush()

            # Update novel content and stats
            novel.content = text
            await self.novel_repo.update_processing_stats(
                novel,
                word_count=word_count,
                chapter_count=len(chapters),
                encoding=encoding,
                file_size=file_size,
                file_path=str(file_path),
            )
            await self.session.commit()

            if progress_callback:
                await progress_callback(0.4, "章节保存完成，开始向量化")

            # Chunk and vectorize
            await self._vectorize_novel(novel, chapters, text, progress_callback)

            novel.mark_completed()
            await self.session.commit()

            if progress_callback:
                await progress_callback(1.0, "处理完成")

            logger.info(f"Novel {novel_id} processed successfully")

        except Exception as e:
            logger.exception(f"Failed to process novel {novel_id}")
            novel.mark_failed()
            await self.session.commit()
            raise

    async def _vectorize_novel(
        self,
        novel: Novel,
        chapters: List[Chapter],
        text: str,
        progress_callback=None,
    ) -> None:
        """Chunk text and create embeddings."""
        chunk_size = settings.CHUNK_SIZE  # 按字符数
        overlap = settings.CHUNK_OVERLAP  # 重叠字符数

        # 初始化token统计
        total_tokens_used = 0
        total_api_calls = 0

        chunks: List[ChunkPayload] = []
        chunk_texts: List[str] = []

        # 按字符数进行滑动窗口分块
        chunk_idx = 0
        pos = 0
        while pos < len(text):
            # 取出一段文本
            chunk_end = min(pos + chunk_size, len(text))
            chunk_text = text[pos:chunk_end].strip()
            
            if not chunk_text:
                pos += chunk_size - overlap
                continue

            # 找到该chunk所属的章节
            chapter = self._find_chapter_for_position(pos, chapters)

            chunk_id = f"{novel.id}_{chunk_idx}"
            payload = ChunkPayload(
                id=chunk_id,
                content=chunk_text,
                novel_id=novel.id,
                novel_title=novel.title,
                chapter_id=chapter.id if chapter else None,
                chapter_title=chapter.title if chapter else None,
                chapter_number=chapter.chapter_number if chapter else None,
                paragraph_index=chunk_idx,
                start_position=pos,
            )
            chunks.append(payload)
            chunk_texts.append(chunk_text)
            
            chunk_idx += 1
            pos += chunk_size - overlap

        if not chunks:
            logger.warning(f"No chunks created for novel {novel.id}")
            return
        
        # 🔥 元数据提取阶段
        if progress_callback:
            await progress_callback(0.35, "开始提取文本元数据")
        
        logger.info(f"Extracting metadata for {len(chunks)} chunks")
        metadata_list = await self.metadata_service.extract_metadata_batch(
            chunk_texts,
            batch_size=5  # 并发批次大小
        )
        
        # 将元数据附加到chunk
        for chunk, metadata in zip(chunks, metadata_list):
            if metadata:
                chunk.characters = metadata.characters
                chunk.keywords = metadata.keywords
                chunk.summary = metadata.summary
                chunk.scene_type = metadata.scene_type
                chunk.emotional_tone = metadata.emotional_tone
        
        successful_extractions = sum(1 for m in metadata_list if m is not None)
        logger.info(f"Metadata extraction completed: {successful_extractions}/{len(chunks)} successful")
        
        if progress_callback:
            await progress_callback(0.4, f"元数据提取完成 ({successful_extractions}/{len(chunks)})")

        # 使用配置的batch_size进行批量embedding
        batch_size = settings.EMBEDDING_BATCH_SIZE
        total_chunks = len(chunk_texts)
        logger.info(f"Starting vectorization of {total_chunks} chunks with batch_size={batch_size}")

        for batch_idx in range(0, total_chunks, batch_size):
            batch_texts = chunk_texts[batch_idx : batch_idx + batch_size]
            batch_chunks = chunks[batch_idx : batch_idx + batch_size]

            try:
                # 记录每个batch的文本长度，方便调试
                max_len = max(len(t) for t in batch_texts)
                batch_num = batch_idx//batch_size + 1
                logger.debug(f"Batch {batch_num}: {len(batch_texts)} texts, max_len={max_len}")
                
                # 调用embedding API并获取token使用统计
                embedding_result = await self.rag.embed_texts(batch_texts)
                await self.rag.upsert_chunks(batch_chunks, embedding_result.vectors)
                
                # 累计token消耗
                total_api_calls += 1
                total_tokens_used += embedding_result.usage.total_tokens
                
                logger.info(
                    f"Batch {batch_num} completed: "
                    f"tokens={embedding_result.usage.total_tokens}, "
                    f"累计tokens={total_tokens_used}, "
                    f"API调用={total_api_calls}"
                )
            except Exception as e:
                logger.error(f"Failed to embed batch {batch_idx//batch_size + 1}: {e}")
                raise

            if progress_callback:
                progress = 0.4 + 0.6 * min(batch_idx + batch_size, total_chunks) / total_chunks
                completed = min(batch_idx + batch_size, total_chunks)
                # 在进度消息中包含token统计
                await progress_callback(
                    progress, 
                    f"向量化进度 {completed}/{total_chunks} (已用{total_tokens_used}tokens)"
                )

        # 计算费用（智谱AI embedding-3: 0.5元/百万tokens）
        EMBEDDING_PRICE_PER_MILLION = 0.5
        estimated_cost = (total_tokens_used / 1_000_000) * EMBEDDING_PRICE_PER_MILLION
        
        # 更新novel的token统计
        novel.embedding_tokens_used = total_tokens_used
        novel.total_tokens_used = total_tokens_used  # 目前只有embedding，后续可能加上chat
        novel.api_calls_count = total_api_calls
        novel.estimated_cost = round(estimated_cost, 4)
        await self.session.flush()
        
        logger.info(
            f"Vectorized {len(chunks)} chunks for novel {novel.id}: "
            f"total_tokens={total_tokens_used}, "
            f"api_calls={total_api_calls}, "
            f"estimated_cost=¥{estimated_cost:.4f}"
        )

    def _find_chapter_for_position(self, position: int, chapters: List[Chapter]) -> Chapter | None:
        for chapter in chapters:
            if chapter.start_position <= position < chapter.end_position:
                return chapter
        return None


__all__ = ["TextProcessingService"]

