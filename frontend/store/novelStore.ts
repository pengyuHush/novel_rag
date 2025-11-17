/**
 * 小说状态管理
 * 使用Zustand进行状态管理
 */

import { create } from 'zustand';
import type { NovelListItem } from '@/types/api';

interface NovelState {
  // 状态
  novels: NovelListItem[];
  selectedNovelId: number | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setNovels: (novels: NovelListItem[]) => void;
  setSelectedNovel: (id: number | null) => void;
  addNovel: (novel: NovelListItem) => void;
  updateNovel: (id: number, data: Partial<NovelListItem>) => void;
  removeNovel: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  novels: [],
  selectedNovelId: null,
  isLoading: false,
  error: null,
};

export const useNovelStore = create<NovelState>((set) => ({
  ...initialState,

  setNovels: (novels) => set({ novels }),

  setSelectedNovel: (id) => set({ selectedNovelId: id }),

  addNovel: (novel) =>
    set((state) => ({
      novels: [...state.novels, novel],
    })),

  updateNovel: (id, data) =>
    set((state) => ({
      novels: state.novels.map((novel) =>
        novel.id === id ? { ...novel, ...data } : novel
      ),
    })),

  removeNovel: (id) =>
    set((state) => ({
      novels: state.novels.filter((novel) => novel.id !== id),
      selectedNovelId: state.selectedNovelId === id ? null : state.selectedNovelId,
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () => set(initialState),
}));

// 选择器
export const selectSelectedNovel = (state: NovelState) =>
  state.novels.find((n) => n.id === state.selectedNovelId);

