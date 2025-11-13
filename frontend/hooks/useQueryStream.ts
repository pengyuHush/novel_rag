/**
 * WebSocket流式查询Hook
 */

import { useState, useCallback, useRef } from 'react';
import { apiClient } from '@/lib/api';
import { StreamMessage, Citation } from '@/types/query';

interface UseQueryStreamResult {
  answer: string;
  stage: string;
  progress: number;
  citations: Citation[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  sendQuery: (novelId: number, query: string, model?: string) => void;
  disconnect: () => void;
}

export const useQueryStream = (): UseQueryStreamResult => {
  const [answer, setAnswer] = useState('');
  const [stage, setStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsLoading(false);
  }, []);

  const sendQuery = useCallback(
    (novelId: number, query: string, model: string = 'glm-4') => {
      // 重置状态
      setAnswer('');
      setStage('');
      setProgress(0);
      setCitations([]);
      setError(null);
      setIsLoading(true);

      // 断开之前的连接
      disconnect();

      try {
        const ws = apiClient.createQueryStream(
          novelId,
          query,
          model,
          (message: StreamMessage) => {
            setIsConnected(true);
            setIsLoading(true);
            setStage(message.stage);
            setProgress(message.progress || 0);

            if (message.error) {
              setError(message.error);
              setIsLoading(false);
              return;
            }

            // 处理增量内容
            if (message.is_delta && message.content) {
              setAnswer((prev) => prev + message.content);
            } else if (message.content && !message.is_delta) {
              setAnswer(message.content);
            }

            // 处理引用
            if (message.citations) {
              setCitations(message.citations);
            }

            // 完成
            if (message.done) {
              setIsLoading(false);
              setProgress(1);
            }
          },
          (error) => {
            setError(error.message || 'WebSocket连接错误');
            setIsLoading(false);
            setIsConnected(false);
          },
          () => {
            setIsConnected(false);
            if (!error) {
              setIsLoading(false);
            }
          }
        );

        wsRef.current = ws;
      } catch (err: any) {
        setError(err.message || '创建连接失败');
        setIsLoading(false);
      }
    },
    [disconnect, error]
  );

  return {
    answer,
    stage,
    progress,
    citations,
    isConnected,
    isLoading,
    error,
    sendQuery,
    disconnect,
  };
};

