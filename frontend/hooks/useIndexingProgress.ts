/**
 * 索引进度监听 Hook
 * 通过WebSocket实时接收索引进度更新
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { createProgressStream, WebSocketClient, WebSocketMessage } from '@/lib/websocket';

export interface ProgressData {
  novelId: number;
  progress: number; // 0.0 ~ 1.0
  message: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalChapters?: number;
  completedChapters?: number;
  totalChunks?: number;
}

export interface UseIndexingProgressOptions {
  novelId: number | null;
  enabled?: boolean;
  onComplete?: (data: ProgressData) => void;
  onError?: (error: string) => void;
}

export function useIndexingProgress({
  novelId,
  enabled = true,
  onComplete,
  onError,
}: UseIndexingProgressOptions) {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsClientRef = useRef<WebSocketClient | null>(null);

  // 处理WebSocket消息
  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      if (message.type === 'progress' && message.data) {
        const data: ProgressData = {
          novelId: message.data.novel_id,
          progress: message.data.progress,
          message: message.data.message,
          status: message.data.status,
          totalChapters: message.data.total_chapters,
          completedChapters: message.data.completed_chapters,
          totalChunks: message.data.total_chunks,
        };

        setProgressData(data);
        setError(null);

        // 如果完成，触发回调
        if (data.status === 'completed' && onComplete) {
          onComplete(data);
        }
      } else if (message.type === 'error') {
        const errorMsg = message.error || '未知错误';
        setError(errorMsg);
        onError?.(errorMsg);
      }
    },
    [onComplete, onError]
  );

  // 建立WebSocket连接
  useEffect(() => {
    if (!novelId || !enabled) {
      return;
    }

    const client = createProgressStream(novelId, {
      onOpen: () => {
        setIsConnected(true);
        setError(null);
      },
      onMessage: handleMessage,
      onError: (event) => {
        const errorMsg = 'WebSocket连接错误';
        setError(errorMsg);
        setIsConnected(false);
        onError?.(errorMsg);
      },
      onClose: (event) => {
        setIsConnected(false);
        // 如果不是正常关闭，显示错误
        if (event.code !== 1000 && event.code !== 1001) {
          const errorMsg = `连接关闭: ${event.reason || '未知原因'}`;
          setError(errorMsg);
        }
      },
      reconnect: true,
      reconnectDelay: 2000,
      maxReconnectAttempts: 5,
    });

    wsClientRef.current = client;

    // 清理函数
    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.close();
        wsClientRef.current = null;
      }
      setIsConnected(false);
    };
  }, [novelId, enabled, handleMessage, onError]);

  // 手动断开连接
  const disconnect = useCallback(() => {
    if (wsClientRef.current) {
      wsClientRef.current.close();
      wsClientRef.current = null;
    }
    setIsConnected(false);
  }, []);

  return {
    progressData,
    isConnected,
    error,
    disconnect,
  };
}

