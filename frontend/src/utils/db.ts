// 注意：此文件已弃用，现在使用API调用代替IndexedDB存储
// 请使用 ../utils/api.ts 中的API函数

export const dbUtils = {
  // 抛出弃用警告
  addNovel: () => { throw new Error('dbUtils已弃用，请使用novelAPI.uploadNovel()'); },
  getAllNovels: () => { throw new Error('dbUtils已弃用，请使用novelAPI.getAllNovels()'); },
  getNovelById: () => { throw new Error('dbUtils已弃用，请使用novelAPI.getNovel()'); },
  updateNovel: () => { throw new Error('dbUtils已弃用，请使用novelAPI.updateNovel()'); },
  deleteNovel: () => { throw new Error('dbUtils已弃用，请使用novelAPI.deleteNovel()'); },
  addSearchHistory: () => { throw new Error('搜索历史功能已移除'); },
  getSearchHistory: () => { throw new Error('搜索历史功能已移除'); },
  clearSearchHistory: () => { throw new Error('搜索历史功能已移除'); },
  deleteSearchHistory: () => { throw new Error('搜索历史功能已移除'); },
  saveCharacterGraph: () => { throw new Error('dbUtils已弃用，请使用graphAPI.generateGraph()'); },
  getCharacterGraph: () => { throw new Error('dbUtils已弃用，请使用graphAPI.getGraph()'); },
  getStorageInfo: () => { throw new Error('dbUtils已弃用，请使用apiUtils.getStorageInfo()'); }
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

