/**
 * 查询状态管理
 * 管理智能问答的实时状态
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  QueryStage,
  Citation,
  Contradiction,
  TokenStats,
  Confidence,
  QueryConfig,
} from '@/types/api';

interface QueryState {
  // 查询状态
  isQuerying: boolean;
  currentStage: QueryStage | null;
  stageProgress: number; // 0-1

  // 内容
  thinking: string; // 思考过程（累积）
  answer: string; // 最终答案（累积）
  citations: Citation[]; // 引用列表
  contradictions: Contradiction[]; // 矛盾检测结果

  // 元数据
  queryId: number | null;
  tokenStats: TokenStats | null;
  confidence: Confidence | null;
  responseTime: number | null;
  error: string | null;

  // 查询配置
  queryConfig: QueryConfig;

  // Actions
  startQuery: () => void;
  setStage: (stage: QueryStage, progress: number) => void;
  appendThinking: (delta: string) => void;
  appendAnswer: (delta: string) => void;
  setCitations: (citations: Citation[]) => void;
  setContradictions: (contradictions: Contradiction[]) => void;
  setTokenStats: (stats: TokenStats) => void;
  completeQuery: (queryId: number, confidence?: Confidence, responseTime?: number) => void;
  setError: (error: string) => void;
  reset: () => void;
  setQueryConfig: (config: Partial<QueryConfig>) => void;
  resetQueryConfig: () => void;
}

const defaultQueryConfig: QueryConfig = {
  top_k_retrieval: 30,
  top_k_rerank: 10,
  max_context_chunks: 10,
};

const initialState = {
  isQuerying: false,
  currentStage: null,
  stageProgress: 0,
  thinking: '',
  answer: '',
  citations: [],
  contradictions: [],
  queryId: null,
  tokenStats: null,
  confidence: null,
  responseTime: null,
  error: null,
  queryConfig: defaultQueryConfig,
};

export const useQueryStore = create<QueryState>()(
  persist(
    (set, get) => ({
      ...initialState,

      startQuery: () =>
        set({
          ...initialState,
          queryConfig: get().queryConfig, // 保留持久化的配置
          isQuerying: true,
        }),

      setStage: (stage, progress) =>
        set({
          currentStage: stage,
          stageProgress: progress,
        }),

      appendThinking: (delta) =>
        set((state) => ({
          thinking: state.thinking + delta,
        })),

      appendAnswer: (delta) =>
        set((state) => ({
          answer: state.answer + delta,
        })),

      setCitations: (citations) => set({ citations }),

      setContradictions: (contradictions) => set({ contradictions }),

      setTokenStats: (stats) => {
        console.log('Store setting tokenStats:', stats);
        set({ tokenStats: stats });
      },

      completeQuery: (queryId, confidence, responseTime) =>
        set({
          isQuerying: false,
          queryId,
          confidence: confidence || null,
          responseTime: responseTime || null,
        }),

      setError: (error) =>
        set({
          isQuerying: false,
          error,
        }),

      reset: () =>
        set((state) => ({
          ...initialState,
          queryConfig: state.queryConfig, // 保留持久化的配置
        })),

      setQueryConfig: (config) =>
        set((state) => ({
          queryConfig: { ...state.queryConfig, ...config },
        })),

      resetQueryConfig: () =>
        set({
          queryConfig: defaultQueryConfig,
        }),
    }),
    {
      name: 'query-config-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ queryConfig: state.queryConfig }), // 只持久化 queryConfig
    }
  )
);

// 选择器
export const selectIsGenerating = (state: QueryState) =>
  state.currentStage === 'generating' && state.isQuerying;

export const selectHasResults = (state: QueryState) =>
  state.answer.length > 0 || state.citations.length > 0;

