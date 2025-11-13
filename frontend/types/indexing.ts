/**
 * 索引相关类型定义
 */

export enum IndexStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface IndexingProgressMessage {
  novel_id: number;
  status: IndexStatus;
  progress: number; // 0-1
  current_chapter: number;
  total_chapters: number;
  message: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'progress' | 'complete' | 'error';
  progress?: number;
  task?: string;
  novel_id?: number;
  message?: string;
}

