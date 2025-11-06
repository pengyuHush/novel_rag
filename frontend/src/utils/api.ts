import type {
  Novel,
  Chapter,
  ChapterContent,
  SearchResult,
  CharacterGraph,
  NovelProcessingStatus,
  Reference
} from '../types';
import { mockNovelAPI, mockSearchAPI, mockGraphAPI } from './mockApi';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true';

// 启动时输出配置信息
console.log('🔧 API 配置信息:');
console.log('  - API_BASE_URL:', API_BASE_URL);
console.log('  - USE_MOCK_API:', USE_MOCK_API);
console.log('  - VITE_USE_MOCK_API (raw):', import.meta.env.VITE_USE_MOCK_API);
console.log('  - 模式:', USE_MOCK_API ? '🎭 Mock 模式' : '🌐 真实 API 模式');

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
    throw new APIError(`Network error: ${(error as Error).message}`, 0, 'NETWORK_ERROR');
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
    if (USE_MOCK_API) {
      return mockNovelAPI.getAllNovels();
    }
    const response = await apiRequest<{ data: Novel[]; pagination: any }>('/novels?page=1&page_size=1000');
    return response.data;
  },

  // 获取单个小说详情
  async getNovel(id: string): Promise<Novel> {
    if (USE_MOCK_API) {
      return mockNovelAPI.getNovel(id);
    }
    return apiRequest<Novel>(`/novels/${id}`);
  },

  // 创建小说记录（步骤1：创建元数据）
  async createNovel(metadata: {
    title: string;
    author?: string;
    description?: string;
    tags?: string[];
  }): Promise<Novel> {
    if (USE_MOCK_API) {
      throw new Error('Mock 模式请使用 uploadNovel 方法一次性上传');
    }
    // 后端直接返回 NovelDetail，不是 { message, novel } 包装
    return apiRequest<Novel>('/novels', {
      method: 'POST',
      body: JSON.stringify(metadata),
    });
  },

  // 上传小说文件（步骤2：上传文本内容）
  async uploadNovelFile(novelId: string, file: File): Promise<{ message: string; status: string }> {
    if (USE_MOCK_API) {
      throw new Error('Mock 模式请使用 uploadNovel 方法一次性上传');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/novels/${novelId}/upload`, {
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

  // 便捷方法：一步完成小说上传（供组件使用）
  async uploadNovel(file: File, metadata: {
    title: string;
    author?: string;
    description?: string;
    tags?: string[];
  }): Promise<string> {
    if (USE_MOCK_API) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', metadata.title);
      if (metadata.author) formData.append('author', metadata.author);
      if (metadata.description) formData.append('description', metadata.description);
      if (metadata.tags) formData.append('tags', metadata.tags.join(','));
      
      const result = await mockNovelAPI.uploadNovel(formData);
      return result.novelId;
    }

    // 先创建小说记录
    const novel = await this.createNovel(metadata);
    
    // 再上传文件
    await this.uploadNovelFile(novel.id, file);
    
    return novel.id;
  },

  // 更新小说信息
  async updateNovel(id: string, updates: Partial<Novel>): Promise<Novel> {
    if (USE_MOCK_API) {
      return mockNovelAPI.updateNovel(id, updates);
    }
    return apiRequest<Novel>(`/novels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // 删除小说
  async deleteNovel(id: string): Promise<void> {
    if (USE_MOCK_API) {
      return mockNovelAPI.deleteNovel(id);
    }
    return apiRequest<void>(`/novels/${id}`, {
      method: 'DELETE',
    });
  },

  // 获取小说处理状态
  async getProcessingStatus(id: string): Promise<NovelProcessingStatus> {
    if (USE_MOCK_API) {
      return mockNovelAPI.getProcessingStatus(id);
    }
    return apiRequest<NovelProcessingStatus>(`/novels/${id}/status`);
  },

  // 文件预验证（上传前快速检查文件是否合格）
  async validateFile(novelId: string, file: File): Promise<{
    valid: boolean;
    encoding?: string;
    wordCount?: number;
    chineseRatio?: number;
    estimatedChapters?: number;
    warnings: string[];
    errors: string[];
  }> {
    if (USE_MOCK_API) {
      // Mock 模式直接返回成功
      return {
        valid: true,
        encoding: 'UTF-8',
        wordCount: Math.floor(Math.random() * 500000) + 100000,
        chineseRatio: 0.95,
        estimatedChapters: Math.floor(Math.random() * 50) + 10,
        warnings: [],
        errors: []
      };
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/novels/${novelId}/validate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `Validation failed: ${response.statusText}`,
        response.status
      );
    }

    return response.json();
  },

  // 获取小说章节列表
  async getChapters(novelId: string): Promise<Chapter[]> {
    if (USE_MOCK_API) {
      return mockNovelAPI.getChapters(novelId);
    }
    return apiRequest<Chapter[]>(`/novels/${novelId}/chapters`);
  },

  // 注意：获取章节内容请使用 chapterAPI.getChapterContent(novelId, chapterId)
  // 该方法返回简单的章节元数据，不包含完整内容
};

// 搜索和问答API
export const searchAPI = {
  // 执行搜索（使用POST方法 + JSON Body）
  async search(params: {
    query: string;
    novelIds?: string[];
    searchMode?: 'keyword' | 'semantic';
    topK?: number;
    includeReferences?: boolean;
    saveHistory?: boolean;
  }): Promise<SearchResult> {
    if (USE_MOCK_API) {
      return mockSearchAPI.search(params.query, params.novelIds || []);
    }
    return apiRequest<SearchResult>('/search', {
      method: 'POST',
      body: JSON.stringify({
        query: params.query,
        novelIds: params.novelIds || [],
        searchMode: params.searchMode || 'semantic',
        topK: params.topK || 5,
        includeReferences: params.includeReferences !== false,
        saveHistory: params.saveHistory !== false,
      }),
    });
  }
};

// 章节API
export const chapterAPI = {
  // 获取章节内容
  async getChapterContent(novelId: string, chapterId: string): Promise<{ content: string }> {
    if (USE_MOCK_API) {
      // Mock实现：返回模拟章节内容
      return {
        content: `这是章节 ${chapterId} 的内容。\n\n` +
                 `在实际应用中，这里会显示从小说文件中读取的真实章节内容。\n\n` +
                 `内容会根据章节的起始位置和结束位置从原文中提取。`
      };
    }
    return apiRequest<{ content: string }>(`/novels/${novelId}/chapters/${chapterId}/content`, {
      method: 'GET',
    });
  }
};

// 人物关系图谱API
export const graphAPI = {
  // 获取人物关系图谱
  async getGraph(novelId: string): Promise<CharacterGraph> {
    if (USE_MOCK_API) {
      return mockGraphAPI.getGraph(novelId);
    }
    return apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
  },

  // 生成人物关系图谱
  async generateGraph(novelId: string): Promise<{ taskId: string; message?: string }> {
    if (USE_MOCK_API) {
      return mockGraphAPI.generateGraph(novelId);
    }
    return apiRequest<{ taskId: string }>(`/novels/${novelId}/graph`, {
      method: 'POST',
    });
  },

  // 删除人物关系图谱
  async deleteGraph(novelId: string): Promise<void> {
    if (USE_MOCK_API) {
      return mockGraphAPI.deleteGraph(novelId);
    }
    return apiRequest<void>(`/novels/${novelId}/graph`, {
      method: 'DELETE',
    });
  },

  // 获取人物列表
  async getCharacters(novelId: string): Promise<CharacterGraph['characters']> {
    if (USE_MOCK_API) {
      return mockGraphAPI.getCharacters(novelId);
    }
    const graph = await apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
    return graph.characters;
  }
};

// 系统管理API
export const systemAPI = {
  // 系统健康检查
  async checkHealth(): Promise<{
    status: string;
    version: string;
    services: Record<string, string>;
  }> {
    if (USE_MOCK_API) {
      return {
        status: 'healthy',
        version: '1.0.0-mock',
        services: {
          database: 'healthy',
          vector_db: 'healthy',
          llm: 'healthy'
        }
      };
    }
    return apiRequest('/health');
  },

  // 系统信息
  async getSystemInfo(): Promise<{
    version: string;
    features: string[];
    limits: {
      maxFileSize: number;
      maxNovels: number;
    };
  }> {
    if (USE_MOCK_API) {
      return {
        version: '1.0.0-mock',
        features: ['search', 'graph', 'reader'],
        limits: {
          maxFileSize: 10 * 1024 * 1024, // 10MB
          maxNovels: 100
        }
      };
    }
    return apiRequest('/system/info');
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
