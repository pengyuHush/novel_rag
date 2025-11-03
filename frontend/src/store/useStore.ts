import { create } from 'zustand';
import type { Novel, SearchHistory } from '../types';

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
  
  // 搜索历史
  searchHistory: SearchHistory[];
  setSearchHistory: (history: SearchHistory[]) => void;
  addSearchHistory: (item: SearchHistory) => void;
  
  // 加载状态
  loading: boolean;
  setLoading: (loading: boolean) => void;
  
  // 存储统计
  storageInfo: {
    novelCount: number;
    totalWords: number;
    totalSize: number;
    formattedSize: string;
  };
  setStorageInfo: (info: AppState['storageInfo']) => void;
}

export const useStore = create<AppState>((set) => ({
  // 初始状态
  novels: [],
  selectedNovelIds: [],
  searchHistory: [],
  loading: false,
  storageInfo: {
    novelCount: 0,
    totalWords: 0,
    totalSize: 0,
    formattedSize: '0 B'
  },
  
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
  
  removeNovel: (id) => set((state) => ({
    novels: state.novels.filter((novel) => novel.id !== id)
  })),
  
  setSelectedNovelIds: (ids) => set({ selectedNovelIds: ids }),
  
  setSearchHistory: (history) => set({ searchHistory: history }),
  
  addSearchHistory: (item) => set((state) => ({
    searchHistory: [item, ...state.searchHistory].slice(0, 20) // 只保留最近20条
  })),
  
  setLoading: (loading) => set({ loading }),
  
  setStorageInfo: (info) => set({ storageInfo: info })
}));

