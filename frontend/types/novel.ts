/**
 * 小说相关类型定义
 */

export enum IndexStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum FileFormat {
  TXT = 'txt',
  EPUB = 'epub',
}

export interface Novel {
  id: number;
  title: string;
  author?: string;
  total_chars: number;
  total_chapters: number;
  index_status: IndexStatus;
  index_progress: number;
  file_format: FileFormat;
  total_chunks: number;
  total_entities: number;
  total_relations: number;
  embedding_tokens: number;
  upload_date: string;
  indexed_date?: string;
  created_at: string;
  updated_at: string;
}

export interface NovelListItem {
  id: number;
  title: string;
  author?: string;
  total_chars: number;
  total_chapters: number;
  index_status: IndexStatus;
  index_progress: number;
  file_format: FileFormat;
  upload_date: string;
}

export interface NovelProgress {
  novel_id: number;
  status: IndexStatus;
  progress: number;
  current_chapter?: number;
  total_chapters: number;
  message: string;
}

export interface UploadNovelRequest {
  title: string;
  author?: string;
  file: File;
}

