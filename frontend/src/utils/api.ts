import type {
  Novel,
  Chapter,
  SearchResult,
  CharacterGraph,
  NovelProcessingStatus,
  Reference
} from '../types';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 通用请求函数
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData.code
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${error.message}`, 0, 'NETWORK_ERROR');
  }
}

// 自定义错误类
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// 小说管理API
export const novelAPI = {
  // 获取所有小说
  async getAllNovels(): Promise<Novel[]> {
    return apiRequest<Novel[]>('/novels');
  },

  // 获取单个小说详情
  async getNovel(id: string): Promise<Novel> {
    return apiRequest<Novel>(`/novels/${id}`);
  },

  // 上传小说文件
  async uploadNovel(file: File): Promise<{ novelId: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/novels`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `Upload failed: ${response.statusText}`,
        response.status
      );
    }

    return response.json();
  },

  // 更新小说信息
  async updateNovel(id: string, updates: Partial<Novel>): Promise<Novel> {
    return apiRequest<Novel>(`/novels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // 删除小说
  async deleteNovel(id: string): Promise<void> {
    return apiRequest<void>(`/novels/${id}`, {
      method: 'DELETE',
    });
  },

  // 获取小说处理状态
  async getProcessingStatus(id: string): Promise<NovelProcessingStatus> {
    return apiRequest<NovelProcessingStatus>(`/novels/${id}/status`);
  },

  // 获取小说章节列表
  async getChapters(novelId: string): Promise<Chapter[]> {
    return apiRequest<Chapter[]>(`/novels/${novelId}/chapters`);
  },

  // 获取单个章节内容
  async getChapter(novelId: string, chapterId: string): Promise<Chapter & { content: string }> {
    return apiRequest<Chapter & { content: string }>(`/novels/${novelId}/chapters/${chapterId}`);
  }
};

// 搜索和问答API
export const searchAPI = {
  // 执行搜索
  async search(params: {
    query: string;
    novelIds?: string[];
    mode?: 'keyword' | 'semantic';
    topK?: number;
  }): Promise<SearchResult> {
    const queryParams = new URLSearchParams();
    queryParams.append('query', params.query);

    if (params.novelIds && params.novelIds.length > 0) {
      params.novelIds.forEach(id => queryParams.append('novelIds', id));
    }

    if (params.mode) {
      queryParams.append('mode', params.mode);
    }

    if (params.topK) {
      queryParams.append('topK', params.topK.toString());
    }

    return apiRequest<SearchResult>(`/search?${queryParams.toString()}`);
  }
};

// 人物关系图谱API
export const graphAPI = {
  // 获取人物关系图谱
  async getGraph(novelId: string): Promise<CharacterGraph> {
    return apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
  },

  // 生成人物关系图谱
  async generateGraph(novelId: string): Promise<{ taskId: string }> {
    return apiRequest<{ taskId: string }>(`/novels/${novelId}/graph`, {
      method: 'POST',
    });
  },

  // 删除人物关系图谱
  async deleteGraph(novelId: string): Promise<void> {
    return apiRequest<void>(`/novels/${novelId}/graph`, {
      method: 'DELETE',
    });
  },

  // 获取人物列表
  async getCharacters(novelId: string): Promise<CharacterGraph['characters']> {
    const graph = await apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
    return graph.characters;
  }
};

// 工具函数
export const apiUtils = {
  // 文件大小格式化
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },

  // 字数格式化
  formatWordCount(count: number): string {
    if (count < 10000) {
      return count + '字';
    }
    return Math.round(count / 10000 * 10) / 10 + '万字';
  },

  // 获取小说统计信息
  async getStorageInfo(): Promise<{
    novelCount: number;
    totalWords: number;
    totalSize: number;
    formattedSize: string;
  }> {
    const novels = await novelAPI.getAllNovels();
    const novelCount = novels.length;
    const totalWords = novels.reduce((sum, novel) => sum + novel.wordCount, 0);

    // 估算文件大小（假设平均每个字符占用2字节）
    const totalSize = totalWords * 2;

    return {
      novelCount,
      totalWords,
      totalSize,
      formattedSize: this.formatFileSize(totalSize)
    };
  },

  // 轮询任务状态
  async pollStatus(
    novelId: string,
    onProgress?: (status: NovelProcessingStatus) => void,
    interval: number = 2000
  ): Promise<NovelProcessingStatus> {
    while (true) {
      const status = await novelAPI.getProcessingStatus(novelId);

      if (onProgress) {
        onProgress(status);
      }

      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }

      // 等待指定时间间隔后继续轮询
      await new Promise(resolve => setTimeout(resolve, interval));
    }
  }
};