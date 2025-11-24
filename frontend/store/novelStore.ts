/**
 * 小说状态管理
 * 使用Zustand进行状态管理
 */

import { create } from 'zustand';
import type { NovelListItem } from '@/types/api';

interface NovelState {
  // 状态
  novels: NovelListItem[];
  selectedNovelIds: number[];  // 改为数组支持多选
  isLoading: boolean;
  error: string | null;

  // Actions
  setNovels: (novels: NovelListItem[]) => void;
  setSelectedNovels: (ids: number[]) => void;
  toggleNovelSelection: (id: number) => void;
  addNovel: (novel: NovelListItem) => void;
  updateNovel: (id: number, data: Partial<NovelListItem>) => void;
  removeNovel: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  
  // 向后兼容的getter（用于需要单个ID的场景）
  selectedNovelId: number | null;
  setSelectedNovel: (id: number | null) => void;
}

const initialState = {
  novels: [],
  selectedNovelIds: [],
  isLoading: false,
  error: null,
};

export const useNovelStore = create<NovelState>((set, get) => ({
  ...initialState,

  setNovels: (novels) => set({ novels }),

  setSelectedNovels: (ids) => set({ selectedNovelIds: ids }),

  toggleNovelSelection: (id) =>
    set((state) => {
      const ids = state.selectedNovelIds;
      if (ids.includes(id)) {
        return { selectedNovelIds: ids.filter((i) => i !== id) };
      } else {
        return { selectedNovelIds: [...ids, id] };
      }
    }),

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
      selectedNovelIds: state.selectedNovelIds.filter((i) => i !== id),
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () => set(initialState),

  // 向后兼容：单个选择的getter和setter
  get selectedNovelId() {
    const ids = get().selectedNovelIds;
    return ids.length > 0 ? ids[0] : null;
  },

  setSelectedNovel: (id) => {
    if (id === null) {
      set({ selectedNovelIds: [] });
    } else {
      set({ selectedNovelIds: [id] });
    }
  },
}));

// 选择器
export const selectSelectedNovel = (state: NovelState) =>
  state.novels.find((n) => n.id === state.selectedNovelId);

