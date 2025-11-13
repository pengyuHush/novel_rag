/**
 * Zustand状态管理
 * 全局状态存储
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Novel } from '@/types/novel';

// ========================================
// 应用全局状态
// ========================================

interface AppState {
  // 当前选中的小说
  currentNovel: Novel | null;
  setCurrentNovel: (novel: Novel | null) => void;

  // 侧边栏折叠状态
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // 主题模式
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // 初始状态
      currentNovel: null,
      sidebarCollapsed: false,
      theme: 'light',

      // Actions
      setCurrentNovel: (novel) => set({ currentNovel: novel }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'app-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // 只持久化部分状态
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);

// ========================================
// 用户偏好设置
// ========================================

interface UserPreferencesState {
  // 默认模型
  defaultModel: 'glm-4-flash' | 'glm-4' | 'glm-4-plus' | 'glm-4-5' | 'glm-4-6';
  setDefaultModel: (model: UserPreferencesState['defaultModel']) => void;

  // API Key（前端仅用于测试，生产环境应后端管理）
  apiKey: string;
  setApiKey: (key: string) => void;

  // 查询历史记录
  queryHistory: Array<{
    novelId: number;
    query: string;
    timestamp: number;
  }>;
  addQueryHistory: (item: { novelId: number; query: string }) => void;
  clearQueryHistory: () => void;
}

export const useUserPreferences = create<UserPreferencesState>()(
  persist(
    (set) => ({
      // 初始状态
      defaultModel: 'glm-4',
      apiKey: '',
      queryHistory: [],

      // Actions
      setDefaultModel: (model) => set({ defaultModel: model }),
      setApiKey: (key) => set({ apiKey: key }),
      addQueryHistory: (item) =>
        set((state) => ({
          queryHistory: [
            { ...item, timestamp: Date.now() },
            ...state.queryHistory.slice(0, 49), // 保留最近50条
          ],
        })),
      clearQueryHistory: () => set({ queryHistory: [] }),
    }),
    {
      name: 'user-preferences',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

// ========================================
// 查询状态
// ========================================

interface QueryState {
  // 当前查询状态
  isQuerying: boolean;
  setIsQuerying: (isQuerying: boolean) => void;

  // 当前查询阶段
  currentStage: 'idle' | 'understand' | 'retrieve' | 'generate' | 'verify' | 'complete';
  setCurrentStage: (stage: QueryState['currentStage']) => void;

  // 流式响应文本
  streamingText: string;
  appendStreamingText: (text: string) => void;
  clearStreamingText: () => void;

  // 最终结果
  finalResult: any | null;
  setFinalResult: (result: any) => void;

  // 重置查询状态
  resetQueryState: () => void;
}

export const useQueryStore = create<QueryState>()((set) => ({
  // 初始状态
  isQuerying: false,
  currentStage: 'idle',
  streamingText: '',
  finalResult: null,

  // Actions
  setIsQuerying: (isQuerying) => set({ isQuerying }),
  setCurrentStage: (stage) => set({ currentStage: stage }),
  appendStreamingText: (text) =>
    set((state) => ({ streamingText: state.streamingText + text })),
  clearStreamingText: () => set({ streamingText: '' }),
  setFinalResult: (result) => set({ finalResult: result }),
  resetQueryState: () =>
    set({
      isQuerying: false,
      currentStage: 'idle',
      streamingText: '',
      finalResult: null,
    }),
}));

