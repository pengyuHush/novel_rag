import Dexie, { Table } from 'dexie';
import type { Novel, SearchHistory, CharacterGraph } from '../types';

// 定义数据库类
export class NovelDatabase extends Dexie {
  novels!: Table<Novel, string>;
  searchHistory!: Table<SearchHistory, string>;
  characterGraphs!: Table<CharacterGraph, string>;

  constructor() {
    super('NovelRAGDatabase');
    
    this.version(1).stores({
      novels: 'id, title, importDate',
      searchHistory: 'id, timestamp',
      characterGraphs: 'novelId'
    });
  }
}

// 创建数据库实例
export const db = new NovelDatabase();

// 数据库操作辅助函数
export const dbUtils = {
  // 添加小说
  async addNovel(novel: Novel) {
    return await db.novels.add(novel);
  },

  // 获取所有小说
  async getAllNovels() {
    return await db.novels.toArray();
  },

  // 根据ID获取小说
  async getNovelById(id: string) {
    return await db.novels.get(id);
  },

  // 更新小说
  async updateNovel(id: string, changes: Partial<Novel>) {
    return await db.novels.update(id, changes);
  },

  // 删除小说
  async deleteNovel(id: string) {
    await db.novels.delete(id);
    await db.characterGraphs.delete(id);
  },

  // 添加搜索历史
  async addSearchHistory(history: SearchHistory) {
    return await db.searchHistory.add(history);
  },

  // 获取搜索历史
  async getSearchHistory(limit: number = 20) {
    return await db.searchHistory
      .orderBy('timestamp')
      .reverse()
      .limit(limit)
      .toArray();
  },

  // 清空搜索历史
  async clearSearchHistory() {
    return await db.searchHistory.clear();
  },

  // 删除单条搜索历史
  async deleteSearchHistory(id: string) {
    return await db.searchHistory.delete(id);
  },

  // 保存人物关系图谱
  async saveCharacterGraph(graph: CharacterGraph) {
    return await db.characterGraphs.put(graph);
  },

  // 获取人物关系图谱
  async getCharacterGraph(novelId: string) {
    return await db.characterGraphs.get(novelId);
  },

  // 获取存储空间使用情况（估算）
  async getStorageInfo() {
    const novels = await db.novels.toArray();
    const totalSize = novels.reduce((sum, novel) => sum + novel.fileSize, 0);
    const novelCount = novels.length;
    const totalWords = novels.reduce((sum, novel) => sum + novel.wordCount, 0);
    
    return {
      novelCount,
      totalWords,
      totalSize,
      formattedSize: formatFileSize(totalSize)
    };
  }
};

// 文件大小格式化函数
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// 字数格式化函数
export function formatWordCount(count: number): string {
  if (count < 10000) {
    return count + '字';
  }
  return Math.round(count / 10000 * 10) / 10 + '万字';
}

