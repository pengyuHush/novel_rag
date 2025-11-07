import { create } from 'zustand';
import type { Novel, SearchResult, NovelProcessingStatus, SearchHistory } from '../types';

interface AppState {
  // 小说列表
  novels: Novel[];
  setNovels: (novels: Novel[]) => void;
  addNovel: (novel: Novel) => void;
  updateNovel: (id: string, novel: Partial<Novel>) => void;
  removeNovel: (id: string) => void;

  // 当前选中的小说
  selectedNovelIds: string[];
  setSelectedNovelIds: (ids: string[]) => void;

  // 当前搜索结果
  currentSearchResult: SearchResult | null;
  setCurrentSearchResult: (result: SearchResult | null) => void;

  // 最近搜索查询（简单存储，不包含结果）- 保留用于兼容性
  recentQueries: string[];
  addRecentQuery: (query: string) => void;
  clearRecentQueries: () => void;

  // 历史搜索记录（完整记录，包含答案）
  searchHistory: SearchHistory[];
  addSearchHistory: (history: SearchHistory) => void;
  removeSearchHistory: (id: string) => void;
  clearSearchHistory: () => void;
  loadSearchHistoryItem: (history: SearchHistory) => void;

  // 加载状态
  loading: boolean;
  setLoading: (loading: boolean) => void;

  // 搜索状态
  searching: boolean;
  setSearching: (searching: boolean) => void;

  // 存储统计
  storageInfo: {
    novelCount: number;
    totalWords: number;
    totalSize: number;
    formattedSize: string;
  };
  setStorageInfo: (info: AppState['storageInfo']) => void;

  // 小说处理状态跟踪
  processingStatuses: Record<string, NovelProcessingStatus>;
  setProcessingStatus: (novelId: string, status: NovelProcessingStatus) => void;
  removeProcessingStatus: (novelId: string) => void;
}

// 从localStorage加载搜索查询历史（简单）
const loadRecentQueries = (): string[] => {
  try {
    const saved = localStorage.getItem('recentQueries');
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Failed to load recent queries:', error);
    return [];
  }
};

// 保存搜索查询历史到localStorage
const saveRecentQueries = (queries: string[]) => {
  try {
    localStorage.setItem('recentQueries', JSON.stringify(queries));
  } catch (error) {
    console.error('Failed to save recent queries:', error);
  }
};

// 从localStorage加载完整搜索历史
const loadSearchHistory = (): SearchHistory[] => {
  try {
    const saved = localStorage.getItem('searchHistory');
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Failed to load search history:', error);
    return [];
  }
};

// 保存完整搜索历史到localStorage
const saveSearchHistory = (history: SearchHistory[]) => {
  try {
    // 只保留最近50条记录，避免localStorage过大
    const limitedHistory = history.slice(0, 50);
    localStorage.setItem('searchHistory', JSON.stringify(limitedHistory));
  } catch (error) {
    console.error('Failed to save search history:', error);
  }
};

export const useStore = create<AppState>((set) => ({
  // 初始状态
  novels: [],
  selectedNovelIds: [],
  currentSearchResult: null,
  recentQueries: loadRecentQueries(),
  searchHistory: loadSearchHistory(),
  loading: false,
  searching: false,
  storageInfo: {
    novelCount: 0,
    totalWords: 0,
    totalSize: 0,
    formattedSize: '0 B'
  },
  processingStatuses: {},

  // Actions
  setNovels: (novels) => set({ novels }),

  addNovel: (novel) => set((state) => ({
    novels: [...state.novels, novel]
  })),

  updateNovel: (id, updatedNovel) => set((state) => ({
    novels: state.novels.map((novel) =>
      novel.id === id ? { ...novel, ...updatedNovel } : novel
    )
  })),

  removeNovel: (id) => set((state) => {
    const newNovels = state.novels.filter((novel) => novel.id !== id);
    const newSelectedIds = state.selectedNovelIds.filter(selectedId => selectedId !== id);
    const newProcessingStatuses = { ...state.processingStatuses };
    delete newProcessingStatuses[id];

    return {
      novels: newNovels,
      selectedNovelIds: newSelectedIds,
      processingStatuses: newProcessingStatuses
    };
  }),

  setSelectedNovelIds: (ids) => set({ selectedNovelIds: ids }),

  setCurrentSearchResult: (result) => set({ currentSearchResult: result }),

  addRecentQuery: (query) => set((state) => {
    if (!query.trim()) return state;

    const filtered = state.recentQueries.filter(q => q !== query);
    const newQueries = [query, ...filtered].slice(0, 10); // 只保留最近10条查询

    saveRecentQueries(newQueries);
    return { recentQueries: newQueries };
  }),

  clearRecentQueries: () => {
    saveRecentQueries([]);
    set({ recentQueries: [] });
  },

  // 历史搜索记录管理
  addSearchHistory: (history) => set((state) => {
    // 检查是否已存在相同的查询（避免重复）
    const filtered = state.searchHistory.filter(h => h.id !== history.id);
    const newHistory = [history, ...filtered];
    
    saveSearchHistory(newHistory);
    return { searchHistory: newHistory };
  }),

  removeSearchHistory: (id) => set((state) => {
    const newHistory = state.searchHistory.filter(h => h.id !== id);
    saveSearchHistory(newHistory);
    return { searchHistory: newHistory };
  }),

  clearSearchHistory: () => {
    saveSearchHistory([]);
    set({ searchHistory: [] });
  },

  loadSearchHistoryItem: (history) => set((state) => {
    // 恢复历史记录到当前搜索状态
    return {
      currentSearchResult: {
        query: history.query,
        answer: history.answer,
        references: history.references,
        elapsed: history.elapsed,
        tokenStats: history.tokenStats
      },
      selectedNovelIds: history.selectedNovelIds
    };
  }),

  setLoading: (loading) => set({ loading }),

  setSearching: (searching) => set({ searching }),

  setStorageInfo: (info) => set({ storageInfo: info }),

  setProcessingStatus: (novelId, status) => set((state) => ({
    processingStatuses: {
      ...state.processingStatuses,
      [novelId]: status
    }
  })),

  removeProcessingStatus: (novelId) => set((state) => {
    const newStatuses = { ...state.processingStatuses };
    delete newStatuses[novelId];
    return { processingStatuses: newStatuses };
  })
}));

