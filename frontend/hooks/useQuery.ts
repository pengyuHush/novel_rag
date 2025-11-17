/**
 * WebSocket流式查询Hook
 * 管理查询WebSocket连接和状态更新
 */

'use client';

import { useCallback, useRef } from 'react';
import { useQueryStore } from '@/store/queryStore';
import { createQueryWebSocket, QueryWebSocket } from '@/lib/websocket';
import { toast } from 'sonner';
import type { ModelType } from '@/types/api';

export function useQueryWebSocket() {
  const wsRef = useRef<QueryWebSocket | null>(null);
  const {
    startQuery,
    setStage,
    appendThinking,
    appendAnswer,
    setCitations,
    setContradictions,
    setTokenStats,
    completeQuery,
    setError,
  } = useQueryStore();

  const executeQuery = useCallback(
    (novelId: number, query: string, model: ModelType) => {
      // 关闭之前的连接
      if (wsRef.current) {
        wsRef.current.close();
      }

      // 重置状态并开始查询
      startQuery();

      // 创建新的WebSocket连接
      wsRef.current = createQueryWebSocket(novelId, query, model, {
        onStage: (stage, progress) => {
          setStage(stage, progress);
        },

        onThinking: (thinkingDelta) => {
          appendThinking(thinkingDelta);
        },

        onAnswer: (answerDelta) => {
          appendAnswer(answerDelta);
        },

        onCitations: (citations) => {
          setCitations(citations);
        },

        onTokenStats: (stats) => {
          setTokenStats(stats);
        },

        onComplete: (queryId) => {
          completeQuery(queryId);
          toast.success('查询完成');
        },

        onError: (error) => {
          setError(error);
          toast.error(error || '查询失败');
        },
      });
    },
    [
      startQuery,
      setStage,
      appendThinking,
      appendAnswer,
      setCitations,
      setContradictions,
      setTokenStats,
      completeQuery,
      setError,
    ]
  );

  const cancelQuery = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      toast.info('已取消查询');
    }
  }, []);

  return {
    executeQuery,
    cancelQuery,
  };
}

